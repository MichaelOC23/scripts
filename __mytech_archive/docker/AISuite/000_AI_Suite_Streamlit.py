# from sqlalchemy import column, values
import streamlit as st
import os
import uuid
import asyncio
import json
import re
import json
import requests
import hashlib
import chromadb
from datetime import date, datetime
import time




#?############################################
#?#######     HEADER / SETUP     #############
#?############################################
PAGE_TITLE = "AI Suite Sample Code"
st.set_page_config(
        page_title=PAGE_TITLE, page_icon=":earth_americas:", layout="wide", initial_sidebar_state="collapsed",
        menu_items={'Get Help': 'mailto:michael@justbuildit.com','Report a bug': 'mailto:michael@justbuildit.com',})    



####################################
####      AISUITE CLASS      ####
####################################
class _AISuite:
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
        if bot_id is None or bot_id == '':
            bot_id='7N1aMJqEGbWm'
        
        data = {"name": 'CommSectorInsights', "bot_id": bot_id}
        
        if document_ids:
            data['document_ids'] = document_ids
        response = requests.post(f"{self.base_url}/conversations", headers=self.headers, json={"name": 'CommSectorInsights', "bot_id": bot_id})
        dict_responsse = response.json()
        convo_id = dict_responsse.get('data', {}).get('id', '')
        print(convo_id)
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
        
        st.write(data)
        
            
        response = requests.post(f"{self.base_url}/documents", headers=self.headers, json=json.dumps(data, indent=4))
        st.write(response.json())
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

            
                     
# Initialize the API client
AISuite_Client = _AISuite()

####################################
####       TEST AI SUITE        ####
####################################


def set_up_page(page_title_text=PAGE_TITLE, light_or_dark="dark", session_state_variables=[]):  
        
    def initialize_session_state_variable(variable_name, variable_value):
        if variable_name not in st.session_state:
                    st.session_state[variable_name] = variable_value
    model_dict = {
            "Finance": "nlpaueb/sec-bert-base", 
            "General": "roberta-base",
            "ChatGPT-3.5": "gpt-3.5-turbo",
            "ChatGPT-4": "gpt-4-turbo",
            }
    
    LOGO_URL = "https://devcommunifypublic.blob.core.windows.net/devcommunifynews/jbi-logo-name@3x.png"

    for variable in session_state_variables:
        if isinstance(variable, dict):
            for key in variable.keys():
                initialize_session_state_variable(key, variable[key])
    

    # Standard Session state    
    initialize_session_state_variable("show_session_state", False)
    initialize_session_state_variable("AdminMode", False) 
    initialize_session_state_variable("settings", {"divider-color": "gray",})
    initialize_session_state_variable("temperature", .1)
    initialize_session_state_variable("conversation_id", "")
    initialize_session_state_variable("bot_id", "")
    initialize_session_state_variable("bot_dict", {})
    initialize_session_state_variable("convo_dict", {})
    initialize_session_state_variable("prompt_list", [])
    initialize_session_state_variable("new_prospect_name", None)
    initialize_session_state_variable("open_sales_box_dict", {})
    
    # initialize_session_state_variable("c_need", '')
    # initialize_session_state_variable("c_economics", '')
    # initialize_session_state_variable("c_decisionprocess", '')
    # initialize_session_state_variable("c_competition", '')
    # initialize_session_state_variable("c_timing", '')
    
    # Page Title Colors
    border_color = "#FFFFFF"
    text_color = "#FFFFFF"
    background_color = "#1D1D1D"
    
    # Display the page title and logo and top buttons
    title_col, button_col1, button_col2 = st.columns([8, 1,1])
    st.markdown(f"""
            <div style="
            display: flex; 
            align-items: start; 
            width: 100%; 
            padding: 10px; 
            border: 1px solid {border_color}; 
            border-radius: 10px; 
            height: 80px; background-color: {background_color}; 
            margin-bottom: 20px;"> 
            
            <img src="{LOGO_URL}" alt="{PAGE_TITLE}" 
            style="width: 80px; 
            height: auto; 
            margin: 10px 40px 5px 20px;">  
            
            <span style="flex: 1; 
            font-size: 30px; 
            margin: 2px 0px 10px 10px; 
            font-weight: 400; 
            text-align: top; 
            align: right; 
            white-space: nowrap; 
            overflow: hidden; 
            color: {text_color}; 
            text-overflow: ellipsis;
            ">{PAGE_TITLE}</span>  </div>""", 
            unsafe_allow_html=True)

set_up_page()

def display_result(result):
    st.json(result)

# Helper function to display results


st.subheader("AI Suite - API Examples")
bcol1, bcol2, bcol3,bcol4,bcol5, bcol6 = st.columns([1,1,1,1,1,1,])

# Step 1: List Bots
if bcol1.button("List Bots", use_container_width=True):
    result = AISuite_Client.list_bots()
    display_result(result)



