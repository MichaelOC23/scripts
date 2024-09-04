from flask import Flask, request, redirect, url_for, session
import requests
from urllib.parse import urlencode
import base64
import os
import json
import hashlib

app = Flask(__name__)


CLIENT_ID = '6a25a3f9-2c15-4b0f-9b9b-60327dceff46'
TENANT_ID = '050376de-b1f5-4dbc-8c0f-8929b6e68a08' 



app.secret_key = os.urandom(24)

# OAuth Endpoints
AUTH_ENDPOINT = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize'
TOKEN_ENDPOINT = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'

# Microsoft Graph Endpoint
GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0'

def generate_code_verifier():
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')

def generate_code_challenge(code_verifier):
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')

@app.route('/')
def homepage():
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    session['code_verifier'] = code_verifier
    
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': url_for('auth_redirect', _external=True),
        'scope': 'openid profile User.Read Mail.Read',
        'response_mode': 'query',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }
    auth_url = f'{AUTH_ENDPOINT}?{urlencode(auth_params)}'
    return redirect(auth_url)

@app.route('/redirect')
def auth_redirect():
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

if __name__ == '__main__':
    app.run(port=5000)
