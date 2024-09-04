"""Functions to connect and parse ArticleRetrieval JSON format"""

import json
import os
import streamlit as st
import requests
from datetime import datetime
import pages.dow_jones_service.class_dow_jones as dj
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
        return get_category_taxonomy(category=category, endpoint=endpoint, child_endpoint_suffix=child_endpoint_suffix, language=language)
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
