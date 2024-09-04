

import os
from sqlalchemy import true
import streamlit as st
import sys
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)
import functions_constants as con
import numpy as np
import pandas as pd
import json
current_directory = os.getcwd()
st.set_page_config(layout="wide")




# from openai import OpenAI
# # Now you can import your custom modules
# import _record_audio as audio
# import _process_audio as process_audio
# import _extract_pdf_text as extract
# import _ask_llm as ask_llm
# import _correct_grammar as correct_grammar
# import _stablediffusion as sd

study_areas = ['Marketing', 'Sales', 'Customers', 'Staff', 'Product', 'Services', 'Financial & Business Model', 'Investors', 'Founders & Executive Shareholders', 'Management']


def display_message_in_sidebar(message="Default Message"):
    st.sidebar.write(message)

title_container = st.container()
with title_container:
    st.title('Structured Notes')
    

project_container = st.container(border=True)
content_category_container = st.container(border=True)
# with open('example.json', 'r') as f:
#     data = f.read()
#     f.close()
#     json_data = json.loads(data)

with project_container:
    project_container.subheader("Project Container")
    project_selectbox = st.selectbox('Project', ['EmergeGen','Capital Preferences','Cognito'])
    project_type = st.selectbox('Content Type', ['JBI Study','General Notes','JBI Data Study'])
    select_project_button = st.button("Select Project")
    if select_project_button:
        st.write("You selected", project_selectbox)
        with content_category_container:
            content_category_container.subheader("Content Category Container")
            content_category_selectbox = st.selectbox('Content Category', ['JBI Study','General Notes','JBI Data Study'])
            select_content_category_button = st.button("Select Content Category")
            if select_content_category_button:
                st.write("You selected", content_category_selectbox)
    
    
    new_project_button = st.button("Create Project")
    if new_project_button:
        project_name = st.text_input("Enter a project name")

