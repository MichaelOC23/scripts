import debugpy
import os
import asyncio
import socket
import json
import asyncpg
import datetime
import uuid
from quart import Quart, session, jsonify
from quart_session import Session
from signal import SIGINT, SIGTERM
from dotenv import load_dotenv
import pyaudio
import threading
from typing import Optional, Callable

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
)
import setproctitle
from typing import Optional, Callable, Awaitable
import logging

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

# Suppress detailed asyncio task completion logs
asyncio.get_event_loop().set_debug(False)
logging.getLogger('asyncio').setLevel(logging.WARNING)


async def shutdown(signal, loop):
    print(f"Received exit signal {signal.name}...")
    stop_event.set()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
    AUDIOINFO_GLOBAL['recstate'] = "Not transcribing"

def get_audio_device_dict():
    p = pyaudio.PyAudio()

    AUDIOINFO_GLOBAL["default_input_device_info"]= p.get_default_input_device_info()['index']
    AUDIOINFO_GLOBAL["default_output_device_info"]= p.get_default_output_device_info()['index']
    AUDIOINFO_GLOBAL['device_count'] = p.get_device_count()

    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        AUDIOINFO_GLOBAL[f"#{i}-{dev['name']}"] = dev
    p.terminate()
            
    return AUDIOINFO_GLOBAL

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("0.0.0.0", port)) == 0


