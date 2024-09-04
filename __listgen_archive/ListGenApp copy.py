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

from _class_list_generation import contact_generation_pipeline as clg
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
# api_client = _AISuite()
# scraper = _scrape()


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
# psql = PsqlSimpleStorage()


Quick_Site_Crawl_Expander = st.expander(":green[Quick page crawl . . .]")
with Quick_Site_Crawl_Expander:
    urltxt, btncrwl = st.columns([8,2])
    url = urltxt.text_input("URL", key="url", placeholder="Enter a URL ...", label_visibility="collapsed")
    crawl = btncrwl.button(":green[Crawl Page]", key="crawl", use_container_width=True)
    result_dict = {}
    if crawl:
        result_dict = asyncio.run(clg.async_scrape_single_url(url))
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



#? FULL SITE CRAWL
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
    