# Step 2: Create Conversation
if 'bot_id' in st.session_state and bcol2.button("Create Conversation", use_container_width=True):
    conversation_name = "Test Conversation"
    result = AISuite_Client.create_conversation(conversation_name, st.session_state.bot_id)
    display_result(result)
    if 'data' in result:
        st.session_state.conversation_id = result['data']['id']
        # print(result.get('data', {}).get())
    else:
        st.error("Failed to create conversation.")

# Step 3: List Conversations
if 'bot_id' in st.session_state and bcol2.button("List Conversations", use_container_width=True):
    result = AISuite_Client.list_conversations(bot_id=st.session_state.bot_id)
    display_result(result)

# Step 4: Get Conversation
if 'conversation_id' in st.session_state and bcol2.button("Get Conversation", use_container_width=True):
    result = AISuite_Client.get_conversation(st.session_state.conversation_id)
    display_result(result)

# Step 5: Update Conversation
if 'conversation_id' in st.session_state and bcol2.button("Update Conversation", use_container_width=True):
    conversation_name = "Test Conversation Updated"
    result = AISuite_Client.update_conversation(st.session_state.conversation_id, conversation_name, st.session_state.bot_id)
    display_result(result)

# Step 6: Create Document
if bcol3.button("Create Document", use_container_width=True):
    document_name = "Test Document"
    folder_id = None  # Assuming no specific folder
    content = "This is a test document."
    result = AISuite_Client.create_document(document_name, folder_id, content)
    display_result(result)
    if 'data' in result:
        st.session_state.document_id = result['data']['id']
    else:
        st.error("Failed to create document.")

# Step 7: List Documents
if bcol3.button("List Documents", use_container_width=True):
    result = AISuite_Client.list_documents()
    display_result(result)

# Step 8: Get Document
if 'document_id' in st.session_state and bcol3.button("Get Document", use_container_width=True):
    result = AISuite_Client.get_document(st.session_state.document_id)
    display_result(result)

# Step 9: List Folders
if bcol4.button("List KBs", use_container_width=True):
    result = AISuite_Client.list_folders()
    display_result(result)

# Step 10: Create Folder
if bcol4.button("Create KB", use_container_width=True):
    folder_name = "Test KB"
    result = AISuite_Client.create_folder(folder_name)
    display_result(result)
    if 'data' in result:
        st.session_state.folder_id = result['data']['id']
    else:
        st.error("Failed to create folder.")

# Step 11: Get Folder
if 'folder_id' in st.session_state and bcol4.button("Get KB", use_container_width=True):
    result = AISuite_Client.get_folder(st.session_state.folder_id)
    display_result(result)

# Step 12: Update Folder
if 'folder_id' in st.session_state and bcol4.button("Update KB", use_container_width=True):
    folder_name = "Test KB Updated"
    result = AISuite_Client.update_folder(st.session_state.folder_id, folder_name)
    display_result(result)

# Step 13: Send Message
if 'conversation_id' in st.session_state and bcol5.button("Send Message", use_container_width=True):
    message_content = "Hello, this is a test message."
    result = AISuite_Client.send_message(message_content, st.session_state.conversation_id)
    display_result(result)
    if 'data' in result:
        st.session_state.message_id = result['data']['id']
    else:
        st.error("Failed to send message.")

# Step 14: List Messages
if 'conversation_id' in st.session_state and bcol5.button("List Messages", use_container_width=True):
    result = AISuite_Client.list_messages(conversation_id=st.session_state.conversation_id)
    display_result(result)

# Step 15: Get Message
if 'message_id' in st.session_state and bcol5.button("Get Message", use_container_width=True):
    result = AISuite_Client.get_message(st.session_state.message_id)
    display_result(result)

# Step 16: Send Message for Stream
if 'conversation_id' in st.session_state and bcol5.button("Send Message for Stream", use_container_width=True):
    message_content = "Hello, this is a test message for streaming."
    result = AISuite_Client.send_message_for_stream(message_content, st.session_state.conversation_id, redirect=False)
    display_result(result)

# Step 17: Get Uploads Signed URL
if bcol6.button("Get Upload URL", use_container_width=True):
    file_name = "test_upload.txt"
    content_type = "text/plain"
    result = AISuite_Client.get_uploads_signed_url(file_name, content_type)
    display_result(result)

# Cleanup: Delete Document and Conversation
if bcol6.button("Cleanup", use_container_width=True):
    if 'document_id' in st.session_state:
        result = AISuite_Client.delete_document(st.session_state.document_id)
        display_result(result)
    if 'conversation_id' in st.session_state:
        result = AISuite_Client.delete_conversation(st.session_state.conversation_id)
        display_result(result)
    st.success("Cleanup completed.")



