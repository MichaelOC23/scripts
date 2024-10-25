import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import functions_gmail as sf
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_recent_emails(run_id2):
    """
    Function printing python version.
    """

    creds = get_creds()
    # Assuming 'messages' is your list of messages
    sender_count = {}  # Dictionary to keep track of sender occurrences

    count = 0
    service = build('gmail', 'v1', credentials=creds)
    try: # Call the Gmail API
        page_messages = []
        page_token = None

        while True:
            if count >= 50:
                with open(f'SenderCount {run_id2}.text', 'w', encoding='utf-8') as f:
                    for sender, count in sender_count.items():
                        f.write(f'{sender}: {count}\n')
                break

            count = count + 1
            results = service.users().messages().list(userId='me', pageToken=page_token).execute()
            # results = service.users().messages().list(pageToken=page_token).execute()

            messages = results.get('messages', [])
            
            for message in messages:
                msg_id = message.get('id')
                msg_data = service.users().messages().get(userId='me', id=msg_id).execute()
                thread_id = message.get('threadId')
                
                headers = msg_data['payload']['headers']
                date = subject = sender = cc = None
                #body = get_body(msg_data)  # This should be msg_data not message
                #if body and '<html' in body.lower():
                 #   body = html_to_plain_text(body)
                
                for header in headers:
                    name = header.get('name')
                    value = header.get('value')
                    if name == 'Date':
                        date = value
                    elif name == 'Subject':
                        subject = value
                    elif name == 'From':
                        sender = value
                        #Append to senders file
                        sender_count[sender] = sender_count.get(sender, 0) + 1

                        with open(f'senders {run_id2} {count}.text', 'a', encoding='utf-8') as f:
                            f.write(f'{sender}\n')
                    elif name == 'Cc':
                        cc = value
            
                page_messages.append({
                    'id': msg_id,
                    'date': date,
                    'subject': subject,
                    'sender': sender,
                    'cc': cc,
                    #'body': body,
                    'headers': headers,
                    'threadid': thread_id
                })
                with open(f'allmessages {run_id2}.text', 'a', encoding='utf-8') as f:
                    f.write(f'{msg_id} | {sender} | {date} | {subject}  | {cc}\n')

            data = json.dumps(page_messages, indent=4)
            
            #connection_string = sf.getVal('storage_blob_connection_string')
            #blob_name = f'allmessages {run_id2} {count}.text'
            #sf.upload_file_to_azure(data, 'gmail-blob', blob_name, connection_string)
            page_token = results.get('nextPageToken')
            #print (f'{blob_name} complete.')
            if not page_token:

                break
    except Exception as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

        

def get_recent_emails(run_id2):
    """
    Function printing python version.
    """

    creds = get_creds()
    # Assuming 'messages' is your list of messages
    sender_count = {}  # Dictionary to keep track of sender occurrences

    count = 0
    service = build('gmail', 'v1', credentials=creds)
    try: # Call the Gmail API
        page_messages = []
        page_token = None

        while True:
            if count >= 50:
                with open(f'SenderCount {run_id2}.text', 'w', encoding='utf-8') as f:
                    for sender, count in sender_count.items():
                        f.write(f'{sender}: {count}\n')
                break

            count = count + 1
            results = service.users().messages().list(userId='me', pageToken=page_token).execute()
            # results = service.users().messages().list(pageToken=page_token).execute()

            messages = results.get('messages', [])
            
            for message in messages:
                msg_id = message.get('id')
                msg_data = service.users().messages().get(userId='me', id=msg_id).execute()
                thread_id = message.get('threadId')
                
                headers = msg_data['payload']['headers']
                date = subject = sender = cc = None
                #body = get_body(msg_data)  # This should be msg_data not message
                #if body and '<html' in body.lower():
                 #   body = html_to_plain_text(body)
                
                for header in headers:
                    name = header.get('name')
                    value = header.get('value')
                    if name == 'Date':
                        date = value
                    elif name == 'Subject':
                        subject = value
                    elif name == 'From':
                        sender = value
                        #Append to senders file
                        sender_count[sender] = sender_count.get(sender, 0) + 1

                        with open(f'senders {run_id2} {count}.text', 'a', encoding='utf-8') as f:
                            f.write(f'{sender}\n')
                    elif name == 'Cc':
                        cc = value
            
                page_messages.append({
                    'id': msg_id,
                    'date': date,
                    'subject': subject,
                    'sender': sender,
                    'cc': cc,
                    #'body': body,
                    'headers': headers,
                    'threadid': thread_id
                })
                with open(f'allmessages {run_id2}.text', 'a', encoding='utf-8') as f:
                    f.write(f'{msg_id} | {sender} | {date} | {subject}  | {cc}\n')

            data = json.dumps(page_messages, indent=4)
            
            #connection_string = sf.getVal('storage_blob_connection_string')
            #blob_name = f'allmessages {run_id2} {count}.text'
            #sf.upload_file_to_azure(data, 'gmail-blob', blob_name, connection_string)
            page_token = results.get('nextPageToken')
            #print (f'{blob_name} complete.')
            if not page_token:

                break
    except Exception as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')





def get_creds():
    """ some stuff to say """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # get the folder path of the current file
    folder_path = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(f'{folder_path}/token.json'):
        creds = Credentials.from_authorized_user_file(f'{folder_path}/token.json', SCOPES)
        return creds
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(f'{folder_path}/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'{folder_path}/token.json', 'w', encoding='utf-8') as token:
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

def get_emails_full_contents(run_id2):
    """
    Function printing python version.
    """

    creds = get_creds()
    count = 0
    service = build('gmail', 'v1', credentials=creds)
    try: # Call the Gmail API
        page_messages = []
        page_token = None

        while True:
            count = count + 1
            results = service.users().messages().list(userId='me', pageToken=page_token).execute()
            messages = results.get('messages', [])
            
            for message in messages:
                msg_id = message.get('id')
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
            
            page_messages.append({
                'id': msg_id,
                'date': date,
                'subject': subject,
                'sender': sender,
                'cc': cc,
                'body': body,
                'headers': headers,
                'threadid': thread_id
            })

            data = json.dumps(page_messages, indent=4)
            connection_string = sf.getVal('storage_blob_connection_string')
            blob_name = f'allmessages {run_id2} {count}.text'
            sf.upload_file_to_azure(data, 'gmail-blob', blob_name, connection_string)
            page_token = results.get('nextPageToken')
            print (f'{blob_name} complete.')
            if not page_token:
                break
    except Exception as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


def main(run_id1):
    """Hello this is it"""
    get_recent_emails(run_id1)
    #send_sms()

if __name__ == '__main__':
    # Usage:
    run_id = sf.generate_run_id()
    print(f'Run ID: {run_id}')  # Output: Unique run ID of 12 characters
    main(run_id)
    