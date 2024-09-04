import requests
import os
import uuid
import asyncio
import asyncpg
import json
import psycopg2
import re
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin
import urllib.parse
import tldextract
import html2text
import hashlib
import chromadb
import ollama
from datetime import date, datetime
import time

import base64
import subprocess
import csv
import streamlit as st
from _class_streamlit import streamlit_mytech as cs
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode, ColumnsAutoSizeMode
# import nats 
# from nats.aio.client import Client as NATS
# from _class_storage import _storage as embed_storage
# import _class_BMM as BMM

PROJECT_PATH = '/Users/michasmi/code/platform/Src/Api'
NATS_RESULT_LOGS = '/Users/michasmi/code/nats_logs'
WATCHLIST_CSV_PATH = '/Users/michasmi/code/data/sources/privateasset1or2.csv'

cs.set_up_page(page_title_text="Communify Product Tools", jbi_or_cfy="jbi", light_or_dark="dark", 
    session_state_variables=[{"SectorList": []}, 
                             {"PrivateAssetList": []}, 
                             {"PersonalPositionDict": {}},
                             {"AccountBalancesList": []},
                             {"AccountFinancialSummaryList": []},
                             {'lotdata': {}}, 
                             {'pgldata': {}}, 
                             {'tickers': []},
                             {'nats_token': ''}, 
                             {'NatsIsConnected': False}, 
                             {'nats_error_message_string': ''}, 
                            {'tickers_string': ""}], 
    connect_to_dj=False) 
st.write(st.session_state['nats_token'])

