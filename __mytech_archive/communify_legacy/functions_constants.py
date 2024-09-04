
import os
import re
import sys
from datetime import date, datetime
import time
import subprocess
import random
import inspect

import json
import functions_db_postgres as db
import ast


# from cv2 import log
import math
from collections import Counter

# For encryption and decryption
from cryptography.fernet import Fernet

# Load your encryption key from an environment variable
encryption_key = os.getenv("ROTATING_ENCRYPTION_KEY")

# Function to encrypt data


def fernet_encrypt(data, key=encryption_key):
    data_in_bytes = data.encode()
    fernet = Fernet(key)
    result = fernet.encrypt(data_in_bytes)
    return result

# Function to decrypt data


def calculate_entropy(text):
    # Count the frequency of each character in the string
    frequencies = Counter(text)
    total_chars = len(text)

    # Calculate probabilities and entropy
    entropy = 0
    for freq in frequencies.values():
        prob = freq / total_chars
        if prob != 0:  # Handle the case where the probability is zero
            entropy -= prob * math.log2(prob)

    return entropy


def convert_string_to_dict(string):
    try:
        # Attempt to convert the string to a dictionary
        result = ast.literal_eval(string)
        if isinstance(result, dict):
            return result
        else:
            return string
    except (ValueError, SyntaxError):
        # Handle the case where the string is not a valid dictionary
        return string

# Example usage
# string_representation = "{'key': 'value', 'another_key': 123}"
# converted_dict = convert_string_to_dict(string_representation)
# print(converted_dict)


def UNIQUE_DATE_TIME_STRING():
    # note this is unique to the second i.e. per run
    return datetime.now().strftime("%Y%m%d.%H%M%S")


def random_sleep(min_seconds, max_seconds):
    pause_duration = random.uniform(min_seconds, max_seconds)
    time.sleep(pause_duration)


def show_notification(title, message):
    apple_script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", apple_script])

# Example usage
# show_notification("Test Title", "This is a test message")


log_level_all = ["DEBUG", "INFO", "ERROR", "LLM"]
system_log_level = log_level_all

#################################
#!#    FOLDER/FILE SETUP       ##
#################################

# Function to create a required directory if it does not exist


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    # else:
    #     print(f"Directory '{directory_path}' already exists.")

# Function to create a required file if it does not exist


def create_file_if_not_exists(file_path, file_content=None):
    if file_content is None:
        file_content = ""
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write(file_content)
            f.close()
        print(f"File '{file_path}' created.")
    # else:
    #     print(f"File '{file_path}' already exists.")


#################################
#!#    GENERAL CONSTANTS       ##
#################################

# Location of the project folder
PROJECT_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))

# Base location for all input and output files
IO_FOLDER_PATH = os.getenv("IO_FOLDER_PATH")

# KEY IO Folder Locations
COMMUNIFY_IO_FOLDER_PATH = os.environ["COMMUNIFY_IO_FOLDER_PATH"]
NOTES_IO_FOLDER_PATH = os.environ["NOTES_IO_FOLDER_PATH"]
AUDIO_IO_FOLDER_PATH = os.environ["AUDIO_IO_FOLDER_PATH"]
IMAGES_IO_FOLDER_PATH = os.environ["IMAGES_IO_FOLDER_PATH"]
TEMP_IO_FOLDER_PATH = os.environ["TEMP_IO_FOLDER_PATH"]
TRANSCRIPTIONS_IO_FOLDER_PATH = os.environ["TRANSCRIPTIONS_IO_FOLDER_PATH"]
SCRAPED_CONTENT_IO_FOLDER_PATH = os.environ["SCRAPED_CONTENT_IO_FOLDER_PATH"]
LOGS_IO_FOLDER_PATH = os.environ["LOGS_IO_FOLDER_PATH"]
PROMPTS_IO_FOLDER_PATH = os.environ["PROMPTS_IO_FOLDER_PATH"]
LLM_IO_FOLDER_PATH = os.environ["LLM_IO_FOLDER_PATH"]
EMAIL_IO_FOLDER_PATH = os.environ["EMAIL_IO_FOLDER_PATH"]


SCRIPT_START_TIME = datetime.now()
SCRIPT_START_TIME_IN_SECONDS = time.time()  # Get current time in seconds

# Folder and File Path Constants (Relative to the current file)
SYSTEM_LOG_FILE_PATH = os.path.join(LOGS_IO_FOLDER_PATH, "system_log.txt")
LLM_LOG_FILE_PATH = os.path.join(LOGS_IO_FOLDER_PATH, "llm_log.txt")


