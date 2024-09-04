import requests
import os
import uuid
import asyncio
import asyncpg
import json
import re
from urllib.parse import urlparse, urljoin
from datetime import date, datetime
import time
import google.generativeai as genai
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
from _class_list_generation import contact_generation_pipeline as clg_class
clg = clg_class()

async def execute_listgen_pipeline(batch_size=1, max_urls_per_client=75, start_processing_status='', next_processing_status=''):   
    while True:
        
        try:
        
            # Get a new set of urls to scrape
            scrape_dicts = await self.get_next_batch_of_targets(batch_size=batch_size, start_processing_status=start_processing_status)
            
            for scrape_dict in scrape_dicts:
                try: 
                    if scrape_dict.get('urls', []) == []:
                        continue
                    
                    #! SCRAPE PIPELINE for NEW->SCRAPE1
                    if start_processing_status == 'NEW':
                        # Scrape the seed urls (this includes finding extended urls)
                        seed_scrape_dict = await self.scrape_seed_urls(scrape_dict, next_processing_status=next_processing_status)
                        
                        # Scrape the extended urls
                        new_scrape_dict = await self.scrape_extended_urls(seed_scrape_dict, max_urls_per_client=max_urls_per_client)
                        
                        # Update the processing status
                        new_scrape_dict['processingstatus'] = next_processing_status
                    
                        # Update the database with the new scrape results
                        upsert_result = await self.upsert_data([new_scrape_dict], table_name='targetlist', schema="public", column_name_of_current_record_key='uniquebuskey', new_processing_status=next_processing_status)
                        print(f"\n\033[1;36m** Upsert result: {upsert_result} for {new_scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {new_scrape_dict.get('uniquebuskey', 'NOKEY')}\033[0m")
                
                except Exception as e:
                    print(f"Error in pipeline: {str(e)} for {scrape_dict.get('primary_business_name', 'NO NAME')} with uniquebuskey {scrape_dict.get('uniquebuskey','')}")
                    continue
        except Exception as e:
            print(f"Error in pipeline: {str(e)}")
            continue