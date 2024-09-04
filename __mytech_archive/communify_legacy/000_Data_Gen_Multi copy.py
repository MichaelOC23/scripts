
# import streamlit as st
import os
import json
import csv
from queue import Empty
import random
import pandas as pd
from multiprocessing import Pool, cpu_count
from bs4 import BeautifulSoup
import requests
import spacy
from datetime import datetime, date, timedelta
from playwright.async_api import async_playwright

import time
from sympy import sec
from titlecase import titlecase
import shutil
import zipfile
from io import StringIO
from setuptools import sic
import nasdaqdatalink 
import asyncio
import aiohttp
import tldextract
from urllib.parse import urlparse, urljoin

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Ensure the directory "logs" is created off of the workng directory



def log_it(message, print_it=True, color='black'):
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
        
    with open(os.path.join(log_directory, 'flask1.log'), 'a') as f:
        f.write(message)
        print(message)

PositionToChaseMapping = {
    "BaseCurrencyDayChangeUnrealizedFXAccruedIncomeGainLoss": "Today's Value Change",
    "BaseCurrencyDayCostBasis": "Cost",
    "BaseCurrencyDayEndAccruedDividendIncome": "Accrued Income",
    "BaseCurrencyDayEndPriceDate": "Pricing Date",
    "BaseCurrencyDayEndUnrealizedPriceGainLoss": "Unrealized G/L Amt.",
    "BaseCurrencyEndMarketValue": "Value",
    "BaseCurrencyOriginalUnitCost": "Unit Cost",
    "BaseCurrencyYTDRealizedDividendIncome": "Accrued/Income Earned",
    "HasStalePrice": "PriceInd",
    "LocalCurrencyCode": "Local CCY",
    "LocalCurrencyDayEndUnrealizedPriceGainLoss": "Local Unrealized G/L Amt.",
    "LocalCurrencyEndMarketValue": "Local Value",
    "LocalCurrencyEndPrice": "Local Price",
    "LocalCurrencyOriginalUnitCost": "Local Unit Cost",
    "MarketPrice": "Price",
    "OtherSecurityStrategyLevel1": "Asset Strategy",
    "OtherSecurityStrategyLevel2": "Asset Strategy Detail",
    "SymCusip": "CUSIP",
    "SymTicker": "Ticker",
    "UnitsHeld": "Quantity"
}

SecMappingToNasdaq = {
    "AssetClassLevel1":"category",
    "GICSSector": "sector",
    "SICCode": "siccode",
    "SICIndustryTitle": "industry",
    "InvestmentType": "category",
    "CompanyWebsiteURL": "companysite",
    "CurrencyCode": "currency",
    "SymCusip": "cusips",
    "Exchange": "exchange",
    "OtherIndustryLevel2": "sicindustry",
    "OtherSectorLevel3": "sicsector",
    "InceptionDate": "firstadded",
    "NasdaqEarliestPriceDate": "firstpricedate",
    "NasdaqEarliestFinancialQuarter": "firstquarter",
    "IsDelisted": "isdelisted",
    "NasdaqMostRecentPriceDate": "lastpricedate",
    "NasdaqLatestFinancialQuarter": "lastquarter",
    "CountryOfIssuance": "location",
    "SecurityLegalName": "name",
    "SymNasdaqPermanentTicker": "permaticker",
    "RelatedTickers": "relatedtickers",
    "SECFilingURLs": "secfilings",
    "SymTicker": "ticker"
    }