####################################
####      POSTGRESQL CLASS      ####
####################################
class PsqlSimpleStorage():
    def __init__(self ):
        self.connection_string = conn = os.environ.get('POSTGRES_AWS_PRODUCT_DB_CONN_STRING', 'POSTGRES: COULD NOT GET CONNECTION STRING')
        self.unique_initialization_id = uuid.uuid4()
        self.textlibrary_table = "textlibrary"   
        self.table_names = [self.textlibrary_table]
        self.default_table = self.textlibrary_table
        self.table_col_defs = {}

    async def get_connection(self):
        conn = await asyncpg.connect(self.connection_string)
        if not self.table_col_defs or self.table_col_defs == {}:
            self.table_col_defs = await self.get_column_types_dict(conn)
        return conn
    
    async def get_column_types_dict(self, conn):
        query = f"""SELECT table_name, column_name, data_type, udt_name
                    FROM information_schema.columns c 
                    WHERE c.table_name NOT LIKE 'pg%'
                    AND c.table_schema <> 'information_schema';"""
                
        column_types = await conn.fetch(query)
        
        # Organize the results in a dictionary
        column_types_by_table = {}
        for record in column_types:
            table_name = record['table_name']
            column_name = record['column_name']
            data_type = f"{record['udt_name']}"
            
            if table_name not in column_types_by_table:
                column_types_by_table[table_name] = {}
            
            column_types_by_table[table_name][column_name] = data_type
        
        with open("column_types_by_table.json", "w") as f:
            json.dump(column_types_by_table, f, indent=4)

        return column_types_by_table    
    
    def close_connection(self, conn):
        conn.close()
    
    def apply_upsert(self, base_row, new_row, merge_or_replace="MERGE"):
        
        def isnull_or_empty(value):
            if value is None or value == "" or value == [] or value == {}:
                return True
            return False
                
        
        # Replace the base row with the new row where there are existing values
        for key in base_row.keys():
            if new_row.get(key, None) is not None:  # A value exists in the new row
                if merge_or_replace == "MERGE":
                    if not isnull_or_empty(new_row[key]):  # The value is not empty or null
                        base_row[key] = new_row[key]
                
                elif merge_or_replace == "APPEND":
                    if isnull_or_empty(new_row[key]):
                        continue
                    if isnull_or_empty(base_row[key]):
                        base_row[key] = new_row[key]
                        
                    if isinstance(base_row[key], list):
                        if isinstance(new_row[key], list):
                            for item in new_row[key]:
                                if item not in base_row[key]:
                                    base_row[key].append(item)
                        else:
                            if new_row[key] not in base_row[key]:
                                base_row[key].append(new_row[key])
                    else:
                        base_row[key] = new_row[key]
                
                elif merge_or_replace == "REPLACE":
                    base_row[key] = new_row[key]  # Replace the value regardless of whether it's empty or null

        for key in new_row.keys():
            if base_row.get(key, None) is None:  # A value exists in the new row but not in the base row
                base_row[key] = new_row[key]  # Add the new value to the base row
        return base_row
            
    async def upsert_append_data(self, data_items, table_name=None):
        if table_name is None or table_name == "":
            table_name = self.default_table
        
        
        if not isinstance(data_items, list):
            data_items = [data_items]
        
        conn = await self.get_connection()
        
        id_to_soft_delete = ""
        
        # try:
        async with conn.transaction():
            table_def = self.table_col_defs.get(table_name, {})
            rows_to_upsert = []

            for item in data_items:
                existing_data = None
                row_to_upsert = {}
                if item.get('id', None) is not None:
                    # Fetch the current data for merging (using the ID field)
                    existing_data = await conn.fetchrow(f"""
                            SELECT * from {table_name} WHERE id = $1 AND iscurrent = TRUE""",
                            item['id'])

                elif item.get('rowcontext', None) is not None and item.get('uniquebuskey', None) is not None and existing_data is None:
                    # Fetch the current data for merging (using the rowcontext and uniquebuskey fields)
                    existing_data = await conn.fetchrow(f"""
                            SELECT * from {table_name} WHERE rowcontext = $1 AND uniquebuskey = $2 AND iscurrent = TRUE""",
                            item['rowcontext'], item['uniquebuskey'])

                if not existing_data:
                    # If no existing data, use incoming data as is
                    row_to_upsert = item.copy()
                else:
                    # Convert existing_data to a mutable dictionary
                    existing_data = dict(existing_data)
                    merge_or_replace = "APPEND"
                    row_to_upsert = self.apply_upsert(existing_data, item, merge_or_replace)

                rows_to_upsert.append(row_to_upsert)
                id_to_soft_delete = row_to_upsert.get('id', None)

            # Prepare the data for insertion
            columns = []
            placeholders = []
            values = []
            placeholder_index = 1
            for row in rows_to_upsert:
                row_values = []
                for key in row.keys():
                    if key in table_def.keys():
                        # print(f"Key: {key}, Value: {row[key]}")
                        columns.append(key)
                        if table_def[key] in ["uuid", "bool", "boolean", "numeric", "int", "bigint", "bigserial", "smallint", "text", "varchar", "timestamp", "date", "time"]:
                            placeholders.append(f"${placeholder_index}")
                            
                            # If the incoming value is a string and the column is a date, convert the string to a date
                            if table_def[key] == "date" and isinstance(row[key], str):
                                #Error handling if the date string is not a datetime object already
                                try:
                                    row_values.append(datetime.strptime(row[key], '%Y-%m-%d').date())
                                except:
                                    print(f"Error: {row[key]} is not a valid date string or date object on record {row}.")
                                    row_values.append(None)
                            else:
                                row_values.append(row[key])
                        
                        # JSONB must be dumped to a string        
                        elif table_def[key] == "jsonb":  # JSONB
                            placeholders.append(f"${placeholder_index}")
                            row_values.append(json.dumps(row[key]))
                        
                        # _JSONB must be dumped to a list of strings string
                        elif table_def[key] == "_jsonb":  # Array of JSONB
                            placeholders.append(f"${placeholder_index}::jsonb[]")
                            if isinstance(row[key], dict):
                                # Error handling if the value is a dictionary that hasn't been converted to a list of dictionaries
                                row_values.append([json.dumps(row[key])])
                            else:
                                row_values.append([json.dumps(item) for item in row[key]])
                        
                        else:
                            placeholders.append(f"${placeholder_index}")
                            row_values.append(row[key])
                        placeholder_index += 1
                    else:
                        print(f"\033[1;31;40mError: {key} is not a recognized data type. Please add it to the function: upsert_append_data \033[0m")
                values.extend(row_values)

            columns_str = ', '.join(columns)
            placeholders_str = ', '.join(placeholders)
            if id_to_soft_delete is not None and id_to_soft_delete != "":
                if merge_or_replace in ["REPLACE", "APPEND"]:
                    await self.delete_data([id_to_soft_delete], table_name=table_name)
            
            insert_query = f"""
                INSERT INTO {table_name} 
                ({columns_str})
                VALUES ({placeholders_str})
                ON CONFLICT (id) DO UPDATE
                SET {', '.join([f"{col} = EXCLUDED.{col}" for col in columns])}
            """
            print(f"Insert Query: {insert_query} \n values: {values}")
            await conn.execute(insert_query, *values)

            

        # except Exception as e:
        #     print("Error: ", e)
        #     raise

        # finally:
            # await conn.close()
                
    async def get_data(self, rowcontext=None, uniquebuskey=None, id=None, table_name=None):
    
        if table_name is None or table_name == "":
            table_name = self.default_table
        
        query = f"SELECT * FROM {table_name}"
        conditions = ["iscurrent = TRUE"]
        params = []
        
        if id:
            conditions.append(f"id = ${len(params) + 1}")
            params.append(id)
        
        if rowcontext:
            conditions.append(f"rowcontext = ${len(params) + 1}")
            params.append(rowcontext)
        
        if uniquebuskey:
            conditions.append(f"uniquebuskey = ${len(params) + 1}")
            params.append(uniquebuskey)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # try:
            
            conn = await self.get_connection()
            col_defs = self.table_col_defs.get(table_name, {})
            
            async with conn.transaction():
                all_records = await conn.fetch(query, *params)
                # records = []
                for record in all_records:
                    full_record = dict(record)
                    for key in full_record:
                        Before = f"Before: {full_record[key]}"
                        if col_defs.get(key, "Error") in ['jsonb', 'json']:
                            full_record[key] = json.loads(full_record[key])
                        elif col_defs.get(key, "Error") in ["_jsonb"]:
                            full_record[key] = [json.loads(item) for item in full_record[key]]
                        else:
                            pass
                        print(f"Key: {key}, Before: {Before}, After: {full_record[key]}")
                    # records.append(full_record)
            return all_records
        
        # except Exception as e:
        #     print(f"Database error during Get Data database connection: {e}")
        #     return []
        # finally:
        #     await conn.close()

    async def delete_data(self, ids_to_delete, table_name=None):
        if table_name is None or table_name == "":
            table_name = self.default_table
        
        if not isinstance(ids_to_delete, list):
            keys = [ids_to_delete]
        
        try:
            conn = self.get_connection()
            try:
                async with conn.transaction():
                    for id in ids_to_delete:
                        query = f"""
                            UPDATE {table_name}
                            SET iscurrent = FALSE, archivedon = (NOW() AT TIME ZONE 'UTC')
                            WHERE id = '{id}
                        """
                        deleted_result = await conn.execute(query)
                        print(f"Deleted data: {id} and got result: {deleted_result}")
            finally:
                await conn.close()
        except Exception as e:
            print(f"Database error during delete: {e}")
     

