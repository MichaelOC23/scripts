from azure.storage.blob import BlobServiceClient
from azure.communication.sms import SmsClient
import uuid
import base64
from bs4 import BeautifulSoup
import base64
import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import shared.functions_gmail as gmail
import shared.functions_constants as constants
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build



def html_to_plain_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()


def generate_run_id():
    unique_id = uuid.uuid4()
    base64_id = base64.urlsafe_b64encode(unique_id.bytes).decode('utf-8').rstrip('==')
    return base64_id[:12]


def getVal(ValName):
    if ValName == 'storage_blob_connection_string':
        return #! FIX ME USE ENV VAR
    if ValName == 'azure_communication_connection_string':
        return #! FIX ME USE ENV VAR



def send_sms(from_phone_number, to_phone_number, message):
    azure_connection_string = getVal('azure_communication_connection_string')  # Removed trailing comma
    sms_client = SmsClient.from_connection_string(azure_connection_string)
    sms_response = sms_client.send(
        from_=from_phone_number,
        to=[to_phone_number],
        message=message
    )
    return sms_response



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_creds():
    """ some stuff to say """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        return creds
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
    return creds

def get_body(message):
    try:
        if 'data' in message['payload']['body']:
            return base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        elif 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/html' or part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    if 'parts' in part:  # If parts exist in the current part, recursively look into them
                        return get_body({'payload': part})
        return None  # Return None if no body data is found
    except Exception as e:
        print(f"An error occurred while getting the email body: {e}")
        return None


def html_to_plain_text(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def get_email_body(service, user_id, email_id):
    message = service.users().messages().get(userId=user_id, id=email_id).execute()
    body = get_body(message)
    if body and '<html' in body.lower():
        return html_to_plain_text(body)
    return body

def get_emails_full_contents(run_id2, message_count=10):
    """
    Function printing python version.
    """

    creds = get_creds()
    count = 0
    service = build('gmail', 'v1', credentials=creds)
    try: # Call the Gmail API
        page_messages = []
        page_token = None

        while True and count <= message_count:
            count = count + 1
            results = service.users().messages().list(userId='me', pageToken=page_token).execute()
            messages = results.get('messages', [])
            
            for message in messages:
                msg_id = message.get('id')
                output_file = f'{constants.EMAIL_IO_FOLDER_PATH}/gmail_message_{msg_id}.json'
                if os.path.exists(output_file):
                    print(f'{output_file} already exists. Skipping...')
                    continue
                msg_data = service.users().messages().get(userId='me', id=msg_id).execute()
                thread_id = message.get('threadId')

                headers = msg_data['payload']['headers']
                date = subject = sender = cc = None
                body = get_body(msg_data)  # This should be msg_data not message
                if body and '<html' in body.lower():
                    body = html_to_plain_text(body)

                for header in headers:
                    name = header.get('name')
                    value = header.get('value')
                    if name == 'Date':
                        date = value
                    elif name == 'Subject':
                        subject = value
                    elif name == 'From':
                        sender = value
                    elif name == 'Cc':
                        cc = value

                next_message = {
                    'id': msg_id,
                    'date': date,
                    'subject': subject,
                    'sender': sender,
                    'cc': cc,
                    'body': body,
                    'headers': headers,
                    'threadid': thread_id
                }

                page_messages.append(next_message)

            
            with open(output_file, 'w') as file:
                json.dump(next_message, file, indent=4)
            
            
            # connection_string = sf.getVal('storage_blob_connection_string')
            # blob_name = f'allmessages {run_id2} {count}.text'
            # sf.upload_file_to_azure(data, 'gmail-blob', blob_name, connection_string)
            page_token = results.get('nextPageToken')
            # print (f'{blob_name} complete.')
            if not page_token:
                break
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')




if __name__ == "__main__":
    print("This is a module not a script")



#upload_file_to_azure('123456', 'your-container-name', 'test.text', connection_string)
