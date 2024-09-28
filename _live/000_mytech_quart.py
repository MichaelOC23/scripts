from quart import Quart, request, jsonify, redirect, url_for, session  # Changed from Flask to Quart

import json
import os
import setproctitle
from openai import OpenAI

from _class_deepgram import deepgram_audio_transcription
from _class_office365 import office365_tools

dg = deepgram_audio_transcription()
o365 = office365_tools()


app = Quart(__name__)

DEFAULT_INPUT_DEVICE_CODE = 'InCaMi'
print("Loaded Standard Quart Libraries")


#########################################
####       DEEPGRAM  FUNCTIONS       ####
#########################################

@app.route('/')
async def call_openai_api(prompt=None):
    return "No logic in home page"
    
    """
    Call OpenAI API with the given prompt and return the response.
    """
    try:
        if not prompt:
            prompt = "Write me a haiku about Star Wars."

        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        reply = completion.choices[0].message.content
        return jsonify({'response': reply})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/startlog')
async def start_log_default():
    val = await start_meeting_log()
    return "Starting default meeting"

@app.route('/startlogmic')
async def start_log_mic():
    val = await start_meeting_log('InCaMic')
    return "Starting mic meeting"
    
    
@app.route('/startlogap')
async def start_log_airpods():
    val = await start_meeting_log('InCaAp')
    return "Starting AirPod meeting"
    
@app.route('/startlogcustom')
async def start_log_custom():
    val = await start_meeting_log('InCaCustom')
    return "Starting custom meeting"


async def start_meeting_log(input_device=DEFAULT_INPUT_DEVICE_CODE):
    print (f"Starting Meeting Log with Input Device{input_device}")
    try:
        result = await dg.start_transcription(input_device)
        config = await list_devices()
        return jsonify({'status': 'started', 'transcription': result, 'config': config})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/listdevices')
async def list_devices():
    config = await dg.get_audio_config_dict()
    list = await dg.get_audio_device_list()
    
    return jsonify({'devices': [config, list]})

@app.route('/stoplog')
async def stop_meeting_log():
    """
    Stop the transcription process.
    """
    try:
        await dg.stop_transcription()
        return jsonify({'status': 'stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_response(response_text):
    """
    Parse the response text to extract a JSON object.
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            start_index = response_text.find('{')
            end_index = response_text.rfind('}') + 1
            if start_index != -1 and end_index != -1:
                json_str = response_text[start_index:end_index]
                return json.loads(json_str)
            else:
                print("Error: No JSON object found in the response.")
                return None
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON from the cleaned response.")
            return None



#########################################
####      OFFICE 365  FUNCTIONS      ####
#########################################


@app.route('/setglobalaccesstoken', methods=['POST'])
async def setglobalaccesstoken():
    return await (o365.set_value(request))
 
 
@app.route('/exporttoken')
async def exporttoken():
    return await o365.export_token(request)

@app.route('/')
async def index():
    return await o365.homepage(request)
 
@app.route('/redirect')
async def redirect(request):
    return await o365.auth_redirect(request)


@app.route('/create_task_auth', methods=['POST'])
async def createtask(request):
    return await o365.create_task(request)
 
@app.route('/create_task_no_auth', methods=['POST'])
async def createtasknoauth(request):
    return await o365.create_task_no_auth
 



if __name__ == "__main__":
    # Set the process title
    setproctitle.setproctitle("mytechbackground")
    port_number = os.environ.get('OFFICE365_BACKGROUND_PORT', '4001')
    app.run(host="0.0.0.0", port=port_number, debug=False)
    print("mytechbackground server started.")

print("Loaded Cusotm Quart App")