# Make sure the project folder and the shared folder are in the python path so we can import from them
sys.path.append(PROJECT_FOLDER_PATH)
sys.path.append(os.path.join(PROJECT_FOLDER_PATH, "shared"))


#################################
#!#      LLM CONSTANTS         ##
#################################

TEXT_BREAK = f"\n{'*'*50}\n"
DATA_BREAK = f"\n*{'-'*7}  DATA  {'-'*7}*\n"

# CHUNK size of text if you are breaking it up to send to an LLM
DEFAULT_CHUNK_SIZE = 20000


### MODELS ###
MODEL_GPT3 = "gpt-3.5-turbo-16k"
MODEL_GPT4 = "gpt-4"
MODEL_GPT4_TURBO = "gpt-4-1106-preview"
MODEL_WHISPER = "whisper-1"
MODEL_MISTRAL_LOCAL = "local-model"
MODEL_DEFAULT = MODEL_GPT3

# OpenAI Constants
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = 'https://api.openai.com/v1/chat/completions'
OPENAI_COMP_ENDPOINT = 'chat/completions'
OPENAI_TRANSCRIPTION_ENDPOINT = 'transcriptions'

# MISTRAL Constants
MISTRAL_API_KEY = 'not-needed'
MISTRAL_TRANSCRIPTION_ENDPOINT = '### NOT AVAILABLE YET ###'  # ! NEED TO SORT THIS
MISTRAL_BASE_URL = 'http://localhost:1234/v1/'
MISTRAL_COMP_ENDPOINT = 'chat/completions'

# OpenAI Defaults
DEFAULT_TEMPERATURE = 0.1
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."
DEFAULT_MAX_TOKENS = 4096
DEFAULT_METHOD = "CLI"  # Alternative valid value is "API"
DEFAULT_OUTPUT_FOLDER_PATH = LLM_IO_FOLDER_PATH
DEFAULT_BASE_URL = 'http://api.openai.com/v1/'
DEFAULT_COMP_ENDPOINT = 'chat/completions'


def model_config(model=MODEL_DEFAULT, temperature=DEFAULT_TEMPERATURE, max_tokens=DEFAULT_MAX_TOKENS, method=DEFAULT_METHOD, base_url=DEFAULT_BASE_URL, endpoint=DEFAULT_COMP_ENDPOINT):
    str = f'"model":"{model}","temperature":{temperature},"max_tokens":{max_tokens},"base_url":"{base_url}","endpoint":"{endpoint}","url_endpoint":"{base_url+endpoint}","method":"{method}"'
    json_str = json.loads("{" + str + "}")
    return json_str


# Model Configurations
MODEL_CONFIGS = {}
MODEL_CONFIGS["DEFAULT_LOCAL"] = model_config(
    "local-model", 0, 2000, DEFAULT_METHOD, MISTRAL_BASE_URL, MISTRAL_COMP_ENDPOINT)
MODEL_CONFIGS["LOCAL_MISTRAL7B_GRAMMAR_CORRECT"] = model_config(
    "local-model", 0, 2000, DEFAULT_METHOD, MISTRAL_BASE_URL, MISTRAL_COMP_ENDPOINT)
MODEL_CONFIGS["GPT_4_TURBO_GENERAL"] = model_config(
    MODEL_GPT4_TURBO, 0.2, 2000, DEFAULT_METHOD, OPENAI_BASE_URL, OPENAI_COMP_ENDPOINT)
MODEL_CONFIGS["GPT3.5_TURBO_GENERAL"] = model_config(
    MODEL_GPT3, .2, 2000, DEFAULT_METHOD, OPENAI_BASE_URL, OPENAI_COMP_ENDPOINT)
MODEL_CONFIGS["GPT_4_GENERAL"] = model_config(
    MODEL_GPT4, .2, 2000, DEFAULT_METHOD, OPENAI_BASE_URL, OPENAI_COMP_ENDPOINT)
MODEL_CONFIGS["WHISPER1_MTG_TRANS"] = model_config(
    MODEL_WHISPER, .1, 2000, DEFAULT_METHOD, OPENAI_BASE_URL, OPENAI_TRANSCRIPTION_ENDPOINT)


with open(os.path.join(LOGS_IO_FOLDER_PATH, f"model_config_{UNIQUE_DATE_TIME_STRING()}.json"), "w") as f:
    # model_config_log = json.loads(MODEL_CONFIGS)
    f.write(json.dumps(MODEL_CONFIGS, indent=4))
    f.close()