class SimpleMicrophone:
    """
    This class implements a simplified microphone for local audio input using PyAudio.
    """

    def __init__(
        self,
        push_callback: Callable[[bytes], Awaitable[None]],
        rate: int = 16000,
        chunk: int = 1024,
        channels: int = 1,
        input_device_index: Optional[int] = None,
    ):
        self._audio = pyaudio.PyAudio()
        self._chunk = chunk
        self._rate = rate
        self._format = pyaudio.paInt16
        self._channels = channels
        self._input_device_index = input_device_index
        self._push_callback = push_callback
        self._exit_event = threading.Event()
        self._stream = None
        self._loop = asyncio.get_event_loop()

    def start(self) -> bool:
        """
        Starts the microphone stream.
        """
        if self._push_callback is None:
            print("Error: No callback set.")
            return False

        # Log device info for verification
        if self._input_device_index is not None:
            device_info = self._audio.get_device_info_by_index(self._input_device_index)
            print(f"Using input device {self._input_device_index}: {device_info['name']}")
            print(f"Max input channels: {device_info['maxInputChannels']}")
            print(f"Default sample rate: {device_info['defaultSampleRate']}")

        try:
            self._stream = self._audio.open(
                format=self._format,
                channels=self._channels,
                rate=self._rate,
                input=True,
                frames_per_buffer=self._chunk,
                input_device_index=self._input_device_index,
                stream_callback=self._callback,
            )

            self._exit_event.clear()
            self._stream.start_stream()

            # Log stream info
            print(f"Microphone stream started on device index {self._input_device_index}.")
            print(f"Stream input latency: {self._stream.get_input_latency()}")
            print(f"Stream channels: {self._stream._channels}")

            return True

        except Exception as e:
            print(f"Failed to start microphone stream: {e}")
            return False

    def _callback(self, input_data, frame_count, time_info, status_flags):
        """
        The callback used to process data in callback mode.
        """
        if self._exit_event.is_set():
            return None, pyaudio.paAbort

        if input_data is not None:
            asyncio.run_coroutine_threadsafe(self._push_callback(input_data), self._loop)

        return input_data, pyaudio.paContinue

    def mute(self) -> None:
        """
        Mutes the microphone stream.
        """
        self._exit_event.set()

    def unmute(self) -> None:
        """
        Unmutes the microphone stream.
        """
        self._exit_event.clear()

    def finish(self) -> None:
        """
        Stops the microphone stream.
        """
        self._exit_event.set()
        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
        self._audio.terminate()
        print("Microphone stream stopped.")
