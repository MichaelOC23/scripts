# from sqlalchemy import column, values
import os
import uuid
import asyncio
import json
import re
import json
import requests
import hashlib
from datetime import date, datetime
import time

bot_id = "7N1aMJqEGbWm"
conversation_id = "wMvbm3LO0eYA"

####################################
####      AISUITE CLASS      ####
####################################
class AISuite:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = "gX8NGF0KtNw6BTx5PqQJapYwyhxKia7vHmJgrywCa98df424"
        self.api_key = api_key
        # self.default_table_folder = "W4QbYEX19bzq"
        self.default_table_folder = "Oy5eVO25WaEP"
        self.base_url = "https://getcody.ai/api/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def create_sales_box_document(self, name, content):
        data = {
            "name": name,
            "folder_id": self.default_table_folder,
            "content": content
        }
        response = requests.post(f"{self.base_url}/documents", headers=self.headers, json=data)
        return response.json()
    
    def list_bots(self, keyword=None):
        params = {}
        if keyword:
            params['keyword'] = keyword
        response = requests.get(f"{self.base_url}/bots", headers=self.headers, params=params)
        return response.json()

    def list_conversations(self, bot_id=None, keyword=None, includes=None):
        params = {}
        if bot_id:
            params['bot_id'] = bot_id
        if keyword:
            params['keyword'] = keyword
        if includes:
            params['includes'] = includes
        response = requests.get(f"{self.base_url}/conversations", headers=self.headers, params=params)
        return response.json()

    def create_conversation(self, name, bot_id, document_ids=None):
        data = {
            "name": name,
            "bot_id": bot_id
        }
        if document_ids:
            data['document_ids'] = document_ids
        response = requests.post(f"{self.base_url}/conversations", headers=self.headers, json=data)
        return response.json()

    def get_conversation(self, conversation_id, includes=None):
        params = {}
        if includes:
            params['includes'] = includes
        response = requests.get(f"{self.base_url}/conversations/{conversation_id}", headers=self.headers, params=params)
        return response.json()

    def update_conversation(self, conversation_id, name, bot_id, document_ids=None):
        data = {
            "name": name,
            "bot_id": bot_id
        }
        if document_ids:
            data['document_ids'] = document_ids
        response = requests.post(f"{self.base_url}/conversations/{conversation_id}", headers=self.headers, json=data)
        return response.json()

    def delete_conversation(self, conversation_id):
        response = requests.delete(f"{self.base_url}/conversations/{conversation_id}", headers=self.headers)
        return response.json()

    def list_documents(self, folder_id=None, conversation_id=None, keyword=None):
        params = {}
        if folder_id:
            params['folder_id'] = folder_id
        if conversation_id:
            params['conversation_id'] = conversation_id
        if keyword:
            params['keyword'] = keyword
        response = requests.get(f"{self.base_url}/documents", headers=self.headers, params=params)
        return response.json()

    def get_prospect_content_template(self):
        content_dict = {"salesbox":{
            "need": "We are looking for a solution that can help us with our sales process.",
            "economics": "We are looking for a solution that can help us with our sales process.",
            "timing": "We are looking for a solution that can help us with our sales process.",
            "decisionprocess": "We are looking for a solution that can help us with our sales process.",
            "competition": "We are looking for a solution that can help us with our sales process."
            }}
        return content_dict
        
    def create_prospect(self, prospect_name, content=None):
        if content is None:
            content = self.get_prospect_content_template()
            
        data = {
            "name": f"jbi_{prospect_name}",
            "folder_id": self.default_table_folder,
            "content": content
        }
        
        # st.write(data)
        
            
        response = requests.post(f"{self.base_url}/documents", headers=self.headers, json=json.dumps(data, indent=4))
        # st.write(response.json())
        return response.json()
    
    def create_prospect_dict(self, document_list):
        prospect_dict = {}
        for document in document_list:
            prospect_dict[document['name']] = document['id']
        return prospect_dict
    
    def list_prospects(self, keyword=None):
        params = {}
        params['folder_id'] = self.default_table_folder
        
        response = requests.get(f"{self.base_url}/documents", headers=self.headers, params=params)
        if response.status_code == 200:
            prospect_dict = self.create_prospect_dict(response.json().get('data', []))
            return prospect_dict
        else: 
            return {}

    def get_prospect_document(self, document_id):
        response = requests.get(f"{self.base_url}/documents/{document_id}", headers=self.headers)
        doc_dict = response.json()
        doc_url = doc_dict.get('data', {}).get('content_url', "")
        if doc_url != "":
            doc_content = requests.get(doc_url, headers=AISuite_Client.headers)
        return doc_content.get('content'    , "")

    def create_document(self, name, folder_id, content=None):
        data = {
            "name": name,
            "folder_id": folder_id
        }
        if content:
            data['content'] = content
        response = requests.post(f"{self.base_url}/documents", headers=self.headers, json=data)
        return response.json()

    def create_document_from_file(self, folder_id, key):
        data = {
            "folder_id": folder_id,
            "key": key
        }
        response = requests.post(f"{self.base_url}/documents/file", headers=self.headers, json=data)
        return response.json()

    def create_document_from_webpage(self, folder_id, url):
        data = {
            "folder_id": folder_id,
            "url": url
        }
        response = requests.post(f"{self.base_url}/documents/webpage", headers=self.headers, json=data)
        return response.json()

    def get_document(self, document_id):
        response = requests.get(f"{self.base_url}/documents/{document_id}", headers=self.headers)
        return response.json()

    def delete_document(self, document_id):
        response = requests.delete(f"{self.base_url}/documents/{document_id}", headers=self.headers)
        return response.json()

    def list_folders(self, keyword=None):
        params = {}
        if keyword:
            params['keyword'] = keyword
        response = requests.get(f"{self.base_url}/folders", headers=self.headers, params=params)
        return response.json()

    def create_folder(self, name):
        data = {
            "name": name
        }
        response = requests.post(f"{self.base_url}/folders", headers=self.headers, json=data)
        return response.json()

    def get_folder(self, folder_id):
        response = requests.get(f"{self.base_url}/folders/{folder_id}", headers=self.headers)
        return response.json()

    def update_folder(self, folder_id, name):
        data = {
            "name": name
        }
        response = requests.post(f"{self.base_url}/folders/{folder_id}", headers=self.headers, json=data)
        return response.json()

    def list_messages(self, conversation_id=None, includes=None):
        params = {}
        if conversation_id:
            params['conversation_id'] = conversation_id
        if includes:
            params['includes'] = includes
        response = requests.get(f"{self.base_url}/messages", headers=self.headers, params=params)
        return response.json()

    def send_message(self, content, conversation_id):
        data = {
            "content": content,
            "conversation_id": conversation_id
        }
        response = requests.post(f"{self.base_url}/messages", headers=self.headers, json=data)
        return response.json()

    def get_message(self, message_id, includes=None):
        params = {}
        if includes:
            params['includes'] = includes
        response = requests.get(f"{self.base_url}/messages/{message_id}", headers=self.headers, params=params)
        return response.json()

    def send_message_for_stream(self, content, conversation_id, redirect=True):
        data = {
            "content": content,
            "conversation_id": conversation_id,
            "redirect": redirect
        }
        response = requests.post(f"{self.base_url}/messages/stream", headers=self.headers, json=data)
        return response.json()

    def get_uploads_signed_url(self, file_name, content_type):
        data = {
            "file_name": file_name,
            "content_type": content_type
        }
        response = requests.post(f"{self.base_url}/uploads/signed-url", headers=self.headers, json=data)
        return response.json()

    def test_all_functions(self):
        try:
            # 1. List Bots
            bots = self.list_bots()
            print("List Bots:", bots)
            if 'data' in bots and bots['data']:
                bot_id = bots['data'][0]['id']
            else:
                print("No bots available to test with.")
                return

            # 2. Create Conversation
            conversation_name = "Test Conversation"
            conversation = self.create_conversation(conversation_name, bot_id)
            print("Create Conversation:", conversation)
            if 'data' in conversation:
                conversation_id = conversation['data']['id']
            else:
                print("Failed to create conversation.")
                return

            # 3. List Conversations
            conversations = self.list_conversations(bot_id=bot_id)
            print("List Conversations:", conversations)

            # 4. Get Conversation
            conversation_details = self.get_conversation(conversation_id)
            print("Get Conversation:", conversation_details)

            # 5. Update Conversation
            updated_conversation = self.update_conversation(conversation_id, conversation_name + " Updated", bot_id)
            print("Update Conversation:", updated_conversation)

            # 6. Create Document
            document_name = "Test Document"
            folder_id = None  # Assuming no specific folder
            content = "This is a test document."
            document = self.create_document(document_name, folder_id, content)
            print("Create Document:", document)
            if 'data' in document:
                document_id = document['data']['id']
            else:
                print("Failed to create document.")
                return

            # 7. List Documents
            documents = self.list_documents()
            print("List Documents:", documents)

            # 8. Get Document
            document_details = self.get_document(document_id)
            print("Get Document:", document_details)

            # 9. List Folders
            folders = self.list_folders()
            print("List Folders:", folders)

            # 10. Create Folder
            folder_name = "Test Folder"
            folder = self.create_folder(folder_name)
            print("Create Folder:", folder)
            if 'data' in folder:
                folder_id = folder['data']['id']
            else:
                print("Failed to create folder.")
                return

            # 11. Get Folder
            folder_details = self.get_folder(folder_id)
            print("Get Folder:", folder_details)

            # 12. Update Folder
            updated_folder = self.update_folder(folder_id, folder_name + " Updated")
            print("Update Folder:", updated_folder)

            # 13. Send Message
            message_content = "Hello, this is a test message."
            message = self.send_message(message_content, conversation_id)
            print("Send Message:", message)
            if 'data' in message:
                message_id = message['data']['id']
            else:
                print("Failed to send message.")
                return

            # 14. List Messages
            messages = self.list_messages(conversation_id=conversation_id)
            print("List Messages:", messages)

            # 15. Get Message
            message_details = self.get_message(message_id)
            print("Get Message:", message_details)

            # 16. Send Message for Stream
            stream_message = self.send_message_for_stream(message_content, conversation_id, redirect=False)
            print("Send Message for Stream:", stream_message)

            # 17. Get Uploads Signed URL
            file_name = "test_upload.txt"
            content_type = "text/plain"
            upload_url = self.get_uploads_signed_url(file_name, content_type)
            print("Get Uploads Signed URL:", upload_url)

            # Cleanup
            self.delete_document(document_id)
            self.delete_conversation(conversation_id)

            print("All functions tested successfully.")
        except Exception as e:
            print("An error occurred while testing functions:", str(e))


def extract_questions(data):
    return [value for key, value in data.items() if key.startswith('Q')]

def getContent(result):
    
    data = result.get("data",{})

    if data.get("failed_responding",True):
        return False
    
    try: 
        
        content = json.loads(data.get("content",{}))

        resp = {
            "Commentary" : content.get("commentary",""),
            "Questions" : extract_questions(content)
        }
        return resp
    except:
        return False
   

def get(retries):
    aisuite = AISuite()  


    message_content = "My porfolio contains the following securities: " + ", ".join(Tickers) + ".  Would you help me analyze my portfolio?"
    result = aisuite.send_message(message_content, conversation_id)

    
    content = getContent(result)

    # if content==False:
    #     if (retries>3)
    #         return False

    #     get(++retries)
    
    return content

result = {
    "Success": True,
    "Reasons": [],
    "Value": get(0)
}





[
    {
      "Name": "Tickers",
      "Value": ["NVDA", "AAPL", "CSCO"]
    }
]