#################################
#!#        TRANSCRIPTION       ##
################################
# TRANSCRIPTION_TEST_FOLDER_PATH  = os.path.join(TRANSCRIPTIONS_IO_FOLDER_PATH, "test-transcription")
# create_directory_if_not_exists(TRANSCRIPTION_TEST_FOLDER_PATH)


#################################
#!#      IMAGE GENERATION      ##
#################################
IMAGE_PATH_EXTENSIONS = ['.jpg', '.gif', '.png']

#################################
#!#    AUDIO PROCESSING        ##
#################################

# Audio Processing Configuration Parameters
# in MB, the maximum file size for a single audio file
AUDIO_FILE_SPLIT_REQUIRED_THRESHOLD = 3
AUDIO_FILE_SPLIT_API_MAX = 20  # in MB, the maximum file size for a single audio file


# Audio Processing Fixed Constants
AUDIO_FILE_SPLIT_REQUIRED_THRESHOLD_IN_BYTES = AUDIO_FILE_SPLIT_REQUIRED_THRESHOLD * \
    1024 * 1024  # in bytes, the maximum file size for a single audio file
AUDIO_PATH_EXTENSIONS = ['.mp3', '.m4a', '.wav', '.flac', '.ogg', '.aiff']
BIT_RATE = "128k"
AUDIO_COMPRESSION_FORMAT = "mp3"
# TRANSCRIPTIONS_FOR_EMBEDDING_FOLDER_PATH = TRANSCRIPTIONS_IO_FOLDER_PATH


# Folder and File Path Constants (Relative to the current file)
# AUDIO_PROCESSING_FOLDER_PATH = AUDIO_IO_FOLDER_PATH
# AUDIO_WORKING_FOLDER_PATH = os.path.join(AUDIO_PROCESSING_FOLDER_PATH, "working")
# TEMP_RAW_AUDIO_FOLDER_PATH = os.path.join(AUDIO_PROCESSING_FOLDER_PATH, "temp-raw-audio")
AUDIO_STOP_FILE_PATH = os.path.join(
    PROJECT_FOLDER_PATH, 'temp', "stopfile.txt")


# Audio Processing PER RUN Constants: Variable per run of any script that uses this Constants file)
# DAILY_TRANSCRIPTIONS_FOLDER_PATH = os.path.join(AUDIO_PROCESSING_FOLDER_PATH, f'transcriptions-{DAILY_UNIQUE_DATE_TIME_STRING}')
# DAILY_SUMMARIZATION_FOLDER_PATH = os.path.join(AUDIO_PROCESSING_FOLDER_PATH, f'summarizations-{DAILY_UNIQUE_DATE_TIME_STRING}')
PROMPT_FILE_PATH_SUMMARIZATION = os.path.join(
    PROJECT_FOLDER_PATH, "prompts", "document-summary-prompt-001.txt")
PROMPT_FILE_PATH_CORRECT_GRAMMAR = os.path.join(
    PROJECT_FOLDER_PATH, "prompts", "transcription-clean-up-prompt-001.txt")
PROMPT_FILE_PATH_CREATE_GOOGLE_CALENDAR_EVENT = os.path.join(
    PROJECT_FOLDER_PATH, "prompts", "create-google-calendar-event.txt")

# create_directory_if_not_exists(AUDIO_PROCESSING_FOLDER_PATH)
# create_directory_if_not_exists(AUDIO_WORKING_FOLDER_PATH)
# create_directory_if_not_exists(TEMP_RAW_AUDIO_FOLDER_PATH)
# create_directory_if_not_exists(DAILY_TRANSCRIPTIONS_FOLDER_PATH)
# create_directory_if_not_exists(DAILY_SUMMARIZATION_FOLDER_PATH)


# Import System Arguments
SYS_ARG_0 = sys.argv[0]
SYS_ARG_1 = sys.argv[1] if len(sys.argv) > 1 else "NOT_USED"
SYS_ARG_2 = sys.argv[2] if len(sys.argv) > 2 else "NOT_USED"
SYS_ARG_3 = sys.argv[3] if len(sys.argv) > 3 else "NOT_USED"
print(f"SYS_ARG_0: {SYS_ARG_0}", f"SYS_ARG_1: {SYS_ARG_1}",
      f"SYS_ARG_2: {SYS_ARG_2}", f"SYS_ARG_3: {SYS_ARG_3}", sep=" | ")


#################################
#!#    LLM INTERACTIONS        ##
#################################

