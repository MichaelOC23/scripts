"""Functions to connect and parse ArticleRetrieval JSON format"""

import json
import os
import streamlit as st
import requests
from datetime import datetime
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


def dj_authz_access_token_action(dj_token_Action="GET"):
    """
    Perform action on DJ authorization access token.

    Args:
        action (str): Action to perform on the token. Defaults to "GET".
                      Possible values are "GET", "SET", or "CLEAR".

    Returns:
        str: The result of the action performed on the token.
    """
    def request_token(client_id, password, username):
        url = "https://accounts.dowjones.com/oauth2/v1/token"

        payload = {
            "client_id": client_id,
            "connection": "service-account",
            "device": "orion-tablet",
            "grant_type": "password",
            "password": password,
            "scope": "openid service_account_id offline_access",
            "username": username
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        djlog(f"Response from request_token {response.text}")

        if response.ok:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"

    def request_jwt_token(authn_id_token, client_id):
        url = "https://accounts.dowjones.com/oauth2/v1/token"

        payload = {
            "assertion": authn_id_token,
            "client_id": client_id,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "scope": "openid pib"
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        djlog(f"Response from request_jwt_token {response.text}")
        if response.ok:
            return response.text
        else:
            return f"Error: {response.status_code} - {response.text}"

    def refresh_authz_access_token():
        # This function orchestrates tryingt to use the stored token, but, if it's not there, get a new one.
        # Ideally we could validate it in this fucntion, but I'm not clear that's possible without adding overhead and slowing the calls.
        # Usage example (replace with actual credentials):

        client_id = os.environ.get('DOW_JONES_CLIENT_ID')
        password = os.environ.get('DOW_JONES_PASSWORD')
        username = os.environ.get('DOW_JONES_USER_NAME')

        response_text = request_token(client_id, password, username)

        authn_id_token = json.loads(response_text)['id_token']

        jwt_response = request_jwt_token(authn_id_token, client_id)

        authz_access_token = json.loads(jwt_response)['access_token']

        djlog(f"authz token {authz_access_token}", 'AUTHZ_ACCESS_TOKEN')
        return authz_access_token

    if dj_token_Action == "GET":
        djlog(f"Getting the authz access token")
        if os.environ.get('DJ_AUTHZ_ACCESS_TOKEN'):
            return os.environ.get('DJ_AUTHZ_ACCESS_TOKEN')
        else:
            return dj_authz_access_token_action("SET")
    elif dj_token_Action == "SET":
        djlog(f"Creating a new authz access token")
        os.environ['DJ_AUTHZ_ACCESS_TOKEN'] = refresh_authz_access_token()
        djlog(
            f"authz token {os.environ['DJ_AUTHZ_ACCESS_TOKEN']}", 'AUTHZ_ACCESS_TOKEN')
        return os.environ['DJ_AUTHZ_ACCESS_TOKEN']

    else:
        djlog(f"Clearing the authz access token")
        os.environ.pop('DJ_AUTHZ_ACCESS_TOKEN', None)


def search_content(search_string='p/pmdm', search_date_range="Last30Days", from_date=None, to_date=None, page_offset=0, page_limit=10, is_return_headline_coding=True, is_return_djn_headline_coding=True):
    url = "https://api.dowjones.com/content/realtime/search"

    token = dj_authz_access_token_action("GET")

    headers = {
        "accept": "application/vnd.dowjones.dna.content.v_1.0+json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    if search_date_range is not None and search_date_range == "SpecificDateRange":
        from_date = from_date.strftime("%Y-%m-%d")
        to_date = to_date.strftime("%Y-%m-%d")
        date_key_value = [{"custom": {"from": from_date, "to": to_date}}]
    else:
        date_key_value = {"days_range": search_date_range}

    payload = {
        "data": {
            "id": "Search",
            "type": "content",
            "attributes": {
                "query": {
                    "search_string": [
                        {
                            "mode": "Unified",
                            "value": "Joe Biden"

                            # "value": f"djn={search_string.lower()}"
                        }
                    ],
                    # "date": date_key_value
                },
                "formatting": {
                    "is_return_rich_article_id": True
                    # },
                    # "navigation": {
                    #     "is_return_headline_coding": is_return_headline_coding,
                    #     "is_return_djn_headline_coding": is_return_djn_headline_coding
                },
                "page_offset": page_offset,
                "page_limit": page_limit
            }
        }
    }

    with open(f'{DOWJONES_IO_FOLDER_PATH}/djlog_search_payload_{run_uid}.json', 'w') as f:
        f.write(json.dumps(payload, indent=4))

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if 'payload' not in st.session_state:
        st.session_state['payload'] = json.dumps(payload)
    else:
        st.session_state.payload = json.dumps(payload)

    uid = UNIQUE_DATE_TIME_STRING()

    if response.ok:
        djlog(response.text, f"search_result_{uid}")
        return response.text
    elif response.status_code == 401:
        dj_authz_access_token_action("CLEAR")
        return search_content(search_string=search_string, search_date_range=search_date_range, from_date=from_date, to_date=to_date, page_offset=page_offset, page_limit=page_limit, is_return_headline_coding=is_return_headline_coding, is_return_djn_headline_coding=is_return_djn_headline_coding)
    else:
        djlog(response.text, f"search_result_{uid}")
        error_message = f"Error: {response.status_code} - {response.text}"
        print(error_message)


def get_content_item(content_id):

    url = f"https://api.dowjones.com/content/{content_id}"

    token = dj_authz_access_token_action("GET")

    headers = {
        "accept": "application/vnd.dowjones.dna+json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    time.sleep(4)

    # djlog(response.text, f"dj_content_dict_{content_id}")

    if response.ok:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"


def extract_txt(txt_dict) -> str:
    hl_part = ''

    if isinstance(txt_dict, dict):
        if 'content' in txt_dict.keys():
            subcontent = txt_dict['content']
            if isinstance(subcontent, dict):
                return extract_txt(subcontent)
            elif isinstance(subcontent, list):
                for content_item in subcontent:
                    hl_part += extract_txt(content_item)
                return hl_part
            return ''
        elif 'text' in txt_dict.keys():
            return txt_dict['text']

    elif isinstance(txt_dict, list):
        for p_item in txt_dict:
            hl_part += extract_txt(p_item)
        return hl_part

    return hl_part


def extract_headline(headline_dict: dict) -> str:
    headline = ''
    if isinstance(headline_dict, dict):
        hkeys = headline_dict.keys()
        for key in hkeys:
            if key == 'main':
                headline += headline_dict['main']['text']
            elif key == 'content':
                txt_list = headline_dict['content']
                for txt_item in txt_list:
                    headline += extract_txt(txt_item)

    return headline


def extract_body(body_dict: dict, format='txt') -> str:
    if not 'content' in body_dict.keys():
        raise ValueError('Unexpected dict structure')

    content = '\n'
    p_list = body_dict['content']

    for p_item in p_list:
        if format == 'html':
            content += "\n<p style='content'>"
        content += extract_txt(p_item)
        if format == 'html':
            content += '</p>\n'
        elif format == 'txt':
            content += '\n\n'
    return content


def format_content_item(content_dict, format='TEXT'):
    """
    Format the content item based on the specified format.

    Args:
        content_dict (dict): The content item dictionary.
        format (str, optional): The format to use for formatting the content item.
            Possible values are 'JSON', 'TEXT', or 'HTML'. Defaults to 'TEXT'.

    Returns:
        str: The formatted content item.
    """

    if not 'headline' in content_dict.keys():
        raise ValueError('Unexpected dict structure')

    headline = extract_headline(content_dict['headline'])
    body = extract_body(content_dict['body'], format)

    return f"{headline}\n\n{body}"


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


def extract_article(article_dict: dict):
    """
    Extract the article from the article dictionary.

    Args:
        article_dict (dict): The article dictionary.

    Returns:
        Article: The extracted article.
    """
    def get_id(article_dict: dict) -> str:
        try:
            return article_dict['data']['id']
        except:
            log_extraction_error('id', article_dict)

    def get_headline(article_dict: dict) -> str:
        try:
            return extract_headline(article_dict['data']['attributes']['headline'])
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
                return sources[0].get('name', "Source: None")
            else:
                return "Source: None"
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


def get_category_taxonomy(category=None, endpoint=None, child_endpoint_suffix="", language="en", request_attempt=1):
    # API endpoint

    url = f"https://api.dowjones.com{endpoint}{child_endpoint_suffix}?language={language}"
    print(url)

    token = dj_authz_access_token_action("GET")

    # Headers
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # Making the GET request
    response = requests.get(url, headers=headers)
    time.sleep(4)

    uid = UNIQUE_DATE_TIME_STRING()

    if response.ok:
        # Token is valid, response is good.
        return response.json()
    elif response.status_code == 401:
        # Token Expired
        dj_authz_access_token_action("CLEAR")
        return search_content(category=category, endpoint=endpoint, child_endpoint_suffix=child_endpoint_suffix, language=language)
    elif response.status_code == 500:
        break_time = 0
        retry_message = ""
        if request_attempt == 1 and "does not have any children" not in response.text:
            break_time = 10
            retry_message = f"Taking a {break_time} second break from API Calls as code 500 was returned.  Attempt {request_attempt} of 2. For category {category}"
            # Take a break from API Calls
            time.sleep(break_time)
            request_attempt += 1
            return get_category_taxonomy(category=category, endpoint=endpoint, child_endpoint_suffix=child_endpoint_suffix, language=language, request_attempt=request_attempt)
        else:
            return f"\n\n >>>>> Error: {retry_message} | >>>>>>> {response.status_code} - {response.text} \n\n"
    else:
        # Error
        djlog(response.text, f"get_taxonomy_result_{uid}")
        error_message = f"\n\n ^^^^^Error: {response.status_code} - {response.text}\n\n"

        return error_message


def get_sub_category_taxonomy(sub_category=None, endpoint=None, language="en"):
    # Using this wrapper so that the code is more readable ..... getting categories and sub-categrories is the same thing
    return get_category_taxonomy(category=sub_category, endpoint=endpoint, child_endpoint_suffix=f"/{sub_category}/children", language=language)


if __name__ == "__main__":

    # Get the official "Category" taxonomy. This is the top level categories published by Dow Jones structured from the top down.
    # I made this document from the official taxonomy list published by Dow Jones.
    # It's a JSON file that I created from the official taxonomy list.  It does not change at all really so safe to rely on it.
    with open(f'{DOWJONES_IO_FOLDER_PATH}/official-taxonomy/dj_official_taxonomy.json', 'r') as f:
        official_taxonomy_str = f.read()
    official_category_taxonomy_dict = json.loads(official_taxonomy_str)

    # The entire taxonomy cannot be downloaded. It must be obtained by category.
    # This sequence will create the entire taxonomy by category and save it to a JSON file.
    complete_dj_taxonomy_dict = {}

    # The DJID Taxonomy API uses categories as dimensions to classify its content. Some categories compliment others.
    # For example, the Industries category is part of the classifying dimensions for the Companies category.
    # see https://developer.dowjones.com/site/docs/factiva_apis/factiva_workflow_apis_rest/factiva_news_search/factiva_djid_taxonomy_api/index.gsp#currToc
    for category_key in official_category_taxonomy_dict.keys():
        with open(f'{DOWJONES_IO_FOLDER_PATH}/complete_category_taxonomy_{run_uid}.json', 'w') as f:
            f.write(json.dumps(complete_dj_taxonomy_dict, indent=4))

        if official_category_taxonomy_dict[category_key].get("endpoint"):
            # If true, this category has sub-categories:
            # We need to get the sub-categories and add them to the complete taxonomy
            # As of the time this code was writte, the Categories are as follows:
            # Author    (NO sub-categories)     (Only searchable, CANNOT download the entire list)  (Handled differently)
            # Company   (NO sub-categories)     (Only searchable, CANNOT download the entire list)  (Handled differently)
            # |-----|
            # Language  (NO sub-categories)     (CAN download the entire list)
            # |-----|
            # Industry  (HAS sub-categories)    (CAN download the entire list)
            # Subject   (HAS sub-categories)    (CAN download the entire list)
            # Region    (HAS sub-categories)    (CAN download the entire list)
            # |-----|
            # Source    (HAS sub-categories)    (CANNOT download the entire list)

            category_taxonomy_dict = get_category_taxonomy(
                category=category_key, endpoint=official_category_taxonomy_dict[category_key].get("endpoint"))

            with open(f'{DOWJONES_IO_FOLDER_PATH}/category_taxonomy_{category_key}.json', 'w') as f:
                f.write(json.dumps(category_taxonomy_dict, indent=4))

             # Add the category to the complete taxonomy
            complete_dj_taxonomy_dict[category_key] = {}
            attribute_dictionary_name = official_category_taxonomy_dict[category_key].get(
                "category").replace("factiva-", "")

            if isinstance(category_taxonomy_dict.get('data'), list):
                # the below supports language and sets category_data_items to be a list of dicts
                category_data_items = category_taxonomy_dict.get('data')
            else:
                if isinstance(category_taxonomy_dict.get('data'), dict):

                    # The below supports industry and sets category_data_items to be a list of dicts
                    category_data_items = category_taxonomy_dict.get('data').get(
                        "attributes").get(attribute_dictionary_name)

            for category_data_item in category_data_items:
                if category_data_item is not None:
                    if category_data_item.get('code'):
                        complete_dj_taxonomy_dict[category_key][category_data_item.get(
                            'code')] = category_data_item
                    elif category_data_item.get('id'):
                        complete_dj_taxonomy_dict[category_key][category_data_item.get(
                            'id')] = category_data_item

            # complete_dj_taxonomy_dict should now be fully populated for the first level of categories.
            # Which is: Language, Industry, Subject, Region
            # Language is entirely complete. The others have sub-categories and which are handled next.

            if official_category_taxonomy_dict[category_key].get("children"):
                # Industry  (HAS sub-categories)    (CAN download the entire list)
                # Subject   (HAS sub-categories)    (CAN download the entire list)
                # Region    (HAS sub-categories)    (CAN download the entire list)

                # Note: Source has children but a full list cannot be downloaded so it is not handled here.
                # Source    (HAS sub-categories)    (CANNOT download the entire list)

                sub_category_connection_dict = official_category_taxonomy_dict[category_key].get(
                    "children")

                for sub_category_key in category_taxonomy_dict.get("data"):
                    # Note: Below get_sub_category_taxonomy is a modifying wrapper for get_category_taxonomy
                    with open(f'{DOWJONES_IO_FOLDER_PATH}/sub_category_log_{run_uid}.text', 'a') as f:
                        f.write(
                            f"Beginning attempt to get sub-category {sub_category_key.get('id','MISSING')} for category {category_key}.\n")
                    sub_category_taxonomy_dict = get_sub_category_taxonomy(
                        sub_category=sub_category_key.get("id", ""), endpoint=official_category_taxonomy_dict[category_key].get("endpoint"))

                    if isinstance(sub_category_taxonomy_dict, str):
                        # If the sub-category is not a list, it's an error message
                        print(sub_category_taxonomy_dict)
                        with open(f'{DOWJONES_IO_FOLDER_PATH}/sub_category_log_{run_uid}.text', 'a') as f:
                            f.write(sub_category_taxonomy_dict)
                    else:
                        # Save the sub-category to a JSON file
                        with open(f'{DOWJONES_IO_FOLDER_PATH}/category_taxonomy_{category_key}_{sub_category_key.get("id","MISSING")}.json', 'w') as f:
                            f.write(json.dumps(
                                sub_category_taxonomy_dict, indent=4))

                        # Add the subcategories whichis delivered as a list to the complete taxonomy
                        for sub_category_data_item in sub_category_taxonomy_dict.get("data"):
                            complete_dj_taxonomy_dict[category_key][sub_category_key.get(
                                "id", "")] = sub_category_data_item

                        with open(f'{DOWJONES_IO_FOLDER_PATH}/sub_category_log_{run_uid}.text', 'a') as f:
                            f.write(
                                f"Successfully completed attempt to get sub-category {sub_category_key.get('id','MISSING')} for category {category_key}.\n")

            # End of Sub-Category Logic:

        else:
            # Code to handle:
            # Author    (NO sub-categories)     (Only searchable, cannot download the entire list)  (Handled differently)
            # Company   (NO sub-categories)     (Only searchable, cannot download the entire list)  (Handled differently)
            # Source    (HAS sub-categories)    (CANNOT download the entire list)
            print(f'{category_key} is handled at run time and not in this loop.')


    # def _get_sub_category_taxonomy(self, category="",  language="en"):
    #     #getting the endpoint for the list for the passed in category
    #     endpoint = self.official_taxonomy_dict[category].get('endpoint', "")
    #     self.all_children[category]={}
    #     sub_cat_number = -1
    #     for sub_category_key in self.complete_taxonomy_dict[category]['data']['attributes'].keys():
    #         sub_cat_number += 1
    #         list_of_sub_categories = self.complete_taxonomy_dict[category].get('data', {}).get('attributes', {}).get(sub_category_key, [])
    #         for sub_category_dict in list_of_sub_categories:
    #             if sub_category_dict['has_children']:
    #                 sub_category = sub_category_dict['code']
    #                 self.add_log_entry(f"Getting children for {category}.{sub_category}")
    #                 children_dict = self._get_category_taxonomy(category=sub_category, endpoint=endpoint, child_endpoint_suffix=f"/{sub_category}/children", language=language)
    #                 if 'error' in json.dumps(children_dict).lower():
    #                     self.add_log_entry(f"Error: {category}.{sub_category} - {json.dumps(children_dict)}", 'ERROR')
    #                 self.complete_taxonomy_dict[category].get('data', {}).get('attributes', {}).get(sub_category_key, [])[sub_cat_number]['children'] = children_dict['data']
    #                 children = {}
                    
    #                 for child in children_dict['data']:
    #                     children[child['id']] = child
    #                 self.all_children[category].update(children)
    #                 with open(f'{COMPLETE_TAXONOMY_SUB_PATH}', 'w') as f:
    #                     f.write(json.dumps(self.complete_taxonomy_dict, indent=4))
    #                 with open(f'{CHILDREN_TAXONOMY_SUB_PATH}', 'w') as f:
    #                     f.write(json.dumps(self.all_children, indent=4))
    #             else:
    #                 self.add_log_entry(f"No children for {category}.{sub_category_dict['code']}")
                    
    #     return True
