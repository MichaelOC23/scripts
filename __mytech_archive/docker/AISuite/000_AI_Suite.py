# from sqlalchemy import column, values
import streamlit as st
import requests
import os
import uuid
import asyncio
import asyncpg
import json
import psycopg2




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




#?############################################
#?#######     HEADER / SETUP     #############
#?############################################
PAGE_TITLE = "JBI Sales - Powered by AI Suite"
st.set_page_config(
        page_title=PAGE_TITLE, page_icon=":earth_americas:", layout="wide", initial_sidebar_state="collapsed",
        menu_items={'Get Help': 'mailto:michael@justbuildit.com','Report a bug': 'mailto:michael@justbuildit.com',})    



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


####################################
####      POSTGRESQL CLASS      ####
####################################
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
    
    def isnull_or_empty(self, value):
        if value is None or value == "" or value == [] or value == {}:
            return True
        return False
            
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
                    if not isnull_or_empty(new_row[key]): 
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
                    if not isnull_or_empty(new_row[key]): 
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
                        
                     
# Initialize the API client
api_client = _AISuite()
scraper = _scrape()
####################################
####       TEST AI SUITE        ####
####################################

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = True

if st.session_state.admin_mode:
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
psql = PsqlSimpleStorage()


def select_a_bot():
    st.session_state.bot_id = st.session_state.bot_dict.get(st.session_state.bot_selectbox_value, "")
    st.toast(f"Selected Bot: {st.session_state.bot_selectbox_value}")  

def select_a_conversation():
    st.session_state.conversation_id = st.session_state.convo_dict.get(st.session_state.selected_conversation_id, "")
    st.toast(f"Selected Conversation: {st.session_state.selected_conversation_id}")
        
def get_conversations():
    result = api_client.list_conversations(bot_id=st.session_state.bot_id)
    if 'data' in result:
        return result['data']
    else:
        return []

def create_convo_dict_for_bot_id(bot_id):
    conversations = api_client.list_conversations(bot_id=bot_id)
    name_set = set()
    i = 0
    convo_dict = {}
    for conversation in conversations['data']:
        if conversation['name'] not in name_set:
            convo_dict[conversation['name']] = conversation['id']
        else:
            convo_dict[f"{conversation['name']}-({i})"] = conversation['id']
            i += 1
    st.session_state.convo_dict = convo_dict
    return convo_dict


    


crm1, crm2, crm3, crm4= st.columns([1, 1,1, 1 ])

if st.session_state.bot_dict == {}:
    bots = api_client.list_bots()
    for bot in bots['data']:
        if "JBI" in bot['name']:
            st.session_state.bot_dict[bot['name']] = bot['id']
            
# test_button = crm1.button("upsert")
# if test_button:
#     #create unique date and time string that could be used as a numbefor sorting
#     unique_date_time_str = datetime.now().strftime("%Y%m%d%H%M%S%s")
#     test_entity = {}
#     test_entity['rowcontext'] = "test_context"
#     test_entity['uniquebuskey']= unique_date_time_str
#     result = asyncio.run(psql.test_psqldb(test_entity))
    
    
crm1.markdown("Select Prospect and Document")

bot_selectbox = crm2.selectbox(f"Select Client", st.session_state.bot_dict.keys(), on_change=select_a_bot, key="bot_selectbox_value", index=0, label_visibility="collapsed", placeholder="Select a client / prospect:",)  

if st.session_state.bot_id != "" and st.session_state.bot_id is not None:
    create_convo_dict_for_bot_id(st.session_state.bot_id)
        
if st.session_state.convo_dict != {}:
    crm3.selectbox("Select a topic", st.session_state.convo_dict.keys(), key="selected_conversation_id", label_visibility="collapsed", on_change=select_a_conversation, placeholder="Select a topic:")

if st.session_state.new_prospect_name != None:
    new_name = st.session_state.new_prospect_name
    st.session_state.new_prospect_name = None
    if not new_name.startswith("JBI"):
        new_name = "JBI-" + new_name
    api_client.create_folder(new_name)    

