# General Python Libraries
import os
import requests
import hashlib
import json
from tqdm import tqdm
import asyncio
import aiofiles
import httpx
from contextlib import asynccontextmanager
import aiohttp
import re
import sys
from datetime import datetime, timezone, timedelta
from dateutil import parser
import time
import random
import csv
import decimal
import uuid
import pandas as pd
from decimal import Decimal
from psycopg2 import sql
import asyncpg
from multiprocessing import Pool
import html2text
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urlencode, urlparse, urljoin
import urllib.parse
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright,  TimeoutError as PlaywrightTimeoutError
from multiprocessing import Process, Queue, set_start_method, Manager
import nest_asyncio
import nltk
# nltk.download('punkt')
# nltk.download('maxent_ne_chunker')
# nltk.download('words')
# nltk.download('averaged_perceptron_tagger')
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree
import concurrent.futures


#AI Libraries
import ollama
import chromadb
import google.generativeai as genai
# pip install -q -U google-generativeai

# Ner via Bert Slim
from transformers import AutoTokenizer, TFBertForTokenClassification #, TFAutoModelForTokenClassification
from transformers import pipeline

import requests
from pdf2image import convert_from_path, convert_from_bytes
from io import BytesIO
import pytesseract



nest_asyncio.apply()
set_start_method("spawn", force=True)

