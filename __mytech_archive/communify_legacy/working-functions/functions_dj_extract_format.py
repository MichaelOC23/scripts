"""Functions to connect and parse ArticleRetrieval JSON format"""

import json
import os
import streamlit as st
import requests
from datetime import datetime
import sys
sys.path.append('/Users/michasmi/code/communify/shared')
# from typing import List, Optional
# from pydantic import BaseModel
# import functions_constants as constants
import time

WAIT_TIME = 4


def UNIQUE_DATE_TIME_STRING():
    # note this is unique to the second i.e. per run
    return datetime.now().strftime("%Y%m%d.%H%M%S")


def try_to_get_dict(text):
    try:
        return json.loads(text)
    except:
        return text


run_uid = UNIQUE_DATE_TIME_STRING()

DOWJONES_IO_FOLDER_PATH = os.environ.get('DOWJONES_IO_FOLDER_PATH')


def djlog(text, key=None):
    print(text)
    # text = try_to_get_dict(text)

    # if key is not None and isinstance(text, dict):
    #     print(text)
    #     # with open(f'{DOWJONES_IO_FOLDER_PATH}/djlog_{key}_{run_uid}.json', 'a') as f:
    #     #     json.dump(text, f, indent=4)
    # else:


def extract_search_result(search_result: dict) -> list:
    """
    Extract the search result from the search result dictionary.

    Args:
        search_result (dict): The search result dictionary.

    Returns:
        list: The extracted search result.
    """

    def extract_headline(search_result: dict) -> str:
        try:
            headline = search_result['attributes']['headline']['main']['text']
            headline = f"### {headline}"
            return headline
        except:
            return "### BREAKING NEWS"

    def extract_snippet(search_result: dict) -> str:
        try:
            snippet_list = search_result['attributes']['snippet']['content']
            djlog(f"{snippet_list}", 'SNIPPET_LIST')
            snippet = ""

            for snip in snippet_list:
                snippet = f"{snippet} {snip['text']}"
            formatted_snippet = f"> {snippet}"
            print(formatted_snippet)
            return formatted_snippet
        except:
            return "> More to come..."

    formatted_result = []
    formatted_headline = extract_headline(search_result)
    formatted_snippet = extract_snippet(search_result)
    formatted_result.append(formatted_headline)
    formatted_result.append(formatted_snippet)
    return formatted_result