load_dotenv()

psql = PsqlSimpleStorage()

PROD_PORT = 4003

AUDIOINFO_GLOBAL = {}
AUDIOINFO_GLOBAL['recstate'] = "Not transcribing"


is_finals = []
API_KEY = os.getenv("DEEPGRAM_API_KEY")
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

RESULTS_LIST = []

app = Quart(__name__)
app.config['SESSION_TYPE'] = 'redis'
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

Session(app)

stop_event = asyncio.Event()

# Only enable debugpy if we're in development mode and the port is not already in use
if os.getenv("QUART_ENV") == "development" and not is_port_in_use(5678):
    debugpy.listen(("0.0.0.0", 5678))
    print("Waiting for debugger attach...")
    debugpy.wait_for_client()

@app.route('/isup', methods=['GET'])
async def isup():
    return jsonify({"status": "SUCCESS! AudioBackground is up and running"})

@app.route('/getaudioinfo', methods=['GET'])
async def getaudioinfo():
    ret_val = get_audio_device_dict()
    return jsonify(ret_val)

@app.route('/stopaudiorec', methods=['GET'])
async def stopaudiorec():
    stop_event.set()
    return jsonify({"status": "Transcription Stopped"})

@app.route('/startaudiorec', methods=['GET'])
async def startaudiorec():
    stop_event.clear()
    asyncio.create_task(main())
    return jsonify({"status": "Transcription Started"})

