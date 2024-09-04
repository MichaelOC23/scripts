from PIL.Image import new
from numpy import ma, place
import streamlit as st
import requests
import os
import uuid
import asyncio
import asyncpg
import json
import psycopg2
from sympy import div, rem, use


from decimal import Decimal
import asyncio
import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import json
from urllib.parse import urlparse, urljoin
import urllib.parse
import tldextract

import html2text
import requests
import hashlib
import chromadb
import ollama
from datetime import date, datetime
import time
import dotenv
dotenv.load_dotenv()

import _class_list_generation as clg
import _class_pgl_data_loader_v2 as pgl

#?############################################
#?#######     HEADER / SETUP     #############
#?############################################
PAGE_TITLE = "Sales Target List Generation and Management"
st.set_page_config(
        page_title=PAGE_TITLE, page_icon=":earth_americas:", layout="wide", initial_sidebar_state="collapsed",
        menu_items={'Get Help': 'mailto:michael@justbuildit.com','Report a bug': 'mailto:michael@justbuildit.com',})    


####################################
####        SCRAPE CLASS        ####
####################################
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
        
        self.downloadable_extensions = ['.gz', '.zip', 
                                        '.csv', '.txt', '.json', '.xml',
                                        '.pptx', '.xlsx', '.docx',  
                                        '.pdf', '.tiff',
                                        '.jpg', '.jpeg', '.png', 
                                        '.mp4', '.avi', '.mp3', '.m4a', '.wav']
         
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
    
    def downloaded_file(self, url, download_path):
        for ext in self.downloadable_extensions:
            if url.endswith(ext):
                response = requests.get(url)
                with open(f"{download_path}{ext}", 'wb') as f:
                    f.write(response.content)
                return True, f"{download_path}{ext}"
        return False, ""
    
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
                        url = urljoin(base_url, href).strip()
                        # Parse URLs
                        base_domain = urlparse(base_url).netloc
                        url_domain = urlparse(url).netloc
                        # Check if the domain matches
                        if base_domain == url_domain:
                            same_domain_urls.append(url)
                        else: 
                            diff_domain_urls.append(url)
                            
                urls = {}
                urls['same_domain'] = list(set(same_domain_urls))
                urls['diff_domain'] = list(set(diff_domain_urls))

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
                if not os.path.exists("scrapes"):
                    os.makedirs("scrapes")
                if "http" not in url:
                    url = f"https://{url}"
                                        
                if url == "" or not is_a_valid_url(url):
                    return ""
                
                unique_date_key = datetime.now().strftime("%Y%m%d%H%M%S%f")
                simple_domain_key = get_domain_name(url).replace(".", "_")
                base_domain = f"https://{get_domain_name(url)}"
                text_file_name = f"scrapes/{simple_domain_key}_{unique_date_key}"
                return_dict = {}
                
                WasDownloaded, file_path = self.downloaded_file(url, text_file_name)
                if WasDownloaded:
                    return_dict["url"] = url
                    return_dict["file_path"] = file_path
                    return return_dict

                text_file_name = f"{text_file_name}.json"
                
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




####################################
####        AISUITE CLASS       ####
####################################
class _AISuite:
    def __init__(self, api_key=None):
        if not api_key:
            api_key = "gX8NGF0KtNw6BTx5PqQJapYwyhxKia7vHmJgrywCa98df424"
        self.api_key = api_key
        self.base_url = "https://getcody.ai/api/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

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