add_document = crm4.button("Add Document", use_container_width=True)


    
def save_sales_box():
    st.session_state.open_sales_box_dict = {
        "need": st.session_state.c_need,
        "economics": st.session_state.c_economics,
        "competition": st.session_state.c_competition,
        "decision_process": st.session_state.c_decision_process,
        "timing": st.session_state.c_timing,
    }
    # api_client.create_prospect("Test Value", st.session_state.open_sales_box_dict)
    # st.session_state.open_sales_box_dict = {}

def revert_sales_box():
    st.session_state.c_need = st.session_state.open_sales_box_dict.get("need", "")
    st.session_state.c_economics = st.session_state.open_sales_box_dict.get("economics", "")
    st.session_state.c_competition = st.session_state.open_sales_box_dict.get("competition", "")
    st.session_state.c_decisionprocess = st.session_state.open_sales_box_dict.get("decisionprocess", "")
    st.session_state.c_timing = st.session_state.open_sales_box_dict.get("timing", "")


def open_sales_box():
    # Get the document given the client selectdd
    # json_loads
    
    st.session_state.open_sales_box_dict = {
        "need": st.session_state.c_need,
        "economics": st.session_state.c_economics,
        "competition": st.session_state.c_competition,
        "decision_process": st.session_state.c_decision_process,
        "timing": st.session_state.c_timing,
    }
    

gc1, gc2, gc3, gc4 = st.columns([3, 1, 1, 1])
prospect_dicts = api_client.list_prospects()
def on_select_prospect():
    prospect_id = prospect_dicts[selected_prospect_name]
    doc_dict = api_client.get_prospect_document(prospect_id)
    doc_url = doc_dict.get('data', {}).get('content_url', "")
    if doc_url != "":
        doc_content = requests.get(doc_url, headers=api_client.headers)

    st.session_state.open_sales_box_dict['need'] = doc_dict.get('need', "")
    st.session_state.open_sales_box_dict['economics'] = doc_dict.get('economics', "")
    st.session_state.open_sales_box_dict['competition'] = doc_dict.get('competition', "")
    st.session_state.open_sales_box_dict['decision_process'] = doc_dict.get('decision_process', "")
    st.session_state.open_sales_box_dict['timing'] = doc_dict.get('timing', "")
    st.session_state.c_need = doc_dict.get('need', "")
    st.session_state.c_economics = doc_dict.get('economics', "")
    st.session_state.c_competition = doc_dict.get('competition', "")
    st.session_state.c_decision_process = doc_dict.get('decision_process', "")
    st.session_state.c_timing = doc_dict.get('timing', "")
    
    

selected_prospect_name = gc1.selectbox("Select prospect / clientt", prospect_dicts.keys(), 
                                       key="selected_client", label_visibility="collapsed", 
                                       placeholder="Select a client / prospect:", on_change=on_select_prospect)







new_p = False
new_prospect_po =  gc4.popover("New prospect / client")
new_name = new_prospect_po.text_input("Name of new prospect / client")
if new_prospect_po.button("Create"):
    st.session_state.new_prospect_name = new_name
    new_p = True

st.write(st.session_state.new_prospect_name)

if new_p:
    api_client.create_prospect(st.session_state.new_prospect_name)
    new_p = False








    

sb_tab, powmap_tab, ai_tab, crm_tab = st.tabs(["Sales Box", "PowerMap", "AI Suite", "CRM"])
with sb_tab:
    sbc1, sbc2 = st.columns([6,4])
    sbc11,sbc12 = sbc1.columns([1,1])
    SALES_BOX_HEIGHT = 225
    
    c_needv = sbc11.text_area("Need", height=SALES_BOX_HEIGHT, key="c_need")
    c_economicsv = sbc12.text_area("Economics",height=SALES_BOX_HEIGHT, key="c_economics")
    c_competitionv = sbc11.text_area("Competition",height=SALES_BOX_HEIGHT, key="c_competition")
    c_decisionprocessv = sbc12.text_area("Decision Process",height=SALES_BOX_HEIGHT, key="c_decisionprocess")
    c_timingv = sbc1.text_area("Timing", height=SALES_BOX_HEIGHT, key="c_timing")
    
    btn1_col, btn2_col, spacer, = sbc1.columns([1,1,3])
    save_box = btn1_col.button("Save", use_container_width=True, type='primary', on_click=save_sales_box)
    discard_changes = btn2_col.button("Revert", use_container_width=True, type='secondary', on_click=revert_sales_box)
        
