import re
import os
import streamlit as st
import json
from datetime import datetime

import pages.dow_jones_service.class_dow_jones as dj

import shared.functions_common as oc2c

oc2c.configure_streamlit_page(Title="Dow Jones Realtime News")

DOWJONES_IO_FOLDER_PATH = os.environ.get('DOWJONES_IO_FOLDER_PATH')

# st.set_page_config(layout="wide")
st.header('Dow Jones Realtime News ', divider='orange')

auth_z_token = dj._dj_authz_access_token_action("GET")

with st.expander('Authorization (AuthZ) Token'):
    st.write(auth_z_token)

st.subheader('Search Content', divider='gray')

custom_date_from = None
custom_date_to = None


def on_date_range_change():
    if date_days_range is not None and date_days_range == "SpecificDateRange":
        custom_date_from.date_input("Custom Date From", value=datetime.now())
        custom_date_to.date_input("Custom Date To", value=datetime.now()-30)


s_col1, s_col2, s_col3, s_col4, s_col5 = st.columns(
    [2, 1, 1, 1, 1], gap="medium")
with s_col1:
    search_string = st.text_input('Search String', 'djn=p/pmdm')
    search_string_mode = "Unified"  # Fixed value, no need for user input
    search_string_value = st.text_area("Search String Value", height=100)

with s_col2:
    date_days_range = st.radio(f'Simple Date Range', ('LastDay', 'LastWeek', 'LastMonth', 'Last3Months', 'Last6Months',
                               'LastYear', 'Last2Years', 'Last5Years', 'AllDates', "SpecificDateRange"), on_change=on_date_range_change)
    custom_date_from = st.empty()
    custom_date_to = st.empty()
with s_col3:
    return_type = st.radio(
        "Return Type", ('Search Only', 'Search and Retrieve Article'))
with s_col4:
    page_limit = st.number_input(
        "Search Limit", min_value=1, max_value=100, value=3)
st.divider()

if st.button("Search", use_container_width=True, type="secondary"):

    search_results = dj.search(search_string=search_string, search_date_range=date_days_range,
                                          page_limit=page_limit, from_date=custom_date_from, to_date=custom_date_to)
    if 'dj_search_results' not in st.session_state:
        st.session_state['dj_search_results'] = search_results
    else:
        st.session_state.dj_search_results = search_results

    st.subheader('Search Header and Response', divider='gray')
    header1, header2 = st.columns(2)
    with header1:
        with st.expander('Search Request Header', expanded=False):
            st.write(json.loads(st.session_state.payload))
    with header2:
        with st.expander('Search Results', expanded=False):
            st.write(search_results)

    st.subheader('Search Results', divider='gray')

    # col1, col2, col3 = st.columns([1,1,3])

if 'dj_search_results' in st.session_state and isinstance(st.session_state.dj_search_results, dict):
    count = 0
    for search_result_item in st.session_state.dj_search_results['data']:
        count += 1
        if return_type == 'Search Only':
            # Just search .... not retrieving the article yet
            formatted_search_result_item = dj.extract_search_result(
                search_result_item)
            st.write(formatted_search_result_item)
        else:
            # Search and Retrieve Article
            article_dict = dj.get_content_item(search_result_item['id'])
            clean_article_id = re.sub(r'\W+', '', search_result_item["id"])

            if article_dict is None or article_dict == "" or not isinstance(article_dict, dict):
                # something is wrong with the Article. caputre the error and move on
                article_dict = f"Error obtaining content for {search_result_item['id']}: {article_dict}"
                with open(f'{DOWJONES_IO_FOLDER_PATH}/article_dict_json_{clean_article_id}-{count}-ERROR.txt', 'w') as f:
                    f.write(article_dict)
                print(
                    f"Error obtaining content for {search_result_item['id']}: {article_dict}")
            else:
                # For now, save the article to a unique file name
                # Write the json to screen
                with open(f'{DOWJONES_IO_FOLDER_PATH}/article_dict_json_{clean_article_id}-{count}.json', 'w') as f:
                    f.write(json.dumps(article_dict))
                print(
                    f"Saved article_dict_json_{clean_article_id}-{count}.json")

                st.write(article_dict)
                st.divider()

            # upload_blob(item['id'], article_dict)
            # article = dj_as.extract_article(article_dict)
            # st.write(article)

            # i = 0
            # prior_result = None
            # prior_article = None
            # for item in json.loads(st.session_state.dj_search_results)['data']:
            #     if item == prior_result:
            #         print('!!!!!!!!! next search result == prior_result')
            #         continue
            #     i += 1
            #     prior_result = item
            #     if return_type == 'Search Only':
            #         formatted_result = dj_as.extract_search_result(item)
            #         for result_part in formatted_result:
            #             st.markdown(result_part)
            #             st.divider()

            #     if return_type == 'Search and Retrieve Article':

            #         article_dict = dj_as.get_content_item(item['id'])
            #         if prior_article == article_dict:
            #             print('!!!!!!!!!prior_article == article_dict')
            #             continue
            #         prior_article = article_dict
            #         article_dict = json.loads(article_dict)
            #         article = dj_as.extract_article(article_dict)
            #         with col1:
            #             for key in article.keys():
            #                 if not isinstance(article[key], dict) and not isinstance(article[key], list):
            #                     st.markdown(f"{article[key]}")
            #         with col2:
            #             st.write(article)
            #         with col3:
            #             st.write(article_dict)