async def main():
    try:
        AUDIOINFO_GLOBAL['recstate'] = "Starting Transcription ..."
        loop = asyncio.get_event_loop()

        for signal in (SIGTERM, SIGINT):
            loop.add_signal_handler(
                signal,
                lambda: asyncio.create_task(
                    shutdown(signal, loop)
                ),
            )


        is_final_sentences = []
        is_final_sentences_by_speaker = {}

        
        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(API_KEY, config)
        dg_connection = deepgram.listen.asynclive.v("1")

        async def on_open(self, open, **kwargs):
            print(f"Connection Open")

        async def on_message(self, result, **kwargs):
            # Message is any result from the Deepgram API
            # We will throw away if the result is not final
            # as otherwise the transcription could be repeated
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return

            if result.is_final:
                # If the result is final, add it to the final sentences list (i.e. this is the final transcription of that sentence)
                is_final_sentences.append(sentence.strip())
                speaker_id = f"{result.channel.alternatives[0].words[0].speaker}"
                is_final_sentences_by_speaker[speaker_id] = f"{is_final_sentences_by_speaker.get(speaker_id, '') }{sentence.strip()}"

                if result.speech_final:
                    # If the result is final and the speech is final, then we have a full utterance
                    # which is basicallly someone's turn to speak
                    
                    utterances = " ".join(is_final_sentences)
                    
                    new_result = {}
                    #Varchars
                    new_result['rowcontext'] = 'Transcription'
                    new_result['uniquebuskey'] = result.metadata.request_id
                    new_result['contenttype'] = 'FinalUtterance'
                    new_result['parentid'] = result.metadata.request_id
                    
                    # _Text
                    new_result['speakers'] = is_final_sentences_by_speaker.keys()
                    new_result['utterances'] = [utterances]
                    
                    sd = {}
                    sd['model'] = result.metadata.model_info.name
                    sd['start'] = result.start
                    sd['duration'] = result.duration
                    sd['channel_index'] = result.channel_index
                    
                    #_JSONB
                    new_result['structdata'] = [sd]
                    new_result['allpages'] = [is_final_sentences_by_speaker]

                    #Reset  the variables
                    is_final_sentences = []
                    is_final_sentences_by_speaker = {}
                    RESULTS_LIST.append(new_result)

                    #Upsert the data
                    result = await psql.upsert_append_data(new_result, table_name="textlibrary")
                else:
                    pass
            else:
                pass

        async def on_metadata(self, metadata, **kwargs):
            pass

        async def on_speech_started(self, speech_started, **kwargs):
            pass

        async def on_utterance_end(self, utterance_end, **kwargs):
            global is_finals
            if len(is_finals) > 0:
                utterance = " ".join(is_finals)
                is_finals = []

        async def on_close(self, close, **kwargs):
            print(f"Connection Closed")

        async def on_error(self, error, **kwargs):
            print(f"Handled Error: {error}")

        async def on_unhandled(self, unhandled, **kwargs):
            print(f"Unhandled Websocket Message: {unhandled}")

        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=300,
            punctuate=True,
            diarize=True,
        )

        addons = {"no_delay": "true"}
        print("\n\n Transcription started .... \n")

        if await dg_connection.start(options, addons=addons) is False:
            print("Failed to connect to Deepgram")
            AUDIOINFO_GLOBAL['recstate'] = "Connection Failed"
            return

        device_dict = get_audio_device_dict()
        input_device_index = None
        for key, dev in device_dict.items():
            if "MicInputAggBH" in key:
                input_device_index = dev['index']
                print(f"Using Input Source: {key}: \n{dev}")

        if input_device_index is None:
            print("No suitable input device found.")
            return

        microphone = SimpleMicrophone(
            push_callback=dg_connection.send,
            rate=16000,
            chunk=1024,
            channels=1,
            input_device_index=input_device_index
        )

        if not microphone.start():
            print("Failed to start the microphone.")
            return

        AUDIOINFO_GLOBAL['config'] = microphone._audio.get_default_host_api_info()
        AUDIOINFO_GLOBAL['recstate'] = "Transcribing Live Audio"

        try:
            while not stop_event.is_set():
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass
        finally:
            microphone.finish()
            await dg_connection.finish()
            AUDIOINFO_GLOBAL['recstate'] = "Not transcribing"

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return

if __name__ == "__main__":
    
        


    setproctitle.setproctitle("AudioBackground")
    app.run(debug=True, host='0.0.0.0', port=PROD_PORT)
