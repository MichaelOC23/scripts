from re import search
from flask import request
import streamlit as st
import sys
import base64
import io


def display_pdf_from_url(url):
    # Fetch the PDF from the URL
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for bad response codes

    # Read file as bytes
    pdf_bytes = response.content

    # Encode bytes in base64
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

    # Embed PDF in HTML with desired width and height
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="400" type="application/pdf"></iframe>'

    return pdf_display
    
    




import _class_streamlit as cs
from bs4 import BeautifulSoup
import urllib

cs.set_up_page(page_title_text="Historical News", jbi_or_cfy="jbi", light_or_dark="dark", 
    session_state_variables=[{"search_result_cache": {}}, {"viewed_article_cache": {}},],
                            connect_to_dj=False) 


import requests #import the library that we use to make the http request

state_url=""
publisher_text = ""
subject_text = ""
state_text = ""
city_text = ""
date_text = ""
title_normal_text = ""
page_text = ""
protext_url =""


state_s = "California"
protext_s ='"St. Anthony''s Seminary"'
rows_s = 100
start_year_s = 1920
end_year_s = 1960

#make this string url safe using urllib.parse.quote
state_s = urllib.parse.quote(state_s)
protext_s = urllib.parse.quote(protext_s)


if state_s != "": state_url = f"state={state_s}"
if protext_s != "": protext_url = f"&protext={protext_s}"
search_url = f"http://chroniclingamerica.loc.gov/search/pages/results/?{state_url}{protext_url}&rows={rows_s}&sort=relevance&format=json"
print(search_url)
r = requests.get(search_url).json()

st.write(f"Total Results: {r['itemsPerPage']}") #print out the number of items per page:
for item in r['items']:
    if item.get('subject', []) != []:
        subject_text = f"Subject: {item['subject'][0].split('--')[0]}"
    if item.get('publisher', "") != "":
        publisher_text = f"Publisher: {item['publisher']}"
    if item.get('state', "") != "":
        state_text = f"State: {item['state'][0]}"
    if item.get('city', "") != "":
        city_text = f"City: {item['city'][0]}"
    if item.get('date', "") != "":
        date_text = f"Date: {item['date']}"
    if item.get('title_normal', "") != "":
        title_normal_text = f"{item['title_normal'].title()}"  
    if item.get('page', "") != "":
        page_text = f"Page: {item['page']}"
    
    st.markdown(f"### {title_normal_text}")
    st.markdown(f"#### {publisher_text} - {date_text} - {state_text} - {city_text} - {page_text}")
    st.write(item['url']) #print out the URL for each item
    text_col, image_col = st.columns([1, 1])
    text_col.write(item)
    # Display PDF using unsafe_allow_html (careful with external URLs)
    pdf_display = display_pdf_from_url(item['url'].replace("/ocr.txt",".pdf"))
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    
    # image_col.image(item['url'].replace("/ocr.txt",".jp2") , use_column_width=True)
    st.markdown(f"---")
    
    # st.write(item['ocr_eng']) #print out the OCR text for each item
    # response = requests.get(item['url'])
    # import classes._class_search_web as sw
    # search = sw.Search()
    # response = search.sync_wrapper(item['url'])
    # if response.status_code != 500:
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     body = soup.body.get_text(separator=' ', strip=True)
    #     st.write(body)

    # st.html(f"<a href='{item['url']}' target='_blank'>View Article</a>")
    

# ocr_col, url_col = st.columns([1, 1])
# ocr_col.write(r['items'][0]['ocr_eng']) #no need to repeat the code from above since jupyter notebooks retains it
# url_col.write(r['items'][0]['url'])
# r2 = requests.get(r['items'][0]['url'])
# url_col.write(r2.text)
# url_col.markdown(r2, unsafe_allow_html=True)

# dogs_search = requests.get('http://chroniclingamerica.loc.gov/search/pages/results/?proxtext=dogs&format=json').json()
# dogs_search['totalItems']
# dogs_search['items'][0]['url']

# requests.get('http://chroniclingamerica.loc.gov/lccn/sn83045487/1913-04-21/ed-1/seq-20/ocr.txt').text
# pages = requests.get("http://chroniclingamerica.loc.gov/search/pages/results/?proxtext=dog&rows=20&format=json").json()


# from collections import Counter

# c = Counter()
# for page in pages['items']:
#     c[page['state'][0]] += 1
    
# c.most_common()



# import requests

# # Define the base URL for the newspaper search
# base_url = "https://www.loc.gov/newspapers/"

# # Set up parameters for the API request
# params = {
#     'fo': 'json',           # Format of the output
#     'q': 'moon landing',    # Query or keywords to search for
#     'dates': '1969'         # Specific year or date range
# }

# # Send a GET request to the LOC API
# response = requests.get(base_url, params=params)

# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()  # Convert the response to JSON
#     print(data)
#     with open('loc.json', 'w') as f:
#         f.write(response.text)

#     # # Loop through the results and print some details
#     # for item in data.get('results', []):
#     #     print(f"Title: {item['title']}")
#     #     print(f"Date: {item['date']}")
#     #     print(f"URL: {item['url']}")
#     #     print('-' * 60)
# else:
#     print("Failed to retrieve data")