class Logger:
    def __init__(self, output_folder="logs"):
        # Create a folder for the logs
        self.output_folder = output_folder
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        self.uid = f"{uuid.uuid4()}"
        self.start_time = datetime.now()
        self.last_log_time = self.start_time
        self.filename = f"{self.output_folder}/log_{self.start_time}_{self.uid}.txt"
        self.largefilename = f"{self.output_folder}/log_LARGE_{self.start_time}_{self.uid}.txt"
        self.log_entries = []
        self.shell_color_dict = {
            "BLACK": "\033[1;30m",
            "RED": "\033[1;31m",
            "GREEN": "\033[1;32m",
            "YELLOW": "\033[1;33m",
            "BLUE": "\033[1;34m",
            "PURPLE": "\033[1;35m",
            "CYAN": "\033[1;36m",
            "WHITE": "\033[1;37m",
            "GRAY": "\033[1;90m",
            "LIGHT_RED": "\033[1;91m",
            "LIGHT_GREEN": "\033[1;92m",
            "LIGHT_YELLOW": "\033[1;93m",
            "LIGHT_BLUE": "\033[1;94m",
            "LIGHT_PURPLE": "\033[1;95m",
            "LIGHT_CYAN": "\033[1;96m",
            "LIGHT_WHITE": "\033[1;97m",
            "ORANGE": "\033[1;38;5;208m",
            "PINK": "\033[1;95m",
            "LIGHTBLUE": "\033[1;94m",
            "MAGENTA": "\033[1;95m",
            "NC":"\033[0m" # No Color
            }
            # "BOLD":"\033[1m",
            # "UNDERLINE":"\033[4m",
            # "BLINK":"\033[5m",
    
    def log(self, message, print_it=True, color="NC", save_it=True, save_to_large_log=False, reprint=True):
        # Add the message to the log entries
        log_prefix = self.get_log_prefix()
        printable_message = f"{self.shell_color_dict.get(color, "")}{log_prefix} - {message}{self.shell_color_dict.get("NC", "")}"
        self.log_entries.append([log_prefix, message, color, printable_message])
        
        if len(printable_message) > 1000:
            printable_message = printable_message[:1000] + "..."

        
        if print_it:
            print(printable_message)
        
        if save_to_large_log:
            with open(f"{self.largefilename}", 'a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: \n{message}\n\n\n\n")
                save_it = False
        
        if save_it:
            with open(self.filename, 'w') as f:
                f.write(json.dumps(self.log_entries, indent=4))
    
    def error(self, message="", color="NC", print_it=True, save_it=True, save_to_large_log=False):
        self.log(message, color=color, print_it=print_it, save_it=save_it, save_to_large_log=save_to_large_log)
    
    def get_log_prefix(self):
        current_time = datetime.now()
        cumulative_time = current_time - self.start_time
        
        # Calculate the incremental time since the last log
        incremental_time = current_time - self.last_log_time
        
        
        # format the times as 00:00:00
        current_time_str = current_time.strftime("%H:%M:%S")
        cumulative_time_str = str(cumulative_time).split('.')[0]
        incremental_time_str = str(incremental_time).split('.')[0]
        self.last_log_time = current_time
        log_prefix = f"[Now: {current_time_str}, Cum: {cumulative_time_str}, Inc: {incremental_time_str}"
        return log_prefix
    
    def reprint_log(self):
        print ("\n\n\n|--------------   REPRINTING LOG   --------------|")
        for entry in self.log_entries:
            print(entry[3])
    
    def reset_log(self):
        self.uid = f"{uuid.uuid4()}"
        self.start_time = datetime.now()
        self.last_log_time = self.start_time
        self.filename = f"{self.output_folder}/log_{self.start_time}_{self.uid}.txt"
        self.largefilename = f"{self.output_folder}/log_LARGE_{self.start_time}_{self.uid}.txt"
        self.log_entries = []
        
logger = Logger()
    
    
##############################################
######    PROSPECT DATA PIPELINE     #########
##############################################

class contact_generation_pipeline:
    def __init__(self, environment='aws'):
        self.log_folder = "logs"
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        
        
        #Contact-specific items
        self.SECOrgCRDNum = ""
        self.PrimaryBusinessName = ""
        self.CCOName = ""
        self.CCOEmail = ""
        self.Website = ""
        self.CCOEmailDomain = ""
        
        self.required_system_fields = []
        
        self.google_general_cx = os.environ.get('GOOGLE_GENERAL_CX', 'No Key or Connection String found')
        
        self.downloadable_extensions = ['.gz', '.zip', 
                                        '.csv', '.txt', '.json', '.xml',
                                        '.pptx', '.xlsx', '.docx',  
                                        '.pdf', '.tiff',
                                        '.jpg', '.jpeg', '.png', 
                                        '.mp4', '.avi', '.mp3', '.m4a', '.wav']
        
        #Example of AI Pipeline for RBC for 
        
        self.max_depth = 5
        
        self.SeedNamesCommon = ["Smith", "Johnson", "Williams", "Brown"] #"Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        

        self.Markets = ["USA"] #, "Canada", "UK", "Europe", "Asia"]
        
        self.LeadershipAreas = ["Wealth Management", "Digital Wealth "]
        
        self.leadership_titles = ["CEO, Chief Executive Officer", "Leadership", "Founders", "Executive Team", "Partner"]
                        #   "Management Team", "Board of Directors", "COO, Chief Operating Officer", "CFO, Chief Financial Officer",
                        #   "CRO, Chief Risk Officer", "CTO, Chief Technology Officer", "CIO, Chief Information Officer", "CDO, Chief Data Officer",
                        #   "CLO, Chief Legal Officer", "CMO, Chief Marketing Officer", "CSO, Chief Sales Officer", 
                        #   "CPO, Chief Product Officer", "CDO, Chief Digital Officer", "CRO, Chief Revenue Officer", "EVP, Executive Vice President", 
                        #   "Head of Client Service", "Director", "Managing Director", 
                        #   "Executive Director"]
        
        self.log_key = datetime.now().strftime("%Y%m%d%H%M%S")
        
        self.table_col_defs = {}
        
        self.llm_model = 'llama3'
        self.llm_base_url='http://localhost:11434/v1'
        self.llm_model_api_key='Local-None-Needed'
        
        self.embeddings_model = 'mxbai-embed-large'
        self.embeddings_base_url='http://localhost:11434/v1'
        self.embeddings_model_api_key='Local-None-Needed'
        
        self.misleading_domains = ['gmail', 'yahoo', 'hotmail', 'aol', 'outlook', 'icloud', 'protonmail', 'linkedin', 'facebook', 'twitter', 
                                   'youtube', 'instagram', 'www', 'vimeo', 'glassdoor', 'tiktok', 'x', 'podbean', 'apple', 'rocketreach.co',
                                   'soundcloud', 'twitter', 'spotify', 'reddit', 'me', 'mac', 'icloud', 'live', 'msn', 'att.net', 
                                   'sbcglobal.net', 'bellsouth.net', 'verizon.net', 'cox.net', 'charter.net', 'earthlink.net', 'juno', 'optonline.net', 'netzero.net', 'frontiernet.net', 
                                   'windstream.net', 'suddenlink.net', 'cableone.net', 'centurylink.net', 'cogeco.net', 'rogers', 'shaw.ca', 'telus.net', 'videotron.ca', 'sympatico.ca', 
                                   'bell.net', 'mts.net', 'eastlink.ca', 'persona.ca', 'sasktel.net', 'telus.net',  'telusplanet']
        
        self.scrape_session_history = {}

        self.embeddings_model='mxbai-embed-large'
        self.google_api_key = os.environ.get('GOOGLE_API_KEY', 'No Key or Connection String found')
        self.google_general_cx = os.environ.get('GOOGLE_GENERAL_CX', 'No Key or Connection String found')
        
        self.environment_dict = {
            "local": f'postgresql://postgres:test@localhost:5432/platform',
            "aws":   f"postgresql://postgres:lnRipjfDXV07KjgiWXyvv@michael.ch6qakwu269h.us-east-1.rds.amazonaws.com:5432/postgres"
            }
        
        self.connection_string = self.environment_dict.get(environment)
        
        self.HOME = os.path.expanduser("~") #User's home directory
        self.DATA = f"{self.HOME}/code/data" # Working directory for data
        # self.ARCHIVE = f"{self.DATA}/{self.archive_folder}" # Archive directory for prior executions
        # self.SOURCE_DATA = f"{self.DATA}/{self.source_folder}" # Source data directory (downloaded and created data from current execution)
        self.LOGS = 'logs' # Directory for logs
  
#*################################################################
#*     PROSPECT LOAD FUNCTIONS       ##############################
#*################################################################    
        
    def create_empty_entity(self): 
        textlibrary_template = {
                "id": None,  # typically not manually set as it's auto-incremented
                "rowcontext": "",
                "uniquebuskey": "",
                "processingstatus": "",
                "Organization_CRD": "",
                "SEC": "",
                "Primary_Business_Name": "",
                "Legal_Name": "",
                "Main_Office_Location": {},
                "Main_Office_Telephone_Number": "",
                "SEC_Executive": {},
                "SEC_Status_Effective_Date": "",
                "Website_Address": "",
                "Entity_Type": "",
                "Governing_Country": "",
                "Total_Gross_Assets_of_Private_Funds": 0.0,
                "Next_Pipeline_Stage": "",
                "Notes": [],
                "title": "",
                "description": "",
                "summary": "",
                "names": [],
                "emails": [],
                "contacts": [],
                "clients": [],
                "partners": [],
                "companies": [],
                "experience": [],
                "entities": [],
                "needs": [],
                "economics": [],
                "competitors": [],
                "decisionprocesses": [],
                "timelines": [],
                "sasactivity": [],
                "sasstage": [],
                "urls": [],
                "domainurls": [],
                "externalurls": [],
                "scrapedurls": [],
                "urllevellookup": [],
                "authors": [],
                "publishdate": None,  # Use None for dates that should start as null
                "contenttype": "",
                "structdata": [],
                "bypage": [],
                "allpages": [],
                "summaryparts": [],
                "alltext": "",
                "topics": [],
                "speakers": [],
                "binarydoc": None,  # Use None for binary data that should start as null
                "documentids": [],
                "imageids": [],
                "sentiment": "",
                "createdon": None,  # Use None for timestamps that should start as null
                "archivedon": None,
                "iscurrent": True,  # Assuming True is the default
                "createdby": "",
                "archivedby": "",
                "loadsource": ""
            }
        return textlibrary_template
                    
    def create_targetlist_entity(self, incoming_dict):
        targetlist_template = {
            "rowcontext": "SUSPECT",
            "uniquebuskey": incoming_dict.get("organization_crd", ""),  # Map the similar field
            "processingstatus": "NEW",
            "Organization_CRD": incoming_dict.get("organization_crd", ""),
            "SEC": incoming_dict.get("sec", ""),
            "Primary_Business_Name": incoming_dict.get("primary_business_name", ""),
            "Legal_Name": incoming_dict.get("legal_name", ""),
            "Main_Office_Location": {  # Mapping individual address components to a dictionary
                "street_address_1": incoming_dict.get("main_office_street_address_1", ""),
                "street_address_2": incoming_dict.get("main_office_street_address_2", ""),
                "city": incoming_dict.get("main_office_city", ""),
                "state": incoming_dict.get("main_office_state", ""),
                "country": incoming_dict.get("main_office_country", ""),
                "postal_code": incoming_dict.get("main_office_postal_code", ""),
                "private_residence_flag": incoming_dict.get("main_office_private_residence_flag", "")
            },
            "Main_Office_Telephone_Number": incoming_dict.get("main_office_telephone_number", ""),
            "SEC_Executive": {  # Mapping chief compliance officer details to a dictionary
                "name": incoming_dict.get("chief_compliance_officer_name", ""),
                "other_titles": incoming_dict.get("chief_compliance_officer_other_titles", ""),
                "telephone": incoming_dict.get("chief_compliance_officer_telephone", ""),
                "facsimile": incoming_dict.get("chief_compliance_officer_facsimile", ""),
                "email": incoming_dict.get("chief_compliance_officer_email", "")
            },
            "SEC_Status_Effective_Date": datetime.fromtimestamp(
                incoming_dict.get("sec_status_effective_date", 0) // 1000
            ).strftime('%Y-%m-%d') if incoming_dict.get("sec_status_effective_date") else "",
            "Website_Address": incoming_dict.get("website_address", ""),
            "Entity_Type": incoming_dict.get("firm_type", ""),
            "Governing_Country": incoming_dict.get("main_office_country", ""),
            "Total_Gross_Assets_of_Private_Funds": float(incoming_dict.get("total_gross_assets_of_private_funds", 0.0)),
            "Next_Pipeline_Stage": "CRAWLWEBSITE",
            "iscurrent": True,
            "createdby": "MSMITH",
            "loadsource": "SECIARD"
        }
        return targetlist_template
        
    def load_prospects_from_csv(self, csv_file_path):
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            data = [dict(row) for row in csv_reader]
        
        entities = []
        for row in data:
            entity = self.create_prospect_entity(row)
            entities.append(entity)
        
        self.create_textlibrary(entities)

    def transform_xls_to_json(self):
        import pandas as pd
        import re

        def clean_column_name(name, col_set):
            # Replace spaces with underscores and remove characters that might be problematic in JSON keys
            name_str = f"{name}"
            if name_str in col_set:
                name_str = f"{name_str}_{len(col_set)}" 
            col_set.add(f"{name_str}")
            column_to_key = re.sub(r'[^\w\s]', '', f"{name_str}".replace(' ', '_')).lower()
            return column_to_key

        def excel_to_json(file_path, sheet_name=None):
            # Load the Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
            
            # Clean column names
            col_set = set()
            df.columns = [clean_column_name(col, col_set) for col in df.columns]
            
            # Convert the DataFrame to JSON
            json_data = df.to_json(orient='records')
            
            return json_data

        # Usage
        excel_dowloads = ['ia070124-e.xlsx']
        for excel_file in excel_dowloads:
            home_dir_of_current_user = os.path.expanduser("~")
            xls_path=os.path.join(home_dir_of_current_user, 'code', 'data', excel_file)
            
            json_output = json.loads(excel_to_json(xls_path, "IA_SEC_-_FIRM_ROSTER_FOIA_DOWNL"))
            json_path = os.path.join(home_dir_of_current_user, 'code', 'data', excel_file.replace('.xlsx', '.json'))
            with open(json_path, 'w') as f:
                f.write(json.dumps(json_output, indent=4))

    def load_prospects_from_json(self):
        json_files = ['ia070124-e.json']
        for json_file in json_files:
            home_dir_of_current_user = os.path.expanduser("~")
            json_path=os.path.join(home_dir_of_current_user, 'code','data', json_file)
            
            with open(json_path, 'r') as f:
                data = json.loads(f.read())
            
            entities = []
            for row in data:
                entity = self.create_prospect_entity(row)
                entities.append(entity)
            for entity in entities:
                self.create_textlibrary(entity)
        
    def clean_and_convert_str_to_decimal(self, value_str):
        if value_str is None or value_str == "" or not isinstance(value_str, str):
            return Decimal(0.0)
        cleaned_str = value_str.replace(",", "").strip()
        return Decimal(cleaned_str)        

    async def load_json_to_table(self, connection_string=None, table_name="targetlist", json_file_path=None):
        if connection_string is None:
            connection_string = self.environment_dict.get('aws', '')
        
        json_file_path = json_file_path if json_file_path else f"{self.DATA}/ia070124-e.json"
        
        conn = await asyncpg.connect(connection_string)
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            
            def get_domain_name(url):
                try:
                    ext = tldextract.extract(url)
                    return f"{ext.domain}.{ext.suffix}"
                except Exception as e:
                    return ""

            insert_sql = f"""
            INSERT INTO {table_name} (
                organization_crd,
                sec,
                rowcontext,
                uniquebuskey,
                primary_business_name,
                legal_name,
                
                
                main_office_telephone_number,
                

                
                email_address,
                website_address,
                entity_type,
                governing_country,
                total_gross_assets_of_private_funds
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
            );
            """
            # Main_Office_Location jsonb NULL, 
            # SEC_Executive jsonb NULL,
            # sec_status_effective_date,
            
            
            
            for record in data:
                values = (
                    f"{record.get("organization_crd", '')}",
                    record.get("sec", ''),
                    'PROSPECT',   
                    f"{record.get("organization_crd", '')}",
                    record.get("primary_business_name", ''),
                    record.get("legal_name", ''),
                    # json.dumps({"main_office_location": [
                    #     record.get("main_office_street_address_1", ""),
                    #     record.get("main_office_street_address_2", ""),
                    #     record.get("main_office_city", ""),
                    #     record.get("main_office_state", ""),
                    #     record.get("main_office_country", ""),
                    #     record.get("main_office_postal_code", "")]}),
                    record.get("main_office_telephone_number", ""),
                    # json.dumps({"sec_executive": [
                    #     record.get("chief_compliance_officer_name", ""),
                    #     record.get("chief_compliance_officer_other_titles", ""),
                    #     record.get("chief_compliance_officer_telephone", ""),
                    #     
                    # record.get("sec_status_effective_date", ''),
                    record.get("chief_compliance_officer_email", ""),
                    record.get("website_address", ''),
                    record.get("entity_type", ''),
                    record.get("governing_country", ''),
                    f"{self.clean_and_convert_str_to_decimal(record.get("total_gross_assets_of_private_funds", 0))}"
                )
                try:
                    await conn.execute(insert_sql, *values)
                except Exception as e:
                    logger.error(f"Error inserting record: {record} - {e}")
                    continue

            logger.log(f"Data from {json_file_path} loaded into {table_name} successfully.", color="GREEN")
        finally:
            await conn.close()

    def load_xlsx_to_postgres(self, file_path):
         # Read the XLSX file into a pandas DataFrame
        df = pd.read_excel(file_path)

        # Clean the column names
        cleaned_columns = [
            ''.join(c for c in str(col) if c.isalnum() or c == '_')
            for col in df.columns
        ]

        # Get the data types based on the first data row
        data_types = []
        for value in df.iloc[0]:
            try:
                if pd.api.types.is_datetime64_any_dtype(value):
                    data_types.append('TIMESTAMP')
                elif pd.api.types.is_numeric_dtype(value):
                    data_types.append('NUMERIC')
                else:
                    data_types.append('TEXT')
            except ValueError:
                data_types.append('TEXT')

        # Create the table creation query
        create_table_query = sql.SQL("CREATE TABLE IF NOT EXISTS dynamic_table ({})").format(
            sql.SQL(', ').join(
                [sql.SQL("{} {} PRIMARY KEY").format(sql.Identifier(cleaned_columns[1]), sql.SQL(data_types[1]))] +
                [sql.SQL("{} {}").format(sql.Identifier(col), sql.SQL(dtype))
                for col, dtype in zip(cleaned_columns[2:], data_types[2:])]
            )
        )
        
        # Connect to the PostgreSQL database
        conn = self.get_connection()

        try:
            # Create a cursor
            cur = conn.cursor()

            # Execute the create table query
            cur.execute(create_table_query)

            # Insert the data into the table
            for _, row in df.iterrows():
                values = [str(value) for value in row]
                insert_query = sql.SQL("INSERT INTO dynamic_table VALUES ({})").format(
                    sql.SQL(', ').join(map(sql.Literal, values))
                )
                cur.execute(insert_query)

            # Commit the changes
            conn.commit()

        finally:
            # Close the cursor and the connection
            cur.close()
            conn.close()

    def csv_to_list_of_dicts(self, file_path):
        with open(file_path, mode='r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            return [row for row in reader]
     
     
     
#*################################################################
#*     COMMON FUNCTIONS             ##############################
#*################################################################

    def isnull_or_empty(self, value):
        return value is None or value == "" 
    
    def extract_json_dict_from_llm_response(self, content):
        def try_to_json(input_value):
            try:
                return json.loads(input_value)
            except:
                pass
            try:
                return json.loads(f"[{input_value}]")
            except:
                return input_value
        
        # Find the first '{' and the last '}'
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            return None

        try:
            # Extract the JSON string
            json_string = content[start_idx:end_idx + 1]
            
            json_dict = try_to_json(json_string)
            if  isinstance(json_dict, dict) or isinstance(json_dict, list):
                return json_dict
            else:
                return None
        except Exception as e:
            return None
    
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
            "NC":"\033[0m"} # No Colo"}
        # "RED":"\033[0;31m",
                
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
            logger.error(terminal_message)
    


#*################################################################
#*     OLLAMA EMBEDDING             ##############################
#*################################################################
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


#*################################################################
#*     WEB-URL FUNCTIONS            ##############################
#*################################################################    
    def get_domain_from_email(self, email_address):
            try:
                return email_address.split('@')[1]
            except IndexError:
                return "Invalid email address"

    def get_url_domain(self, url):
        try: 
            parsed_url = urlparse(url)        
            domain_parts = parsed_url.netloc.split('.')
            domain = '.'.join(domain_parts[-2:]) if len(domain_parts) > 1 else parsed_url.netloc

            return domain
            
        except:
            return ""
    
    def is_valid_url(self, may_be_a_url):
        if "http" not in may_be_a_url:
            may_be_a_url = f"https://{may_be_a_url}"
        try:
            result = urlparse(may_be_a_url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False    
    
    def get_domain_name(self, url):
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"
        
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
        try:
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
        except Exception as e:
            logger.error(f"An error extracting URLs from markdown occurred: {e}")
            return []
    
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
            
            # Find a random number between 1000, and 5000   
            random_number = random.randint(1000, 30000)
            random_second = random_number / 1000
            
            time.sleep(random_second)
            
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
                    # with open(f"/Users/michasmi/Downloads/{unique_key}test_markdown.md", "w") as f:
                    #     f.write(markdown_text)
                    return markdown_text
                else:
                    logger.log("No body tag found.", color="RED")
            else:
                logger.log(f"Failed to retrieve the page. Status code: {response.status_code}", color="RED")
        except Exception as e:
            logger.log(f"An error occurred: {e}", color="RED")
    
    def randomize_sleep_time(self, min_seconds=1, max_seconds=3):
            expanded = random.randint(min_seconds*1000, max_seconds*1000)
            return expanded / 1000
    
    async def download_file(self, url, download_path):
        async with aiohttp.ClientSession() as session:
            for ext in self.downloadable_extensions:
                if url.endswith(ext):
                    async with session.get(url) as response:
                        if response.status == 200:
                            file_path = f"{download_path}{ext}"
                            async with aiofiles.open(file_path, 'wb') as f:
                                content = await response.read()
                                await f.write(content)
                            return True, file_path
            return False, ""
    
    def make_url_dict_key(self, url):
            # Define a regex pattern for unacceptable characters
            unsafe_chars_pattern = r'[^a-zA-Z0-9]'
            # Replace unsafe characters with underscore
            safe_url = re.sub(unsafe_chars_pattern, '_', url.strip())
            return safe_url

    
    async def extract_emails(self, scrape_dict):
        
        struct_data_text_list = await self.get_jsonb_text_safely(scrape_dict, 'structdata')
        
        text_with_emails = "\n".join(struct_data_text_list)
            
        # Extract email addresses using regex

        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_regex, text_with_emails)
        
        # Create structured JSON output
        output = {"emails": list(set(emails))}
        
        return json.dumps(output, indent=2)
    
#*################################################################
#*     NOT USED         ##############################
#*################################################################ 
    
    async def generate_contact_ollama_rag(self, contact_data):
        def step_0_setup(contact_data):
            self.SECOrgCRDNum = contact_data.get('SECOrgCRDNum')
            self.PrimaryBusinessName = contact_data.get('PrimaryBusinessName')
            self.CCOName = contact_data.get('CCOName')
            self.CCOEmail = contact_data.get('CCOEmail')
            self.CCOEmailDomain = self.get_domain_from_email(self.CCOEmail)
            self.Website = contact_data.get('Website')
            contact_data["EmailUrlList"] = []
            
        def step_1_search(contact_data, url_list):

            for title in self.Leadership_titles:
                for market in self.Markets:
                    # Define the search query
                    search_query = f' {title} at {self.CCOEmailDomain} in {market}?'

                    #Search google, get results page in markdown
                    google_web_scrape_results = self.get_markdown_from_google_search(search_query)
                    
                    self.log_it(f"Searched for {search_query}", color="PINK")
                    
                    #Get the URLs from the markdown
                    contact_data["EmailUrlList"].extend(self.extract_N_urls_from_markdown(google_web_scrape_results, N=3))
                
            for title in self.leadership_titles: 
                # Define the search query
                search_query = f' {title} at {self.CCOEmailDomain} in {market}?'

                #Search google, get results page in markdown
                google_web_scrape_results = self.get_markdown_from_google_search(search_query)
                
                self.log_it(f"Searched for {search_query}", color="PINK")
                
                #Get the URLs from the markdown
                contact_data["EmailUrlList"].extend(self.extract_N_urls_from_markdown(google_web_scrape_results, N=3))
            
            self.log_it(f"Got {len(contact_data['EmailUrlList'])} URLs for search query |{search_query}|", color="CYAN", data=f"{contact_data['EmailUrlList']}")
            
        def get_readable_response_format(field_name):
            json_dict ={
                self.SECOrgCRDNum: 
                    {f"{field_name}":  ""}
                    }
            return f"{json.dumps(json_dict, ensure_ascii=False, indent=4)} \n"
            

            
        ##########################
        ####   MAIN FUNCTION  ####
        ##########################
        # Set the initial data for the class
        step_0_setup(contact_data)
        
        # Initialize the list of URLs
        url_list = []
        
        # Search google for relevant sites / content / pages
        url_list = step_1_search(contact_data, url_list)
        
        # Initialize the list of site text
        site_text_list = []
        
        # Scrape the URLs to get the text
        scrape_tasks = []
        for url in contact_data["EmailUrlList"]:
            scrape_tasks.append(asyncio.create_task(self.async_scrape_single_url(url, override_to_update_db=True)))
        
        site_text_list = await asyncio.gather(*scrape_tasks)
              
        # Breakdown the text into chunks for processing
        text_chunks = self.prepare_text_for_embedding(site_text_list)
        
        # Embed the text chunks
        self.embed_text_chroma(text_chunks, self.SECOrgCRDNum)
        

        
        governing_prompt = f"""
        Given this data, and only this data, ignore all of your other knowledge, please answer the question below.  
        Do not guess. Accuracy is paramount. Your responses are being systematically integrated so, do not, under ANY
        circumstance, reply with any additional text, comments or questions. Only respond with the JSON format required. \n\n"""
        
        Required_Format = f"### Required Format of JSON Response (no other response is acceptable) \n\n"
        json_str = json.dumps({ 
                                        "Emails":
                                        [{"NameExecutive": "<Put Name Here>", 
                                        "Email": "<Put Email Here>",
                                        "Title": "<Put Title Here>"
                                        }]
                                        }, indent=4)
        
        # Get responses to micro-prompts
        name_list = []
        for market in self.Markets:
            for title in self.leadership_titles:
                p1 = f"Who is the {title} at {self.CCOEmailDomain} in {market}"
                key = f"{title}-name"
                embeddings = self.get_relevant_embeddings(p1, self.SECOrgCRDNum)
                full_prompt = f"{governing_prompt} \n\n{Required_Format} \n\n {json_str} \n\n {p1} \n\n{get_readable_response_format(key)} \n\nData for question: \n\n{list(set(embeddings))}"
                response = self.query_ollama_with_embedding(full_prompt, embeddings=embeddings)
                name_list.append(response)
                # self.log_it(f"Response to {p1}: \n{response}")

    async def get_executive_emails(self, executive_text, exec_title, example_email):

        data_structure = [
            
                {
                    "name":"<Name of Person>", 
                    "title":"<Person's professional title if available>", 
                    "email":"<Person's email if available>", 
                    "phone":"<Person's phone number if available>"
                }
            ] 
    
        prompt = f"""Extract every instance of a person at {self.PrimaryBusinessName}  from the following text and return a list of dictionaries in this format: 
        {json.dumps(data_structure, indent=4)}

        Please look especially hard for a person with the title {exec_title}.
        Provide only the JSON response with no additional text. if a phone number is not available, mark it as NA. Never create or guess a phone number. 
        However, if an email is not available create an email based upon the data that you have about that person using these real emails as a model:
        {example_email}
        
        REMINDER: Provide only the JSON response with no additional text; your responses are being systematically integrated. """

        prompt = f"{prompt} \n\n {executive_text}"
        
        genai.configure(api_key='AIzaSyDBzbqq_T584I57jJOnhzT-6jVBVQl687I')

        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(prompt,
                    generation_config=genai.types.GenerationConfig(
                        # Only one candidate for now.
                        candidate_count=1,
                        # stop_sequences=['x'],
                        # max_output_tokens=20,
                        temperature=0.1))
        
        return response
    
    async def clean_name_list_gemini(self, name_list):
        start_time = time.time()
        logger.log("Cleaning names with LLM...", color="CYAN")
        data_structure = {  "success":True,
                            "validnames":["<two word string that IS a person's name>"]
                            }
            
        prompt = f""" Below, you have been provided with a list of two word strings. Please classify each two word string
        as a valid names and discard invalid names. Simply, valid names are the "First Last" names of people and invalid names are any other two word string. 
        Examples of valid names are "John Doe", "Jane Smith", "Alice Johnson", etc.
        Examples of invalid names are "Red Apple", "Green Grass", "Blue Sky", "Ramona St" etc.
        
        As your response, provide only the JSON response specifide below with no additional text because your responses are being systematically integrated.
        {json.dumps(data_structure, indent=4)}
        
        # BEGINNING OF LIST DATA
        {json.dumps(name_list, indent=4)}
        # END OF LIST DATA """
        
        genai.configure(api_key='AIzaSyDBzbqq_T584I57jJOnhzT-6jVBVQl687I')

        model = genai.GenerativeModel('gemini-1.5-flash')

        async def get_response(prompt):
            response= model.generate_content(prompt,
            generation_config=genai.types.GenerationConfig(
                # Only one candidate for now.
                candidate_count=1,
                # stop_sequences=['x'],
                # max_output_tokens=20,
                temperature=0.1))
            return response
            
        
        #Get first response
        
        try :
            response = await get_response(prompt)
            logger.log(f"1st attempt complete in seconds is {time.time() - start_time}", color="CYAN")
            return json.loads(response.text)
        except:
            try :
                response = await get_response(prompt)
                logger.log(f"2nd attempt complete in seconds is {time.time() - start_time}", color="CYAN")
                return json.loads(response.text)
            except:
                return { "success": False,
                        "validnames": [],
                        "error": "Could not process the llm's response"
                        }
        

    
            
    
#*################################################################
#*     POSTGRES FUNCTIONS           ##############################
#*################################################################ 

   
    @asynccontextmanager
    async def async_get_connection(self):
        conn = await asyncpg.connect(self.connection_string)
        try:
            yield conn
        finally:
            await conn.close()
    
    async def get_safe_insert_value(self, value, field_type, field_name):
        def string_to_datetime(date_string: str) -> datetime:
            try:
                # Parse the date string into a datetime object
                date_obj = parser.parse(date_string)
                return date_obj
            except (parser.ParserError, TypeError, ValueError) as e:
                # Handle cases where the string is not a valid date
                logger.log(f"Error parsing date string: {e}", color="RED")
                return None
        
        if value is None or value == "":
            return None

        try:
            if field_type == "smallint":
                return int(value)
            
            if field_type == "name":
                return str(value)
            
            if field_type == "boolean" or field_type == "bool":
                return bool(value)
            
            if field_type == "numeric":
                return decimal.Decimal(value)
            
            if field_type in ["timestamp with time zone", "timestamptz"]:
                if isinstance(value, str):
                    value = string_to_datetime(value)
                if isinstance(value, datetime):
                    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
                return value
            
            if field_type in ["timestamp without time zone", "timestamp"]:
                if isinstance(value, str):
                    value = string_to_datetime(value)
                return value
            
            if field_type == "bigint":
                return int(value)
            
            if field_type == "date":
                if isinstance(value, datetime):
                    return value.date()
                if isinstance(value, str):
                    return string_to_datetime(value).date()
                
            
            if field_type == "xid":
                return int(value)
            
            if field_type == "char":
                return str(value)
            
            if field_type in ["character varying", "text"]:
                return str(value)
            
            if field_type == "jsonb":
                pass
            if field_name == "names":
                pass
            #Cricital that this check is before the list check afterward
            if field_type in ["jsonb", "_jsonb"]:
                ret_val =  json.dumps(value) if field_type == 'jsonb' else [json.dumps(item) for item in value]
                return ret_val
            
            if field_type in ["anyarray", "ARRAY", "_ARRAY", "_text"] or field_type.startswith("_"):
                if isinstance(value, list): 
                    return value
                return [value]
            
            if field_type == "double precision" or field_type == "real":
                return float(value)
            

            
            if field_type == "bytea":
                return bytes(value, 'utf-8')  # Ensure value is byte encoded
            
            if field_type in ["integer", "int4"]:
                return int(value)
            
            return value  # Default case, return the value as is

        except Exception as e:
            logger.log(f"Error converting {value} in filed {field_name} of type {field_type}: {e}", color="RED")
            return None
    
    async def execute_select_query(self, query, key='uniquebuskey', output_format='dict', conn=None):
        if conn is None:
            async with self.async_get_connection() as conn:
                rows = await conn.fetch(query)
        else:
            rows = await conn.fetch(query)
        
        if output_format == 'dict':
            result = [dict(row) for row in rows]
        else:
            result = rows
        return result
        
    async def get_column_types_dict(self, conn=None):
        if self.table_col_defs:
            return self.table_col_defs

        async with self.async_get_connection() as conn:
    
        
            query = """SELECT table_name, column_name, data_type, udt_name, character_maximum_length
                        FROM information_schema.columns c 
                        WHERE c.table_name NOT LIKE 'pg%'
                        AND c.table_schema <> 'information_schema';"""
            
            column_types = await self.execute_select_query(query, key='table_name', output_format='dict', conn=conn)

        column_types_by_table = {}
        for record in column_types:
            table_name = record.get('table_name', 'NO TABLE NAME')
            if table_name not in column_types_by_table:
                column_types_by_table[table_name] = {}
            column_types_by_table[table_name][record['column_name']] = {
                'data_type': record['data_type'],
                'udt_name': record['udt_name'],
                'character_maximum_length': record.get('character_maximum_length')
            }
            
        self.table_col_defs = column_types_by_table
        return self.table_col_defs
    
    async def apply_upsert(self, base_row, new_row, append_or_replace="REPLACE"):
        new_row['updatedon'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base_row['updatedon'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        def isnull_or_empty(value):
            return value is None or value == "" 
        if base_row is None:
            return new_row
        else:
            row_to_return = base_row.copy()
        # We use the base row as the starting point because we want to retain as much data as possible and ignore any new_row keys that aren't in the base_row
        for key in row_to_return.keys():
            if key not in new_row:
                continue
            
            if isnull_or_empty(new_row.get(key, None)):
                continue
            
            if isnull_or_empty(base_row.get(key, None)) and not isnull_or_empty(new_row.get(key, None)):
                row_to_return[key] = new_row.get(key)
                continue
            
            if key == 'contacts':
                pass
            
            new_scrape_dict_keys = [key for key in new_row.keys() if key not in base_row.keys()]
            logger.log(f"New scrape dict keys: {new_scrape_dict_keys}", color="BLLUE")
            
            # If the new_row has a non null/emoty value for the key AND new row is neither a list nore a dict THEN the new value will be used. Base value will be overwritten
            if not isinstance(new_row.get(key), dict) and not isinstance(new_row.get(key), list):
                # Check to make sure that base_row is not a list or dict, then overwrite
                if not isinstance(base_row.get(key), list) and not isinstance(base_row.get(key), dict):
                    #  primative types are overwritten
                    if new_row.get(key, None) is None:
                        continue
                    row_to_return[key] = new_row.get(key)
                    continue
            

            if isinstance(new_row.get(key), list):
                if not isinstance(row_to_return.get(key), list):
                    row_to_return[key] = []
                for item in new_row.get(key):
                    if item is None: 
                        continue
                    if item not in row_to_return.get(key, []):
                        row_to_return[key].append(item)
                    continue

            
            # Now handle lists
            # if the base row is a list, (and we know the new row has worthwhile data) we will append the new row to the base row
            if isinstance(row_to_return.get(key), list):
                #Clean up over-dumpted dictionary items in _jsonb fields
                if self.table_col_defs.get(key, '') == '_jsonb':
                    new_base_row = []
                    for dict_item in base_row[key]:
                        if dict_item is None:
                            continue
                        # If the item is a string it is an over-dumped dictionary. Try to restore it.
                        if isinstance(dict_item, str):
                            new_dict_item = self.get_dict_from_mess (dict_item)
                            new_base_row.append(new_dict_item)
                        else:
                            new_base_row.append(dict_item)
                    base_row[key] = new_base_row
                if isinstance(new_row.get(key), list):
                    # Extend if both are lists
                    base_row[key].extend(new_row.get(key))
                else:
                    #Otherwise append
                    base_row[key].append(new_row.get(key))
                row_to_return[key] = base_row[key]
                continue
            
            if isinstance(base_row.get(key), dict):
                # If both are dicts, we will update the base row with the new row
                if isinstance(new_row.get(key, {}), dict):
                    if key == 'contacts':
                        self.merge_contacts(base_row[key], new_row[key])
                        continue
                    else:
                        # Update the base row with the new row
                        base_row[key].update(new_row.get(key))
                        row_to_return[key] = base_row[key]
                        continue
                else:
                    # If the new row is not a dict, we will skip this field. We can't safely update a dict with a non-dict
                    logger.log(f"Error updating field {key}: cannot insert/update a dict value {new_row.get(key)} into a non-dict field with value: {base_row.get(key)}, column type: {self.table_col_defs.get(key, '')}", color="RED")
                    continue
            
               
                
        return row_to_return
        
    async def upsert_data(self, data_items, table_name='targetlist', schema="public", column_name_of_current_record_key='uniquebuskey', accommodate_system_fields=False, new_processing_status=None):
        async with self.async_get_connection() as conn:
            if not isinstance(data_items, list):
                data_items = [data_items]
            rows_to_load = []
            for item in data_items:
                #If a table key is provided and the key is not empty, we will check if the record exists in the table
                if column_name_of_current_record_key and item.get(column_name_of_current_record_key, '') != '':
                    query = f'SELECT * FROM {schema}."{table_name}" WHERE "{column_name_of_current_record_key}" = $1'
                    existing_data = await conn.fetchrow(query, item[column_name_of_current_record_key])
                    if existing_data is not None and len(existing_data) > 0:
                        # If we have existing data, we will apply the upsert operation
                        existing_data_dict = dict(existing_data) if existing_data else None
                        row_to_upsert = await self.apply_upsert(existing_data_dict, item)
                        if row_to_upsert:
                            rows_to_load.append(row_to_upsert)
            
            result = await self.get_column_types_dict(conn=conn)
            table_def = result.get(table_name, {})
            
            # Proceeding through the next lines we assume we have records that optimally
            # combine new data witha any existing data in the table 
            for row in rows_to_load:
                fields_in_table = [key for key in row.keys() if key in table_def]
                row_columns = [f'"{key}"' for key in fields_in_table]
                row_values = []
                if column_name_of_current_record_key in row_columns:
                    row_values.append(row[column_name_of_current_record_key])
                
                for col in fields_in_table:
                    value = await self.get_safe_insert_value(row[col], table_def[col]['udt_name'], col)
                    row_values.append(value)
                
                # Update or Insert the record
                if existing_data_dict:
                    sql = f'''
                        UPDATE {schema}."{table_name}"
                        SET {', '.join([f"{col} = ${i+1}" for i, col in enumerate(row_columns)])}
                        WHERE "{column_name_of_current_record_key}" = ${len(row_columns) + 1}
                    '''
                    row_values.append(existing_data_dict[column_name_of_current_record_key])
                else:
                    sql = f'''
                        INSERT INTO {schema}."{table_name}" 
                        ({', '.join(row_columns)})
                        VALUES ({', '.join([f'${i+1}' for i in range(len(row_columns))])})
                    '''
                
                try:
                    result = await conn.execute(sql, *row_values)
                    logger.error(f"Query executed successfully: {result}")
                except Exception as e:
                    # scrape_dict['notes'].append({"Error": f"executing query: {e}"})
                    logger.error(f"Error executing query: {e}")
                    logger.error(f"SQL: {sql}")
                    logger.log(f"Values: {row_values}", print_it=False, save_to_large_log=True)

        return "Upsert operation completed"
    
    async def reset_target(self, uniquebuskey="ABCD"):
        curlies = "{}"
        query = f"UPDATE public.targetlist SET processingstatus = '{curlies}', externalurls = '{curlies}', domainurls = '{curlies}', urls = '{curlies}', notes = ARRAY[]::jsonb[], bypage = ARRAY[]::jsonb[], structdata = ARRAY[]::jsonb[]"
        query+= f'  WHERE "uniquebuskey" = {"'"}{uniquebuskey}{"'"};'
        logger.error(f"\n{query}\n")
        async with self.async_get_connection() as conn:
            result = await conn.execute(query)
            return result
        

    
#*################################################################
#*     WEB SCRAPER                  ##############################
#*################################################################
  
    async def crawl_web_site_with_depth(self, url, max_depth=1, scrape_dict=None):
        
        # this function will create a new scrape_dict if one is not provided
        # after that it sues the provided scrape_dict to keep track of the urls to scrape and the urls 
        # that have been scraped or are toscrape.
        
        #*# This function can be called in a recursive/nested manner to scrape 
        #*  multiple levels of a website. Increment depth to navigate deeper
        scrape_dict = self.update_scrape_dict(scrape_dict=scrape_dict, toscrape=[url], level=0)
        still_more_to_scrape = True
        
        #* Recursive function to scrape the website begins here
        while still_more_to_scrape:            
            # Check if there are any urls to scrape
            if len(scrape_dict['toscrape']) == 0:
                # If there are no urls to scrape, then we are done
                still_more_to_scrape = False
                continue
            
            # Get the next url to scrape (randomly)
            if len(scrape_dict['toscrape']) > 1:
                random.shuffle(scrape_dict['toscrape'])
            
            url_to_scrape = scrape_dict['toscrape'][0]
            current_url_level = scrape_dict['levellookup'].get(f'{self.make_url_dict_key(url_to_scrape)}', self.max_depth)
            
            # Scrape the url    
            scraped_url_dict = await self.async_scrape_single_url(url_to_scrape, override_to_update_db=False)
            # The above needs to be updated to handle overrides that are occuring when the function is called recursively
            ValueError

            next_url_level = current_url_level + 1

            scraped_dict = self.update_scrape_dict(
                scrape_dict=scrape_dict, 
                toscrape=scraped_url_dict.get('found_urls', {}).get('same_domain', []), 
                level=next_url_level,
                max_depth=max_depth, 
                scraped=[url_to_scrape],
                body_text=scraped_url_dict.get('body_text', ''),
                body_html=scraped_url_dict.get('body', ''),
                domainurls=list(set(scraped_url_dict.get('found_urls', {}).get('same_domain', []))), 
                externalurls=list(set(scraped_url_dict.get('found_urls', {}).get('diff_domain', [])))
                # titles=[]], Gfd
                # names=None, 
                # emails=None, 
                # contacts=None
            )
            sleep_time = self.randomize_sleep_time()
            logger.error(f"Scraped URL: {url_to_scrape} at level {current_url_level}. Total to scrape: {len(scrape_dict['toscrape'])}. Total scraped: {len(scrape_dict['scraped'])}. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)
        return scrape_dict
       
    def update_scrape_dict(self, scrape_dict=None, toscrape=None, level=0, max_depth=5, scraped=None, body_text=None, body_html=None, domainurls=None, externalurls=None, titles=None, names=None, emails=None, contacts=None):
        def make_list_from_other(other):
            if other is None:
                return []
            if not isinstance(other, list):
                return [other]
            return other
        
        toscrape = make_list_from_other(toscrape)
        scraped = make_list_from_other(scraped)
        body_text = make_list_from_other(body_text)
        body_html = make_list_from_other(body_html)
        domainurls = make_list_from_other(domainurls)
        externalurls = make_list_from_other(externalurls)
        titles = make_list_from_other(titles)
        names = make_list_from_other(names)
        emails = make_list_from_other(emails)
        contacts = make_list_from_other(contacts)
        
        
        if scrape_dict is None:
            scrape_dict =  {
            "toscrape": [],
            "scraped": [],
            "levellookup": {},
            "body_text": [],
            "body_html": [],
            "domainurls": [],
            "externalurls": [],
            "titles": [],
            "names": [],
            "emails": [],
            "contacts": []}
            
            
        def extend_uniquely(scrape_dict, key, value):
            for item in value:
                if item.strip() not in scrape_dict[key]:
                    scrape_dict[key].append(item.strip())
                
            return scrape_dict
        
       
            
        
        scrape_dict = extend_uniquely(scrape_dict, 'body_text', body_text)
        scrape_dict = extend_uniquely(scrape_dict, 'body_html', body_html)
        scrape_dict = extend_uniquely(scrape_dict, 'domainurls', domainurls)
        scrape_dict = extend_uniquely(scrape_dict, 'externalurls', externalurls)
        scrape_dict = extend_uniquely(scrape_dict, 'titles', titles)
        scrape_dict = extend_uniquely(scrape_dict, 'names', names)
        scrape_dict = extend_uniquely(scrape_dict, 'emails', emails)
        scrape_dict = extend_uniquely(scrape_dict, 'contacts', contacts)

        # Add the newly scraped urls to the scraped list
        # Do this first to avoid adding the same url to the toscrape list
        for url in scraped:
            if url in scrape_dict['toscrape']:
                scrape_dict['toscrape'].remove(url)
                scrape_dict['scraped'].append(f"{url}")
            if f"{url}/" in scrape_dict['scraped']:
                scrape_dict['toscrape'].remove(url)
                scrape_dict['scraped'].append(f"{url}/")
        
        if level <= max_depth:

            
            for new_url in toscrape:
                if new_url not in scrape_dict['toscrape']:
                    if new_url not in scrape_dict['scraped']:
                        scrape_dict['toscrape'].append(new_url)
                        url_safe_key = self.make_url_dict_key(new_url)
                        scrape_dict['levellookup'][url_safe_key] = level
            
        # In case we somehome missed a url, 
        # we will remove it from the toscrape list
        # along with any other variations of the url
        for url in scrape_dict['toscrape']:
            if url in scrape_dict['scraped']:
                scrape_dict['toscrape'].remove(url)
            if f"{url}/" in scrape_dict['scraped']:
                scrape_dict['toscrape'].remove(url)
                scrape_dict['scraped'].append(f"{url}/")
    
            
        return scrape_dict
    def scrape_pdf_url(self, url, base_domain):
        return_dict = {}
        unique_date_time_key = datetime.now().strftime("%Y%m%d%H%M%S")
        def pdf_to_text(pdf_url):

            # Download the PDF file from the URL
            response = requests.get(pdf_url)
            response.raise_for_status()  # Check for request errors
            
            # Convert PDF to a list of images
            pdf_bytes = BytesIO(response.content)
            images = convert_from_bytes(pdf_bytes.read())
            
            all_text = ""
            
            for image in tqdm(images, desc="Processing PDF Page Images"):
                # Perform OCR on each image
                text = pytesseract.image_to_string(image)
                all_text += text + "\n"
            return all_text
        
        def extract_urls_from_text(text):
            urls = []
            same_domain_urls = []
            diff_domain_urls = []
            url_pattern = re.compile(r'(https?://\S+|www\.\S+)')
            more_urls = url_pattern.findall(text)
            if isinstance(more_urls, list) and len(more_urls) > 0:
                urls.extend(more_urls)
                
            url_pattern = re.compile(r'(http?://\S+|www\.\S+)')
            more_urls = url_pattern.findall(text)
            if isinstance(more_urls, list) and len(more_urls) > 0:
                urls.extend(more_urls)
                
            for url in urls:
                if base_domain in url:
                    same_domain_urls.append(url)
                else:
                    diff_domain_urls.append(url)
            
            urls = {
                'same_domain': list(set(same_domain_urls)),
                'diff_domain': list(set(diff_domain_urls))
            }
            
            return urls
        
        if not url.endswith('.pdf'):
            return f"URL {url} does not end with .pdf"
        body_text = pdf_to_text(url)
        body = body_text
        urls = extract_urls_from_text(body_text)
        message = f"Successfully got pdf text extraction for {url} with {len(body_text)} characters."
        
        return_dict["url"] = url
        return_dict['domainurls'] = urls['same_domain']
        return_dict['externalurls'] = urls['diff_domain']
        return_dict['bypage'] = [{unique_date_time_key: {'url': url, 'text': body_text}}]
        return_dict['structdata'] = [{'html': body}]
        return_dict['contact_emails'] = self.extract_emails_from_text(body)
        return_dict['notes'] = [{'type':'scrapelog', 'success': True, 'message': message}]
        return_dict["success"] = True
            
        return return_dict 
            
    
    
    def process_pdf_urls(self, pdf_urls, base_url):
        results = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            future_to_url = {executor.submit(self.scrape_pdf_url, url, base_url): url for url in pdf_urls}
            for future in tqdm(concurrent.futures.as_completed(future_to_url), "PDF URL Processing"):
                url = future_to_url[future]
                try:
                    data = future.result()
                    results.append(data)
                    logger.log (f"PDF URL {url} processed successfully", color="PINK")
                except Exception as exc:
                    logger.error (f'PDF URL FAILED {url} generated an exception: {exc}', color="RED")

        return results

    
    def extract_emails_from_text(self, text):
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        emails = email_pattern.findall(text)
        return emails
    
    async def async_scrape_single_url(self, url):
        scrape_start_time = datetime.now()
        return_dict = {}
        
        async def extract_same_domain_urls(page, base_url):
            # Get all anchor elements
            same_domain_urls = []
            diff_domain_urls = []
            anchor_elements = await page.query_selector_all('a')
            # logger.log(f"Found {len(anchor_elements)} anchor elements")

            # Extract href attributes and filter for same domain
            
            for anchor in anchor_elements:
                href = await anchor.get_attribute('href')
                if href:
                    # Resolve relative URLs
                    full_url = urljoin(base_url, href).strip()
                    # Parse URLs
                    
                    base_domain = urlparse(base_url).netloc
                    # Extract everything to the left of the last .
                    site_name = base_domain.split('.')[-2]
                    url_domain = urlparse(full_url).netloc
                    # Check if the domain matches
                    if site_name in url_domain and site_name not in f"{self.misleading_domains}":
                        same_domain_urls.append(full_url)
                    else:
                        diff_domain_urls.append(full_url)
                        
            urls = {
                'same_domain': list(set(same_domain_urls)),
                'diff_domain': list(set(diff_domain_urls))
            }
            return urls
        
        def extract_text_from_html(html_body):
            soup = BeautifulSoup(html_body, 'html.parser')
            return soup.get_text(separator=' ', strip=True)

        def is_a_valid_url(may_be_a_url):
            
            try:
                result = urlparse(may_be_a_url)
                return all([result.scheme, result.netloc])
            except Exception as e:
                return False

        if url is None or url == "":
            return_dict = {}
            return_dict["error_message"] = "URL is empty or None."
            return_dict["success"] = False
            return return_dict
    
        base_domain = f"https://{self.get_domain_name(url)}"
        
        if not os.path.exists("scrapes"):
            os.makedirs("scrapes")
        
        if "http" not in url:
            url = f"https://{url}"
        
        if url == "" or not is_a_valid_url(url):
            return_dict["error_message"] = f"URL |{url}| is invalid."
            return_dict["success"] = False
            return return_dict
        
        unique_date_time_key = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, timeout=10000)  # Set a timeout for page navigation
                await page.wait_for_selector('body', timeout=10000)  # Set a timeout for waiting for body
            except PlaywrightTimeoutError as e:
                logger.log(f"Playwright timeout for {url} : {str(e)}", color="ORANGE")
                return_dict["error_message"] = f"Playwright timeout error for URL | {url} |: {str(e)}"
                return_dict["success"] = False
                await browser.close()
                return return_dict
            except Exception as e:
                logger.error(f"Playwright error: {str(e)}")
                return_dict["error_message"] = f"Playwright error for URL |{url}|: {str(e)}"
                return_dict["success"] = False
                await browser.close()
                return return_dict
                
            logger.log(f"\033[1;32mSCRAPE SUCCESSFUL: Duration: {datetime.now() - scrape_start_time} seconds for url: {url}\033[0m")
            
            body = await page.content()
            body_text = extract_text_from_html(body)                
            urls = await extract_same_domain_urls(page, base_domain)
            message = f"Successfully got full webpage for {url} with {len(body_text)} characters."
            await browser.close()
                
        # except Exception as e:
        #     logger.error(f"Playwright error: {str(e)}")
        #     return_dict["error_message"] = f"Playwright/Scraping error for URL |{url}|: {str(e)}"
        #     return_dict["success"] = False
        #     logger.error(f"\033[1;31mAfter {datetime.now() - scrape_start_time} seconds, the scrape failed for {url} with error: {return_dict["error_message"]}\033[0m")
        #     return return_dict
        
        # finally:
        #     await browser.close()
        
        
        
        return_dict["url"] = url
        return_dict['domainurls'] = urls['same_domain']
        return_dict['externalurls'] = urls['diff_domain']
        return_dict['bypage'] = [{unique_date_time_key: {'url': url, 'text': body_text}}]
        return_dict['structdata'] = [{'html': body}]
        return_dict['contact_emails'] = self.extract_emails_from_text(body)
        return_dict['notes'] = [{'type':'scrapelog', 'success': True, 'message': message}]
        return_dict["success"] = True
            
        return return_dict 
        
    def sync_scrape_single_url(self, url):
        return asyncio.run(self.async_scrape_single_url( url))
    
    async def google_search(self, query, num_results=10):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        cx_id = os.getenv("GOOGLE_GENERAL_CX")
        search_endpoint = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx_id,  # Important for specifying your search engine
            "q": query,
            "num": num_results,  # Pass num_results directly as an integer

        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(search_endpoint, params=params)
                logger.error(f"Google Search API response: {response}")  # Log response for debugging
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"Google Search API error: {e.response.status_code} - {e.response.text}")
                raise ValueError(f"Google Search API error: {e.response.status_code} - {e.response.text}") from e
                
        try:
            return response.json()
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON response from Google Search API")
            raise ValueError("Invalid JSON response from Google Search API") from e 


#!################################################################
#!     PIPELINE 1  (MAIN PAGES)  ##############################
#!################################################################
    
    async def create_scrape_dict(self, url, processing_status='NEW'):
        scrape_dicts = await self.get_next_batch_of_targets(batch_size=1, start_processing_status='NEW')
        scrape_dict = scrape_dicts[0]
        for key in scrape_dict.keys():
            if isinstance(scrape_dict[key], list):
                scrape_dict[key] = []
            elif isinstance(scrape_dict[key], dict):
                scrape_dict[key] = {}
            elif isinstance(scrape_dict[key], str):
                scrape_dict[key] = ""
            elif isinstance(scrape_dict[key], int):
                scrape_dict[key] = 0
            
            scrape_dict['urls'] = [url]
            scrape_dict['website_address'] = url
            scrape_dict['processingstatus'] = processing_status
            scrape_dict['notes'] = {}
            scrape_dict['uniquebuskey'] = uuid.uuid4()
            
        return scrape_dict
    
    async def get_next_batch_of_targets(self, batch_size=20, start_processing_status='NEW', optional_ubuskey=None, column_type_dict = None):
        
        async with self.async_get_connection() as conn:

            where_clause = []
            #if batch_size < this means get all records
         
            limit=''
            if optional_ubuskey:
                where_clause.append(f" uniquebuskey = '{optional_ubuskey}' ")
            else:
                where_clause.append(f" processingstatus = '{start_processing_status}' ")
                if batch_size > 0:
                    limit = f" LIMIT {batch_size} "
            
            sql = f''' select id, primary_business_name, uniquebuskey, processingstatus, 
            website_address, urls, domainurls, externalurls, bypage, notes, structdata  
            from targetlist t
            where {" and ".join(where_clause)} {limit};'''
            
            logger.error(sql)
            
            rows = await conn.fetch(sql)
            
            # Turn all the rows into dictionaries
            scrape_dicts = [dict(row) for row in rows]
            

                
                    
            
        logger.log(f"Obtained {len(scrape_dicts)} scrape_dicts in batch")
        return scrape_dicts

    async def search_for_executives(self, scrape_dict ):
        def get_domain_name(url):
                try:
                    ext = tldextract.extract(url)
                    return f"{ext.domain}.{ext.suffix}"
                except Exception as e:
                    return ""
        
        name = scrape_dict.get('primary_business_name', '') 
        website = scrape_dict.get('website_address', '')
        website_domain = get_domain_name(website)
        
        query = f"{name} {website_domain} executives team -linkedin -facebook -instagram -rocketreach -crunchbase -zoominfo"
        scrape_dict['id'] = f"{scrape_dict.get('id', 'NO KEY')}"
        logger.log(f"Searching for executives with query: {query}")
        result_list = await self.google_search(query=query)
        
        image_link_list = []
        bypage_list = []
        url_list = []
        
        for result in result_list.get('items', []):
            url_list.append(result.get('link', ''))

            if result.get('snippet', '') != '' and result.get('snippet', '') not in bypage_list:
                bypage_list.append(result.get('snippet', ''))
            if len(result.get('pagemap', {}).get('cse_thumbnail', [])) > 0  :
                if result.get('pagemap', {}).get('cse_thumbnail', [])[0].get('src', '') not in image_link_list:
                    image_link_list.append(result.get('pagemap', {}).get('cse_thumbnail', [])[0].get('src', ''))
            
            metatag_list = result.get('pagemap', {}).get('metatags', []) 
            if len(metatag_list) > 0:
                for metatag in metatag_list:
                    if metatag.get('og:image', '') != '' and metatag.get('og:image', '') not in image_link_list:
                        image_link_list.append(metatag.get('og:image', ''))
                    if metatag.get('og:description', '') != '' and metatag.get('og:description', '') not in bypage_list:
                        bypage_list.append(metatag.get('og:description', ''))
        
        if scrape_dict.get('bypage',[]) is None or len(scrape_dict.get('bypage', [])) == 0:
            scrape_dict['bypage'] = bypage_list
        else :
            scrape_dict['bypage'].extend(bypage_list)
        
        if scrape_dict.get('urls',[]) is None or len(scrape_dict.get('urls', [])) == 0:
            scrape_dict['urls'] = url_list
        else :
            scrape_dict['urls'].extend(url_list)
        
        if scrape_dict.get('imageurls',[]) is None or len(scrape_dict.get('imageurls', [])) == 0:
            scrape_dict['imageurls'] = image_link_list
        else :
            scrape_dict['urls'].extend(url_list)
        


        return scrape_dict
     
    async def scrape_seed_urls(self, scrape_dict, next_processing_status='SCRAPE1'):

        uniquebuskey = scrape_dict.get('uniquebuskey', f"{uuid.uuid4()}")

        current_urls = scrape_dict.get('urls', [])
        if current_urls is None:
            current_urls = []
        current_urls.append(scrape_dict.get('website_address', ''))
        current_urls.append(f"https://{scrape_dict.get('domain', '')}/")
        current_urls.append(f"https://www.{scrape_dict.get('domain', '')}/")
        current_urls.append(f"http://{scrape_dict.get('domain', '')}/")
        current_urls.append(f"http://www.{scrape_dict.get('domain', '')}/")
        scrape_dict['urls'] = [url for url in current_urls if url is not None and url != "" and self.is_valid_url(url)]
        scrape_dict['urls'] = list(set(current_urls))
        scrape_dict['urls'] = [url for url in scrape_dict['urls'] if url is not None and url != "" and self.is_valid_url(url)]
        # Print the urls for the log
        url_for_print = "\n---->  ".join([url for url in scrape_dict.get('urls', []) if url is not None][:10])
        logger.error(f"\033[1;96m\n\nSEED 'LEVEL 0' SCRAPE for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {uniquebuskey} and urls (10): \n{url_for_print}\033[0m")
        pdf_urls = []
        regular_urls = []
        seed_scrape_results = []
        for url in tqdm(scrape_dict.get('urls', []), "Processing Seed URLs"):   
            if url.endswith('.pdf'):
                pdf_urls.append(url)
            else:
                regular_urls.append(url)
                seed_scrape_results.append(self.async_scrape_single_url(url=url))

        # Process regular URLs with asyncio
        url_results = await asyncio.gather(*seed_scrape_results)
        
        # Process PDF URLs with multiprocessing
        pdf_results = self.process_pdf_urls(pdf_urls, scrape_dict.get('domain', ''))
        
        # Combine the results
        results = url_results + pdf_results
        pass        
                    
        #Nothing to scrape
        if len(results) == 0:
           return scrape_dict             
        
               
        #Many URLs to scrape
        if len(results) > 0:
            single_result = scrape_dict
             
            for result in results:
                # Combine with upsert logic
                single_result = await self.apply_upsert(single_result, result)
                single_result['urls'] = list(set(single_result.get('urls', [])))
                single_result['updatedon'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                single_result['processingstatus'] = next_processing_status
        
        return single_result

    async def scrape_extended_urls(self, scrape_dict, max_urls_per_client=1):
        # Somewhere in this fucntion scrape_dict becomes a string
        all_urls = []
        if scrape_dict is None or scrape_dict.get('domainurls', []) is None or scrape_dict.get('externalurls', []) == []:
            scrape_dict['domainurls'] = []
        if scrape_dict is None or scrape_dict.get('externalurls', []) is None or scrape_dict.get('externalurls', []) == []:
            scrape_dict['externalurls'] = []
        all_urls.extend(scrape_dict.get('domainurls', []))
        all_urls.extend(scrape_dict.get('externalurls', []))
        scraped_urls = []
        
        # get urls already scraped
        struct_data_list_of_strings = scrape_dict.get('structdata', [])
        if struct_data_list_of_strings:
            for struct in struct_data_list_of_strings:
                if isinstance(struct, str):
                    struct_dict = await self.get_dict_from_mess(struct)
                elif isinstance(struct, dict):
                    struct_dict = struct
                else:
                    continue
                if isinstance(struct_dict, str):
                    continue
                if struct_dict.get('url', '')!= '':
                    scraped_urls.append(struct_dict.get('url', ''))
        
        def prioritze_urls(url_list):
            key_words = ['contact', 'about', 'team', 'executive', 'leadership', 'people'
                         'management', 'staff', 'founders', 'appoint', 'board']
            
            skip_words = ['privacy', 'policy', 'terms', 'conditions', 'careers', 'adobe', 
                          'facebook', 'twitter', 'linkedin', 'instagram', "investopedia", 'youtube']
            skip_words.extend(self.misleading_domains)
            
            priority_urls = []
            regular_urls = []
            skip_urls = []
            
            for url in url_list:
                if any(word in url for word in key_words):
                    priority_urls.append(url)
                elif any(word in url for word in skip_words):
                    skip_urls.append(url)
                else:
                    regular_urls.append(url)
            priority_urls.extend(regular_urls)
            # priority_urls.extend(skip_urls)
            return priority_urls
            
            
            

        
        uniquebuskey = scrape_dict.get('uniquebuskey', 'NOKEY')
        all_urls = list(set(all_urls))
        all_urls = [url for url in all_urls if url is not None and url != "" and self.is_valid_url(url)]
        all_urls = prioritze_urls(all_urls)
        new_urls = [{uniquebuskey: url} for url in all_urls if url not in scraped_urls]  
              
        
        if len(new_urls) == 0:
            if 'notes' not in scrape_dict.keys() or scrape_dict.get('notes', []) is None:
                scrape_dict['notes'] = []
            scrape_dict['notes'].append({'type':'scrapelog', 'success': True, 'message': 'No new URLs to scrape'})
        new_scrape_tasks = []
        
        #  LIMIT new_urls to max_urls_per_client
        original_length = len(new_urls)
        if len(new_urls) > max_urls_per_client:
            new_urls = new_urls[:max_urls_per_client]
        
        # Break the URLs into groups and process each group
        batch_size = 25
        results = []
        urls_for_print = "\n--->  ".join([url.get(uniquebuskey, '') for url in new_urls][:10])
        logger.error(f"\033[1;95m\n\nLEVEL 1 SCRAPE: {scrape_dict.get('primary_business_name', 'NO NAME')} | {uniquebuskey} for {len(new_urls)} of {original_length} urls: \n{urls_for_print}\033[0m")
        
        ### ? Multi Processing Method METHOD ####
            # def run_multiprocessing(urls):
            #     # loop = asyncio.get_event_loop()
            #     with Pool() as pool:
            #         results = pool.map(self.sync_scrape_single_url, urls)
            #     return results
            # url_str_iterable = []
            # for new_url in new_urls:
            #         for value in new_url.values():
            #             url_str_iterable.append(value)
            
            # results = run_multiprocessing(url_str_iterable)
        
        ## ? END ASYNC METHOD ####
        for new_url in new_urls:
            for key in new_url.keys():
                new_scrape_tasks.append(self.async_scrape_single_url(new_url[key]))         
        results = await asyncio.gather (*new_scrape_tasks)
        
        
   
        #Many URLs to scrape
        if len(results) > 0:
            single_result = scrape_dict
            for result in results:
                try:
                    err = result.get('error_message', '')
                    if "Timeout error" in err:
                        continue
                except:
                    pass
                # Combine with upsert logic
                single_result = await self.apply_upsert(single_result, result)
        else:
            single_result = scrape_dict
            # Add URL List as a page
            unique_date_time_key_in_ms = datetime.now().strftime("%Y%m%d%H%M%S%f")
            url_page = {f'urls_{unique_date_time_key_in_ms}': all_urls}
                
            if single_result.get('bypage', []) is None or len(single_result.get('bypage', [])) == 0:
                single_result['bypage'] = [url_page]
            else:
                single_result['bypage'].append(url_page)
                
                
        
        return single_result
        
    async def get_dict_from_mess(self, text):
        if isinstance(text, dict):
            return text
        not_a_dict = True
        count = 0
        while not_a_dict and count<=10:
            try:
                text = json.loads(text)
                if isinstance(text, dict):
                    return text
                else:
                    count+=1
            except:
                return text

    async def extract_all_emails(self, scrape_dict):   
        def get_dict_from_dumped(text):
            if isinstance(text, dict):
                return text
            not_a_dict = True
            while not_a_dict:
                try:
                    text = json.loads(text)
                    if isinstance(text, dict):
                        return text
                    return json.loads(json.loads(text))
                except:
                    return text
        scrape_dict['emails'] = get_dict_from_dumped(scrape_dict['structdata'])
        return scrape_dict

    async def extract_names(self, text):
        """
        Extracts full names (first and last names) from a given text.

        Parameters:
        text (str): The text to extract names from.

        Returns:
        list: A list of full names extracted from the text.
        """
        logger.error("Extracting names with NLTK...")
        start_time = time.time()
        # Tokenize the text into words
        words = word_tokenize(text)

        # Perform part-of-speech tagging
        pos_tags = pos_tag(words)

        # Perform named entity recognition
        named_entities = ne_chunk(pos_tags, binary=False)

        # Extract names
        names = []
        for subtree in named_entities:
            if isinstance(subtree, Tree) and subtree.label() == 'PERSON':
                name = " ".join([token for token, pos in subtree.leaves()])
                names.append(name)
        
        deduped_names = list(set(names))
        async def is_two_words(name):
            try:
                return len(name.split()) == 2
            except:
                return False
        
        time_taken = time.time() - start_time
        logger.error(f"Extracted {len(deduped_names)} names in {time_taken:.2f} seconds.")
        likely_names = []
        for name in deduped_names:
            if await is_two_words(name):
                likely_names.append(name)
                
        very_likely_names = await self.clean_name_list_gemini(likely_names)
        
        return very_likely_names
    
    async def get_framework_from_gemini(self, scrape_dict):
        

        prompt = ""
        
        async def ask_llm(text, llm='ollama'):
            if llm == 'gemini-1.5-flash':
                model = genai.GenerativeModel("gemini-1.5-flash")                
                max_tokens = 12000
                generation_config = {
                    "temperature": .1,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 12000,
                    "response_mime_type": "text/plain",
                    }
                ask_text = f"{prompt}\n\n### TEXT BLOCK ###\n{text}"
                result = model.generate_content(ask_text, generation_config=generation_config)
                return result
            
            
        json_response_format = [{
            "name": "<Name of person entity you found",
            "title": "<Title of person entity you found",
            "Company": f"{scrape_dict.get('primary_business_name', '')} or affiliated entity.",
            "email": "<Email of person entity you found",
            "phone": "<Phone number of person entity you found",
            },{
            "name": "<Name of person entity you found",
            "title": "<Title of person entity you found",
            "Company": f"{scrape_dict.get('primary_business_name', '')} or affiliated entity.",
            "email": "<Email of person entity you found",
            "phone": "<Phone number of person entity you found",
        }]
        
        prompt = f"""
            Extract all the names, titles, emails and phone numbers from the text content provided for executives 
            and employees at {scrape_dict.get('primary_business_name', '')} or affiliated entities.
            Associate each name with the title, email and phone number found in the text where possible.
            Do not generate ANY email addresses or names that are not in the provided text.
            Return them as a JSON object in the format below.
            Your responses are being systematically integrated into a database.
            
            To help you, in addition to the text provided we have run an extraction of emails and names from the text, which is below.
            Names:
            {scrape_dict.get('names', '')}
            
            Emails:
            {scrape_dict.get('emails', '')}
            
            
            
            Do not include any text or commentary outside of the requested json object.
            JSON Format:
            {json.dumps(json_response_format)}
            
            
            ## BEGIN TEXT ##
            {scrape_dict.get('bypage', '')}
            ## END TEXT ##"""
        raw_text = ""
        for page in scrape_dict.get('bypage', []):
            if isinstance(page, dict):
                for key, value in page.items():
                    raw_text += f"{value}\n\n"
            if isinstance(page, str):
                clean_str = await self.get_dict_from_mess(page)
                if isinstance(clean_str, dict):
                    for key, value in clean_str.items():
                        if isinstance(value, str):  
                            raw_text += f"{value}\n\n"
                        elif isinstance(value, list):
                            raw_text += f"{"\n\n".join(value)}\n\n"
                        elif isinstance(value, dict):
                            for k, v in value.items():
                                raw_text += f"{v}\n\n"
            
                if isinstance(clean_str, str):
                    raw_text += f"{clean_str}\n\n"
                
                if isinstance(page, list):
                        raw_text += f"{"\n\n".join(page)}\n\n"
            if isinstance(page, list):
                raw_text += f"{"\n\n".join(page)}"
        sentences = raw_text.split("\n\n\n")  # Split into sentences
        pass
        get_responses = [await ask_llm(sentence) for sentence in sentences if sentence is not None and sentence != ""]
        if not isinstance(get_responses, list):
            get_responses = [get_responses]
        
        # /await asyncio.gather(*get_responses)
        
        return get_responses

    async def get_final_contacts_from_gemini(self, initial_framework_dict, scrape_dict):

        model = genai.GenerativeModel("gemini-1.5-flash")
        generation_config = {
            "temperature": .1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 12000,
            "response_mime_type": "text/plain",
            }
        json_response_format = [{
            "name": "<Name of person entity you found>",
            "title": "<Title of person entity you found in the text>",
            "Company": f"<{scrape_dict.get('primary_business_name', '')} or affiliated entity.>",
            "foundemail": "<Email of person entity found>",
            "generatedemail": "<If there is no foundemail, this must be an email address you generate using the email format or other same-company emails, if you there is a matching name already in this dictionary or found in the text>",
            "phone": "<Phone number of person entity you found in the text",
            },{
            "name": "<Name of person entity you found>",
            "title": "<Title of person entity you found in the text>",
            "Company": f"<{scrape_dict.get('primary_business_name', '')} or affiliated entity.>",
            "foundemail": "<Email of person entity found>",
            "generatedemail": "<If there is no foundemail, this must be an email address you generate using the email format or other same-company emails, if you there is a matching name already in this dictionary or found in the text>",
            "phone": "<Phone number of person entity you found in the text",
        }]
        
        result = model.generate_content(
            f"""
            Below is a partially completed dictionary of names, titles, companies, emails, and phone numbers
            Beneath the partially completed dictionary, is a text block that contains additional information that may be useful in completing the dictionary.
            Using the information in the text block, complete the dictionary with the names, titles, companies, emails, and phone numbers of executives 
            and employees at {scrape_dict.get('primary_business_name', '')} or affiliated entities.

            For emails only, note that you should make utilize the email format or other same-company emails to generate the email address if you cannot find an email address.
            To help you, in addition to the text provided we have run an extraction of emails and names from the text, which is below.
            Names:
            {scrape_dict.get('names', '')}
            
            Emails:
            {scrape_dict.get('emails', '')}
            
            Return them as a JSON object in the format after you have populated the data points as instructed.
            Your responses are being systematically integrated into a database.
            Do not include any text or commentary outside of the requested json object.
            
            JSON Format:
            {json.dumps(json_response_format)}
            ## BEGIN TEXT ##
            
            Partially Completed Dictionary:
            {initial_framework_dict}
            
            ## START OF TEXT BLOCK ##
            Text Block:
            {scrape_dict.get('bypage', '')}
            ## END OF TEXT BLOCK ##""",
            
            generation_config=generation_config)
        
            
        try:
            result_list = self.extract_json_dict_from_llm_response(result.text)
            to_return = {
                "success": True,
                "response": result_list
                }
        
        except Exception as e:
            to_return = {
                "success": False,
                "error": str(e),
                "response": result.text
                }
        return to_return

    async def merge_contacts(self, initial_contacts, final_contacts):
        if not isinstance(initial_contacts, dict):
            initial_contacts = {}
        if not isinstance(final_contacts, dict):
            final_contacts = {}
        # Set initial contacts as the base
        merged_contacts = initial_contacts
        
        for key, value in merged_contacts.items():
            # If the base has no value, but the final does, add the final value
            if value is None or value == "":
                if final_contacts.get(key, "") != "" and final_contacts.get(key, "") != "":
                    merged_contacts[key] = final_contacts[key]
            # If the base has a value AND the final has a value, pipe concatenate them
            if key in final_contacts.keys():
                if final_contacts[key] is not None and final_contacts[key]!= "":
                    merged_val = merged_contacts[key]
                    if merged_val is None: merged_val = ""
                    merged_contacts[key] = f"{merged_contacts[key]} | {final_contacts[key]}"
        
        # Add any keys from the final that are not in the base
        for key, value in final_contacts.items():
            if key not in merged_contacts.keys():
                merged_contacts[key] = final_contacts[key]
                
        return merged_contacts

    async def execute_listgen_pipeline(self, batch_size=1, max_urls_per_client=75, start_processing_status='', next_processing_status=''):   

        tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
        model = TFBertForTokenClassification.from_pretrained("dslim/bert-base-NER")
        
        # Get a new set of urls to scrape
        logger.log(message=f"\n\033[1;36m** Starting pipeline ")   
        scrape_dicts = await self.get_next_batch_of_targets(batch_size=batch_size, start_processing_status=start_processing_status)
    
        async def execute_pipeline(scrape_dict):
            if scrape_dict['notes'] is None:
                scrape_dict['notes'] = []
                
            logger.log(f"\n\033[1;36m** Starting pipeline for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
            # One search for executives
            scrape_dict = await self.search_for_executives(scrape_dict)
            scrape_dict['contacts'] = {}
            logger.log (f"\n\033[1;36m** Executives search complete for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
        
            if scrape_dict.get('urls', []) == []:
                return scrape_dict
            
            #! SCRAPE PIPELINE for NEW->SCRAPE1
            if start_processing_status == 'NEW':
                
                scrape_dict['urls']=[url for url in scrape_dict.get('urls', []) if url is not None and url != "" and self.is_valid_url(url)]
                
                site_address = scrape_dict.get('website_address', '')
                if site_address is not None and site_address != "":
                    scrape_dict['domain']= self.get_domain_name(site_address)
                else:
                    scrape_dict['domain'] = "NO.DOMAIN.FOUND"
                
                
                #! 1 Scrape the seed urls (this includes finding extended urls)
                logger.log(f"\n\033[1;36m** Starting seed url scrape for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                scrape_dict['priority_urls'] = await self.scrape_seed_urls(scrape_dict, next_processing_status=next_processing_status)
                logger.log(f"\n\033[1;36m** Seed url scrape complete for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                
                #! 2 Scrape the extended urls
                logger.log(f"\n\033[1;36m** Starting extended url scrape for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                # dskjgh
                # FIXME: I don'tthink this is working scrape_dict is not being returned correctly
                scrape_dict = await self.scrape_extended_urls(scrape_dict['priority_urls'], max_urls_per_client=max_urls_per_client)
                logger.log(f"\n\033[1;36m** Extended url scrape complete for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                
                #! 3 Extract all emails
                logger.log(f"\n\033[1;36m** Starting email extraction for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                emails = await self.extract_emails(scrape_dict)
                if emails and len(emails) > 0:
                    try: 
                        email_dict = json.loads(emails)
                        main_url = [u for u in scrape_dict.get('urls', '') if u is not None][0]
                        main_domain = tldextract.extract(main_url).domain   

                        emails_main = []
                        emails_other = []
                        for email in [e for e in email_dict.get('emails', []) if e is not None]:
                            if main_domain in email: emails_main.append(email)
                            else: emails_other.append(email)
                        emails_main.extend(emails_other)
            
                        scrape_dict['emails'] = emails_main
                        scrape_dict['emails_other'] = emails_other
                    except Exception as e:
                        error_message = f"Error extracting emails for {scrape_dict.get('primary_business_name', '')} with uniquebuskey {scrape_dict.get('uniquebuskey', '')}: {str(e)}"
                        # print the error and add it to the notes
                        logger.error(f"\033[1;31m{error_message}\033[0m")
                        scrape_dict['notes'].append({'type':'scrapelog', 'success': False, 'message': error_message})
                        return scrape_dict
                
                with open(f"scrapes/{scrape_dict.get('primary_business_name', '')}_.json", "w") as f:
                    f.write(json.dumps(scrape_dict))

                    
                # framework = await self.get_framework_from_gemini(scrape_dict,)
                # # Update the processing status
                scrape_dict['processingstatus'] = next_processing_status
            
                # # Update the database with the new scrape results
                upsert_result = await self.upsert_data([scrape_dict], table_name='targetlist', schema="public", column_name_of_current_record_key='uniquebuskey', new_processing_status=next_processing_status)
                print(f"\n\033[1;36m** Upsert result: {upsert_result} for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                
                return scrape_dict
        
        batch_tasks = [execute_pipeline(scrape_dict) for scrape_dict in scrape_dicts]
        await asyncio.gather(*batch_tasks)
            
            # except Exception as e:
            #     print(f"Error in pipeline: {str(e)} for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey','')}")
            #     continue
        return True
    
    async def get_jsonb_text_safely(self, scrape_dict, scrape_dict_key='bypage'):
        if scrape_dict.get(scrape_dict_key, []) is None or len(scrape_dict.get(scrape_dict_key, [])) == 0:
            scrape_dict[scrape_dict_key] = []
        
        def get_jsonb_text_value_safely(jsonb_text_value):
            bp_text =""
            if isinstance(jsonb_text_value, dict):
                for key, value in jsonb_text_value.items(): 
                    bp_text += f"{'-' * 30}\n{key}\n{value}\n\n"
                return bp_text
            count = 0
            while count<=10:
                try:
                    jsonb_text_value = json.loads(jsonb_text_value)
                    if isinstance(jsonb_text_value, dict):
                        for key, value in jsonb_text_value.items(): 
                            bp_text += f"{'-' * 30}\n{key}\n{value}\n\n"
                        return bp_text 
                    elif isinstance(jsonb_text_value, list):
                        bp_text += f"{"\n\n".join(jsonb_text_value)}\n\n"
                        return bp_text 
                    else: count+=1
                except: return f"{jsonb_text_value}"
            return f"{jsonb_text_value}"

        bypage_list = []
        for page in scrape_dict.get(scrape_dict_key, []):
            bypage_list.append(get_jsonb_text_value_safely(page))
        return bypage_list
    
    async def ollama_process_text_blocks(self, blocks, prompt, max_tokens=1500, model="nuextract"):
        def estimate_tokens(text):
            # Approximate tokens based on the average number of characters per 
            # token in English (which is about 4.5 characters per token)
            average_token_length = 4.5
            estimated_tokens =  len(text) / average_token_length
            return estimated_tokens

            return len(re.findall(r'\S+', text))  # Counting non-whitespace sequences as words
        def chunk_text(text, prompt, max_tokens=2000):
            prompt_tokens = estimate_tokens(prompt)
            text_tokens = estimate_tokens(text)
            
            if text_tokens + prompt_tokens <= max_tokens:
                return [text]
            
            chunks = []
            current_chunk = ""
            current_tokens = 0
            
            for paragraph in text.split('.  '):
                paragraph_tokens = estimate_tokens(paragraph)
                if current_tokens + paragraph_tokens + prompt_tokens <= max_tokens:
                    current_chunk += paragraph + "\n"
                    current_tokens += paragraph_tokens
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n"
                    current_tokens = paragraph_tokens
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks    
        def ask_ollama(chunk, prompt, model):

            output = ollama.generate(
                model=model,
                prompt=f"{prompt}\n\n {chunk}")
            return output['response']
        
        if not isinstance(blocks, list):
            blocks = [f"{blocks}"]
        
        results = []
        contact_list = []
        text_list = []
        empty_contacts = []
        for block in blocks:
            
            chunks = chunk_text(block, prompt, max_tokens)
            chunk_count=0
            for chunk in chunks:
                chunk_count+=1
                start_time = datetime.now()
                print(f"start time of {start_time} for {chunk_count} of {len(chunks)} with {estimate_tokens(chunk)} estimated tokens. ")
                response = ask_ollama(chunk, prompt, model)
                print(f"Processing time of {datetime.now()-start_time} for {chunk_count} of {len(chunks)}")
                if response : 
                    results.append(response)
            
            
            for result in results:
                try:
                    data = json.loads(result)
                    if isinstance(data, list):
                        for item in data:
                            if item.get('first and last name', '') != "" or item.get('email address', '') != "":
                                contact_list.append(item)
                            else:
                                empty_contacts.append(result)

                    else:
                        contact_list.append(data)
                    
                except:
                    if result and result.strip() != "" and result.strip() != "\n" and result.strip() != "[]" and result.strip() != "{}" and len(result.strip()) > 20:   
                        text_list.append(result)

        contact_list.append({"other_text": text_list, "empty_contacts": empty_contacts})
        
        with open(f"scrapes/text_blocks_{uuid.uuid4()}.json", "w") as f:
            f.write(json.dumps(contact_list))
        return contact_list
                    
    async def test_contact_extraction(self):
        test_folder_path = '/Users/michasmi/code/mytech/docker/ListGen/scrapes'
        test_file_list = ['moonsail', 'swancap', 'intrinsic', 'quic']
        for test_file in test_file_list:
            with open(f"{test_folder_path}/{test_file}.json", "r") as f:
                test_text = f.read()
                scrape_dict = json.loads(test_text)        
                blocks_list  = await self.get_jsonb_text_safely(scrape_dict, 'bypage')
                prompt = await self.get_contact_framework_prompt(scrape_dict)
                responses = await self.ollama_process_text_blocks(blocks_list, prompt=prompt, max_tokens=1750, model="nuextract")
                with open(f"scrapes/test_contact_extraction_{uuid.uuid4()}.json", "w") as f:
                    f.write(json.dumps(responses))
                pass
            
    async def get_contact_framework_prompt(self, scrape_dict):
        json_template = [
            {
            "Professional Profile": {
                "first and last name": "",
                "Company or Organization": scrape_dict.get('primary_business_name', ''),
                "email address": "",
                "professional title": "",
                "phone": ""
                }
            }
        ]
        
        json_example = [ {
            "Professional Person Profile": {
                "first and last name": "James Cameron",
                "Company or Organization": scrape_dict.get('primary_business_name', ''),
                "email address": "username@domain.com",
                "professional title": "CEO",
                "phone": "310.224.3333"
                }
            }
        ]
                    
        prompt = f"""
            ### Template:
            {json.dumps(json_template)}
            
            ### Example:
            {json.dumps(json_example)}
            
            ### Extraction Instructions:
            In the template provided, with no additional text or commentary, complete and return the 
            - first and last name, 
            - email address, 
            - professional title, 
            - and phone number 
            for each person and/or email address found in the text content provided who is
            associated with {scrape_dict.get('primary_business_name' '')}.
            If no contact data is found, return an empty list:  []
            Every record returned must have either or both "first and last name" or "email address" populated.
            Other data fields are optional
            
            ### Text: \n"""
        return prompt
            


if __name__ == "__main__":
    pass
    gen_contact = contact_generation_pipeline()        
    # results = asyncio.run(gen_contact.test_contact_extraction())

    run_adhoc = False if len(sys.argv) == 2 else True
    if run_adhoc:
        results = asyncio.run(gen_contact.execute_listgen_pipeline(batch_size=1, max_urls_per_client=75, start_processing_status='NEW', next_processing_status='SCRAPE1'),) 
    else:     
        results = asyncio.run(gen_contact.execute_listgen_pipeline(batch_size=1, max_urls_per_client=75, start_processing_status='NEW', next_processing_status='SCRAPE1'),)
    