# Transcription Correction Prompt Constants
TRANSCRIPTION_CORRECTION_SYSTEM_PROMPT = """
You are a helpful assistant for the company JustBuildIt. 
Your task is to correct any spelling discrepancies in the transcribed text. 
Only add necessary punctuation such as periods, commas, and capitalization, and use only the context provided.
Please insert sensible line breaks where you see changes in speaker, subject, or topic."
"""  # Make sure that the names of the following products are spelled correctly:


#################################
#!#     GMAIL CREDENTIALS      ##
#################################


def get_gmail_access_token():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    access_token = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    GMAIL_TOKEN_JSON = ""
    GMAIL_TOKEN = None
    GMAIL_CREDENTIALS_JSON = ""
    got_new_token = False

    # The scope here enable read/write access to the calendar and gmail
    SCOPES = ['https://www.googleapis.com/auth/calendar',
              'https://www.googleapis.com/auth/gmail.modify']

    try:
        # Check to see if we have recently authenticated and stored the token.
        gmail_token_path = os.path.join(
            IO_FOLDER_PATH, "temp", "gmail_token.json")
        if os.path.exists(gmail_token_path):
            with open(gmail_token_path, "rb") as f:
                encrypted_token = f.read()
                GMAIL_TOKEN_JSON = fernet_decrypt(encrypted_token)
                GMAIL_TOKEN = json.loads(GMAIL_TOKEN_JSON)
                f.close()
    except Exception as e:
        print(
            f"Error getting GMAIL_TOKEN_JSON from environment variables: {e}")
        pass

    if GMAIL_TOKEN != None and isinstance(GMAIL_TOKEN, dict):
        # A token exists .... let's use it.
        access_token = Credentials.from_authorized_user_info(
            GMAIL_TOKEN, SCOPES)
        if not access_token or not access_token.valid:
            GMAIL_CREDENTIALS_JSON = os.environ["GMAIL_CREDENTIALS_JSON"]
            flow = InstalledAppFlow.from_client_config(
                json.loads(GMAIL_CREDENTIALS_JSON), SCOPES)
            access_token = flow.run_local_server(port=0)
            got_new_token = True

    else:
        # There is no token, so we need to get one using the stored credentials
        GMAIL_CREDENTIALS_JSON = os.environ["GMAIL_CREDENTIALS_JSON"]
        flow = InstalledAppFlow.from_client_config(
            json.loads(GMAIL_CREDENTIALS_JSON), SCOPES)
        access_token = flow.run_local_server(port=0)
        got_new_token = True

    # Save the credentials for the next run
    if got_new_token:
        with open(gmail_token_path, "wb") as f:
            access_token_json = access_token.to_json()
            encrypted_token = fernet_encrypt(access_token_json)
            f.write(encrypted_token)
            f.close()

    # return the access token
    return access_token


def completion_response_to_dict(response):
    if response.choices and len(response.choices) > 0:
        return_text = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
    else:
        return_text = response['error']['message']
        finish_reason = "ERROR"
        return response_data

    response_data = {
        "id": response.id,
        "object": response.object,
        "created": response.created,
        "model": response.model,
        "choices_count": len(response.choices),
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
        "content": return_text,
        "finish_reason": finish_reason,
    }
    return response_data


#################################
#!#     PROJECT LOGGING        ##
#################################


def log_it(message, log_level="INFO", message2=None, error_type=""):
    try:
        if log_level not in log_level_all:
            log_level = "INFO"
        if message2 is not None:
            message = f"{message} | {message2}"

        # create the log entry string
        caller = inspect.stack()[1][3]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry_lite = f"LOG-ENTRY {timestamp} | {caller} | {log_level} | {message[:25]} | {error_type}"
        log_entry = f"LOG-ENTRY {timestamp} | {caller} | {log_level} | {message} | {error_type}\n"
        db.log_to_db(timestamp, message, log_level, caller, error_type)

        if log_level in ["LLM"]:
            with open(LLM_LOG_FILE_PATH, "a") as f:
                f.write(log_entry)
                f.close()
            # lighten the log for the system log file ....
            log_entry = log_entry_lite

        if log_level in system_log_level:
            # st.sidebar.info(message)
            print(log_entry)
            with open(SYSTEM_LOG_FILE_PATH, "a") as f:
                f.write(log_entry)
                f.close()
    except Exception as e:
        db.log_to_db(
            timestamp, f"logging function failed for unkown reason: \n\n {e}", "ERROR", caller, "Unhandled Logging Error")
        pass