####################################
####      POSTGRESQL CLASS      ####
####################################
class PsqlSimpleStorage():
    def __init__(self ):
        
        self.connection_string = os.environ.get('LOCAL_POSTGRES_CONNECTION_STRING1', 'postgresql://mytech:mytech@localhost:5400/mytech')    
        self.unique_initialization_id = uuid.uuid4()
        self.transcription_table = "transcription"
        self.bmm_table = "bmm_table"
        self.parameter_table_name = "parameter"
        self.access_token_table_name = "accesstoken"
        self.search_results_table_name = "searchresults"
        self.url_results_table_name = "urlcontent"
        self.default = self.transcription_table
        
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
    
    def get_database_connection_string(self):
        return self.connection_string
    
    def get_parameter(self, parameter_name, parameter_value=None):
        try:
            conn = psycopg2.connect(self.connection_string)
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT * FROM {self.parameter_table_name} WHERE partitionkey = '{self.parameter_partition_key}' AND rowkey = '{parameter_name}'")
                    record = cursor.fetchone()
                    if record:
                        return record[2]
                    else:
                        return parameter_value
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
            return parameter_value  
        
    async def get_data(self, partitionkey=None, rowkey=None, table_name=None, unpack_structdata=True):
        
        def try_to_dict(record):
            try:
                return json.loads(record)
            except:
                return record
        
        if table_name is None or table_name == "": table_name = self.default
        
        
        
        query = f"SELECT Id, iscurrent, archivedon, partitionkey, rowkey, structdata FROM {table_name}"
        conditions = [" iscurrent = TRUE "]
        params = []

        
        if partitionkey:
            conditions.append("partitionkey = $1")
            params.append(partitionkey)
        
        if rowkey:
            conditions.append("rowkey = $2" if partitionkey else "rowkey = $1")
            params.append(rowkey)
        
        if conditions:
            query += " WHERE" + " AND ".join(conditions)
            
        try:
            conn = await asyncpg.connect(self.connection_string)
            try:

                async with conn.transaction():
                    records = []
                    all_records = await conn.fetch(query, *params)
                    for record in all_records:
                        # Convert Record to a dict. merge with 'structdata' JSON (if unpack_structdata is True)
                        full_record = dict(record)
                        full_record['structdata'] = try_to_dict(record['structdata'])
                        if unpack_structdata:
                            full_record.update(json.loads(record['structdata'].lower()))
                        records.append(full_record)
                return records

            finally:
                await conn.close()
        except Exception as e:
            print(f"Database error during Get Data: {e}")
            return []

    async def get_unique_pkeys(self, rowkey = None, table_name=None):
        if table_name is None or table_name == "": table_name = self.default
        if rowkey is None or rowkey == "": rowkey_condition = ""
        else: rowkey_condition = f"AND rowkey = '{rowkey}'"
        
        query = f"SELECT DISTINCT partitionkey FROM {table_name} WHERE iscurrent = TRUE {rowkey_condition}"
        try:
            conn = await asyncpg.connect(self.connection_string)
            try:
                async with conn.transaction():
                    records = await conn.fetch(query)
                return [record['partitionkey'] for record in records]
            finally:
                await conn.close()
        except Exception as e:
            print(f"Database error during Get Unique PKeys: {e}")
            return []
    
    async def get_unique_rkeys(self, partitionkey = None, table_name=None):
        if table_name is None or table_name == "": table_name = self.default
        if partitionkey is None or partitionkey == "": partitionkey_condition = ""
        else: partitionkey_condition = f"AND partitionkey = '{partitionkey}'"
        
        query = f"SELECT DISTINCT rowkey FROM {table_name} WHERE iscurrent = TRUE {partitionkey_condition}"
        try:
            conn = await asyncpg.connect(self.connection_string)
            try:
                async with conn.transaction():
                    records = await conn.fetch(query)
                return [record['rowkey'] for record in records]
            finally:
                await conn.close()
        except Exception as e:
            print(f"Database error during Get Unique rowkeys: {e}")
            return []
            
    async def upsert_data(self, data_items, table_name=None):
        if table_name is None or table_name == "": table_name = self.default
        
        if not isinstance(data_items, list):
            data_items = [data_items]
            conn = await asyncpg.connect(self.connection_string)
        # try:
            for item in data_items:
                async with conn.transaction():
                    # Fetch the current data for merging
                    existing_data = await conn.fetchrow(f"""
                        SELECT title, url, authors, publishdate, contenttype, structdata, bypage, allpages, alltext, summaryparts, 
                        textdump, summary, topics, speakers, loadsource, recordcontext, entities, sentiment FROM {table_name} 
                        WHERE partitionkey = $1 AND rowkey = $2 AND iscurrent = TRUE
                    """, item['partitionkey'], item['rowkey'])
                    
                    # Prepare the merged data
                    merged_data = {}
                    
                    if existing_data:
                        # Merge text fields (replace)
                        merged_data['title'] = item.get('title', existing_data['title'])
                        merged_data['contenttype'] = item.get('contenttype', existing_data['contenttype'])
                        merged_data['textdump'] = item.get('textdump', existing_data['textdump'])
                        merged_data['summary'] = item.get('summary', existing_data['summary'])
                        merged_data['sentiment'] = item.get('sentiment', existing_data['sentiment'])
                        merged_data['url'] = item.get('url', existing_data['url'])
                        merged_data['rowkey'] = item['rowkey']
                        merged_data['partitionkey'] = item['partitionkey']
                        merged_data['loadsource'] = existing_data['loadsource']
                        merged_data['recordcontext'] = existing_data['recordcontext']
                        
                        # Merge JSONB fields
                        jsonb_fields = ['structdata', 'bypage', 'allpages', 'alltext', 'summaryparts']
                        for field in jsonb_fields:
                            existing_json = existing_data[field]
                            new_json = item.get(field, {})
                            # Ensure both are dictionaries
                            if not isinstance(existing_json, dict):
                                existing_json = {}
                            if not isinstance(new_json, dict):
                                new_json = {}
                            merged_json = {**existing_json, **new_json}
                            merged_data[field] = json.dumps(merged_json)  # Convert to JSON string
                        
                        # Merge text[] fields (add unique values)
                        text_array_fields = ['authors', 'topics', 'speakers', 'entities']
                        for field in text_array_fields:
                            existing_array = existing_data[field] or []
                            new_array = item.get(field, [])
                            merged_array = list(set(existing_array) | set(new_array))
                            merged_data[field] = merged_array
                    else:
                        # If no existing data, use incoming data as is
                        for key, value in item.items():
                            if key in ['structdata', 'bypage', 'allpages', 'alltext', 'summaryparts']:
                                merged_data[key] = json.dumps(value)  # Convert to JSON string
                            else:
                                merged_data[key] = value

                    # Archive the existing current record if it exists
                    await conn.execute(f"""
                        UPDATE {table_name} SET archivedon = NOW() AT TIME ZONE 'UTC', iscurrent = FALSE
                        WHERE partitionkey = $1 AND rowkey = $2 AND iscurrent = TRUE
                    """, item['partitionkey'], item['rowkey'])

                    # Insert the new record
                    columns =  list(merged_data.keys()) + ['iscurrent']
                    values_placeholders = ', '.join([f"${i+1}" for i in range(len(columns))])
                    insert_sql = f"""
                        INSERT INTO {table_name} ({', '.join(columns)})
                        VALUES ({values_placeholders})
                    """
                    values = list(merged_data.values()) + [True]
                    await conn.execute(insert_sql, *values)
        # finally:
        #     await conn.close()
  
    async def add_update_or_delete_some_entities(self, table_name=None, entities_list=None, instruction_type="UPSERT_MERGE", alternate_connection_string="", attempt=1):
        def create_unique_blob_name():
            return f"{uuid.uuid4()}"
        
        #Check the validity of the parameters
        if table_name is None or table_name == "":
            table_name = self.default
        if table_name is None or table_name == "":
            raise ValueError("Table name cannot be None or empty")
        if entities_list is None or entities_list == [] or entities_list == {}:
            return ""
        if instruction_type not in ["DELETE", "UPSERT_MERGE", "UPSERT_REPLACE", "INSERT"]:
            raise ValueError("Instruction type must be either 'DELETE' 'UPSERT_REPLACE', 'INSERT', 'UPSERT_MERGE' ")
        
        #entities_list should ideally be a list of dicts
        if not isinstance(entities_list, list):
            # If it isn't and it's one dict, just turn that into a one-tem list
            if isinstance(entities_list, dict):
                entities_list = [entities_list]
            #Not sure what to do with the input value
            else:
                raise ValueError("Entities must be a list or dictionary")
        
        # Initialize the blob extension dictionary.
        # We will put large dictionary values into blobs and store the blob name in the entity.
        blob_extension = {}
        
        entity_count = len(entities_list)
        prior_percent_complete = 0
        percent_complete = 0
        on_entity = 0
        #Iterate through each entity in the list
        for entity in entities_list:
            on_entity += 1
            
            percent_complete = (on_entity / entity_count)
            
            # if round(percent_complete, 1) > round(prior_percent_complete, 1):
            #     print(f"Percent Complete: {round(percent_complete * 100, 2)}%")

            #rowkey is required for each Entity
            if entity.get("rowkey", '') == '' or entity.get("rowkey", None) == None:
                raise ValueError("rowkey cannot be None or empty")
            
            #partitionkey is required for each Entity
            if entity.get("partitionkey") == '' or entity['partitionkey'] == None:
                raise ValueError("partitionkey cannot be None or empty")
            
            #If the instruction type is not DELETE, then check for blob fields in the entity
            # Not point in checking for blobs if we are deleting the entity
            if instruction_type not in ["DELETE"]:    
                pass
                # # Iterate through each key in the entity. If the field has _blob in it,
                # # that is the indicator that the size could be too large for the entity.
                # for key in entity.keys():
                #     if "_blob".lower() in key.lower():
                #         # If the value in the field is empty, skip it
                #         blob_value = entity.get(key, None)  
                #         if blob_value is None:
                #             continue
                #         # if not isinstance(blob_value, list) and blob_value == "":
                #         #     continue
                #         # if (isinstance(blob_value, list) and len(blob_value) == 0):
                #         #     continue
                #         # If it's not empty, then create a new unique key for the blob field
                #         blob_field_key = f"{key}|{create_unique_blob_name()}"        
                #         # Put the value of the field in the blob_extension dictionary
                #         blob_extension[blob_field_key] = entity[key]
                #         # Replace the value in the entity with the new blob field key
                #         entity[key] = blob_field_key
                
                # # If there are any blob fields in the entity, then upload the blob to the storage account
                # if blob_extension != {}:
                #     for key in blob_extension.keys():
                #         raise ValueError("Blob extension is created yet")
                #         # resp = await self.upload_blob(self.table_field_data_extension, blob_field_key, blob_extension[blob_field_key], overwrite_if_exists=True, alternate_connection_string=self.transaction_pf_con_string)
                #         # print(f"Uploaded blob: {blob_field_key}")
            
            

            resp_list = []
            #The entity is now ready to be added, updated, or deleted in the tale
            conn = await asyncpg.connect(self.connection_string)
            async with conn.transaction():
                try:
                        
                    if instruction_type == "DELETE":
                        raise ValueError("DELETE Not Implemented Yet")
                    
                    if instruction_type == "UPSERT_MERGE":
                        resp = await self.upsert_data(entity, table_name)
                        
                    if instruction_type == "UPSERT_REPLACE":
                        raise ValueError("UPSERT_REPLACE Not Implemented Yet")
                        # resp = await table_client.upsert_entity(mode=UpdateMode.REPLACE, entity=entity)
                        # print(f"UPSERT_REPLACE entity: {entity['rowkey']}: {resp}")
                    
                    if instruction_type == "INSERT":
                        raise ValueError("INSERT Not Implemented Yet")
                    
                    resp_list.append(resp)
                
                except Exception as e:
                    print(f"Error: {e}")

        return resp_list
    
           #! get_entities_by_partition_key
     
    async def delete_data(self, keys, table_name=None):
        if table_name is None or table_name == "": table_name = self.default
        
        if not isinstance(keys, list):
            keys = [keys]

        try:
            conn = await asyncpg.connect(self.connection_string)
            for key in keys:
                # Construct the WHERE clause based on input keys
                where_clause = []
                values = []
                if 'partitionkey' in key:
                    where_clause.append("partitionkey = $1")
                    values.append(key['partitionkey'])
                if 'rowkey' in key:
                    where_clause.append(f"rowkey = ${len(values) + 1}")
                    values.append(key['rowkey'])

                # Construct and execute the update query to mark records as archived
                if where_clause:
                    query = f"""
                        UPDATE {table_name}
                        SET iscurrent = FALSE, archivedon = (NOW() AT TIME ZONE 'UTC')
                        WHERE {" AND ".join(where_clause)}
                    """
                    deleted_result = await conn.execute(query, *values)
                    print(f"Deleted data: {key} and got result: {deleted_result}")

            await conn.close()
        except Exception as e:
            print(f"Database error during delete: {e}")

    def _setup_text_library_table(self):

        conn = psycopg2.connect(self.connection_string)
        cursor = conn.cursor()
        
        create_table_dict = {

        "create_table": f"""CREATE TABLE IF NOT EXISTS textlibrary (
                id serial4 NOT NULL,
                rowcontext varchar(100) NULL,
                uniquebuskey varchar(250) NULL,
                processingstatus varchar(50) NULL,
                Organization_CRD varchar(100) NULL,
                SEC varchar(100) NULL,
                Primary_Business_Name varchar(100) NULL,
                Legal_Name varchar(100) NULL,
                Main_Office_Location jsonb NULL,
                Main_Office_Telephone_Number varchar(50) NULL,
                SEC_Executive jsonb NULL,
                SEC_Status_Effective_Date varchar(100) NULL,
                Website_Address varchar(500) NULL,
                Entity_Type varchar(200) NULL,
                Governing_Country varchar(100) NULL,
                Total_Gross_Assets_of_Private_Funds DECIMAL,
                Next_Pipeline_Stage varchar(100) NULL,
                Notes jsonb[] NULL,
                title varchar(500) NULL,
                description varchar(500) NULL,
                summary text NULL,
                names text[] NULL,
                emails text[] NULL,
                contacts text[] NULL,
                clients text[] NULL,
                partners text[] NULL,
                companies text[] NULL,
                experience text[] NULL,
                entities text[] NULL,
                needs text[] NULL,
                economics text[] NULL,
                competitors text[] NULL,
                decisionprocesses text[] NULL,
                timelines text[] NULL,
                sasactivity jsonb[] NULL,
                sasstage jsonb[] NULL,
                urls text [] NULL,
                domainurls text [] NULL,
                externalurls text [] NULL,
                scrapedurls text [] NULL,
                urllevellookup jsonb[] NULL,
                authors text[] NULL,
                publishdate date null,
                sourcefilename varchar(100) null,
                contenttype varchar(100) null,
                structdata jsonb[] NULL,
                bypage jsonb[] NULL,
                allpages jsonb[] NULL,
                summaryparts jsonb[] NULL,
                alltext text NULL,
                topics text[] NULL,
                speakers text[] NULL,
                binarydoc bytea NULL,
                documentids int[] NULL,
                imageids int[] NULL,
                sentiment varchar(100) NULL,
                createdon timestamp DEFAULT CURRENT_TIMESTAMP NULL,
                archivedon timestamp NULL,
                iscurrent bool DEFAULT true NULL,
                createdby varchar(50) NULL,
                archivedby varchar(50) NULL,
                loadsource varchar(10) NULL,
                CONSTRAINT textlibrary_pkey PRIMARY KEY (id));""",

            "index1": "CREATE UNIQUE INDEX idx_rowcontext_current ON textlibrary USING btree (rowcontext, uniquebuskey) WHERE (iscurrent = true);"
        }
        
        conn = psycopg2.connect(self.connection_string)
        with conn:
            with conn.cursor() as cursor:
                for key, command in create_table_dict.items():
                    try:
                        cursor.execute(command)
                    except Exception as e:
                        print(f"Database error during table setup: {e} with statement: {command}")
                        break  # Or decide how to handle the error

    def _setup_parameter_table(self, table_name):

        conn = psycopg2.connect(self.connection_string)
        cursor = conn.cursor()
        
        create_table_dict = {

        "create_table": f"""CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            parametername VARCHAR(50),
            parametervalue VARCHAR(50),
            parametervaluelong VARCHAR(200),
            recordcontext VARCHAR(15) DEFAULT 'PARAMETER',
            createdon TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            archivedon TIMESTAMP,  
            iscurrent BOOLEAN DEFAULT TRUE,  
            createdby VARCHAR(50),
            archivedby VARCHAR(50),
            loadsource VARCHAR(10)
        );""",
            
            "index1": f"CREATE UNIQUE INDEX idx_partitionkey_rowkey_current ON {table_name} (parametername) WHERE iscurrent = TRUE;"


        }
        
        conn = psycopg2.connect(self.connection_string)
        with conn:
            with conn.cursor() as cursor:
                for key, command in create_table_dict.items():
                    try:
                        cursor.execute(command)
                    except Exception as e:
                        print(f"Database error during table setup: {e} with statement: {command}")
                        break  # Or decide how to handle the error
    
    def _delete_all_tables(self, limit_to_table=None):
        
        # Safety check or environment check could go here
        # e.g., confirm deletion or check if running in a production environment

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
                     
       

