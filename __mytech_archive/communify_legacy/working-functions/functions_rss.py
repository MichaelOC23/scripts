
#standard modules   
import json
# import sys

#data processing
# import pandas as pd
# import numpy as np
from bs4 import BeautifulSoup, NavigableString

#multi-threading
import asyncio


#Streamlit UI
import streamlit as st
import itertools


#Data Sources
import feedparser

#my modules
import functions_data_tools as dt
import functions_constants as con




#@st.cache_data #Note: do not cache this function unless you plan to expire the cache on a regular basis
async def fetch_rss_feeds(rss_source_url_list = None, output_file = None):
    if rss_source_url_list is None:
        print(f"ERROR: List of RSS Feeds is empty. URL list is required. Received: {rss_source_url_list}")
        return None
    
    if output_file is None:
        output_file = f'temp/rss_feed_list_{con.UNIQUE_DATE_TIME_STRING()}.json'

    # Iterate through the list of URLs and get the RSS feed list for each URL
    tasks = []
    for rss_source in rss_source_url_list:
        task = asyncio.create_task(fetch_rss_feed(rss_source['url'], rss_source['source']))
        tasks.append(task)
    
    # Schedule all tasks to run concurrently
    # the returned value is a list of lists with identical structure.
    rss_feed_entries_list = await asyncio.gather(*tasks)

    # Flatten the list of lists into a single list
    # that is stacked into a dataframe
    #df = pd.DataFrame(rss_feed_entries_list)
    #flattened_RSS_list = pd.concat(rss_feed_entries_list, ignore_index=True)
    flattened_RSS_list = list(itertools.chain(*rss_feed_entries_list))


    return flattened_RSS_list

#@st.cache_data #Note: do not cache this function unless you plan to expire the cache on a regular basis
async def fetch_rss_feed(url = None, source = None):
    if url is None or source is None:
        print(f"""Cannot get RSS feed list from URL. 
              URL and Source are required.
              Received: url: {url}, source: {source}""")
        return None
    
    # Parse the RSS feed
    feed = feedparser.parse(url)

    # Turn the feed parser into standard JSON
    # This is necessary because the feedparser library does not return standard JSON
    feed_json = json.dumps(feed)
    feed_json = json.loads(feed_json)
    
    # Flatten the feed entries and append to the provided list (if provided)
    def try_to_get_value_from_feed_json(entry, field_l1, field_l2 = None):
        try:
            if field_l2 is None:
                field_value = entry[field_l1]
            else:
                field_value = entry[field_l1][field_l2]
            return field_value
        except:
            print(f"Could not get value for field(s): l1:{field_l1}: l2:{field_l2}")
            return ""

    
    
    #The feed_json is a list of dictionaries named 'entries'
    entries_list = []
    if len(feed_json['entries']) > 0:
        entries_list = feed_json['entries']
    
    # This is empyt list that will be populated with the flattened RSS feed entries
    # and returned to the caller
    flat_rss_list = []
    def extract_text_from_html(html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            img_tag = soup.find('img')
            desired_text = ""
            if img_tag and isinstance(img_tag.next_sibling, NavigableString):
                desired_text = img_tag.next_sibling.strip()
                return desired_text
        except:
            return ""

    #entry is each item in the entries_list (.i.e. each RSS feed entry/article)
    for entry in entries_list:
        #(entry)
        
        #!to do: try to find/review a RSS standards document to see if there is a standard way to flatten the JSON
        flat_rss = {
            'source': source, 
            'title': try_to_get_value_from_feed_json(entry, 'title'),  
            'title_detail_type': try_to_get_value_from_feed_json(entry, 'title_detail', 'type'),
            'title_detail_language': try_to_get_value_from_feed_json(entry, 'title_detail', 'language'),    
            'title_detail_base': try_to_get_value_from_feed_json(entry, 'title_detail', 'base'),
            'title_detail_value': try_to_get_value_from_feed_json(entry, 'title_detail', 'value'),
            'link': try_to_get_value_from_feed_json(entry, 'link'),
            'summary': try_to_get_value_from_feed_json(entry, 'summary'),
            'summary_type': try_to_get_value_from_feed_json(entry, 'summary_detail', 'type'),
            'summary_language': try_to_get_value_from_feed_json(entry, 'summary_detail', 'language'),
            'summary_base': try_to_get_value_from_feed_json(entry, 'summary_detail', 'base'),
            'summary_value': try_to_get_value_from_feed_json(entry, 'summary_detail', 'value'),
            'summary_value_text': extract_text_from_html(try_to_get_value_from_feed_json(entry, 'summary_detail', 'value')),
            'id': try_to_get_value_from_feed_json(entry, 'id'),
            'tags': "|".join([item['term'] for item in try_to_get_value_from_feed_json(entry, 'tags') if 'term' in item]),
            'published_date': try_to_get_value_from_feed_json(entry, 'published')
                }
        
        # the images may be separately useful ... pulling them out into their own field
        img_list = []
        img_list = dt.get_image_urls_from_text(json.dumps(flat_rss), img_list)
        img_list = list(set(img_list))
        flat_rss['image_urls'] = "|".join(img_list)
        
        #Add the flattened RSS feed entry to the list that will be returned
        flat_rss_list.append(flat_rss)
    
    #return the flattened RSS feed list
    return flat_rss_list

if __name__ == "__main__":
    st.header('RSS Data Visualization', divider="blue")

    #! Test #1: RSS Feed List from URL
    st.subheader('RSS Feed List from major news sources', divider="blue")
    
    wsj, ft = st.columns(2)
    with wsj:
        st.image('https://library.rice.edu/sites/default/files/styles/wide/public/media-images/Wall-Street-Journal_0.png?itok=pX2q_fat', width=50)
    with ft:
        st.image('https://upload.wikimedia.org/wikipedia/commons/6/6b/Financial_Times_corporate_logo_%28dark%29.svg', width=50)
    
                 
    
    # prepare a list of RSS URLs
    rss_url_list = [
        {'source': 'FT', 'url': 'https://www.ft.com/myft/following/1f5bb351-6628-4cd7-b33f-54b4e0112edc.rss'},
        {'source': 'WSJ', 'url': 'https://feeds.a.dj.com/rss/RSSWSJD.xml'}
    ]


    # get the RSS feed list from the URL list
    rss_feed_list = asyncio.run(fetch_rss_feeds(rss_url_list))

    # display the RSS feed listt
    st.write(rss_feed_list)

