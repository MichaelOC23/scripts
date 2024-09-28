
# Standard Python libraries
import streamlit as st
import os
# if "role" not in st.session_state or st.session_state.role is None or os.environ.get("STREAMLIT_DEV_MODE", "FALSE") == "TRUE":
#     st.switch_page("login.py")

import toml
from pathlib import Path
import math
from collections import Counter
from datetime import datetime
import re
import tempfile
import uuid
import os
import base64
import asyncio
from datetime import date
from threading import Thread
import requests
import asyncpg
import json
import psycopg2 
import tldextract
# To analyze PDF layouts and extract text
# from cv2 import AGAST_FEATURE_DETECTOR_THRESHOLD, log
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
import PyPDF2

# To extract text from tables in PDF
# import pdfplumber
import pdfplumber

# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path

# To perform OCR to extract text from images 
import pytesseract 

# Data manipulation libraries
import pandas as pd
from sqlalchemy import create_engine
from decimal import Decimal



MODEL_DICT = {
            "Finance": "nlpaueb/sec-bert-base", 
            "General": "roberta-base",
            "ChatGPT-3.5": "gpt-3.5-turbo",
            "ChatGPT-4": "gpt-4-turbo",
            
            }


####################################
####       STREAMLIT CLASS      ####
####################################
class streamlit_mytech():
    def __init__(self, theme = 'cflight' ):
        themes = {
            'cflight':{
                'primary':'#003366',
                'background':'#FFFFFF',
                'sidebar':'#F0F2F6',
                'text':'#003366',
                'logo_url':'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/cfyd.png',
                'logo_icon_url': 'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/cficonlogo.png',
                'font': 'sans serif'
                },
            'cfdark':{
                'primary':'#98CCD0',
                'background':'#003366',
                'sidebar':'#404040',
                'text':'#CBD9DF',
                'logo_url':'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/cfyd.png',
                'logo_icon_url': 'https://devcommunifypublic.blob.core.windows.net/devcommunifynews/cficonlogo.png',
                'font': 'sans serif'
                },
            'otherdark':{}
            }
        
        
        self.model_dict = MODEL_DICT
        self.setup_database = False
        self.primary_color = themes.get(theme, {}).get('primary', '')
        self.background_color = themes.get(theme, {}).get('background', '')
        self.secondary_background_color = themes.get(theme, {}).get('sidebar', '')
        self.text_color = themes.get(theme, {}).get('text', '')
        self.font = themes.get(theme, {}).get('font', '')
        self.logo_url = themes.get(theme, {}).get('logo_url', '')
        self.logo_icon_url = themes.get(theme, {}).get('logo_icon_url', '')
        
        self.page_title = "New Page"
        
        self.home_dir = Path.home()
        self.home_config_file_path = f'{self.home_dir}/.streamlit/config.toml'
        self.working_config_file_path = f'.streamlit/config.toml'
        self.master_config_file_path = f'{self.home_dir}/code/scripts/.streamlit/master_streamlit_config.toml'

        self.set_theme()
    
    def set_theme(self):
        # Step 1: Load the existing config.toml file
        # use pathlib to get the directory of user's home directory
        
        
        if os.path.exists(self.master_config_file_path):
            with open(self.master_config_file_path, 'r') as file:
                config_data = toml.load(file)
        else:
            config_data = {}
        
        settings = [
            ["theme", "primaryColor", self.primary_color],
            ["theme", "backgroundColor", self.background_color],
            ["theme", "secondaryBackgroundColor", self.secondary_background_color],
            ["theme", "textColor", self.text_color],
            ["theme", "base", "light"],
            ["theme", "font", self.font],
        ]
        
        for setting in settings:
            if setting[0] not in config_data:
                config_data[setting[0]] = {}
            config_data[setting[0]][setting[1]] = setting[2]
    
        # Step 3: Write the changes back to the config.toml file
        with open(self.home_config_file_path, 'w') as file:
            toml.dump(config_data, file)    
        
        with open(self.working_config_file_path, 'w') as file:
            toml.dump(config_data, file)    
    
   
    def set_up_page(self, page_title_text=None, 
                    logo_url=None, 
                    session_state_variables=[], 
                    connect_to_dj=False, 
                    hideResultGridButton=False, initial_sidebar_state="expanded"):  
        
        
        def initialize_session_state_variable(variable_name, variable_value):
            if variable_name not in st.session_state:
                        st.session_state[variable_name] = variable_value
        
        # Page Title and Logo
        self.page_title = page_title_text if page_title_text is not None else self.page_title
        self.logo_url = logo_url if logo_url is not None else self.logo_url
            
            
        for variable in session_state_variables:
            if isinstance(variable, dict):
                for key in variable.keys():
                    initialize_session_state_variable(key, variable[key])
            
        st.set_page_config(
                page_title=self.page_title, page_icon=":earth_americas:", layout="wide", initial_sidebar_state=initial_sidebar_state,
                menu_items={'Get Help': 'mailto:michael@communify.com','Report a bug': 'mailto:michael@communify.com',})    
        
        self.set_theme()
        

        if connect_to_dj:
            initialize_session_state_variable("djsession", None)
            initialize_session_state_variable("djtoken", {})
            initialize_session_state_variable("djtoken_status_message", "") 
            initialize_session_state_variable("search_result_cache", "") 
            initialize_session_state_variable("viewed_article_cache", "") 
            initialize_session_state_variable("show_results", False)
            initialize_session_state_variable("show_article", False) 
            initialize_session_state_variable("chat_has_started", False)
            initialize_session_state_variable("show_search_results", False)
            initialize_session_state_variable("current_search_summary", "")

        # Standard Session state    
        initialize_session_state_variable("show_session_state", False)
        initialize_session_state_variable("DevModeState", False) 
        initialize_session_state_variable("settings", {"divider-color": "gray",})
        initialize_session_state_variable("model_type_value", MODEL_DICT["Finance"])
        initialize_session_state_variable("temperature", .1)
        
        # 
        st.logo(self.logo_icon_url, icon_image=self.logo_url)
        st.header(f"{self.page_title}",divider=True)
        
        