####################################
##    PROSPECT LIST CLASS    ####
####################################         
class prospect_list():
    def __init__(self):
        self.connection_string = os.getenv('LOCAL_POSTGRES_CONNECTION_STRING1', 'postgresql://mytech:mytech@localhost:5400/mytech')
    def clean_and_convert_str_to_decimal(self, value_str):
        cleaned_str = value_str.replace(",", "").strip()
        return Decimal(cleaned_str)
    
    async def create_prospect(self, table_name):
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS prospect (
                id serial4 NOT NULL,
                rowkey varchar(100),
                partitionkey varchar(100),
                Organization_CRD varchar(100) NULL,
                SEC varchar(100) NULL,
                Primary_Business_Name varchar(100) NULL,
                Legal_Name varchar(100) NULL,
                Main_Office_Location jsonb NULL,
                Main_Office_Telephone_Number varchar(50) NULL,
                SEC_Executive jsonb NULL,
                SEC_Status_Effective_Date varchar(100) NULL,
                Website_Address varchar(500) NULL,
                Entity_Type varchar(200) NULL,
                Governing_Country varchar(100) NULL,
                Total_Gross_Assets_of_Private_Funds DECIMAL
                Next_Pipeline_Stage varchar(100) NULL,
                Notes jsonb NULL,
            );
        """
        
        
        
        conn = await asyncpg.connect(self.connection_string)
        try:
            # await conn.execute("drop table if exists prospect;")
            await conn.execute(create_table_sql)
            print(f"Table prospect created successfully.")
        finally:
            await conn.close()
            
    async def load_json_to_table(self, connection_string, table_name, json_file_path):
        conn = await asyncpg.connect(connection_string)
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            
            def get_domain_name(url):
                ext = tldextract.extract(url)
                return f"{ext.domain}.{ext.suffix}"

            insert_sql = f"""
            INSERT INTO {table_name} (
                Organization_CRD,
                SEC,
                partitionkey,
                rowkey,
                Primary_Business_Name,
                Legal_Name,
                
                Main_Office_Location jsonb NULL, 
                Main_Office_Telephone_Number text NULL,
                SEC_Executive jsonb NULL,

                SEC_Status_Effective_Date,
                Email_Domain
                Website_Address,
                Entity_Type,
                Governing_Country,
                Total_Gross_Assets_of_Private_Funds
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
            );
            """

            for record in data:
                values = (
                    record.get("Organization_CRD"),
                    record.get("SEC"),
                    'PROSPECT',   
                    record.get("Organization_CRD"),
                    record.get("Primary_Business_Name"),
                    record.get("Legal_Name"),
                    {"Main_Office_Location": [
                        record.get("Main_Office_Street_Address_1", ""),
                        record.get("Main_Office_Street_Address_2", ""),
                        record.get("Main_Office_City", ""),
                        record.get("Main_Office_State", ""),
                        record.get("Main_Office_Country", ""),
                        record.get("Main_Office_Postal_Code", "")]},
                    record.get("Main_Office_Telephone_Number", ""),
                    {"SEC_Executive": [
                        record.get("Chief_Compliance_Officer_Name", ""),
                        record.get("Chief_Compliance_Officer_Other_Titles", ""),
                        record.get("Chief_Compliance_Officer_Telephone", ""),
                        record.get("Chief_Compliance_Officer_Email", "")]},
                    record.get("SEC_Status_Effective_Date"),
                    get_domain_name(record.get("Email_Domain")),
                    record.get("Website_Address"),
                    record.get("Entity_Type"),
                    record.get("Governing_Country"),
                    self.clean_and_convert_str_to_decimal(record.get("Total_Gross_Assets_of_Private_Funds"))
                )
                await conn.execute(insert_sql, *values)

            print(f"Data from {json_file_path} loaded into {table_name} successfully.")
        finally:
            await conn.close()





                     
# Initialize the API client
api_client = _AISuite()
scraper = _scrape()
####################################
####       TEST AI SUITE        ####
####################################
with st.expander("Test All Functions"):
    # Helper function to display results
    def display_result(result):
        st.json(result)

    st.title("Cody AI API Test App")
    bcol1, bcol2, bcol3,bcol4,bcol5, bcol6 = st.columns([1,1,1,1,1,1,])
    
    # Step 1: List Bots
    if bcol1.button("List Bots", use_container_width=True):
        result = api_client.list_bots()
        display_result(result)

    # Step 2: Create Conversation
    if 'bot_id' in st.session_state and bcol2.button("Create Conversation", use_container_width=True):
        conversation_name = "Test Conversation"
        result = api_client.create_conversation(conversation_name, st.session_state.bot_id)
        display_result(result)
        if 'data' in result:
            st.session_state.conversation_id = result['data']['id']
        else:
            st.error("Failed to create conversation.")

    # Step 3: List Conversations
    if 'bot_id' in st.session_state and bcol2.button("List Conversations", use_container_width=True):
        result = api_client.list_conversations(bot_id=st.session_state.bot_id)
        display_result(result)

    # Step 4: Get Conversation
    if 'conversation_id' in st.session_state and bcol2.button("Get Conversation", use_container_width=True):
        result = api_client.get_conversation(st.session_state.conversation_id)
        display_result(result)

    # Step 5: Update Conversation
    if 'conversation_id' in st.session_state and bcol2.button("Update Conversation", use_container_width=True):
        conversation_name = "Test Conversation Updated"
        result = api_client.update_conversation(st.session_state.conversation_id, conversation_name, st.session_state.bot_id)
        display_result(result)

    # Step 6: Create Document
    if bcol3.button("Create Document", use_container_width=True):
        document_name = "Test Document"
        folder_id = None  # Assuming no specific folder
        content = "This is a test document."
        result = api_client.create_document(document_name, folder_id, content)
        display_result(result)
        if 'data' in result:
            st.session_state.document_id = result['data']['id']
        else:
            st.error("Failed to create document.")

    # Step 7: List Documents
    if bcol3.button("List Documents", use_container_width=True):
        result = api_client.list_documents()
        display_result(result)

    # Step 8: Get Document
    if 'document_id' in st.session_state and bcol3.button("Get Document", use_container_width=True):
        result = api_client.get_document(st.session_state.document_id)
        display_result(result)

    # Step 9: List Folders
    if bcol4.button("List KBs", use_container_width=True):
        result = api_client.list_folders()
        display_result(result)

    # Step 10: Create Folder
    if bcol4.button("Create KB", use_container_width=True):
        folder_name = "Test KB"
        result = api_client.create_folder(folder_name)
        display_result(result)
        if 'data' in result:
            st.session_state.folder_id = result['data']['id']
        else:
            st.error("Failed to create folder.")

    # Step 11: Get Folder
    if 'folder_id' in st.session_state and bcol4.button("Get KB", use_container_width=True):
        result = api_client.get_folder(st.session_state.folder_id)
        display_result(result)

    # Step 12: Update Folder
    if 'folder_id' in st.session_state and bcol4.button("Update KB", use_container_width=True):
        folder_name = "Test KB Updated"
        result = api_client.update_folder(st.session_state.folder_id, folder_name)
        display_result(result)

    # Step 13: Send Message
    if 'conversation_id' in st.session_state and bcol5.button("Send Message", use_container_width=True):
        message_content = "Hello, this is a test message."
        result = api_client.send_message(message_content, st.session_state.conversation_id)
        display_result(result)
        if 'data' in result:
            st.session_state.message_id = result['data']['id']
        else:
            st.error("Failed to send message.")

    # Step 14: List Messages
    if 'conversation_id' in st.session_state and bcol5.button("List Messages", use_container_width=True):
        result = api_client.list_messages(conversation_id=st.session_state.conversation_id)
        display_result(result)

    # Step 15: Get Message
    if 'message_id' in st.session_state and bcol5.button("Get Message", use_container_width=True):
        result = api_client.get_message(st.session_state.message_id)
        display_result(result)

    # Step 16: Send Message for Stream
    if 'conversation_id' in st.session_state and bcol5.button("Send Message for Stream", use_container_width=True):
        message_content = "Hello, this is a test message for streaming."
        result = api_client.send_message_for_stream(message_content, st.session_state.conversation_id, redirect=False)
        display_result(result)

    # Step 17: Get Uploads Signed URL
    if bcol6.button("Get Upload URL", use_container_width=True):
        file_name = "test_upload.txt"
        content_type = "text/plain"
        result = api_client.get_uploads_signed_url(file_name, content_type)
        display_result(result)

    # Cleanup: Delete Document and Conversation
    if bcol6.button("Cleanup", use_container_width=True):
        if 'document_id' in st.session_state:
            result = api_client.delete_document(st.session_state.document_id)
            display_result(result)
        if 'conversation_id' in st.session_state:
            result = api_client.delete_conversation(st.session_state.conversation_id)
            display_result(result)
        st.success("Cleanup completed.")

         


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
psql = PsqlSimpleStorage()

Quick_Site_Crawl_Expander = st.expander(":green[Quick page crawl . . .]")
with Quick_Site_Crawl_Expander:
    urltxt, btncrwl = st.columns([8,2])
    url = urltxt.text_input("URL", key="url", placeholder="Enter a URL ...", label_visibility="collapsed")
    crawl = btncrwl.button(":green[Crawl Page]", key="crawl", use_container_width=True)
    result_dict = {}
    if crawl:
        result_dict = asyncio.run(scraper.async_scrape_single_url(url))
    if result_dict != {} and result_dict is not True:
        st.markdown(f"##### :blue[Results for: {result_dict.get('url', '')}]")
        st.divider()
        qc1, qc2 = st.columns([3,2])
        qt1, qt2, qt3 = qc1.tabs(["Text", "HTML Code", "Rendered HTML"])
        qt1.write(result_dict.get("body_text", ""))
        qt2.write(result_dict.get("body", ""))
        qt2.html(result_dict.get("body", ""))
        base_domain = tldextract.extract(url).domain
        qtut1, qtut2 = qc2.tabs([f"Links to {base_domain}", "Links to Other Sites"])
        qtut1.write(result_dict.get("found_urls", {}).get("same_domain", []))
        qtut2.write(result_dict.get("found_urls", {}).get("diff_domain", []))
    elif result_dict is True:
        st.write("File saved successfully to scrapes/ folder.")

Full_Site_Crawl_Expander = st.expander(":blue[Full site crawl . .]")

def call_crawl_site_with_depth(url, max_depth=2):
    # Define the endpoint
    endpoint = "http://localhost:5000/crawlurl"

    # Prepare the data payload
    data = {
        'url': url,
        'max_depth': max_depth
    }

    # Make the POST request
    response = requests.post(endpoint, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Request was successful.")
        print("Response JSON:", response.json())
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response text:", response.text)


with Full_Site_Crawl_Expander:
    urltxt, pagesdeep, labeld, btncrwl = st.columns([6,1,1,2])
    url_to_scrape = urltxt.text_input("URL", key="url_to_scrape",placeholder="Enter a URL ...", label_visibility="collapsed")
    pages_deep = pagesdeep.number_input("Pages Deep", key="pages_deep", min_value=0, max_value=5, value=2, label_visibility="collapsed") 
    labeld.markdown("""###### :blue[Crawl Page Depth]""")
    crawl_url = btncrwl.button(":blue[Crawl URL]", key="crawl_url", use_container_width=True)
    if crawl_url:
        call_crawl_site_with_depth(url_to_scrape, pages_deep)
    gc1, gc2, gc3, gc4, gc5 = st.columns([1, 1, 1, 1, 1])
    















