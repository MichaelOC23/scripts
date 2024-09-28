
# Standard Python libraries
import streamlit as st
import os
import json
from pathlib import Path
import google_auth_oauthlib.flow
import time
from googleapiclient.discovery import build
from _class_google_cloud_auth import Authenticate, CookieHandler

import os



MODEL_DICT = {
            "Finance": "nlpaueb/sec-bert-base", 
            "General": "roberta-base",
            "ChatGPT-3.5": "gpt-3.5-turbo",
            "ChatGPT-4": "gpt-4-turbo",
            
            }

user_list = ["michaelsmith9905",  "vincent", "yaelas", "walker", "noelle", "barb", "sarah"]

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
        self.font = themes.get(theme, {}).get('font', '')
        self.logo_url = themes.get(theme, {}).get('logo_url', '')
        self.logo_icon_url = themes.get(theme, {}).get('logo_icon_url', '')
        
        self.page_title = "New Page"
        
        self.home_dir = Path.home()
        self.home_config_file_path = f'{self.home_dir}/.streamlit/config.toml'
        self.working_config_file_path = f'.streamlit/config.toml'
        self.master_config_file_path = f'{self.home_dir}/code/scripts/.streamlit/master_streamlit_config.toml'    
 

    def create_google_secret(self, secret_id, secret_value, project_id='toolsexplorationfirebase'):
        
        # for key in os.environ.keys():
        #     if 'HOMEBREW' not in key:
        #         try:
        #             stm.create_google_secret(key, os.environ.get(key))
        #             print (f'Successfull added secret {key}')
        #         except:
        #             print (f'Failed to add secret {key}')
        #         time.sleep(1)
        

        
        from google.cloud import secretmanager

        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()

        # Build the resource name of the parent project
        parent = f"projects/{project_id}"

        try:
            # Create the secret with automatic replication
            response = client.create_secret(request={"parent": parent, "secret_id": secret_id, "secret": {"replication": {"automatic": {}},},})
            print(f"Created secret: {response.name}")
            
            secret_name = f"projects/{project_id}/secrets/{secret_id}"
            payload = secret_value.encode("UTF-8")
            response = client.add_secret_version(request={"parent": secret_name,"payload": {"data": payload},})
            print(f"Added secret version: {response.name}")
            
        except Exception as e:
            print(f"Failed to create secret {secret_id} in project {project_id}. Error: {e}")

        return response.name
    
    def get_google_secret(self, secret_id, project_id='toolsexplorationfirebase',  version_id="latest"):
        from google.cloud import secretmanager
        secret_payload = ''
        try:
            # Create the Secret Manager client
            client = secretmanager.SecretManagerServiceClient()

            # Build the resource name of the secret version
            name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

            # Access the secret version
            response = client.access_secret_version(request={"name": name})

            # Decode the secret payload and return it
            secret_payload = response.payload.data.decode("UTF-8")
            
        except:
            secret_payload = os.environ.get(secret_id, '')
        
        return secret_payload
    
    def get_google_oauth_credentials(self):
        # Return credentials or initialize session_state placeholder
        if 'GOOGLE_OAUTH_CREDENTIALS' not in st.session_state: 
            st.session_state["GOOGLE_OAUTH_CREDENTIALS"] = {}
        
        if st.session_state['GOOGLE_OAUTH_CREDENTIALS'] != {}:
            return st.session_state['GOOGLE_OAUTH_CREDENTIALS']
        
        # Get Google OAuth Credentials
        cred_json = self.get_google_secret('DATASCIENCETOOLS_CLIENT_OAUTH_JSON')
        cred_dict = json.loads(cred_json)
        st.session_state["GOOGLE_OAUTH_CREDENTIALS"] = cred_dict
        return st.session_state["GOOGLE_OAUTH_CREDENTIALS"]
        
    def set_up_page(self, page_title_text=None, 
                    logo_url=None, 
                    session_state_variables=[], 
                    initial_sidebar_state="expanded"):
        
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

    def establish_authentication(self,advanced_menu=False, google_auth=False):
        if advanced_menu:
            from _class_streamlit_navigation import navigation_streamlit   
            nav = navigation_streamlit()
            if nav.check_if_authenticated(): 
                print('The current user is authenticated.')
                pg = st.navigation(nav.menu)
                pg.run()
        
        
        if not google_auth:
            st.logo(self.logo_icon_url, icon_image=self.logo_url)
            st.header(f"{self.page_title}",divider=True)
            return
        else:
            uri='https://simpleappservice-236139179984.us-west2.run.app'
            if os.path.exists("/Users/michasmi"):
                uri = 'http://localhost:5010'
            
            cred_dict = self.get_google_oauth_credentials()
            print(f'Obtained credential {cred_dict}')
            
            authenticator = Authenticate(
                secret_credentials_path = cred_dict,
                cookie_name='795ba442-577b-4231-98ca-aa2cc4845a83',
                cookie_key='2330bacd-3495-4211-9899-5fa47ead6779',
                redirect_uri=uri,
            )
            print ('Instantiated Authenticator')
            
            # Catch the login event
            print ('Beginning confirm_google_authentication')
            authenticator.confirm_google_authentication()
            

            # Create the login button
            authenticator.login(cred_dict=cred_dict)

            
        # Display the user information and logout button if the user is authenticated
        if st.session_state['IS_AUTHENTICATED_TO_GOOGLE'] and 'user_info' in st.session_state:
            if any(substring in st.session_state['user_info'].get('email', '') for substring in user_list):
                gpic, guser = st.sidebar.columns([1,4])
                gpic.image(st.session_state['user_info'].get('picture'))
                # guser.write(f"{st.session_state['user_info'].get('name')}\n{st.session_state['user_info'].get('email')}")
                if guser.button(f"Sign Out: {st.session_state['user_info'].get('name')}", use_container_width=True):
                    authenticator.logout()
                return
                    
        
        st.write(f"You are not authorized to access this site.")
        authenticator.logout()
        st.stop()
            
            

        
        