sbc2.write(st.session_state)
# selected_prompt = gc1.selectbox("Select a Prompt", st.session_state.prompt_list, key="selected_prompt", label_visibility="collapsed")
# send_prompt = gc2.button("Ask AI Suite")
# if send_prompt:
#     result = api_client.send_message(selected_prompt, st.session_state.conversation_id)
#     st.write(result)    








if False:
    st.session_state['urls_to_scrape']['toscrape'].append(url_to_scrape)
    max_count = 20
    while max_count > 0 and len(st.session_state['urls_to_scrape']['toscrape']) > 0:
        max_count -= 1
        new_url = False
        while not new_url:
            url_to_scrape = st.session_state['urls_to_scrape']['toscrape'][0]
            if url_to_scrape in st.session_state['urls_to_scrape']['scraped']:
                st.session_state['urls_to_scrape']['toscrape'].remove(url_to_scrape)
                print(f"Skipping: {url_to_scrape}")
            else:
                new_url = True
                print(f"Scraping: {url_to_scrape}")
            
        scraped_url_dict = asyncio.run(scraper.async_scrape_single_url(url_to_scrape))

        def mark_as_done(url1, url2):
            def remove_from_to_scrape(url):
                try:
                    st.session_state['urls_to_scrape']['toscrape'].remove(url)
                except:
                    pass
            def add_to_scraped(url):
                try:
                    st.session_state['urls_to_scrape']['scraped'].append(url)
                except:
                    pass
            remove_from_to_scrape(url1)
            remove_from_to_scrape(url2)
            remove_from_to_scrape(url1+"/")
            remove_from_to_scrape(url2+"/")
            add_to_scraped(url1)
            add_to_scraped(url2)
            add_to_scraped(url1+"/")
            add_to_scraped(url2+"/")
        
        if scraped_url_dict == {}:
            mark_as_done(url_to_scrape, url_to_scrape)
            continue
        
        # Add found urls to the list to scrape
        current_to_scrape = st.session_state['urls_to_scrape']['toscrape']
        current_to_scrape.extend(scraped_url_dict['found_urls']['same_domain'])
        current_to_scrape = list(set(current_to_scrape))
        
        for url in current_to_scrape:
            if url in st.session_state['urls_to_scrape']['scraped']:
                current_to_scrape.remove(url)                
        st.session_state['urls_to_scrape']['toscrape'] = current_to_scrape

        mark_as_done(url_to_scrape, scraped_url_dict.get('url', ''))


        with open("urls_to_scrape.json", "w") as f:
            json.dump(st.session_state['urls_to_scrape'], f)
        
        time.sleep(1)
        
        
        
        
        
    # def get_database_connection_string(self):
    #     return self.connection_string
    
    # def get_parameter(self, parameter_name, parameter_value=None):
    #     try:
    #         conn = psycopg2.connect(self.connection_string)
    #         with conn:
    #             with conn.cursor() as cursor:
    #                 cursor.execute(f"SELECT * FROM {self.parameter_table_name} WHERE partitionkey = '{self.parameter_partition_key}' AND rowkey = '{parameter_name}'")
    #                 record = cursor.fetchone()
    #                 if record:
    #                     return record[2]
    #                 else:
    #                     return parameter_value
    #     except psycopg2.Error as e:
    #         print(f"An error occurred: {e}")
    #         return parameter_value  
        