def entity_csv_to_dict(csv_file_path, key_field='AttributeName'):
        result_dict = {}
        with open(csv_file_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            print(reader.fieldnames)
            for row in reader:
                # Assuming 'AttributeName' is the name of the column to be used as the key
                key = row.pop(key_field)
                result_dict[key] = row
        return result_dict


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

def fetch_sec_url_once(url):
        headers = {
            'User-Agent': 'JustBuildIt admin@justbuildit.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
            }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Failed to fetch URL with status code {response.status_code}")

#############################
#####     CONSTANTS     #####
#############################

UNIQUE_DATE_KEY = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Investment Account Numbers (Excludes Private Asset Accounts)
ACCOUNT_LIST = ["218550733086", "705625596201", "937914441711", "134367817996", "538776741796", "6953450", "999244", "6958039", "1003833", "6962628", "1008422"]


NASDAQ_TABLES = ['SF1', 'SFP', 'DAILY', 'TICKERS', 'INDICATORS', 'METRICS', 'ACTIONS', 'SP500', 'EVENTS', 'SF3', 'SF3A', 'SF3B', 'SEP']

#User's home directory
HOME = os.path.expanduser("~")
DATA = f"{HOME}/code/data"
ARCHIVE = f"{DATA}/archive"
log_directory = 'logs'

if not os.path.exists(DATA): os.makedirs(DATA)
if not os.path.exists(f"{ARCHIVE}"): os.makedirs(f"{ARCHIVE}")
if not os.path.exists(log_directory): os.makedirs('logs')

# Set the file locations
positions_chase_path = f"{DATA}/positions-chase.csv"
securitymaster_nasdaq_path = f"{DATA}/TICKERS.csv"

company_description_path = f"{DATA}/ticker_desc_list.json"
company_description_dictionary_path = f"{DATA}/ticker_desc_dictionary.json"

securitymaster_entity_path = f"{DATA}/SecurityMasterEntity.csv"
position_entity_path = f"{DATA}/PositionEntity.csv"

sic_code_file_path = f"{DATA}/sic_industry_codes.json"

stock_to_price = "MSFT"
GetPriceForOneStock = False  

GetNewSECTickerFile = False
GetNewSICIndustryFile= False
RebuildCompanyDescriptionDict = False
GetNewNasdaqFiles = False
BuildSecurityMasterData = True
BuildPositionData = False


if GetPriceForOneStock:
    
    nasdaqdatalink.ApiConfig.api_key = "6X82a45M1zJPu2ci4TJP"
    prices = nasdaqdatalink.get_table('SHARADAR/SEP', ticker=stock_to_price, paginate=True)
    with open(f"{DATA}/{stock_to_price}.csv", "w") as f:
        f.write(prices.to_csv())


#!################################################
#!############    SEC Ticker File    #############
#!################################################
def get_listed_ticker():

    url = "https://www.sec.gov/files/company_tickers.json"

    response = fetch_sec_url_once(url)
    data_dict = response.json()
    # Save the data to a file
    with open(f"{DATA}/company_tickers.json", "w") as f:
        json.dump(data_dict, f, indent=4)
    
    # Process the titles in the data dictionary
    
    def process_titles(data):
        def custom_titlecase(text):
            # Define a dictionary of exceptions for specific terms
            
            exceptions = {
                "INC": "Inc.",
                "LLC": "LLC",
                "LLP": "LLP",
                "PLC": "PLC",
                "CORP": "Corp",
                "CO": "Co",
                "LTD": "Ltd",
                "N.V.": "N.V.",
                "S.A.": "S.A.",
                "AG": "AG",
                "S.P.A.": "S.p.A."
            }
            # Convert the title to title case using the titlecase library
            title_cased = titlecase(text)

            # Replace exceptions with correct capitalization
            for term, replacement in exceptions.items():
                title_cased = title_cased.replace(term.title(), replacement)
            
            return title_cased
        
        for key, value in data.items():
            title = value.get('title', '')
            if title.isupper() or title.islower():  # Also handle titles that are all lowercase
                value['title'] = custom_titlecase(title)
        return data
         
    data = process_titles(data_dict)
    return data

if GetNewSECTickerFile:
    
    # Get the current SEC ticker data
    sec_ticker_dict = get_listed_ticker()
    if not sec_ticker_dict:
        print("Failed to retrieve the SEC ticker data")
    #Archive the old file
    if os.path.exists(f"{DATA}/sec_tickers.json"):
        shutil.copy(f"{DATA}/sec_tickers.json", f"{DATA}/archive/sec_tickers{UNIQUE_DATE_KEY}.json")
    
    # Save the new file to the data folder
    with open(f"{DATA}/sec_tickers.json", "w") as f:
        json.dump(sec_ticker_dict, f, indent=4)
else:
    # Use the existing SEC ticker data
    with open(f"{DATA}/sec_tickers.json", "r") as f:
        sec_ticker_dict = json.load(f)

#!##################################################
#!############    SIC Industry File    #############
#!##################################################
def get_sic_table():
    def clean_sic_dict(sic_dict):
        for key in sic_dict.keys():
            sic_dict[key]['Office'] = sic_dict[key]['Office'].replace('Office of', '').strip()
            sic_dict[key]['Office'] = sic_dict[key]['Office'].replace('and Services', '').strip()
            sic_dict[key]['Office'] = sic_dict[key]['Office'].replace('and Services', '').title()
            
            sic_dict[key]['Industry Title'] = sic_dict[key]['Industry Title'].replace('SERVICES-', '').strip()
            sic_dict[key]['Industry Title'] = sic_dict[key]['Industry Title'].replace('RETAIL-', '').strip()
            sic_dict[key]['Industry Title'] = sic_dict[key]['Industry Title'].replace('WHOLESALE-', '').strip()
            sic_dict[key]['Industry Title'] = sic_dict[key]['Industry Title'].replace('WHOLESALE-', '').title()
        
        return sic_dict
    
    # Define the URL
    url = 'https://www.sec.gov/corpfin/division-of-corporation-finance-standard-industrial-classification-sic-code-list'
    
    response = fetch_sec_url_once(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table
    table = soup.find('table', class_='list')
    
    # Extract table headers
    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
    
    # Extract table rows
    rows = []
    for tr in table.find('tbody').find_all('tr'):
        cells = [td.text.strip() for td in tr.find_all('td')]
        rows.append(cells)
    
    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)
    
    # Convert DataFrame to dictionary with formatted keys
    sic_dict = {
        f"{int(row['SIC Code']):04d}": {
            "Office": row["Office"],
            "Industry Title": row["Industry Title"]
        }
        for _, row in df.iterrows()
    }
    # Trim the Office and Industry values to remove unnecessary repetition
    sic_dict_4digit = clean_sic_dict(sic_dict)
    
    # Create a dictionary with 2-digit SIC codes to get approximate industry categories when
    # the 4-digit SIC code is not in the dictionary
    sic_dict_2digit = {}
    for key in sic_dict_4digit.keys():
        d2key = f"{key[:2]}"
        sic_dict_2digit[d2key] = sic_dict_4digit.get(key, {})
    
    sic_dict = { "TWO_DIGIT": sic_dict_2digit, "FOUR_DIGIT": sic_dict_4digit}


    
    return sic_dict



if GetNewSICIndustryFile:
    # Get the current SIC industry codes
    sic_dict = get_sic_table()
    
    if not sic_dict:
        print("Failed to retrieve the SIC industry codes")

    # Archive the old file
    if os.path.exists(f"{DATA}/sic_industry_codes.json"): 
        shutil.copy(f"{DATA}/sic_industry_codes.json", f"{DATA}/archive/sic_industry_codes{UNIQUE_DATE_KEY}.json")
    
    # Save the new file to the data folder
    with open(sic_code_file_path, "w") as f:
        json.dump(sic_dict, f, indent = 4)
else:
    # Use the existing SIC industry codes
    with open(f"{DATA}/sic_industry_codes.json", "r") as f:
        sic_dict = json.load(f)

#!###############################################################
#!############    Company Description Dict Build    #############
#!###############################################################

if RebuildCompanyDescriptionDict:
    def get_company_description():
        with open(company_description_path, "r") as f:
            desc_list_dict = json.loads(f.read())
            desc_dict = {}
            duplicate_tickers = set()
            dup_data = []
            for sec_data in desc_list_dict.get('data', []):
                desc_dict[sec_data.get('ticker', "")] = sec_data.get('description', "")
            with open(company_description_dictionary_path, "w") as f:
                f.write(json.dumps(desc_dict, indent=4))
        return desc_dict
    RebuildCompanyDescriptionDict = get_company_description()

#!########################################
#!###    NASDAQ DOWNLOAD FUNCTIONS    ####
#!########################################
if GetNewNasdaqFiles:
      
    # format a dat 14 days ago in YYYY-MM-DD format
    date_14_days_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')

    async def download_file(session, url, destination):
           
        """
        Asynchronous function to download a file from a URL.
        """
        start_time = time.time()
        print(f"Starting download of {destination} at {start_time}")
        async with session.get(url) as response:
            # Ensure the response is successful
            response.raise_for_status()
            
            # Write the content to a destination file
            with open(destination, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)  # Read chunks of 1KB
                    if not chunk:
                        break
                    f.write(chunk)
            # if the file is a zip file, extract it
            if destination.endswith('.zip'):
                with zipfile.ZipFile(destination, 'r') as zip_ref:
                    filenames = zip_ref.extractall(DATA)
                os.remove(destination)
            print(f"Completed download of {destination} in {time.time() - start_time} seconds")
        
    async def dowload_list_of_files_async(download_status):
        
        waiting_on = []
        download_next_list = []
        # Create a session and download files concurrently
        
        async with aiohttp.ClientSession() as session:

            for file in download_status:
                if 'downloaded' not in file or 'file.status' not in file:
                    continue
                if file["downloaded"] == 0 and file['file.status'] == "fresh":
                    download_next_list.append(download_file(session, file["file.link"], f"{DATA}/{file['name']}.zip"))
                    file["downloaded"] == 1
                elif file["downloaded"] == 1:
                    continue
                else:
                    waiting_on.append(file)
                    
            await asyncio.gather(*download_next_list)
            
            return download_status, waiting_on

    def download_nasdaq():

        print("Beginning download of NASDAQ files")
        
        print("Getting status of NASDAQ files")
        download_list = []
    
        def create_download_item(table):
            url = f"https://data.nasdaq.com/api/v3/datatables/SHARADAR/{table}.csv?qopts.export=true&api_key=6X82a45M1zJPu2ci4TJP"
            response = requests.get(url)
            status_dict = {}
            status_dict["name"] = table
            status_dict["status"] = response.status_code
            status_dict["link"] = url
            status_dict["downloaded"] = 0
            if response.status_code == 200:
                reader = csv.DictReader(StringIO(response.text))
                for row in reader:
                    for column_name in reader.fieldnames:
                        status_dict[column_name] = row[column_name]
                return status_dict
            else:
                status_dict["status"] = "Failed"
                status_dict["error"] = response.text
                print(Exception(f"ERROR ... Failed to get a download link for table {table}: {response.text}"))
                return None
    
    
        for table in NASDAQ_TABLES: 
            item = create_download_item(table)
            if item is not None:
                download_list.append(item)
        
        print("Beginning download of files that are ready")

        download_list, waiting_on = asyncio.run(dowload_list_of_files_async(download_list))
        while len(waiting_on) > 0:
            download_list, waiting_on = asyncio.run(dowload_list_of_files_async(download_list))
            print(f"Still waiting on: waiting_on {waiting_on}")
            time.sleep(5)

    def rename_files():
        for csvfile in os.listdir(DATA):
            if csvfile.endswith('.csv'):
                if "SHARADAR" in csvfile:
                    for filecode in NASDAQ_TABLES:
                        if filecode in csvfile:
                            current_name = os.path.join(DATA, csvfile)
                            new_name = os.path.join(DATA, f"{filecode}.csv")
                            os.rename(current_name, new_name)
                            time.sleep(1)
                            
    download_nasdaq()   

    rename_files()






# # #?#######################################################
# # #!############    SECURITY MASTER BUILD    ##############
# # #?#######################################################
        
# if BuildSecurityMasterData:

#     #!  ------>  Get all the data sources to process  <------  !#

#     #! SEC Offically Published Ticker Lust
#     # Open the file that contains the SEC's Offical Ticker List and turn it into a dictionary with the keys being the
#     # Ticker and the values being the row. Note that this file has been pre-processed above
#     with open(f"{DATA}/sec_tickers.json", 'r') as f:
#         sec_ticker_dict = json.load(f)
    
    
#     #!SECURITYMASTER ENTITY
#     # Open the SecurityMasterEntity.csv file and turn it into a dictionary with the keys being the AttributeName
#     # and empty values
#     SecurityMasterEnitty = entity_csv_to_dict(securitymaster_entity_path)
#     for key in SecurityMasterEnitty.keys():
#         SecurityMasterEnitty[key] = ""
    
#     #!NASDAQ
#     # format a dat 14 days ago in YYYY-MM-DD format
#     date_14_days_ago = (datetime.now() - timedelta(days=14))
    
#     # Open the TICKER.csv file (Nasdaq) and iterate through the rows. 
#     # Securities that are old and no longer priced do not need to be included in the SecurityMaster
#     # for current positions.
#     nasdaq_dict = {}
#     with open(securitymaster_nasdaq_path, 'r') as f:
#         reader = csv.DictReader(f)
#         for row in reader:
#             last_price_date_str = row.get('lastpricedate', "")
#             if last_price_date_str != "":
#                 last_price_date = datetime.strptime(last_price_date_str, "%Y-%m-%d")
#                 # if the timedelta is greater than 14 days ago, skip the row
#                 if last_price_date < date_14_days_ago:
#                     continue
#             ticker = row.get('ticker', "")
#             nasdaq_dict[ticker] = row
    
#     #! Yahoo Finance Company Descriptions
#     # Open the company_description_dictionary.json file and turn it into a dictionary with the keys being the ticker
#     # The CompanyDescription is the value needed here
#     with open(company_description_path, 'r') as f:
#         company_desc_dict = json.load(f)
    
    
    
    
    # #!  ------>  Process the Data  <------  !#
        
    # # The FullSecurityMaster dictionary will be a dictionary where each key's value is a SecurityMasterEntity
    # # The key is the ticker (temporarily) and needs to be our definition of a unique security
    # FullSecurityMaster = {}
    
    # # Iterate through the SEC Ticker List and create 
    # # a SecurityMasterEntity for each ticker
    # for key in sec_ticker_dict.keys():
    #     # Empty Entity
    #     SME = SecurityMasterEnitty.copy()
        
    #     # Get the ticker to match the NASDAQ data
    #     ticker_str = sec_ticker_dict.get(key, {}).get('ticker', "NO-TICKER-FOUND")
        
    #     # Utilize the mapping dict to map the Nasdaq data to the SecurityMasterEntity
    #     for mapped_field in SecMappingToNasdaq.keys():
    #         SME[mapped_field] = nasdaq_dict.get(ticker_str, {}).get(SecMappingToNasdaq[mapped_field], "")
        
    #     # Override the Nasdaw data with the SEC data
    #     SME['SymTicker'] = ticker_str
    #     SME['CIK'] = sec_ticker_dict.get(key, {}).get('cik_str', "")
    #     SME['SecurityLegalName'] = sec_ticker_dict.get(key, {}).get('title', "")
        
    #     #Yahoo Finance Data
    #     SME['CompanyDescription'] = company_desc_dict.get(ticker_str, "")
        
        
        
        
    #     #! FIXME:  Currently, for test data, we are using the ticker as the unique identifier.  
    #     #! This will need to be changed 
    #     #! Note: this is the SEC's ticker and not the Nasdaq ticker so accuracy and completeness is as good as it gets
    #     FullSecurityMaster[ticker_str] = SME
        
        

        
    
    # with open(f'{DATA}/SecurityMasterToLoad.csv', mode='w', encoding='utf-8', newline='', errors='replace') as f:

    #     # All of the SecurityMasterEntities have the same keys, 
    #     # so we can use the first one to get the fieldnames for the field names ( ie column headers)
    #     first_key = list(FullSecurityMaster.keys())[0]
    #     field_names = FullSecurityMaster[first_key].keys()
        
    #     # Create a DictWriter object
    #     writer = csv.DictWriter(f, fieldnames=field_names)
        
    #     # Write the header
    #     writer.writeheader()
        
    #     # Write the data
    #     for key in FullSecurityMaster.keys():
    #         writer.writerow(FullSecurityMaster[key])
    
    







# if BuildPositionData:
    
#     PositionEntityDefinition = entity_csv_to_dict(position_entity_path)

#     # Preparation: Read in the Chase positions data and convert it to a list of dictionaries
    
#     # Get the source position data to load
#     with open(positions_chase_path, 'r') as f:
#         reader = csv.DictReader(f)
#         positions_chase_dict = list(reader)
    
#     # Create and empty PositionEntity dictionary to populate with the source data
#     # Add/modify fields as needed to match the PositionEntity. Ignore fields that
#     # that will not be mapped to the PositionEntity
#     EmptyPositionEntity ={}
#     for key in PositionEntityDefinition.keys():
#         if key in PositionToChaseMapping.keys():
#             EmptyPositionEntity[key] = ""
#         if key in SecMappingToNasdaq.keys():
#             EmptyPositionEntity[key] = ""
#         EmptyPositionEntity['SICOffice'] = ""
#         EmptyPositionEntity['SICCode'] = ""
#         EmptyPositionEntity['ExternalSystemKeyCustody'] = ""

#     # Get the mapping of the PositionEntity Attributes to the Chase positions data
#     posmap = PositionToChaseMapping
    
#     # Function to merge chase data
#     def merge_chase_data(row):
#         position = EmptyPositionEntity.copy()
#         ticker = row.get("Ticker", "")
        
#         security_row = nasdaq_dict.get(ticker, {})
#         # security_row = {}
#         # for security in nasdaq_dict.keys():
#         #     if nasdaq_dict[security].get('ticker', "") == ticker:
#         #         security_row = security
#         #         break
                
#         for key in position.keys():
#             mapped_chase_field = posmap.get(key, "")
#             if mapped_chase_field:
#                 position[key] = row.get(mapped_chase_field, "")
            
#             sec_key_map = SecMappingToNasdaq.get(key, "")
#             if sec_key_map != "":
#                 position[key] = security_row.get(sec_key_map, "")
            
#         if position['SICCode'] != "":
#             office_code = f"{position['SICCode']}"[0] + "000"
#             position['SICOffice'] = sic_dict.get(office_code, {}).get("Office", "")
            
            
#         random.shuffle(ACCOUNT_LIST)
#         position['ExternalSystemKeyCustody'] = ACCOUNT_LIST[0]

#         return position

    # Use multiprocessing to process the data in parallel
    
        
def run_all_concurrently():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_get_listed_ticker = executor.submit(get_listed_ticker)
        future_get_sic_table = executor.submit(get_sic_table)
        future_get_company_description = executor.submit(get_company_description)
        future_get_nasdaq_data = executor.submit(get_nasdaq_data)
        
        listed_ticker = future_get_listed_ticker.result()
        sic_table = future_get_sic_table.result()
        company_description = future_get_company_description.result()
        nasdaq_data = future_get_nasdaq_data.result()

if __name__ == "__main__":
    run_all_concurrently()
        
        
        
        
        print(f"cpu_count: {cpu_count()}")
        with Pool(cpu_count()) as pool:
            Position_List_Master = pool.map(merge_chase_data, positions_chase_dict)

            # Write the data to a csv file
        with open(f'{DATA}/PositionsToLoad.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(EmptyPositionEntity.keys())
            for position in Position_List_Master:
                writer.writerow(position.values())


    