# client_list_expander = st.expander("Client List")
# with client_list_expander:
#     data_col, btn_col = st.columns([8,1])
#     data_col.markdown("### :blue[Client List]")
#     add_client_button = btn_col.button("Add Client", use_container_width=True)
#     st.divider()

    # async def update_psql():
    #     client_list = st.session_state.client_list
    #     client_list_original = st.session_state.client_list_original

    #     edited_rows = []
    #     added_rows = []
    #     deleted_rows = []

    #     # Check for added and edited rows
    #     for client in client_list:
    #         if client not in client_list_original:
    #             added_rows.append(client)
    #         else:
    #             for original_client in client_list_original:
    #                 if original_client["client_id"] == client["client_id"] and original_client != client:
    #                     edited_rows.append(client)

    #     # Check for deleted rows
    #     for original_client in client_list_original:
    #         if original_client not in client_list:
    #             deleted_rows.append(original_client)

    #     # Update database with added rows
    #     for client in added_rows:
    #         await psql.upsert_data(client)

    #     # Update database with edited rows
    #     for client in edited_rows:
    #         await psql.upsert_data(client)

    #     # Update database with deleted rows
    #     for client in deleted_rows:
    #         await psql.delete_data(client)

    # client_list = asyncio.run(psql.get_data(partitionkey="clients"))
    # client_display = []
    
    # def select_client():
    #     st.session_state.selected_client = client
    #     st.write(f"Selected client: {st.session_state.client_list}"  )
        
    # # if client_list:    
        
    # #     for client in client_list:
    # #         if 'structdata' in client and client['firm']:
    # #             client_display.append(client['structdata'])
    # #     st.dataframe(client_display,  use_container_width=True, hide_index=True, key="client_list", on_select=select_client) 
    # # else:
    # #     st.warning("No clients found.")
    
