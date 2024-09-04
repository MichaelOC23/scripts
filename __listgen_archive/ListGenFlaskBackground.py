
from flask import Flask, request, jsonify, redirect, url_for, session
from datetime import datetime

import torch
import ollama
import argparse
from openai import chat, OpenAI
from langchain_community.utilities import YouSearchAPIWrapper as YouRetriever

import asyncio
import openpyxl

import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urlparse, urljoin
import urllib.parse
import html2text
import requests
import tldextract
import time
import random

import psycopg2
import asyncpg
from psycopg2.extras import execute_values
import uuid
import chromadb

import json
import os
from googleapiclient.discovery import build

import hashlib
import setproctitle

import dotenv
dotenv.load_dotenv()

app = Flask(__name__)


def log_it(message, print_it=True, color='black'):
    is_dict, dict_value = got_dict(message)
    if is_dict:
        message = json.dumps(dict_value, indent=4)
    else:
        message = f"{message}"
        
    with open(os.path.join(log_directory, 'flask1.log'), 'a') as f:
        f.write(message)
        print(message)

async def async_scrape_single_url(url):
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
                log_it(f"Error: URL |{url}|is invalid: {str(e)}", color="RED")
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
                    
                    log_it(f"Successfully got full webpage for {url} with {len(body_text)} characters.")
                        
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
                    log_it(error_message, color="RED")
                    return {}
                
                finally:
                    await browser.close()
        except Exception as e:
            error_message = f"Error getting full webpage for {url}: {str(e)}"
            log_it(error_message, color="RED")
            print(error_message)
            return {}