class _scrape():
    def __init__(self): 
        self.log_folder = "logs"
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        
        
        #Contact-specific items
        self.SECOrgCRDNum = ""
        self.RegisteredEntity = ""
        self.CCOName = ""
        self.CCOEmail = ""
        self.Website = ""
        self.CCOEmailDomain = ""
        
        #Example of AI Pipeline for RBC for 
        self.LeadershipTitles = ["CEO"]
        self.LeadershipAreas = ["Wealth Management", "Digital Wealth "]
        self.Markets = ["USA", "Canada", "UK", "Europe", "Asia"]
        self.SeedNamesCommoon = ["Smith", "Johnson", "Williams", "Brown"] #"Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        self.leadership_references = ["Leadership", "Founders", "Executive Team", 
                                      "Management Team", "Board of Directors"]
        
        self.log_key = datetime.now().strftime("%Y%m%d%H%M%S")
        
        self.llm_model = 'llama3'
        self.llm_base_url='http://localhost:11434/v1'
        self.llm_model_api_key='Local-None-Needed'
        
        self.embeddings_model = 'mxbai-embed-large'
        self.embeddings_base_url='http://localhost:11434/v1'
        self.embeddings_model_api_key='Local-None-Needed'
        
        self.scrape_session_history = {}

        self.embeddings_model='mxbai-embed-large'
        self.google_api_key = os.environ.get('GOOGLE_API_KEY', 'No Key or Connection String found')
        self.google_general_cx = os.environ.get('GOOGLE_GENERAL_CX', 'No Key or Connection String found')
    
    def create_email_extraction_prompt(self, name, email, domain, json_str=""):
        prompt = '''Given this text, what are the names and email addresses of the people with an email with ''' + f"{domain}" + "."
        prompt = prompt + ''' Your responses are being systematically integrated. Do not replay with any response other that the names of the people and their emails in this JSON format.  
                    Please extend the data below with the additional records and return the entire new JSON dataset with current and new records in your response.

                    ### JSON Dataset '''
        if json_str == "":
            json_str = json.dumps({ 
                                    "Emails":
                                    [{"Name": name, "Email": email}]
                                    }, indent=4)    
        prompt = prompt + json_str
                    
                    
        return prompt
    
    def chromadb_collection_exists(self, client, collection_name):
        collections = client.list_collections()
        for collection in collections:
            if collection.name == collection_name:
                return True
            else:
                return False
        
    def prepare_text_for_embedding(self, any_text_list_or_dict):
        
        if any_text_list_or_dict is None or any_text_list_or_dict == "":
            return []
        
        if isinstance(any_text_list_or_dict, str):
            any_text_list_or_dict = [any_text_list_or_dict]
        
        # Flatten the JSON data into a single string
        text = json.dumps(any_text_list_or_dict, ensure_ascii=False)
        
        # Normalize whitespace and clean up text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split text into chunks by sentences, respecting a maximum chunk size
        sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            
            # Check if the current sentence plus the current chunk exceeds the limit
            if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                current_chunk += (sentence + " ").strip()
            else:
                # When the chunk exceeds 1000 characters, store it and start a new one
                chunks.append(current_chunk)
                current_chunk = sentence + " "
        if current_chunk:  # Don't forget the last chunk!
            chunks.append(current_chunk)
        
        text_to_embed_list = []
        for chunk in chunks:
            # Write each chunk to its own line
            text_to_embed_list.append(chunk.strip() + "\n")  # Two newlines to separate chunks
        
        return text_to_embed_list

    def embed_text_chroma(self, documents, collection_name):
        client = chromadb.Client()
        if not self.chromadb_collection_exists(client, collection_name):
            collection = client.create_collection(name=collection_name)
        
        # store each document in a vector embedding database
        for i, d in enumerate(documents):
            response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
            embedding = response["embedding"]
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[d]
            )

    def get_relevant_embeddings(self, prompt, collection_name, n_results=10):
        client = chromadb.Client()
        collection = client.get_or_create_collection(name=collection_name)

        # generate an embedding for the prompt and retrieve the most relevant doc
        response = ollama.embeddings(
        prompt=prompt,
        model=self.embeddings_model
        )
        results = collection.query(
        query_embeddings=[response["embedding"]],
        n_results=n_results
        )
        data = results['documents'][0]
        return data

    def query_ollama_with_embedding(self, prompt, embeddings):

        output = ollama.generate(
            model="llama2",
            prompt=f"Using this data:\n {embeddings}. Respond to this prompt: \n{prompt}")
        
        return output['response']

    def log_it(self, message, color='black', data="", print_it=True):
        color_dict = {        
            "BLACK":"\033[0;30m",
            "RED":"\033[0;31m",
            "RED_U":"\033[4;31m",
            "RED_BLINK":"\033[5;31m",
            "GREEN":"\033[0;32m",
            "GREEN_BLINK":"\033[5;32m",
            "YELLOW":"\033[0;33m",
            "YELLOW_BOLD":"\033[1;33m",
            "PURPLE":"\033[1;34m",
            "PURPLE_U":"\033[4;34m",
            "PURPLE_BLINK":"\033[5;34m",
            "PINK":"\033[0;35m",
            "PINK_U":"\033[4;35m",
            "PINK_BLINK":"\033[5;35m",
            "LIGHTBLUE":"\033[0;36m",
            "LIGHTBLUE_BOLD":"\033[1;36m",
            "GRAY":"\033[0;37m",
            "ORANGE":"\033[1;91m",
            "BLUE":"\033[1;94m",
            "CYAN":"\033[1;96m",
            "WHITE":"\033[1;97m",
            "MAGENTA":"\033[1;95m",
            "BOLD":"\033[1m",
            "UNDERLINE":"\033[4m",
            "BLINK":"\033[5m",
            "NC":"\033[0m'"} # No Colo"}
                
        if color.upper() in color_dict:
            color_code = color_dict[color.upper()]
            terminal_message = f"{color_code}{message}{color_dict['NC']} \n {data}"
        
        def got_dict(input_value):
            if isinstance(input_value, dict):
                return True, input_value
            try:
                type_value = type(input_value)
                input_value = json.loads(input_value)
            except Exception as e:
                return False, f"Type is: {type_value}.  Could not convert input to dictionary: {e}"
            return True, input_value
        
        is_dict, dict_value = got_dict(message)
        
        
        if is_dict:
            message = json.dumps(dict_value, indent=4)
        else:
            message = f"{message}"
            
        with open(os.path.join(self.log_folder, f"Contact_Gen_log_{self.log_key}.txt"), 'a') as f:
            f.write(message)
            print(terminal_message)
    
    def get_url_domain(self, url):
        try: 
            parsed_url = urlparse(url)        
            domain_parts = parsed_url.netloc.split('.')
            domain = '.'.join(domain_parts[-2:]) if len(domain_parts) > 1 else parsed_url.netloc

            return domain
            
        except:
            return ""
    
    def is_valid_url(self, may_be_a_url):
        try:
            result = urlparse(may_be_a_url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False    
    
    def get_base_url(self, url):
        try: 
            parsed_url = urlparse(url)            
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return base_url
        except:
            return ""
    
    def generate_unique_key_for_url(self, url):
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        
        # Encode the URL to bytes and update the hash object
        hash_object.update(url.encode('utf-8'))
        
        # Get the hexadecimal representation of the hash
        unique_key = hash_object.hexdigest()
        
        return unique_key
     
    def extract_N_urls_from_markdown(self, markdown, N=5):
        # Split the markdown into lines
        lines = markdown.split('\n')
        
        # Find lines that start with '### '
        h3_lines = [line for line in lines if line.startswith('### ')]
        
        # Regular expression to match the URL
        pattern = r"/url\?q=(https?://[^\s&]+)"

        # Search for the pattern in the text
        

        urls = []
        urls_found = 0
        
        # Search for the URL
        for result in h3_lines:
            match = re.search(pattern, result)
            if match is not None and self.is_valid_url(match.group(1)):
                urls_found += 1
                urls.append(f"{match.group(1)}")
            if urls_found >= N:
                break
        
        return urls
    
    def get_markdown_from_google_search(self, search_query):
        try:
            def clean_search_string(search_query):
                # Remove characters that are not suitable for a URL search query
                allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~ ")
                cleaned_string = ''.join(c for c in search_query if c in allowed_chars)
                return cleaned_string
            
            def create_google_search_url(search_string):
                # Clean the search string
                cleaned_string = clean_search_string(search_string)
                # Encode the search string for use in a URL
                encoded_string = urllib.parse.quote_plus(cleaned_string)
                # Construct the final Google search URL
                google_search_url = f"https://www.google.com/search?q={encoded_string}"
                return google_search_url
            
            time.sleep(1)
            
            url = create_google_search_url(search_query)
            
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract the HTML content of the body
                body_html = soup.find('body')
                if body_html:
                    body_html = str(body_html)
                    # Convert HTML to Markdown
                    h = html2text.HTML2Text()
                    h.skip_internal_links = True  # Skip internal links
                    
                    # Configure options (optional)
                    h.ignore_links = False  # Ignore links 
                    h.ignore_images = True # Ignore images
                    h.body_width = 0  # Don't wrap lines

                    markdown_text = h.handle(body_html)
                    unique_key = self.generate_unique_key_for_url(url)
                    with open(f"/Users/michasmi/Downloads/{unique_key}test_markdown.md", "w") as f:
                        f.write(markdown_text)
                    return markdown_text
                else:
                    print("No body tag found.")
            else:
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
        except Exception as e:
            print(f"An error occurred: {e}")

    async def async_scrape_single_url(self, url):
            async def extract_same_domain_urls(page, base_url):
                # Get all anchor elements
                anchor_elements = await page.query_selector_all('a')

                # Extract href attributes and filter for same domain
                same_domain_urls = []
                diff_domain_urls = []
                for anchor in anchor_elements:
                    href = await anchor.get_attribute('href')
                    if href:
                        # Resolve relative URLs
                        url = urljoin(base_url, href)
                        # Parse URLs
                        base_domain = urlparse(base_url).netloc
                        url_domain = urlparse(url).netloc
                        # Check if the domain matches
                        if base_domain == url_domain:
                            same_domain_urls.append(url)
                        else: 
                            diff_domain_urls.append(url)
                            
                urls = {}
                urls['same_domain'] = same_domain_urls
                urls['diff_domain'] = diff_domain_urls            

                return urls

            def extract_text_from_html(html_body):
                soup = BeautifulSoup(html_body, 'html.parser')
                return soup.get_text(separator=' ', strip=True)

            def is_a_valid_url(may_be_a_url):
                try:
                    result = urlparse(may_be_a_url)
                    return all([result.scheme, result.netloc])
                except Exception as e:
                    self.log_it(f"Error: URL |{url}|is invalid: {str(e)}", color="RED")
                    return ""

            def get_domain_name(url):
                ext = tldextract.extract(url)
                return f"{ext.domain}.{ext.suffix}"
            try:
                if "http" not in url:
                    url = f"https://{url}"
                                        
                if url == "" or not is_a_valid_url(url):
                    return ""
                
                unique_date_key = datetime.now().strftime("%Y%m%d%H%M%S%f")
                simple_domain_key = get_domain_name(url).replace(".", "_")
                base_domain = f"https://{get_domain_name(url)}"
                text_file_name = f"scrapes/{simple_domain_key}_{unique_date_key}.json"
            
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    try:
                        await page.goto(url)
                        await page.wait_for_selector('body')
                        body = await page.content()
                        body_text = extract_text_from_html(body)
                        urls = await extract_same_domain_urls(page, base_domain)
                        
                        self.log_it(f"Successfully got full webpage for {url} with {len(body_text)} characters.")
                            
                        return_dict = {}
                        return_dict['url'] = url
                        return_dict['found_urls'] = urls
                        return_dict['body_text'] = body_text
                        return_dict['body'] = body
                        
                        with open(text_file_name, "w") as f:
                            f.write( json.dumps(return_dict, indent=4))
                            
                        return return_dict
                    
                    except Exception as e:
                        error_message = f"Error getting full webpage for {url}: {str(e)}"
                        self.log_it(error_message, color="RED")
                        return {}
                    
                    finally:
                        await browser.close()
            except Exception as e:
                error_message = f"Error getting full webpage for {url}: {str(e)}"
                self.log_it(error_message, color="RED")
                print(error_message)
                return {}
scraper = _scrape()

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
            doc_content = requests.get(doc_url, headers=api_client.headers)
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
api_client = _AISuite()

class PsqlSimpleStorage():
    def __init__(self ):
        self.connection_string = conn = os.environ.get('POSTGRES_AWS_PRODUCT_DB_CONN_STRING', 'POSTGRES: COULD NOT GET CONNECTION STRING')
        self.unique_initialization_id = uuid.uuid4()
        self.textlibrary_table = "textlibrary"   
        self.table_names = [self.textlibrary_table]
        self.default_table = self.textlibrary_table
        self.table_col_defs = {}

    def get_ngrok_public_url(self, get_new_url=False):
        def get_new_connection_string(self):
            ngrok_tcp_url = self.get_ngrok_public_url()
        
        if 'NGROK_TCP_URL_POSTGRES' in os.environ and not get_new_url:
            return os.environ['NGROK_TCP_URL_POSTGRES']
        elif get_new_url:
            return self.extract_ngrok_public_url(get_new_url=True)
        
        if 'NGROK_API_KEY' not in os.environ:
            print("NGROK_API_KEY not found in environment variables.")
            raise ValueError("NGROK_API_KEY not found in environment variables.")
        
        NGROK_API_KEY = os.getenv("NGROK_API_KEY")
        headers = {
            "Authorization": f"Bearer {NGROK_API_KEY}",
            "Ngrok-Version": "2"
        }
        url = "https://api.ngrok.com/endpoints"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises a HTTPError for bad responses
            data = response.json()
            
            if "endpoints" in data and len(data["endpoints"]) > 0:
                public_url = data["endpoints"][0]["public_url"]
                print(f"Extracted Public URL: {public_url}")
                os.environ['NGROK_TCP_URL_POSTGRES'] = public_url
                return public_url
            else:
                print("Failed to extract the public URL.")
                return None
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    async def get_connection(self):
        conn = await asyncpg.connect(self.connection_string)
        if not self.table_col_defs or self.table_col_defs == {}:
            self.table_col_defs = await self.get_column_types_dict(conn)
        return conn
    

            
    async def get_column_types_dict(self, conn):
        query = f"""SELECT table_name, column_name, data_type, udt_name
                    FROM information_schema.columns c 
                    WHERE c.table_name NOT LIKE 'pg%'
                    AND c.table_schema <> 'information_schema';"""
                
        column_types = await conn.fetch(query)
        
        # Organize the results in a dictionary
        column_types_by_table = {}
        for record in column_types:
            table_name = record['table_name']
            column_name = record['column_name']
            data_type = f"{record['udt_name']}"
            
            if table_name not in column_types_by_table:
                column_types_by_table[table_name] = {}
            
            column_types_by_table[table_name][column_name] = data_type
        
        with open("column_types_by_table.json", "w") as f:
            json.dump(column_types_by_table, f, indent=4)

        return column_types_by_table    
    
    def close_connection(self, conn):
        conn.close()
        
    def isnull_or_empty(self, value):
        """
        Check if a value is None, an empty string, or contains only whitespace.

        :param value: The value to check.
        :return: True if the value is None, an empty string, or contains only whitespace. False otherwise.
        """
        return value is None or str(value).strip() == ""

    def apply_upsert(self, base_row, new_row, merge_or_replace="MERGE"):
        
        if merge_or_replace == "REPLACE":
            # Replace the value regardless of whether it's empty or null
            base_row = new_row  
            return base_row
        
        # Replace the base row with the new row where there are existing values
        for key in base_row.keys():
            if new_row.get(key, None) is not None:  # A value exists in the new row
                ## APPEND means: Replace Primatives, Append to Lists, and Add New Keys. 
                ## Ignore existing keys/values not in new row.
                if merge_or_replace == "APPEND":
                    if not self.isnull_or_empty(new_row[key]): 
                        if not isinstance(new_row[key], list): 
                            #There is a new-row value and this is a primative or dicationary field
                            # Simple replace
                            base_row[key] = new_row[key]
                        else:
                            # If the lists are not teh same and 
                            # the new row value is not in the base row value, append it
                            if base_row[key] != new_row[key] and new_row[key] not in base_row[key]:
                                base_row[key].append(new_row[key])  
                
                ## MERGE means: Replace values of any type where keys match and also add new keys.    
                elif merge_or_replace == "MERGE":
                    if not self.isnull_or_empty(new_row[key]): 
                            #There is a new-row value and this is a primative or dicationary field
                            # Simple replace
                            base_row[key] = new_row[key]
                
        for key in new_row.keys():
            if base_row.get(key, None) is None:  # A value exists in the new row but not in the base row
                base_row[key] = new_row[key]  # Add the new value to the base row
        return base_row
            
    async def upsert_append_data(self, data_items, table_name=None, merge_or_replace="MERGE"):
        if table_name is None or table_name == "": table_name = self.default_table
        if not isinstance(data_items, list): data_items = [data_items]
        conn = await self.get_connection()
        
        try:
            async with conn.transaction():
                # Get the column definitions for the table
                table_def = self.table_col_defs.get(table_name, {})
                
                # Empty list to store the rows to upsert
                rows_to_upsert = []

                for item in data_items:
                    existing_data = None
                    row_to_upsert = {}
                    if item.get('id', None) is not None:
                        # Fetch the current data for merging (using the ID field)
                        existing_data = await conn.fetchrow(f"""
                                SELECT * from {table_name} WHERE id = $1 AND iscurrent = TRUE""",
                                item['id'])

                    elif item.get('rowcontext', None) is not None and item.get('uniquebuskey', None) is not None and existing_data is None:
                        # Fetch the current data for merging (using the rowcontext and uniquebuskey fields)
                        existing_data = await conn.fetchrow(f"""
                                SELECT * from {table_name} WHERE rowcontext = $1 AND uniquebuskey = $2 AND iscurrent = TRUE""",
                                item['rowcontext'], item['uniquebuskey'])

                    if not existing_data:
                        # If no existing data, use incoming data as is
                        row_to_upsert = item.copy()
                    
                    else:
                        # Convert existing_data to a mutable dictionary
                        existing_data = dict(existing_data)
                        
                        # Use the existing data as the base if it exists
                        row_to_upsert = self.apply_upsert(existing_data, item, merge_or_replace)

                    rows_to_upsert.append(row_to_upsert)

                # Prepare the data for insertion
                columns = []
                placeholders = []
                values = []
                placeholder_index = 1
                for row in rows_to_upsert:
                    row_values = []
                    for key in row.keys():
                        if key in table_def.keys():
                            # print(f"Key: {key}, Value: {row[key]}")
                            columns.append(key)
                            if table_def[key] in ["uuid", "bool", "boolean", "numeric", "int", "bigint", "bigserial", "smallint", "text", "varchar", "timestamp", "date", "time"]:
                                placeholders.append(f"${placeholder_index}")
                                
                                # If the incoming value is a string and the column is a date, convert the string to a date
                                if table_def[key] == "date" and isinstance(row[key], str):
                                    #Error handling if the date string is not a datetime object already
                                    try:
                                        row_values.append(datetime.strptime(row[key], '%Y-%m-%d').date())
                                    except:
                                        print(f"Error: {row[key]} is not a valid date string or date object on record {row}.")
                                        row_values.append('')
                                else:
                                    row_values.append(row[key])
                            
                            # JSONB must be dumped to a string        
                            elif table_def[key] == "jsonb":  # JSONB
                                placeholders.append(f"${placeholder_index}")
                                # jsonb must be dumped to a string
                                row_values.append(json.dumps(row[key]))
                            
                            # _JSONB must be dumped to a LIST of DUMPED-STRINGS
                            elif table_def[key] == "_jsonb":  # Array of JSONB
                                placeholders.append(f"${placeholder_index}::jsonb[]")
                                if isinstance(row[key], dict): # Means there is only one dictionary in the list of dictionaries
                                    # This is really Error handling if the value is a dictionary that hasn't been converted to a list of dictionaries
                                    row_values.append([json.dumps(row[key])])
                                else:
                                    row_values.append([json.dumps(item) for item in row[key]])
                            
                            else:
                                placeholders.append(f"${placeholder_index}")
                                row_values.append(row[key])
                            placeholder_index += 1
                        else:
                            print(f"\033[1;31;40mError: {key} is not a recognized data type. Please add it to the function: upsert_append_data \033[0m")
                    values.extend(row_values)

                columns_str = ', '.join(columns)
                placeholders_str = ', '.join(placeholders)

                insert_query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({placeholders_str})
                    ON CONFLICT (id) DO UPDATE
                    SET {', '.join([f"{col} = EXCLUDED.{col}" for col in columns])}
                """
                await conn.execute(insert_query, *values)

        except Exception as e:
            print("Error: ", e)
            raise

        finally:
            await conn.close()
                
    async def get_data(self, rowcontext=None, uniquebuskey=None, id=None, table_name=None):
    
        if table_name is None or table_name == "":
            table_name = self.default_table
        
        query = f"SELECT * FROM {table_name}"
        conditions = ["iscurrent = TRUE"]
        params = []
        
        if id:
            conditions.append(f"id = ${len(params) + 1}")
            params.append(id)
        
        if rowcontext:
            conditions.append(f"rowcontext = ${len(params) + 1}")
            params.append(rowcontext)
        
        if uniquebuskey:
            conditions.append(f"uniquebuskey = ${len(params) + 1}")
            params.append(uniquebuskey)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # try:
            
            conn = await self.get_connection()
            col_defs = self.table_col_defs.get(table_name, {})
            
            async with conn.transaction():
                all_records = await conn.fetch(query, *params)
                # records = []
                for record in all_records:
                    full_record = dict(record)
                    for key in full_record:
                        Before = f"Before: {full_record[key]}"
                        if col_defs.get(key, "Error") in ['jsonb', 'json']:
                            full_record[key] = json.loads(full_record[key])
                        elif col_defs.get(key, "Error") in ["_jsonb"]:
                            full_record[key] = [json.loads(item) for item in full_record[key]]
                        else:
                            pass
                        print(f"Key: {key}, Before: {Before}, After: {full_record[key]}")
                    # records.append(full_record)
            return all_records
        
        # except Exception as e:
        #     print(f"Database error during Get Data database connection: {e}")
        #     return []
        # finally:
        #     await conn.close()
        
    async def delete_data(self, ids_to_delete, table_name=None):
        if table_name is None or table_name == "":
            table_name = self.default_table
        
        if not isinstance(ids_to_delete, list):
            keys = [ids_to_delete]
        
        try:
            conn = self.get_connection()
            try:
                async with conn.transaction():
                    for id in ids_to_delete:
                        query = f"""
                            UPDATE {table_name}
                            SET iscurrent = FALSE, archivedon = (NOW() AT TIME ZONE 'UTC')
                            WHERE id = '{id}
                        """
                        deleted_result = await conn.execute(query)
                        print(f"Deleted data: {id} and got result: {deleted_result}")
            finally:
                await conn.close()
        except Exception as e:
            print(f"Database error during delete: {e}")
    
    async def get_distinct_column_values(self, column_name, entity_filter=None, table_name=None):
        if entity_filter is None:
            entity_filter = {}
        if table_name is None or table_name == "":
            table_name = self.default_table
        
        where_clauses = ["iscurrent = TRUE"]
        params = []

        for i, (key, value) in enumerate(entity_filter.items(), start=1):
            where_clauses.append(f"{key} = ${i}")
            params.append(value)

        query = f"SELECT DISTINCT {column_name} FROM {table_name} WHERE " + " AND ".join(where_clauses)
        
        try:
            conn = await asyncpg.connect(self.connection_string)
            try:
                async with conn.transaction():
                    records = await conn.fetch(query, *params)
                    return [record[column_name] for record in records]
            finally:
                await conn.close()
        except Exception as e:
            print(f"Database error during Get distinct column values: {e}")
            return []
    
    async def test_psqldb(self, test_entity=None):
        async def test_upsert_append_data():
            # Example data for upsert
            data = {
                'rowcontext': test_entity.get('rowcontext', 'test_context'),
                'uniquebuskey': test_entity.get('uniquebuskey', 'test_key'),
                'processingstatus': 'TEST_DATA',
                'organization_crd': 'CRD_1',
                'parentid': 'parentid',
                'parentname': 'parentname',
                'sec': 'SEC_1',
                'primary_business_name': 'Business_1',
                'legal_name': 'Legal_1',
                'main_office_location': {"city": "New York", "state": "NY"},
                'main_office_telephone_number': '123-456-7890',
                'sec_executive': {"name": "John Doe", "position": "CEO"},
                'sec_status_effective_date': datetime.now(),
                'website_address': 'https://example.com',
                'entity_type': 'Type_1',
                'governing_country': 'USA',
                'total_gross_assets_of_private_funds': 1000000.00,
                'next_pipeline_stage': 'Stage_1',
                'notes':  [{"note": "Important note"}],
                'title': 'Title 1',
                'description': 'Description 1',
                'summary': 'Summary 1',
                'names': ['Name 1', 'Name 2'],
                'emails': ['email1@example.com', 'email2@example.com'],
                'contacts': ['Contact 1', 'Contact 2'],
                'clients': ['Client 1', 'Client 2'],
                'partners': ['Partner 1', 'Partner 2'],
                'companies': ['Company 1', 'Company 2'],
                'experience': ['Experience 1', 'Experience 2'],
                'entities': ['Entity 1', 'Entity 2'],
                'needs': ['Need 1', 'Need 2'],
                'economics': ['Economics 1', 'Economics 2'],
                'competitors': ['Competitor 1', 'Competitor 2'],
                'decisionprocesses': ['Decision Process 1', 'Decision Process 2'],
                'timelines': ['Timeline 1', 'Timeline 2'],
                'sasactivity':  [{"activity": "Activity 1"}],
                'sasstage':  [{"stage": "Stage 1"}],
                'urls': ['https://url1.com', 'https://url2.com'],
                'domainurls': ['https://domain1.com', 'https://domain2.com'],
                'externalurls': ['https://external1.com', 'https://external2.com'],
                'scrapedurls': ['https://scraped1.com', 'https://scraped2.com'],
                'urllevellookup':  [{"level": "Level 1"}],
                'authors': ['Author 1', 'Author 2'],
                'publishdate': datetime.now(),
                'sourcefilename': 'sourcefile.txt',
                'contenttype': 'Content Type 1',
                'structdata':  [{"data": "Data 1"}],
                'bypage':  [{"page": "Page 1"}],
                'allpages':  [{"allpages": "All Pages Data"}],
                'summaryparts':  [{"part": "Summary Part 1"}],
                'alltext': 'All text content here',
                'topics': ['Topic 1', 'Topic 2'],
                'speakers': ['Speaker 1', 'Speaker 2'],
                'binarydoc': b'binary data here',
                'documentids': [1, 2, 3],
                'imageids': [4, 5, 6],
                'sentiment': 'Positive',
                'createdby': 'creator',
                'archivedby': 'archiver',
                'loadsource': 'source',
                'utterances': ["utterance", "He Said She Said"]
            }

            # Call the function to insert data
            await self.upsert_append_data(data)
            
            # Verify data
            # inserted_data = await db_connection.fetch("SELECT * FROM textlibrary WHERE rowcontext = $1 AND uniquebuskey = $2", data['rowcontext'], data['uniquebuskey'])
            inserted_data = await self.get_data( data['rowcontext'], data['uniquebuskey'], table_name='textlibrary')
            
            assert len(inserted_data) == 1
            for key in data:
                if  inserted_data[0][key] != data[key]:
                    print(f"Key: {key}, Inserted: {inserted_data[0][key]}, Data: {data[key]}")
               
        async def test_get_data():
            # Insert example data
            example_data = {
                'rowcontext': test_entity.get('rowcontext', 'test_context'),
                'uniquebuskey': datetime.now().strftime('%Y%m%d%H%M%S'),
                'structdata': {"key": "value"}
            }
            
            # Insert the data
            await self.upsert_append_data(example_data)
            
            # Retrieve data using get_data function (the same data)
            data = await self.get_data(rowcontext=example_data['rowcontext'], uniquebuskey=example_data['uniquebuskey'], table_name='textlibrary')
             
            assert len(data) == 1
            assert data[0]['rowcontext'] == example_data['rowcontext']
            assert data[0]['uniquebuskey'] == example_data['uniquebuskey']
            assert data[0]['structdata'][0]['key'] == "value"

        async def test_delete_data():
            # Insert example data
            example_data = {
                'rowcontext': 'test_context9990',
                'uniquebuskey': 'unique_key_9990'
            }
            
            await self.upsert_append_data(example_data, table_name='textlibrary')
            
            # Delete data using delete_data function
            await self.delete_data(keys=[example_data], table_name='textlibrary')

            # Verify deletion
            data = await self.get_data(rowcontext=example_data['rowcontext'], uniquebuskey=example_data['uniquebuskey'], table_name='textlibrary')
            assert len(data) == 0

        await test_upsert_append_data()
        await test_get_data()
        await test_delete_data()

    def _delete_all_tables(self, limit_to_table=None):
        
        # Safety check or environment check could go here
        # e.g., confirm deletion or check if running in a production environment
        saftey_check = True
        if saftey_check:

            try:
                # Connect to the database
                    conn = psycopg2.connect(self.connection_string)
                    with conn:
                        with conn.cursor() as cursor:
                            if limit_to_table:
                                cursor.execute(f"DROP TABLE IF EXISTS {limit_to_table} CASCADE;")
                            else:
                                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                                tables = cursor.fetchall()

                                # Build list of table names, excluding system tables
                                table_names = [table[0] for table in tables if not table[0].startswith(('pg_', 'sql_'))]

                                # Generate and execute DROP TABLE statements in a single transaction
                                if table_names:
                                    drop_query = "DROP TABLE IF EXISTS " + ", ".join(table_names) + " CASCADE;"
                                    print(drop_query)  # Optional: for logging or confirmation
                                    cursor.execute(drop_query)
                                    
                            # Commit changes
                            conn.commit()
                        
            except psycopg2.Error as e:
                print(f"An error occurred: {e}")
                return False
            
            return True
                        
class NatsClass:
    def __init__(self, env="local", project_path='', NatsIsConnected=False, nats_token=''):
       
        self.env = 'test'
        user_email = '1239@456.com'
        user_password= "123abcDEF!!!"
        
        connection_dict = {
            "local":{
                "base_url": 'https://localhost:5001/api',
                "nats_url": 'nats://localhost:4222',
                "login_payload": {"Email": user_email, "Password": user_password},
                "encoded_credentials": base64.b64encode(b'platform:local').decode('utf-8'),
                "register_user": True
            },
            "test":{
                "base_url": 'https://test-jbiengine.app/api',
                "nats_url": 'nats://test-jbiengine.app:4222',
                "login_payload": {"Email": user_email, "Password": user_password},
                "encoded_credentials": base64.b64encode(b'platform:E5XLE7HTiJq5cz').decode('utf-8'),
                "register_user": False
            }}
       
        self.encoded_credentials = connection_dict.get(self.env, {}).get('encoded_credentials', '') 
        self.register_payload = { "Email": user_email,"Name": "123 string", "Password": user_password}
        self.login_payload = connection_dict.get(self.env, {}).get('login_payload', {})
        self.base_url = connection_dict.get(self.env, {}).get('base_url', '')
        self.headers = {'accept': 'application/json','Content-Type': 'application/json'}
        self.nats_url = connection_dict.get(self.env, {}).get('nats_url', '')
        self.nats_token = st.session_state.get('nats_token', '')
        self.project_path = project_path
        self.NatsIsConnected = NatsIsConnected
        if not self.NatsIsConnected or self.nats_token == "":
            self.nats_authenticate(register_user=connection_dict.get(self.env, {}).get('register_user', False))
        

    def convert_date_format(self, date_str):
        # Parse the date string
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        # Convert to the desired format
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date

    def convert_text_num_to_num(self, textnum):
        # Parse the date string
        try:
            if textnum is None or textnum == '':
                decimal_to_return = float(0)
            return float(textnum)
        except ValueError:
            decimal_to_return = float(0)

    def csv_to_dict(self, csv_file_path, key_column='AttributeName'):
        result_dict = {}
        with open(csv_file_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            print(reader.fieldnames)
            rownum=0
            for row in reader: # Assuming 'AttributeName' is the name of the column to be used as the key
                rownum = rownum+1
                printrow = {}
                printrow.update(row)
                
                #! FIXME: This should be a look up to the business mode to see what the field types are
                if 'privateasset' in csv_file_path:
                    printrow['AcquisitionDate'] = self.convert_date_format(row['AcquisitionDate'])
                    printrow['AcquisitionCost'] = self.convert_text_num_to_num(row['AcquisitionCost'])
                    printrow['UnitsHeld'] = self.convert_text_num_to_num(row['UnitsHeld'])
                    
                # Convert dictionary to JSON string with double quotes
                row_string_escaped = json.dumps(printrow)
                row_string_simple = row_string_escaped.replace('\\"', '"')
                result_dict[rownum] = row_string_simple
            
        return result_dict

    def nats_authenticate(self, register_user=False):
        
        if register_user:
            response = requests.post(
                f'{self.base_url}/auth/register',
                        headers=self.headers,
                        json=self.register_payload,
                        verify=False
                    )
        
        nats_login_response = requests.post(
                f'{self.base_url}/auth/login',
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Basic {self.encoded_credentials}'
            },
            json=self.login_payload,
            verify=False
        )
        nats_login_json = nats_login_response.json()

        # Extract Token and NatsJwt
        self.nats_token = nats_login_json.get('Token')

        # Export the values as environment variables
        os.environ['NATS_TOKEN'] = self.nats_token
        
        return self.nats_token

    def extract_json_from_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Find the first '{' and the last '}'
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON object found in the file")

        # Extract the JSON string
        json_string = content[start_idx:end_idx+1]
        
        # Load and return the JSON as a dictionary
        try:
            return json.loads(json_string)
        except Exception as e:
            return({"error": f"Valid JSON could not be extracted from {file_path} Error: {e}"})
    
    def take_action(self,  action_dict={"service":"", "verb":"", "request_dict":[]}, csv_path='', ):
        
        success_list = []
        error_list = []
        
        def nats_request(action_dict, request):
            data_dict = {}
            try:
                # Send the request via nats (adjust the command as needed) "cd {PROJECT_PATH} && 
                log_uid = f'nats_{uuid.uuid4()}.json'
                nats_command = f'cd {self.project_path} && nats req {action_dict["service"]}.{action_dict["verb"]} \'{request}\' -H "Project:CMS" -H Token:{self.nats_token} >{NATS_RESULT_LOGS}/{log_uid} 2>&1'
                response = subprocess.run(nats_command, shell=True)
                data_dict = self.extract_json_from_file(f'{NATS_RESULT_LOGS}/{log_uid}')        
                data_dict['meta'] = {"success": True, "content": f"Success: {request}", "response": response, "nat_command": nats_command}
                return data_dict
            
            except Exception as e:
                data_dict['meta'] = {"error": f"Error: {e}"}
                data_dict['error_message'] = {"success": False, "content": f"Error: {e}", "nat_command": nats_command}
                print(f"\033[4;31m Error: {data_dict}\033[0m")
                return data_dict
        
        if csv_path is not None and csv_path != '':
            request_dict = self.csv_to_dict(csv_path)
            for key in request_dict.keys():  
                request = request_dict[key]
                response = nats_request(action_dict, request)
                if response['success']:success_list.append(response)
                else: error_list.append(response)
                
        if action_dict.get('request_dict', '') != [] and isinstance(action_dict.get('request_dict', ''), list):
            for request in action_dict['request_dict']:
                response = nats_request(action_dict, request)
                if response.get('success', False):
                    success_list.append(response)
                else: 
                    error_list.append(response)
        
        return response.get('data', {}).get('Items', [])







nats_inst = NatsClass(env="local", project_path=PROJECT_PATH, 
                      NatsIsConnected=st.session_state['NatsIsConnected'],  
                      nats_token=st.session_state['nats_token'])   

def test_nats_connection():
    try:
        test = nats_inst.take_action({"service":"privateasset", "verb":"query", "request_dict":['{"SymTicker": "MSFT","RecordContext":"WATCHLIST"}']})
        st.toast(":green[Connected to Nats]")
    except Exception as e: 
        nats_inst.NatsIsConnected = False
        st.markdown(f"### Cannot connect to Nats \n :red[Error: {e}]")



def buildGridOptions(df, show_columns=[], hide_columns=[]):

    if not isinstance(df, pd.DataFrame):
        try:
            pd.dataframe(df)
        except:
            print("Error: Could not create a dataframe or display the dataframe provided.")
            return None
        
    
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Grid
    gb.configure_grid_options(
        # groupDefaultExpanded=0,
        autoSizeStrategy="SizeColumnsToFitProvidedWidthStrategy", # autoSizeStrategy: | SizeColumnsToFitGridStrategy | SizeColumnsToFitProvidedWidthStrategy | SizeColumnsToContentStrategy;
        alwaysShowVerticalScroll=True, 
        groupSelectsChildren=True,
        enableRangeSelection=True,
        
        # pagination=False, 
        # paginationPageSize=10000, 
        domLayout='autoHeight'
        
    )

    # gb.configure_auto_height(True)
    
    gb.configure_default_column(
        groupable=True, 
        value=True, 
        enableRowGroup=True,  
        editable=True, 
        resizable=True,
        filterable=True,
        sortable=True,
        suppressSizeToFit=False, 
        suppressAutoSize=False, 
        # filter=True
        )

    gb.configure_side_bar(
        columns_panel=True, 
        filters_panel=True, 
        )
    
    gb.configure_selection(
        selection_mode =  "single",
        use_checkbox =  False,
        header_checkbox =  False,
        header_checkbox_filtered_only =  True,
        pre_select_all_rows =  False,
        pre_selected_rows =  None,
        rowMultiSelectWithClick =  False,
        suppressRowDeselection =  False,
        suppressRowClickSelection =  False,
        groupSelectsChildren =  True,
        groupSelectsFiltered =  True
    )
    
    # Columns
    if show_columns != [] and hide_columns != []:
        raise ValueError("Cannot show and hide columns at the same time.")
    if show_columns != []:
        col_list = show_columns
    if hide_columns != [] or (show_columns == [] and hide_columns == []):
        col_list = [col for col in df.columns if col not in hide_columns]
    default_val=False
    named_columns = True

    
    for col in df.columns:
        gb.configure_column(
        field=col, 
        type_="dimension", 
        enableRowGroup=False, 
        rowGroup=False, 
        flex=1,
        minWidth=50,
        hide=default_val if col in col_list else named_columns,
        )
     
    gridOptions = gb.build()

    
    return gridOptions
    
    
           
# Functions for this Streamlit App
def load_pgl():
    t1.write("PGL Load is disable for saftey. Re-enable in code to test.")
    # pgl_dict = nats_inst.take_action({"service":"privateasset", "verb":"create"}, csv_path=WATCHLIST_CSV_PATH)
    # t1.dataframe(pgl_dict, height=500, use_container_width=True)

def get_pgl_calcs():
    
    # Clear PGL and Lot Data
    st.session_state['pgldata'] = {}
    st.session_state['lotdata'] = {}
    
    #update the tickers to calc PGL for
    ts = f"{st.session_state["tickers_string"]}"
    try: 
        st.session_state['tickers'] = [tick.strip() for tick in ts.split(",")]
    except: 
        st.session_state['tickers'] = []
        
    # calc and store pgl for each ticker
    for ticker in st.session_state['tickers']:
        st.session_state['pgldata'] = {ticker: nats_inst.take_action({"service":"privateasset", "verb":"query", "request_dict":['{"SymTicker": "'+ticker+'","RecordContext":"WATCHLIST", "ComputePersonalGainLoss": true}']})}
        st.session_state['lotdata'] = {ticker: nats_inst.take_action({"service":"privateasset", "verb":"query", "request_dict":['{"SymTicker": "'+ticker+'","RecordContext":"WATCHLIST"}']})}

def get_all_personal_positions():
    result_dict = nats_inst.take_action({"service":"privateasset", "verb":"query", "request_dict":['{"RecordContext":"WATCHLIST"}']})    
    st.session_state["PersonalPositionDict"] = result_dict

def get_all_private_assets():
    result_list = nats_inst.take_action({"service":"privateasset", "verb":"query", "request_dict":['{"RecordContext":"PRIVATEASSET"}']})    
    st.session_state["PrivateAssetList"] = result_list
    
def get_grouped_sectors():
    result_list = nats_inst.take_action({"service":"position", "verb":"query.grouped", "request_dict":['{"GroupBy": "GICSSector"}, {"SumBy": "BaseCurrencyEndMarketValue"}, {"CodeSetCategory": "GICSSector"}, {"EnrichWithCodeSet": true}']})    
    st.session_state["SectorList"] = result_list

def get_account_balances():
    result_list = nats_inst.take_action({"service":"accountbalance", "verb":"query", "request_dict": ['{"GeneralLedgerType":"Liab"}']})
    st.session_state["AccountBalancesList"] = result_list
def get_account_financial_summary():
    result_list = nats_inst.take_action({"service": "accountfinancialsummary", "verb":"get", "request_dict": ['{"EnrichWithCodeSet": true}, {"CodeSetCategory": true}, {"IncludeInvestments": true}, {"IncludePrivateAssets": true}']})
    st.session_state["AccountFinancialSummaryList"] = result_list

# Main Page Tabs
t1, t2, t3, t4, t5, t6= st.tabs(["Personal Gain/Loss", "Personal Positions", "Private Assets", "Sector Insights", "Account Balances", "Account Summary"])

# Personal Gain Header
col1, col11, col12, col2, = t1.columns([3, .5, 1, 1])
st.session_state["tickers_string"] = col1.text_input("Enter one or more tickers", placeholder="MSFT, AAPL, TSLA", key="ticker_input", label_visibility="collapsed")
col12.button("Test Nats", "connect_to_nats", on_click=test_nats_connection, use_container_width=True)
calc_pgl_button = col2.button("Calc PGL", "test_stock", on_click=get_pgl_calcs, use_container_width=True, type="primary") 

# Personal Gain Loss
res1, res2 = t1.columns([7, 4])
hide_columns = ['Id']
for ticker in st.session_state['tickers']:
    with res1:
        df=pd.DataFrame(st.session_state['pgldata'][ticker])
        grid_response = AgGrid(
            df,
            gridOptions=buildGridOptions(df),
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            theme='balham',
            height=1000,
            key='pgldata1'
        )
    with res2:
        df=pd.DataFrame(st.session_state['lotdata'][ticker])
        grid_response = AgGrid(
            df,
            gridOptions=buildGridOptions(df, hide_columns=['Id', 'RecordContext']),
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            theme='balham',
            height=300,
            key='lotdata1'
        )
# res1.dataframe(data=st.session_state['pgldata'].get('ticker', []), height=500, use_container_width=True, key='pgldata1',)
# res2.dataframe(data=st.session_state['lotdata'].get('ticker', []) , height=500, use_container_width=True, key='lotdata1', column_order=['SymTicker', 'UnitsHeld', 'AcquisitionCost', 'AcquisitionDate'])


# Personal Positions (all data)
show_all_positions = t2.button("Get All Personal Positions", "get_all_personal_positions", on_click=get_all_personal_positions, use_container_width=True)
if st.session_state["PersonalPositionDict"] != {}: t2.dataframe(st.session_state["PersonalPositionDict"], height=1000, use_container_width=True)
else: t2.write("None")

# Private Assets
col31, col32 = t3.columns([3, 1])
get_private_assets = col32.button("Get All Private Assets", "get_all_private_assets", on_click=get_all_private_assets, use_container_width=True)
if st.session_state["PrivateAssetList"] != []: t3.dataframe(st.session_state["PrivateAssetList"], height=1000, use_container_width=True)
else: t3.write("None")

# Sector Insights
col41, col42 = t4.columns([3, 1])
get_sector_insights = col42.button("Get Sector Insights", "get_all_sec_in", on_click=get_grouped_sectors, use_container_width=True)
if st.session_state["SectorList"] != []: t4.dataframe(st.session_state["SectorList"], height=1000, use_container_width=True)
else: t4.write("None")

# AccountBalance Query
col51, col52 = t5.columns([3, 1])
get_account_balance = col52.button("Get Account Balances", "get_acct_balances", on_click=get_account_balances, use_container_width=True)
if st.session_state["AccountBalancesList"] != []: t5.dataframe(st.session_state["AccountBalancesList"], height=1000, use_container_width=True)
else: t5.write("None")

# AccountBalance Query
col61, col62 = t6.columns([3, 1])
get_account_summary = col62.button("Get Account Financial Summary", "get_acct_fin_summary", on_click=get_account_financial_summary, use_container_width=True)
if st.session_state["AccountFinancialSummaryList"] != []: 
    t6.dataframe(st.session_state["AccountFinancialSummaryList"], height=1000, use_container_width=True)
else: 
    t6.write("None")

#     prompt_val = [f"{tick.get('Id', '')}  | Portfolio Percent {tick.get(f'ValuePercent', '')}" for tick in Tickers]
#     message_content = f"My porfolio contains the following percentage breakdown of industry sectors: {"\n".join(prompt_val)}. \n  Please provide your commentary"