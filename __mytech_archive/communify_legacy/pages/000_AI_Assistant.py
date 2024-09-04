import functions_common as oc2c
import streamlit as st
from openai import OpenAI
import json
import os
import functions_common as oc2c
import functions_constants as constants
import functions_gmail as gmail
oc2c.configure_streamlit_page(Title="AI Assistant")
import functions_openai_assistant_calendar as cal_assist

# Iterate through all the files in the EMAIL_IO_FOLDER_PATH folder and write the contents to json files
emails = []
grid  = st.empty()

uid = constants.UNIQUE_DATE_TIME_STRING()

gmail.get_emails_full_contents(uid, 20)

for file in os.listdir(constants.EMAIL_IO_FOLDER_PATH):
    if file.endswith(".json"):
        with open(os.path.join(constants.EMAIL_IO_FOLDER_PATH, file), 'r') as f:
            json_str = f.read()
            json_dict = json.loads(json_str)
            email_raw_dict = json_dict.pop('headers', None)
            email_dict = {}
            for header in email_raw_dict:
                if isinstance(header, dict):
                    if 'name' in header and 'value' in header:
                        email_dict[header['name'].lower()]= header['value']
            email={}
            email['date'] = email_dict.get('date', None)  # Use get() method to handle the case when 'Date' key is not present
            email['subject'] = email_dict.get('subject', None)
            email['sender'] = email_dict.get('from', None)
            email['cc'] = email_dict.get('cc', None)
            email['to'] = email_dict.get('to', None)
            email['body'] = json_dict.get('body', None)
            email['list-unsubscribe'] = json_dict.get('list-unsubscribe', None)
            email['id'] = json_dict.get('id', None)
            email['delivered-to'] = json_dict.get('delivered-to', None)
            email['content-type'] = json_dict.get('content-type', None)
            
            email['content-type'] = json_dict.get('content-type', None)
            
            emails.append(email)
            
            st.write(email_dict)

grid.data_editor(emails)





    

# request = None

# email = st.text_area("Email Body", key='query', height=200, help="Enter your email body here")

# if st.button(label= "Submit",    key='submit'):
#     request = email

# colw1, colw2 = st.columns([1, 1])

# with colw1:
#     st.write("You entered: ", email)

# with colw2:
#     if request is not None:
#         result = cal_assist.get_assistant_response(request)
#         st.header('Events', divider='rainbow')
#         st.text(result)