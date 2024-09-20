

print("Beginning Load of Deepgram Standard Libraries")
from signal import SIGINT, SIGTERM
import asyncio
import socket
import os
import pyaudio
from _class_postgres_note_log import NoteLog
notelog = NoteLog()
print("Loaded Deepgram Standard Libraries")

print("Beginning Load of DeepGram Library")
from deepgram import (
    # Deepgram,
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    # PrerecordedOptions,
    # FileSource,
    Microphone,
)
print("Completed Load of DeepGram Library")


# We will collect the is_final=true messages here so we can use them when the person finishes speaking
is_finals = []
is_final_speaker_words = []
is_final_speaker_statements = []
from _class_postgres_note_log import NoteLog

print("Beginning Load of Deepgram Custom Class")

class deepgram_audio_transcription():
    def __init__(self):
        # Audio Transcription
        self.deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        self.google_api_key = os.environ.get('GOOGLE_API_KEY')
        self.models = {
            "Nova-2": "nova-2-ea",
            "Nova": "nova",
            "Whisper Cloud": "whisper-medium",
            "Enhanced": "enhanced",
            "Base": "base",
        }
        self.languages = {
            "Automatic Language Detection": None,
            "English": "en",
            "French": "fr",
            "Hindi": "hi",
        }
        self.download_directory = os.path.expanduser('~/Downloads')
        if not os.path.exists(self.download_directory):
            os.mkdir(self.download_directory)
        self.AUDIOINFO_GLOBAL = {}


    async def get_audio_config_dict(self):
        p = pyaudio.PyAudio()

        self.AUDIOINFO_GLOBAL["default_input_device_info"]= p.get_default_input_device_info()['index']
        self.AUDIOINFO_GLOBAL["default_output_device_info"]= p.get_default_output_device_info()['index']
        self.AUDIOINFO_GLOBAL['device_count'] = p.get_device_count()

        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            self.AUDIOINFO_GLOBAL[f"#{i}-{dev['name']}"] = dev
        p.terminate()
                
        return self.AUDIOINFO_GLOBAL

    async def is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("0.0.0.0", port)) == 0

    async def get_device_by_input_code(self, input_code='InCaMic'):
        pass
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            if input_code in p.get_device_info_by_index(i)['name']:
                print (f"index:{i}: {p.get_device_info_by_index(i)['name']}")
                return i
        

    async def get_audio_device_list(self):
        import pyaudio

        # Create an instance of PyAudio
        p = pyaudio.PyAudio()

        # Get the number of audio devices
        num_devices = p.get_device_count()

        # Get the info for each audio device
        device_list = []
        for i in range(0, num_devices):
            info = p.get_device_info_by_index(i)
            device_list.append(f"-  Device {i}: {info['name']} - Max Input Channels: {info['maxInputChannels']}  \n")
        return device_list

    async def start_transcription(self, input_code):
        transcription = []
        microphone = None
        try:
            loop = asyncio.get_event_loop()
            for signal in (SIGTERM, SIGINT):
                loop.add_signal_handler(
                    signal,
                    lambda: asyncio.create_task(
                        self.shutdown(signal, loop, dg_connection, microphone)
                    ),
                )

            config: DeepgramClientOptions = DeepgramClientOptions(
                options={"keepalive": "true"}
            )
            # Initialize the DeepgramClient with the API key
            deepgram: DeepgramClient = DeepgramClient(self.deepgram_api_key, config)

            dg_connection = deepgram.listen.asyncwebsocket.v("1")

            async def on_open(self, open, **kwargs):
                try:
                    print("Connection Open")
                except Exception as e:
                    print(f"Error in on_open: {e}")

            async def on_message(self, result, **kwargs):
                try:
                    global is_finals
                    global is_final_speaker_words
                    global is_final_speaker_statements
                    sentence = result.channel.alternatives[0].transcript
                    if len(sentence) == 0:
                        return
                    if result.is_final:
                        is_finals.append(sentence)
                        is_final_speaker_words.extend([{Word.speaker: Word.word} for Word in result.channel.alternatives[0].words])
                        if result.speech_final:
                            utterance = " ".join(is_finals)
                            print(f"Speech Final: {utterance}")
                            transcription.append(utterance)
                            speaker = result.channel.alternatives[0].words[0].speaker
                            is_final_speaker_statements.append({speaker: utterance} )
                            notelog.upsert_note(
                                key=result.metadata.request_id,
                                word_history=is_final_speaker_words,
                                statement_history=is_final_speaker_statements)
                            is_finals = []
                        else:
                            pass
                            print(f"Is Final: {sentence}")
                    else:
                        pass
                        print(f"Interim Results: {sentence}")
                except Exception as e:
                    print(f"Error in on_message: {e}")

            async def on_metadata(self, metadata, **kwargs):
                try:
                    print(f"Metadata: {metadata}")
                except Exception as e:
                    print(f"Error in on_metadata: {e}")

            async def on_close(self, close, **kwargs):
                try:
                    print("Connection Closed")
                except Exception as e:
                    print(f"Error in on_close: {e}")

            # Assign event handlers
            dg_connection.on(LiveTranscriptionEvents.Open, on_open)
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            dg_connection.on(LiveTranscriptionEvents.Close, on_close)

            # Connect to WebSocket
            options: LiveOptions = LiveOptions(
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
                diarize=True,
            )

            addons = {
                "no_delay": "true"
            }

            print("\n\nStart talking! Press Ctrl+C to stop...\n")
            if await dg_connection.start(options, addons=addons) is False:
                print("Failed to connect to Deepgram")
                return

            input_device_index = await self.get_device_by_input_code(input_code=input_code)
            
            microphone = Microphone(dg_connection.send, input_device_index=input_device_index)
            microphone.start()


            try:
                while True:
                    await asyncio.sleep(1)
            except asyncio.CancelledError:
                pass
            finally:
                microphone.finish()
                await dg_connection.finish()
                print("Finished")
                return transcription

        except Exception as e:
            print(f"Could not open socket: {e}")
            return transcription

    async def stop_transcription(self):
        try:
            # Implement the logic to stop the transcription
            # This might involve setting a flag or removing 'logrunning.txt'
            if os.path.isfile('logrunning.txt'):
                os.remove('logrunning.txt')
                print("Transcription stopped successfully.")
            else:
                print("No transcription is currently running.")
        except Exception as e:
            print(f"Error in stop_transcription: {e}")

    async def shutdown(self, signal, loop, dg_connection, microphone):
        print(f"Received exit signal {signal.name}...")
        microphone.finish()
        await dg_connection.finish()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        print(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)
        loop.stop()
        print("Shutdown complete.")
    
    print("Loaded Deepgram Custom Class")