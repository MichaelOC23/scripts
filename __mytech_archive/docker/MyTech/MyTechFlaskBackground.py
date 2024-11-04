from flask import Flask, request, jsonify, redirect, url_for, session
from datetime import datetime

import torch
import ollama
import argparse
from openai import OpenAI

from openai import chat
# from langchain.retrievers.you import YouRetriever 
import asyncio

import re
from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright

import json
import os
import threading

from googleapiclient.discovery import build
from urllib.parse import urlparse
from urllib.parse import urlencode
import urllib.parse

import html2text
import requests

import time
from io import StringIO



import aiohttp

import zipfile
import csv
import uuid 

import base64
import hashlib

import setproctitle
import pyaudio
import subprocess
import threading
import queue
# import websocket

#import urlencode


# yr = YouRetriever()


# import _class_search_web
# import _class_streamlit
# import _class_storage

#Deepgram
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    FileSource,
    LiveOptions,
    LiveTranscriptionEvents,
    PrerecordedOptions,
    Microphone,)
load_dotenv()

print_it = False

def log_it(message, print_it=True, color='black'):
    is_dict, dict_value = got_dict(message)
    if is_dict:
        message = json.dumps(dict_value, indent=4)
    else:
        message = f"{message}"
        
    with open(os.path.join(log_directory, 'flask1.log'), 'a') as f:
        f.write(message)
        print(message)

LOG_FOLDER = "logs"


app = Flask(__name__)


data_directory = os.path.join('data', 'nasdaq')
log_directory = "logs"