def scrape_prospects_direct():
    data = request.json
    new_to_scrape = data.get('toscrape', [])
    new_scraped = data.get('scraped', [])

    with open("urls_to_scrape.json", "r") as f:
        data = json.load(f)
        to_scrape_list = data.get('toscrape', [])
        scraped_list = data.get('scraped', [])
        
        to_scrape_list = to_scrape_list.extend(new_to_scrape)
        scraped_list = scraped_list.extend(new_scraped)
        
        to_scrape_list = list(set(to_scrape_list))
        scraped_list = list(set(scraped_list))
        
        
        
    while len(to_scrape_list) > 0:
        max_count -= 1
        new_url = False
        while not new_url:
            url_to_scrape = to_scrape_list[0]
            if url_to_scrape in scraped_list:
                to_scrape_list.remove(url_to_scrape)
                print(f"Skipping: {url_to_scrape}")
            else:
                new_url = True
                print(f"Scraping: {url_to_scrape}")
            
        scraped_url_dict = asyncio.run(async_scrape_single_url(url_to_scrape))

        def mark_as_done(url1, url2):
            def remove_from_to_scrape(url):
                try:
                    to_scrape_list.remove(url)
                except:
                    pass
            def add_to_scraped(url):
                try:
                    scraped_list.append(url)
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
        
        # handle the case where the url was not scraped (bad url somehow)
        if scraped_url_dict == {}:
            mark_as_done(url_to_scrape, url_to_scrape)
            continue
        
        # Add found urls to the list to scrape
        to_scrape_list = list(set(to_scrape_list))
        
        for url in to_scrape_list:
            if url in scraped_list:
                to_scrape_list.remove(url)                

        mark_as_done(url_to_scrape, scraped_url_dict.get('url', ''))

        with open("urls_to_scrape.json", "w") as f:
            local_store = {"toscrape": to_scrape_list, "scraped": scraped_list} 
            f.write(json.dumps(local_store, indent=4))
        
        time.sleep(1)

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}".replace("channel_alternatives_","alt") if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, (dict, list)):
                    items.extend(flatten_dict({f"{i}": item}, new_key, sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
        
        flat_dict = dict(items)
        log_it(flat_dict)
    return flat_dict

@app.route('/isup', methods=['GET'])
def isup():
    return jsonify({"status": "SUCCESS! Background Flask is up and running"})

def got_dict(input_value):
    if isinstance(input_value, dict):
        return True, input_value
    try:
        type_value = type(input_value)
        input_value = json.loads(input_value)
    except Exception as e:
        return False, f"Type is: {type_value}.  Could not convert input to dictionary: {e}"
    
    
    
    return True, input_value


######################################
####      TEXT LIBRARY CLASS      ####
######################################
class TextLibrary():
    def __init__(self ):
        
        self.connection_string = 'postgresql://listgen:listgen@localhost:5432/listgen'
        self.unique_initialization_id = uuid.uuid4()
        self.textlibrary_table = "textlibrary"   
        self.table_def = {}
        self.table_names = [self.textlibrary_table]

    def get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        if self.table_def == {}:
            self.table_def = self.get_column_types_dict(conn, self.table_names)
        return conn

    def get_column_types_dict(self, conn, table_names):
        query = """
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_name = ANY(%s);
        """
        cursor = conn.cursor()
        cursor.execute(query, (table_names,))
        column_types = cursor.fetchall()
        
        # Organize the results in a dictionary
        column_types_by_table = {}
        for record in column_types:
            table_name = record[0]  # Adjusted to match tuple indexing
            column_name = record[1]  # Adjusted to match tuple indexing
            data_type = record[2]  # Adjusted to match tuple indexing
            
            if table_name not in column_types_by_table:
                column_types_by_table[table_name] = {}
            
            column_types_by_table[table_name][column_name]= data_type

        return column_types_by_table        
    
    def close_connection(self, conn, cursor):
        cursor.close()
        conn.close()

    def create_textlibrary(self, entity):
        conn = self.get_connection()
        cursor = conn.cursor()
        if not isinstance(entity, list): 
            entity = [entity]
        column_types = self.table_def[self.textlibrary_table]
        # You should ensure every key exists in the entity dict or handle it with defaults
        columns = sorted(entity[0].keys())  # Example sorting to maintain order
        values = [
            tuple(
                json.dumps(item.get(key, {})) if 'jsonb' in column_types.get(key.lower(), '')  # JSONB columns
                else '{' + ','.join(item.get(key, [])) + '}' if key in ['emails', 'names']  # array columns
                else item.get(key, None)  # regular columns
                for key in columns
            ) 
            for item in entity
        ]

        columns_string = ', '.join(columns)
        values_string = ', '.join(['%s'] * len(columns))
        query = f"INSERT INTO textlibrary ({columns_string}) VALUES ({values_string})"

        print(query)
        print("\n\n")
        print(values)
        
        
        try:
            execute_values(cursor, query, values)
            conn.commit()
        except Exception as e:
            print("Error: ", e)
            conn.rollback()
        finally:
            self.close_connection(conn, cursor)

    def read_textlibrary(self, entity_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM textlibrary WHERE id = %s"
        
        try:
            cursor.execute(query, (entity_id,))
            result = cursor.fetchall()
            print(result)
        except Exception as e:
            print("Error: ", e)
        finally:
            self.close_connection(conn, cursor)

    def update_textlibrary(self, entity_id, entity):
        conn = self.get_connection()
        cursor = conn.cursor()
        set_clause = ', '.join([f"{k} = %s" for k in entity.keys()])
        values = list(entity.values()) + [entity_id]
        query = f"UPDATE textlibrary SET {set_clause} WHERE id = %s"
        
        try:
            cursor.execute(query, values)
            conn.commit()
        except Exception as e:
            print("Error: ", e)
            conn.rollback()
        finally:
            self.close_connection(conn, cursor)

    def delete_textlibrary(self, entity_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        query = "DELETE FROM textlibrary WHERE id = %s"
        
        try:
            cursor.execute(query, (entity_id,))
            conn.commit()
        except Exception as e:
            print("Error: ", e)
            conn.rollback()
        finally:
            self.close_connection(conn, cursor)

    def update_textlibrary_append(self, entity_id, entity):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Separate handling for array and non-array fields
        set_clauses = []
        values = []
        for key, value in entity.items():
            if isinstance(value, list):  # Assuming the value to append is provided as a list
                if key.endswith('[]'):  # Array fields
                    set_clauses.append(f"{key} = array_cat({key}, %s)")
                else:  # JSONB array fields
                    set_clauses.append(f"{key} = {key} || %s")  # Concatenates JSONB arrays
            else:
                set_clauses.append(f"{key} = %s")
            values.append(value)

        values.append(entity_id)  # Add the ID to the list of values for the WHERE clause
        set_clause = ', '.join(set_clauses)
        query = f"UPDATE textlibrary SET {set_clause} WHERE id = %s"

        try:
            cursor.execute(query, values)
            conn.commit()
        except Exception as e:
            print("Error: ", e)
            conn.rollback()
        finally:
            self.close_connection(conn, cursor)

        
            
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
                            
        async def _create_test_data(self):
                    
            model_list = []
            entity_list = []
            attribute_list = []

            test_volume = 5
            

            for _ in range(test_volume):
                # Unique Key
                modelId = f"{uuid.uuid4()}"
                
                for _ in range(test_volume):
                    # Unique Key
                    entityId = f"{uuid.uuid4()}"
                    
                    for _ in range(test_volume):
                        # Unique Key
                        attributeId = f"{uuid.uuid4()}"
                        
                        #Nest all the constructed dictionaries
                        attribute_list.append({"partitionkey": entityId, "rowkey": attributeId, "structdata": {'attributename': attributeId, 'attributedescription': f"{uuid.uuid4()}",  'entitiId': entityId, 'id': attributeId}})
                    entity_list.append({"partitionkey": modelId, "rowkey": entityId, "structdata": {'entityname': entityId, 'entitydescription': f"{uuid.uuid4()}", 'modelid': modelId, 'id': entityId}})
                model_list.append({"partitionkey": "bmm_model", "rowkey": modelId, "structdata": {'modelname': modelId, 'modeldescription': f"{uuid.uuid4()}", 'id': modelId}})
            
            return model_list, entity_list, attribute_list
        
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
                    
    def create_prospect_entity(self, incoming_dict):
        textlibrary_template = {
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
        return textlibrary_template
        
        def load_prospects_from_csv(self):
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
        excel_dowloads = ['ia060524-exempt.xlsx', 'ia060524.xlsx']
        for excel_file in excel_dowloads:
            home_dir_of_current_user = os.path.expanduser("~")
            xls_path=os.path.join(home_dir_of_current_user, 'Downloads', excel_file)
            
            json_output = json.loads(excel_to_json(xls_path, "sheet"))
            json_path = os.path.join(home_dir_of_current_user, 'Downloads', excel_file.replace('.xlsx', '.json'))
            with open(json_path, 'w') as f:
                f.write(json.dumps(json_output, indent=4))

    def load_prospects_from_json(self):
        json_files = ['ia060524-exempt.json', 'ia060524.json']
        for json_file in json_files:
            home_dir_of_current_user = os.path.expanduser("~")
            json_path=os.path.join(home_dir_of_current_user, 'Downloads', json_file)
            
            with open(json_path, 'r') as f:
                data = json.loads(f.read())
            
            entities = []
            for row in data:
                entity = self.create_prospect_entity(row)
                entities.append(entity)
            for entity in entities:
                self.create_textlibrary(entity)
             

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
        
        self.max_depth = 5
        
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
                            
                        # return_dict["url"] = url
                        # return_dict["file_path"] = file_path
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

    def randomize_sleep_time(self, min_seconds=1, max_seconds=3):
         expanded = random.randint(min_seconds*1000, max_seconds*1000)
         return expanded / 1000
     
    def make_url_dict_key(self, url):
        # Define a regex pattern for unacceptable characters
        unsafe_chars_pattern = r'[^a-zA-Z0-9]'
        # Replace unsafe characters with underscore
        safe_url = re.sub(unsafe_chars_pattern, '_', url.strip())
        return safe_url
    
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
        
        
        if level <= max_depth:
            # Add the newly scraped urls to the scraped list
            # Do this first to avoid adding the same url to the toscrape list
            for newly_scraped_url in scraped:
                if newly_scraped_url not in scrape_dict['scraped']:
                    scrape_dict['scraped'].append(newly_scraped_url)
            
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
                    scrape_dict['scraped'].add(f"{url}/")
    
            
        return scrape_dict
        
    async def crawl_web_site_with_depth(self, url, max_depth=1, scrape_dict=None):

        # this function will create a new scrape_dict if one is not provided
        # after that it sues the provided scrape_dict to keep track of the urls to scrape and the urls 
        # that have been scraped or are toscrape.
        
        #!# This function can be called in a recursive/nested manner to scrape 
        #!  multiple levels of a website. Increment depth to navigate deeper
        scrape_dict = self.update_scrape_dict(scrape_dict=scrape_dict, toscrape=[url], level=0)
        still_more_to_scrape = True
        
        #! Recursive function to scrape the website begins here
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
            scraped_url_dict = await self.async_scrape_single_url(url_to_scrape)

            next_url_level = current_url_level + 1

            scraped_dict = self.update_scrape_dict(
                scrape_dict=scrape_dict, 
                toscrape=scraped_url_dict.get('found_urls', {}).get('same_domain', []), 
                level=next_url_level,
                max_depth=max_depth, 
                scraped=[url_to_scrape],
                body_text=scraped_url_dict.get('body_text', ''),
                body_html=scraped_url_dict.get('body', ''),
                domainurls=scraped_url_dict.get('found_urls', {}).get('same_domain', []), 
                externalurls=scraped_url_dict.get('found_urls', {}).get('diff_domain', [])
                # titles=[]], Gfd
                # names=None, 
                # emails=None, 
                # contacts=None
            )
            sleep_time = self.randomize_sleep_time()
            print(f"Scraped URL: {url_to_scrape} at level {current_url_level}. Total to scrape: {len(scrape_dict['toscrape'])}. Total scraped: {len(scrape_dict['scraped'])}. Sleeping for {sleep_time} seconds.")
            time.sleep(sleep_time)


##############################################
######    PROSPECT DATA PIPELINE     #########
##############################################
class prospect_data_pipeline:
    def __init__(self):
        self.log_folder = log_directory
        self.company =""
        self.location = ""
        self.CRD = ""
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
        self.titles_list = [
                # "Founder",
                # "Managing Partner",
                # "Chairman",
                # "Chief Executive Officer (CEO)"
                "Wealth Management CEO",
                "Head of Wealth Management",
                # "Head of Private Banking",
                # "Head of Client Services",
                # "Head of Client Relations",
                # "Head of Client Experience",
                # "Head of Client Engagement",
                # "Head of Client Success",
                # "Chief Investment Officer (CIO)",
                # "Chief Financial Officer (CFO)",
                # "President",
                # "Managing Director",
                # "Partner",
                # "Executive Vice President (EVP)",
                # "Chief Strategy Officer (CSO)",
                # "Regional Managing Director",
                "Principal"]
    
    def process_prospect_main(self, propsect_data):
        
        new_prospect_dict = asyncio.run(self.async_process_prospect(propsect_data))
        # asyncio.run(storage.add_update_or_delete_some_entities("prospects", [new_prospect_dict], alternate_connection_string=storage.jbi_connection_string))
    
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
    
    def get_domain(self, url):
        try: 
            parsed_url = urlparse(url)        
            domain_parts = parsed_url.netloc.split('.')
            domain = '.'.join(domain_parts[-2:]) if len(domain_parts) > 1 else parsed_url.netloc

            return domain
            
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
    
    # Enable override of default values for configuration options that are set in __init__
    def optional_config(self, log_folder=None, llm_model=None, llm_base_url=None, llm_model_api_key=None, embeddings_model=None, embeddings_base_url=None, embeddings_model_api_key=None, google_api_key=None, google_general_cx=None):
        if log_folder:
            self.log_folder = log_folder
        if llm_model:
            self.llm_model = llm_model
        if llm_base_url:
            self.llm_base_url = llm_base_url
        if llm_model_api_key:
            self.llm_model_api_key = llm_model_api_key
        if embeddings_model:
            self.embeddings_model = embeddings_model
        if embeddings_base_url:
            self.embeddings_base_url = embeddings_base_url
        if embeddings_model_api_key:
            self.embeddings_model_api_key = embeddings_model_api_key
        if google_api_key:
            self.google_api_key = google_api_key
        if google_general_cx:
            self.google_general_cx = google_general_cx
    
    async def async_process_prospect(self, propsect_data):
        
        def extract_N_urls_from_markdown(markdown, N=5):
            # Split the markdown into lines
            lines = markdown.split('\n')
            
            # Find lines that start with '### '
            h3_lines = [line for line in lines if line.startswith('### ')]
            
            # Regular expression to extract URLs from markdown links
            url_pattern = re.compile(r'\(https*://[^\s\)]+')
            
            # List to store the extracted URLs
            urls = []
            urls.append({"Type":"Markdown", "all-google-results": markdown})
            
            # Extract URLs from the first 5 H3 lines
            for line in h3_lines[:N]:
                # Find all URLs in the line
                found_urls = url_pattern.findall(line)
                # If a URL is found, clean it and add to the list
                if found_urls:
                    # Remove the opening parenthesis from the URL
                    clean_url = found_urls[0][1:]
                    clean_dict = {"Type":"google", "Link": clean_url}
                    urls.append(clean_dict)
            
            return urls
        
        def scrape_google_web(search_query):
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
                        # Configure options (optional)
                        h.ignore_links = False  # Ignore links 
                        h.ignore_images = True # Ignore images
                        h.body_width = 0  # Don't wrap lines

                        markdown_text = h.handle(body_html)
                        return markdown_text
                    else:
                        print("No body tag found.")
                else:
                    print(f"Failed to retrieve the page. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        def search_google_api(query):
            # Uses the configured (non image) CSE to search for results. Returns page 1
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            search_results = (service.cse().list(q=query,cx=f"{self.google_general_cx}",).execute())
            
            
            
            results = []
            for result in search_results.get('items', []):
                thumb_list = result.get('pagemap', {}).get('cse_thumbnail', [])
                image_list = result.get('pagemap', {}).get('cse_image', [])
                metatag_list = result.get('pagemap', {}).get('metatags', [])
                
                #Below is my view on prioritizing images and content
                primary_result_image = ""
                primary_site_image = ""
                for image in image_list:
                    if 'src' in image:
                        if self.is_valid_url(image.get('src', '')):
                            primary_result_image = image.get('src', '')
                            
                if primary_result_image == "":
                    for thumb in thumb_list:
                        if primary_result_image != "":
                            continue
                        else:
                            if 'src' in thumb:
                                if self.is_valid_url(thumb.get('src', '')):
                                    primary_result_image = thumb.get('src', '')
                                    
                
                if primary_result_image =="":
                    for meta in metatag_list:
                        if primary_result_image != "":
                            continue
                        else:
                            if 'og:image' in meta:
                                if self.is_valid_url(meta.get('og:image', '')):
                                    primary_result_image = meta.get('og:image', '')
                    
                if primary_site_image == "":
                    if result.get('link', '') != "":
                        base_url = self.get_base_url(result.get('link', ''))
                        if base_url != "":
                            primary_site_image = f"{base_url}/favicon.ico"
                    primary_site_image = f"https://www.google.com/s2/favicons?domain_url={self.get_domain(result.get('link', ''))}"
                    
                    if primary_site_image == "":                
                        for meta in metatag_list:
                            if primary_site_image != "":
                                continue
                            else:
                                if 'og:url' in meta:
                                    if self.is_valid_url(meta.get('og:url', '')):
                                        base_url = self.get_base_url(meta.get('og:url', ''))
                                        if base_url != "":
                                            primary_site_image = f"{base_url}/favicon.ico"
                
                
                result_dict = {
                    "Type" : "google",
                    "Query" : query,
                    "Site" : base_url,
                    "Summary" : result.get('htmlSnippet', result.get('snippet', '')),
                    "Page_Content": "",
                    "Link" : result.get('link', ''),
                    "Title": result.get('title', ''),
                    "primary_result_image" : primary_result_image,
                    "primary_site_image" : primary_site_image
                }
                
                results.append(result_dict)
            
            return results
            
        def search_you_rag_content_api(query):
            ydc_list = []
            # for doc in yr.get_relevant_documents(query):
            #     text_val = f"<strong>{doc.type}</strong>: {doc.page_content}"
            #     ydc_list.append(text_val)
            return ydc_list
        
        #! Step 1 in pipeline: Get the company and location #################################################################
        self.company = propsect_data.get('Legal_Name''')
        self.location = f"{propsect_data.get('Main_Office_City', '')}, {propsect_data.get('Main_Office_State', '')}"
        self.CRD = propsect_data.get('Organization_CRD', '')
        
        #! Step 2 in pipeline: Get all relevant search results #################################################################
        search_results = []
        for title in self.titles_list:
            
            search_query = f'person {title} at {self.company} in {self.location}?'
            
            #?---> Note: FREE SCRAPING (COSTS NO MONEY) (could be blocked by google)
            google_web_scrape_results = scrape_google_web(search_query)
            url_list = extract_N_urls_from_markdown(google_web_scrape_results)
            search_results.extend(url_list)
            

            #?---> Note: THESE TWO LINES OF CODE !WORK! (THEY JUST COST MONEY)
            # google_results = search_google_api(search_query)
            # search_results.extend(google_results)
            
            print(f"Successfully got google search results for query '{search_query}'")
            
            you_results = search_you_rag_content_api(search_query)
            search_results.extend(you_results)
            print(f"Successfully got you.com results for query '{search_query}'")
            
            with open(f"{self.CRD}{title}search_results.json", "w") as f:
                f.write(json.dumps(search_results, indent=4))
        
        #! Step 3 in pipeline: Scrape all search results #################################################################
        async def async_scrape_single_url(url):
            def extract_text_from_html(html_body):
                soup = BeautifulSoup(html_body, 'html.parser')
                return soup.get_text(separator=' ', strip=True)

            def is_a_valid_url(may_be_a_url):
                try:
                    result = urlparse(may_be_a_url)
                    return all([result.scheme, result.netloc])
                except ValueError:
                    return False
            
            if url == "" or not is_a_valid_url(url):
                return "Invalid or missing URL"
                
            
            else:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    try:
                        await page.goto(url)
                        await page.wait_for_selector('body')
                        body = await page.content()
                        body_text = extract_text_from_html(body)
                        
                        return body_text
                    
                    except Exception as e:
                        error_message = f"Error getting full webpage for {url}: {str(e)}"
                        return error_message
                    
                    finally:
                        await browser.close()
        
        search_results_for_llm = []
        for result in search_results:            
            if isinstance(result, dict):
                type = result.get('Type', '')   
                if type == 'google':
                    url = result.get('Link', '')
                    
                    # Check if the URL has already been scraped
                    url_key = self.generate_unique_key_for_url(url)
                    if url_key in self.scrape_session_history:
                        body_text = self.scrape_session_history[url_key]
                    else:
                        # Scrape the URL and store the result
                        body_text = await async_scrape_single_url(url)
                        
                        # Store the result in the session history
                        self.scrape_session_history[url_key] = body_text
                    
                    result['Page_Content'] = body_text
                    search_results_for_llm.append(result)
                    print(f"Successfully scraped {url}")
                    
                    
        
        #! Step 4 in pipeline: prepare embeddings #################################################################
        def prepare_text(data):
            
            # Flatten the JSON data into a single string
            text = json.dumps(data, ensure_ascii=False)
            
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
        
        #! Step 5 in pipeline: organize everything into a package #################################################################
        package = {}
        package['Prospect']= propsect_data
        package['Search_Results'] = search_results_for_llm
        package['Text_To_Embed'] = prepare_text(search_results_for_llm)
        
        #! Step 6 in pipeline: get the embeddings #################################################################
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Ollama Chat")
        parser.add_argument("--model", default=self.llm_model, help="Ollama model to use (default: llama3)")
        args = parser.parse_args()

        # Configuration for the Ollama API client
        client = OpenAI(
            base_url=self.llm_base_url,
            api_key=self.llm_model_api_key
        )

        # Generate embeddings for the vault content using Ollama
        vault_embeddings = []
        for content in package['Text_To_Embed']:
            response = ollama.embeddings(model=self.embeddings_model, prompt=content)
            vault_embeddings.append(response["embedding"])

        # Convert to tensor and print embeddings
        vault_embeddings_tensor = torch.tensor(vault_embeddings) 
        print(f"Successfully got embeddings for the vault content for {self.company}.")
        print("Embeddings for each line in the vault:")
        print(vault_embeddings_tensor)
        
        
        #! Step 7 in pipeline: get the prompt, get relevant embeddings and ask Ollama #################################################################
        
        def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
            if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
                return []
            # Encode the rewritten input
            input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
            
            # Compute cosine similarity between the input and vault embeddings
            cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
            
            # Adjust top_k if it's greater than the number of available scores
            top_k = min(top_k, len(cos_scores))
            
            # Sort the scores and get the top-k indices
            top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
            
            # Get the corresponding context from the vault
            relevant_context = [vault_content[idx].strip() for idx in top_indices]
            
            return relevant_context

           #! Step 7 in pipeline: get the prompt         
        
        # Function to interact with the Ollama model
        def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
           
            # Get relevant context from the vault
            relevant_context = get_relevant_context(user_input, vault_embeddings_tensor, vault_content, top_k=3)
            if relevant_context:
                # Convert list to a single string with newlines between items
                context_str = "\n".join(relevant_context)
                print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
            else:
                print(CYAN + "No relevant context found." + RESET_COLOR)
            
            # Prepare the user's input by concatenating it with the relevant context
            user_input_with_context = user_input
            if relevant_context:
                user_input_with_context = context_str + "\n\n" + user_input
            
            # Append the user's input to the conversation history
            conversation_history.append({"role": "user", "content": user_input_with_context})
            
            # Create a message history including the system message and the conversation history
            messages = [
                {"role": "system", "content": system_message},
                *conversation_history
            ]
            
            
            # Send the completion request to the Ollama model
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=messages
            )
            
            # Append the model's response to the conversation history
            conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
            
            # Return the content of the response from the model
            return response.choices[0].message.content
            
        def get_prompt(PersonTitle, Company):
            prompts = {"GetInfo": ''' {

                    "Instructions": [
                        "Below is an Example_JSON_Data_Record for a contact at a wealth management firm. Use the Example_JSON_Data_Record as a guide to populate the Empty_JSON_Data_Template with information about the person holding the RoleTitle specified in the Empty_JSON_Data_Template.",
                        "Use only the information provided with this prompt. Do not use any external sources. If you are not able to populate a value, leave it as an empty string.",
                        "Return only the Empty_JSON_Data_Template in your response. Do not return any other commentary or text. Your response is being systematically integrated and the assumption is that the Empty_JSON_Data_Template is the only output of your code.",
                        "Your response must be in valid JSON format beginning with: {\"Contact_JSON_Data\": {<The template you populate>} }"
                    ],
                    "Example_and_Template": {
                        "Example_JSON_Data_Record": {
                            "RoleTitle": "Chief Investment Officer (CIO)"
                            "PersonName": "John Doe",
                            "Company": "XYZ Wealth Management",
                            "Email": "John@xyzwealth.com",
                            "Phone": "555-555-5555",
                            "LinkedIn": "https://www.linkedin.com/in/johndoe",
                            "Background": "John Doe is the Chief Investment Officer at XYZ Wealth Management. He has over 20 years of experience in the financial services industry and specializes in investment management and portfolio construction. John holds a CFA designation and is a graduate of the University of ABC with a degree in Finance. He is passionate about helping clients achieve their financial goals and is committed to providing personalized investment solutions tailored to their needs.",
                            "PhotoURLs": ["https://www.xyzwealth.com/johndoe.jpg", "https://www.xyzwealth.com/johndoe2.jpg"],
                            "Location": "New York, NY",
                            "Interests": ["Cars", "Golf", "Travel"],
                            "OtherInfo": ["John is an avid golfer and enjoys spending time with his family and friends.", "He is also a car enthusiast and loves to travel to new destinations."]
                        },
                        
                        "Empty_JSON_Data_Template": {
                            "RoleTitle": " ''' + PersonTitle + ''' ",
                            "PersonName": "",
                            "Company": " ''' + Company + ''' ",
                            "Email": "",
                            "Phone": "",
                            "LinkedIn": "",
                            "Background": "",
                            "PhotoURLs": ["", ""],
                            "Location": "",
                            "Interests": ["", "", ""],
                            "OtherInfo": ["", "", ""]
                        }
                    }
                    }

                    Critical reminder: "Your response must be in valid JSON format beginning with: 
                    {
                        \"Contact_JSON_Data\": {<The populated template>}
                    }'''
                    
            }
            return prompts


            # @st.cache
        
        # ANSI escape codes for colors
        PINK = '\033[95m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        NEON_GREEN = '\033[92m'
        RESET_COLOR = '\033[0m'
        
        # Conversation loop
        conversation_history = []
        system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text."

        key_contacts  = []
        for title in self.titles_list:
            user_input = get_prompt(title, self.company)
            response = ollama_chat(user_input, system_message, vault_embeddings_tensor, package['Text_To_Embed'], args.model, conversation_history)
            print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
            key_contacts.append(response)
        
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
        package['Prospect'][key_contacts] = json.dumps(key_contacts)
        package['Prospect']['pipeline_version'] = "1"
        package['Prospect']['pipeline_as_of'] = current_date_time
        
        #! Step 8 in pipeline: return the package
        return package['Prospect']
            
@app.route('/prospectpipeline', methods=['POST'])
def process_pipeline_all_prospects():
    

    #! FIXME prospect_list = asyncio.run(storage.get_all_prospects())
    prospect_list = []
    print(f"Successfully got prospect list with count '{len(prospect_list)}'")
    
    pipeline = prospect_data_pipeline()
    
    for prospect in prospect_list:
        FIXME = pipeline.process_prospect_main(prospect)



# yr = YouRetriever()
scrape = _scrape()
tl = TextLibrary()



@app.route('/crawlurl', methods=['POST'])
def request_crawl_site_with_depth():

    raw_data = request.data.decode('utf-8')  # Decode the bytes to a string
    data = json.loads(raw_data)
    scrape_data = asyncio.run(scrape.crawl_web_site_with_depth(data.get('url', ''), data.get('max_depth', 2)))
    with open(f"scrape_temp_data.json", "w") as f:
        f.write(json.dumps(scrape_data, indent=4))
    
log_directory = "logs"
print_it = False
if not os.path.exists(log_directory): os.makedirs(log_directory)


if __name__ == "__main__":
    # Set the process title
    
    #activate the following line to transform the xls file to json for suspects
    # tl.transform_xls_to_json()
    tl.load_prospects_from_json()
    
    
    # download_nasdaq()
    setproctitle.setproctitle("ListGenFlaskBackground")    
    app.run(port=5000, debug=True)
    
    