if "bot_id" not in st.session_state: st.session_state.bot_id = ""

crm1, crm2, crm3 = st.columns([1, 1,1])
bots = api_client.list_bots()
bot_dict = {}
if 'urls_to_scrape' not in st.session_state: st.session_state['urls_to_scrape'] = []
if not os.path.exists("./urls_to_scrape.json"): 
    with open("urls_to_scrape.json", "w") as f:
        json.dump({"toscrape":[], "scraped": []}, f)

with open("urls_to_scrape.json", "r") as f:
    text_val = f.read()
    st.session_state['urls_to_scrape'] = json.loads(text_val)


for bot in bots['data']:
    bot_dict[bot['id']] = bot

# st.write(bot_dict)


conversations = []
def select_a_bot():
    st.session_state.bot_id = bot_dict[st.session_state.bot_selectbox_value]['id']
    st.info(f"Selected Bot: {bot_dict[st.session_state.bot_selectbox_value]['name']}")  

def format_bot_list(bot_dict_key):
    return bot_dict[bot_dict_key].get('name', 'Unknown Bot')    

def select_a_conversation():
    if "conversation_id" not in st.session_state: st.session_state.conversation_id = ""
    
bot_selectbox = crm1.selectbox(f"Select A Prospect Bot", list(bot_dict.keys()), on_change=select_a_bot, key="bot_selectbox_value", format_func=format_bot_list, label_visibility="collapsed")  

    
def get_conversations():
    result = api_client.list_conversations(bot_id=st.session_state.bot_id)
    if 'data' in result:
        return result['data']
    else:
        return []

if st.session_state.bot_id:
    conversations = api_client.list_conversations(bot_id=st.session_state.bot_id)
    if conversations:
        conversation_list = []
        for conversation in conversations.get('data', []):
            conversation_list.append(f"{conversation['name']} | {conversation['id']}")
        crm2.selectbox("Select a topic", conversation_list, key="selected_conversation_id", label_visibility="collapsed")
        # st.session_state.conversation_id = conversations[0]['id']
    else:
        st.error("No conversations available to test with.")
        

new_conversation = crm3.button("Create New Conversation")
if new_conversation:
    conversation_name = st.text_input("Conversation Name")
    result = api_client.create_conversation(conversation_name, st.session_state.bot_id)
    if 'data' in result:
        st.session_state.conversation_id = result['data']['id']
    else:
        st.error("Failed to create conversation.")
st.divider()