if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    
# search = _class_search_web.Search()
# storage = _class_streamlit.PsqlSimpleStorage()

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}".replace("channel_alternatives_","alt") if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, (dict, list)):
                    items.extend(flatten_dict({f"{i}": item}, new_key, sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
        
        flat_dict = dict(items)
        log_it(flat_dict)
    return flat_dict

@app.route('/isup', methods=['GET'])
def isup():
    display_endpoint_example()
    return jsonify({"status": "SUCCESS! Background Flask is up and running"})

def got_dict(input_value):
    if isinstance(input_value, dict):
        return True, input_value
    try:
        type_value = type(input_value)
        input_value = json.loads(input_value)
    except Exception as e:
        return False, f"Type is: {type_value}.  Could not convert input to dictionary: {e}"
    
    
    
    return True, input_value


##############################################
####    SEARCH AND SCRAPE WEB FUNCTIONS    ####
##############################################

@app.route('/searchweb', methods=['POST'])
def searchweb():
    data = request.json
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    other = data.get('other', '')
    
    # search.search_web_async_with_assemble(first_name, last_name, other)

@app.route('/scrape', methods=['POST'])
def scrape():
    
    data = request.json
    search_query = data.get('search_query', '')
    if not search_query:
        return jsonify({"error": "Search Query is required"}), 400

   
    # search_results = asyncio.run(search.get_stored_search_results(search_query=search_query))
    # resp = asyncio.run(scrape_all_results_async(search_results))
    
    return_value = ""
    # if resp is not None:
    #     if isinstance(resp, list) or isinstance(resp, dict):
    #         return_value = jsonify(resp)
    #     else:
        # return_value = resp
    return return_value

async def get_web_page_async(result):
    try:
        url = result.get('Orig_RowKey', '')
        
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            body = soup.body.get_text(separator=' ', strip=True)

            result['full_text_blob']= body
            result['full_html_blob']=response.text

            # resp = await storage.add_update_or_delete_some_entities(storage.url_results_table_name, [result])
            return True
        else:
            print(f"Failed to retrieve {result.get('Orig_RowKey', '')}: Status code {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error getting full webpage for {result.get('Orig_RowKey', '')}: {e}")
        return ""

async def scrape_all_results_async(search_results):
    search_tasks = []
    for result in search_results:
        search_tasks.append(get_web_page_async(result))
    scrape_success_list = await asyncio.gather(*search_tasks)
    return search_results


    
    


#########################################
####      OFFICE 365  FUNCTIONS      ####
#########################################
CLIENT_ID = "6ece1fbd-8c47-41ff-896f-ecbbee678b83"
TENANT_ID = "050376de-b1f5-4dbc-8c0f-8929b6e68a08"
       
# CLIENT_ID = os.environ.get('AZURE_APP_CLIENT_ID', 'No Key or Connection String found')
# TENANT_ID = os.environ.get('AZURE_APP_TENANT_ID', 'No Key or Connection String found') 

# OAuth Endpoints
AUTH_ENDPOINT = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize'

TOKEN_ENDPOINT = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'
GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0'

app.secret_key = os.urandom(24)

@app.route('/')
def homepage():
        
    def generate_code_verifier():
        return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')

    def generate_code_challenge(code_verifier):
        code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')
    
    
    
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    session['code_verifier'] = code_verifier
    redirect_uri = redirect_uri = 'http://localhost:5000/redirect'

    
    
    print(url_for('auth_redirect', _external=True))
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': redirect_uri,  # Use the explicit localhost URI
        # 'redirect_uri': url_for('auth_redirect', _external=True),
        'scope': 'openid profile User.Read Mail.Read',
        'response_mode': 'query',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    auth_url = f'{AUTH_ENDPOINT}?{urlencode(auth_params)}'
    return redirect(auth_url)

@app.route('/redirect')
def auth_redirect():
    # Microsoft Graph Endpoint
    GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0'

    code = request.args.get('code')
    if not code:
        return "No code provided"
    
    code_verifier = session.pop('code_verifier', None)
    if not code_verifier:
        return "Missing code verifier"
    
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': url_for('auth_redirect', _external=True),
        'client_id': CLIENT_ID,
        'code_verifier': code_verifier
    }

    token_response = requests.post(TOKEN_ENDPOINT, data=token_data)
    token_json = token_response.json()

    if 'access_token' in token_json:
        access_token = token_json['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        
        with open('office_token.json', 'w') as f:
            f.write(json.dumps(token_json))

        response = requests.get(f'{GRAPH_ENDPOINT}/me/messages', headers=headers)
        if response.status_code == 200:
            messages = response.json()
            return json.dumps(messages, indent=2)
        else:
            return f"Failed to fetch messages: {response.status_code} {response.text}"
    else:
        return f"Failed to obtain access token: {token_response.status_code} {token_json}"



def display_endpoint_example():

    access_token = os.environ.get('JBI_MSFT_ACCESS_TOKEN', '')
    print(f"access token: {access_token}")
    
    
    endpoints = {
        "Email": [
            {"Get messages": "GET /me/messages"},
            {"Send a message": "POST /me/sendMail"},
            {"Get a specific message": "GET /me/messages/{id}"},
            {"Create a new message": "POST /me/messages"}
        ],
        "Calendar": [
            {"Get calendar events": "GET /me/events"},
            {"Create a new event": "POST /me/events"},
            {"Get a specific event": "GET /me/events/{id}"},
            {"Update an event": "PATCH /me/events/{id}"},
            {"Delete an event": "DELETE /me/events/{id}"}
        ],
        "Tasks (To-Do)": [
            {"Get tasks": "GET /me/todo/lists/{listId}/tasks"},
            {"Create a new task": "POST /me/todo/lists/{listId}/tasks"},
            {"Get a specific task": "GET /me/todo/lists/{listId}/tasks/{taskId}"},
            {"Update a task": "PATCH /me/todo/lists/{listId}/tasks/{taskId}"},
            {"Delete a task": "DELETE /me/todo/lists/{listId}/tasks/{taskId}"}
        ],
        "Contacts": [
            {"Get contacts": "GET /me/contacts"},
            {"Create a new contact": "POST /me/contacts"},
            {"Get a specific contact": "GET /me/contacts/{id}"},
            {"Update a contact": "PATCH /me/contacts/{id}"},
            {"Delete a contact": "DELETE /me/contacts/{id}"}
        ]
        }

    if access_token != "":
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(f'{GRAPH_ENDPOINT}/me/messages', headers=headers)
        
        if response.status_code == 200:
            messages = response.json()
            print(json.dumps(messages, indent=4))
        
        else:
            print(f"Failed to fetch messages: {response.status_code} {response.text}")
    else:
        print(f"Failed to obtain access token")


if __name__ == "__main__":
    # Set the process title
    
    # download_nasdaq()
    setproctitle.setproctitle("MyTechFlaskBackground")
    from flask_cors import CORS
    CORS(app)    
    # app.secret_key = 'your_secret_key_here'  # Use a secure, randomly generated key
    # app.run(host="0.0.0.0", port=5000, debug=True)