def extract_article(article_dict: dict):
    """
    Extract the article from the article dictionary.

    Args:
        article_dict (dict): The article dictionary.

    Returns:
        Article: The extracted article.
    """
    def log_extraction_error(field, article_dict):
        error_dict = {}
        error_dict['field_with_error'] = field
        error_dict['article_dict'] = article_dict
        extraction_error_log_file_path = f'{DOWJONES_IO_FOLDER_PATH}/djlog_extraction_error_{run_uid}.json'
        if os.path.exists(extraction_error_log_file_path):

            with open(extraction_error_log_file_path, 'r+') as f:
                error_list = [f.read()]
                error_list.append(error_dict)
                json.dump(error_dict, f, indent=4)
        else:
            with open(extraction_error_log_file_path, 'w') as f:
                f.write(json.dumps([error_dict], indent=4))
        error_string = f"Error extracting {field} from article_dict"
        return error_string

    def get_id(article_dict: dict) -> str:
        try:
            return article_dict['data']['id']
        except:
            log_extraction_error('id', article_dict)

    def get_headline(article_dict: dict) -> str:
        try:
            # FIX THE BELOW .... probably an error
            return article_dict['data']['attributes']['headline'].values()
        except:
            log_extraction_error('headline', article_dict)

    def get_link(article_dict: dict) -> str:
        try:
            return article_dict['data']['links']['self']
        except:
            log_extraction_error('links.self', article_dict)

    def get_source_name(article_dict: dict) -> str:
        try:
            # Navigate through the dictionary safely
            sources = article_dict.get('data', [{}]).get(
                'attributes', {}).get('sources', [])
            if sources:
                return sources[0].get('name', "No Source Name")
            else:
                return "No Source Name"
        except Exception as e:
            log_extraction_error('source_name', article_dict)
            return "None"

    def get_publication_date(article_dict: dict) -> str:
        try:
            return article_dict['data']['attributes']['publication_date']
        except:
            log_extraction_error('publication_date', article_dict)

    def get_metadata(article_dict: dict) -> dict:
        try:
            return article_dict['data']['meta']
        except:
            log_extraction_error('metadata', article_dict)

    def handle_text_item(item):
        return item['text']

    def handle_link_item(item):
        return f"[{item['text']}]({item['uri']})" if item.get('link_type') == 'EXTERNAL' else item['text']

    def handle_entity_item(item):
        # Format based on entity type; simple example given here
        return f"{item['text']} ({item['entity_type']})"

    def handle_emphasis_item(item):
        emphasis_format = {
            'Bold': '**{}**',
            'Italic': '*{}*',
            'Strikethrough': '~~{}~~',
            'Superscript': '^{}^',
            'Subscript': '~{}~',
            'Underline': '<u>{}</u>',  # Markdown does not support underline; using HTML
            # Markdown does not have a highlight; using code format as a placeholder
            'Highlight': '`{}`'
        }

    def format_emphasis(content):
        if isinstance(content, str):
            return content

    def handle_content_item(item):
        item_type = item.get('type')
        if item_type == 'text':
            return handle_text_item(item)
        elif item_type == 'link':
            return handle_link_item(item)
        elif item_type == 'entity':
            return handle_entity_item(item)
        elif item_type == 'emphasis':
            return handle_emphasis_item(item)
        elif item_type == 'paragraph':
            return handle_paragraph_item(item)
        else:
            return ''

    def handle_paragraph_item(item):
        def process_paragraph_content(paragraph):
            paragraph_content = []
            # Check if the paragraph contains 'content' or 'text'
            if 'content' in paragraph:
                for content_item in paragraph.get('content', []):
                    paragraph_content.append(handle_content_item(content_item))
            elif 'text' in paragraph:
                paragraph_content.append(paragraph['text'])
            return paragraph_content

        paragraph_content = process_paragraph_content(item)
        return '\n'.join(paragraph_content)

    def handle_content(content):
        return ''.join(handle_content_item(c) for c in content)

    article_id = get_id(article_dict)
    headline = get_headline(article_dict)
    link = get_link(article_dict)
    source_name = get_source_name(article_dict)
    publication_date = get_publication_date(article_dict)
    metadata = get_metadata(article_dict)
    content = handle_content(
        article_dict['data']['attributes']['body']['content'])

    return {
        'id': article_id,
        'headline': headline,
        'link': link,
        'source_name': source_name,
        'publication_date': publication_date,
        'metadata': metadata,
        'content': content
    }
    
def extract_doc_id(sr_data_item: dict) -> str:
    try:
        doc_id = sr_data_item.get('id', '')
        return doc_id
    except:
        return "<no id>"
def extract_sr_headline(sr_data_item: dict) -> str:
    try:
        main_headline_dict = sr_data_item.get(
            'attributes', '').get('headline', '').get('main', '')
        if isinstance(main_headline_dict, dict):
            headline = " ".join(main_headline_dict.values())
        elif isinstance(main_headline_dict, str):
            headline_list = [main_headline_dict]
            headline = " ".join(headline_list)
        return headline
    except:
        return "BREAKING NEWS"
    
def format_search_results(search_result: dict) -> str:
    formatted_list = [
    f"""
    #### {extract_sr_headline(search_result)}
    > {extract_doc_id(search_result).replace(':', '::')}    
    """
    ]
    
    markdown_formatted_search_result = "\n".join(formatted_list)
    return markdown_formatted_search_result

if __name__ == "__main__":
    import os
    import streamlit as st
    import json
    from datetime import datetime
    import functions_common as oc2c

    oc2c.configure_streamlit_page(
        Title="Dow Jones: Search Result Extraction and Markdown Formatting ")
    
    DOWJONES_IO_FOLDER_PATH = os.environ.get('DOWJONES_IO_FOLDER_PATH')

    with open('search_result.json', 'r') as f:
        sr_text = f.read()
        sr_dict = json.loads(sr_text)
        sr_data_list = sr_dict['data']

    result_count = len(sr_data_list)-1
    
    col1, col2 = st.columns([1.5,2.75])
    
    col1.header("Raw Results", divider="gray")
    col2.header("Formatted Results", divider="gray")
    
    i=0
    for sr_data_list_item in sr_data_list:
        i=i+1
        ### COL1 ###
        col1.write(sr_data_list_item)
        # st.write(sr_data_list[i]['attributes']['headline']['main'])
        col1.divider()
        
        ### COL2 ###
        colimg, col2a, col2b = col2.columns([.5,5,.5])
        formatted_sr = format_search_results(sr_data_list_item)
        col2a.markdown(formatted_sr,)
        col2b.button(f"Read", key=f"{sr_data_list_item['id']}_{i}")
        col2.divider()
        