if st.button("Talk to cody", use_container_width=True):
    
    testdata=[
    {
        "Name": "Tickers",
        "Value": [
        " Cash & Cash Equivalents 28.500938275354134", 
        " Technology 28.054150295120305",
        " Healthcare 10.061465633117535",
        " Consumer Cyclical 9.12137664488726",
        " Financial Services 7.519439701850098",
        " Industrials 4.065707742204118",
        " Communication Services 3.6544319694908785",
        " Consumer Defensive 2.949160381912664",
        " Utilities 1.9413807551514266",
        " Real Estate 1.9207883007029813",
        " Energy 1.381408054818838",
        " Basic Materials 0.829752245389758"
        ]
    }
    ]
    
    data_to_use = testdata[0].get("Value", '')
    
    import json
    import requests

    # Main body of python function begins here
    TICKERS_FOR_TESTING = ['NVDA', 'CSCO']
    TEST_MODE = False
    VALUE_TO_RETURN = ""
    ERROR_REASONS = []
    CODY_RESPONSE = ""

    def get2(retries):
        bot_id = "7N1aMJqEGbWm" 
        conversation_id = "gl9avV8B8aG1"
        default_table_folder = "Oy5eVO25WaEP"
        base_url = "https://getcody.ai/api/v1"
        api_key = "WpQSaGhqj4PVlNP0xK4XvnmdKtYpg8mv3WsdqHCCefa2b909"
        headers = {'Authorization': 'Bearer {}'.format(api_key), 'Content-Type': 'application/json'}

        def extract_questions(data):
            try:
                question_dict = {
                    "Q1": data.get("Q1", ""),
                    "Q2": data.get("Q2", ""),
                }
            except Exception as e:
                ERROR_REASONS.append("Error extracting questions. Function: {}  data: {}: Error Message: {}".format("extract_questions", data, e))

            return question_dict

        def getContent(response_dict):
            data = response_dict.get("data", {})

            if data.get("failed_responding", True):
                return False

            try:
                content = extract_json_dict_from_llm_response(data.get("content", ""))

                resp = {
                    "Commentary": content.get("commentary", ""),
                    "Questions": extract_questions(content)
                }
                return resp
            except Exception as e:
                ERROR_REASONS.append("Error extracting json from llm response. Function: {}  response_dict: {}: Error Message: {}".format("getContent", response_dict, e))

        def extract_json_dict_from_llm_response(content):
            # Find the first '{' and the last '}'
            start_idx = content.find('{')
            end_idx = content.rfind('}')

            if start_idx == -1 or end_idx == -1:
                return None

            try:
                # Extract the JSON string
                json_string = content[start_idx:end_idx + 1]

                # Load and return the JSON as a dictionary
                return json.loads(json_string)
            except Exception as e:
                ERROR_REASONS.append("Error extracting json from llm response. Function: {}  Content: {}: Error Message: {}".format("extract_json_dict_from_llm_response", content, e))

        # Body of get(retries) function
        try:
            message_content = "My portfolio contains the following industry sector allocations: " + ", ".join(data_to_use) + ".  Would you help me analyze my portfolio?"

            data = {
                "content": message_content,
                "conversation_id": conversation_id
            }

            #return data
            response = requests.post("https://getcody.ai/api/v1/messages", headers=headers, json=data)
            
            response_dict = response.json()
            return response_dict #remove

            content = getContent(response_dict)
        except Exception as e:
            ERROR_REASONS.append("Error extracting or formatting json from llm response. Function: {}  Tickers {}: Error Message: {}".format("get(retries)", data_to_use, e))

        return content

    def get(attempts):
        global VALUE_TO_RETURN
        global ERROR_REASONS
        global CODY_RESPONSE
        last_exception = None
        for attempt in range(attempts):
            try:
                result = get2(attempt)
                return result #remove

                if (len(ERROR_REASONS)>0):
                    VALUE_TO_RETURN = ""
                    ERROR_REASONS = []
                    CODY_RESPONSE = ""
                else:
                    return result
            except Exception as e:
                last_exception = e

        # If all attempts fail, raise the last exception encountered
        if last_exception:
            raise last_exception

    # Tickers = TICKERS_FOR_TESTING

    try:
        tickers = ",".join(data_to_use)
        cacheKey = f"plugin.codyai-portfolio-insights/{tickers}"
        #output = JBI.GetFromCache(cacheKey)
        output = None
        
        if not output or len(output)==0:
            output = get(3)
        #     JBI.SetToCache(cacheKey,output,90)

        VALUE_TO_RETURN = output
    except Exception as e:
        pass
        ERROR_REASONS.append("Error in main body of python function. Error Message: {}".format(e))

    result = {
        "Success": True,
        "TestMode": TEST_MODE,
        "Reasons": ERROR_REASONS,
        "Value": VALUE_TO_RETURN,
        "received_input": data_to_use
    }
    print(json.dumps(result, indent=4))