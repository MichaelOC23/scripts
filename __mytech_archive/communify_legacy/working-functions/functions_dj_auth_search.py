"""Functions to connect and parse ArticleRetrieval JSON format"""

import json
import os
import streamlit as st
import requests
from datetime import datetime
# from typing import List, Optional
# from pydantic import BaseModel
# import functions_constants as constants
import time

WAIT_TIME = 4


def UNIQUE_DATE_TIME_STRING():
    # note this is unique to the second i.e. per run
    return datetime.now().strftime("%Y%m%d.%H%M%S")


def try_to_get_dict(text):
    try:
        return json.loads(text)
    except:
        return text


run_uid = UNIQUE_DATE_TIME_STRING()

DOWJONES_IO_FOLDER_PATH = os.environ.get('DOWJONES_IO_FOLDER_PATH')


def djlog(text, key=None):
    print(text)
    # text = try_to_get_dict(text)

    # if key is not None and isinstance(text, dict):
    #     print(text)
    #     # with open(f'{DOWJONES_IO_FOLDER_PATH}/djlog_{key}_{run_uid}.json', 'a') as f:
    #     #     json.dump(text, f, indent=4)
    # else:


def dj_authz_access_token_action(dj_token_Action="GET"):
    """
    Perform action on DJ authorization access token.

    Args:
        action (str): Action to perform on the token. Defaults to "GET".
                      Possible values are "GET", "SET", or "CLEAR".

    Returns:
        str: The result of the action performed on the token.
    """
    def request_token(client_id, password, username):
        url = "https://accounts.dowjones.com/oauth2/v1/token"

        payload = {
            "client_id": client_id,
            "connection": "service-account",
            "device": "orion-tablet",
            "grant_type": "password",
            "password": password,
            "scope": "openid service_account_id offline_access",
            "username": username
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        djlog(f"Response from request_token {response.text}")

        if response.ok:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"

    def request_jwt_token(authn_id_token, client_id):
        url = "https://accounts.dowjones.com/oauth2/v1/token"

        payload = {
            "assertion": authn_id_token,
            "client_id": client_id,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "scope": "openid pib"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        djlog(f"Response from request_jwt_token {response.text}")
        if response.ok:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"

    def refresh_authz_access_token():
        # This function orchestrates tryingt to use the stored token, but, if it's not there, get a new one.
        # Ideally we could validate it in this fucntion, but I'm not clear that's possible without adding overhead and slowing the calls.
        # Usage example (replace with actual credentials):

        client_id = os.environ.get('DOW_JONES_CLIENT_ID')
        password = os.environ.get('DOW_JONES_PASSWORD')
        username = os.environ.get('DOW_JONES_USER_NAME')

        response_text = request_token(client_id, password, username)

        authn_id_token = json.loads(response_text)['id_token']

        jwt_response = request_jwt_token(authn_id_token, client_id)

        authz_access_token = json.loads(jwt_response)['access_token']

        djlog(f"authz token {authz_access_token}", 'AUTHZ_ACCESS_TOKEN')
        return authz_access_token

    if dj_token_Action == "GET":
        djlog(f"Getting the authz access token")
        if os.environ.get('DJ_AUTHZ_ACCESS_TOKEN'):
            return os.environ.get('DJ_AUTHZ_ACCESS_TOKEN')
        else:
            return dj_authz_access_token_action("SET")
    elif dj_token_Action == "SET":
        djlog(f"Creating a new authz access token")
        os.environ['DJ_AUTHZ_ACCESS_TOKEN'] = refresh_authz_access_token()
        djlog(
            f"authz token {os.environ['DJ_AUTHZ_ACCESS_TOKEN']}", 'AUTHZ_ACCESS_TOKEN')
        return os.environ['DJ_AUTHZ_ACCESS_TOKEN']

    else:
        djlog(f"Clearing the authz access token")
        os.environ.pop('DJ_AUTHZ_ACCESS_TOKEN', None)


def search_content(search_string='p/pmdm', search_date_range="Last30Days", from_date=None, to_date=None, page_offset=0, page_limit=10, is_return_headline_coding=True, is_return_djn_headline_coding=True):
    url = "https://api.dowjones.com/content/realtime/search"

    token = dj_authz_access_token_action("GET")

    headers = {
        "accept": "application/vnd.dowjones.dna.content.v_1.0+json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    if search_date_range is not None and search_date_range == "SpecificDateRange":
        from_date = from_date.strftime("%Y-%m-%d")
        to_date = to_date.strftime("%Y-%m-%d")
        date_key_value = [{"custom": {"from": from_date, "to": to_date}}]
    else:
        date_key_value = {"days_range": search_date_range}

    payload = {
        "data": {
            "id": "Search",
            "type": "content",
            "attributes": {
                "query": {
                    "search_string": [
                        {
                            "mode": "Unified",
                            "value": "Joe Biden"

                            # "value": f"djn={search_string.lower()}"
                        }
                    ],
                    # "date": date_key_value
                },
                "formatting": {
                    "is_return_rich_article_id": True
                    # },
                    # "navigation": {
                    #     "is_return_headline_coding": is_return_headline_coding,
                    #     "is_return_djn_headline_coding": is_return_djn_headline_coding
                },
                "page_offset": page_offset,
                "page_limit": page_limit
            }
        }
    }

    with open(f'{DOWJONES_IO_FOLDER_PATH}/djlog_search_payload_{run_uid }.json', 'w') as f:
        f.write(json.dumps(payload, indent=4))

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # create SS and store the payload for use later
    if 'payload' not in st.session_state:
        st.session_state['payload'] = json.dumps(payload)
    else:
        st.session_state.payload = json.dumps(payload)

    uid = UNIQUE_DATE_TIME_STRING()

    if response.ok:
        with open(f'{DOWJONES_IO_FOLDER_PATH}/dj_search_only_result_{uid}.json', 'w') as f:
            f.write(response.text)
        return response.json()
    elif response.status_code == 401:
        dj_authz_access_token_action("CLEAR")
        return search_content(search_string=search_string, search_date_range=search_date_range, from_date=from_date, to_date=to_date, page_offset=page_offset, page_limit=page_limit, is_return_headline_coding=is_return_headline_coding, is_return_djn_headline_coding=is_return_djn_headline_coding)
    else:
        djlog(response.text, f"search_result_{uid}")
        error_message = f"Error: {response.status_code} - {response.text}"
        print(error_message)


def get_content_item(content_id):

    url = f"https://api.dowjones.com/content/{content_id}"

    token = dj_authz_access_token_action("GET")

    headers = {
        "accept": "application/vnd.dowjones.dna+json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    time.sleep(4)

    # djlog(response.text, f"dj_content_dict_{content_id}")

    if response.ok:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"
