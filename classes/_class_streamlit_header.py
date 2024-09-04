import streamlit as st

MODEL_DICT = {
            "Finance": "nlpaueb/sec-bert-base", 
            "General": "roberta-base",
            "ChatGPT-3.5": "gpt-3.5-turbo",
            "ChatGPT-4": "gpt-4-turbo",
            
            }

####################################
####       STREAMLIT CLASS      ####
####################################
class streamlit_header():
    def __init__(self):
        self.model_dict = MODEL_DICT
        self.setup_database = False
        
    def set_up_page(page_title_text="[TITLE NEEDED FOR PAGE]", jbi_or_cfy="jbi", light_or_dark="dark", session_state_variables=[]):  
            
        def initialize_session_state_variable(variable_name, variable_value):
            if variable_name not in st.session_state:
                        st.session_state[variable_name] = variable_value
        
        # Page Title and Logo
        if page_title_text != "":
            PAGE_TITLE = page_title_text
            LOGO_URL = ""
            if jbi_or_cfy == "jbi":
                LOGO_URL = "https://devcommunifypublic.blob.core.windows.net/devcommunifynews/jbi-logo-name@3x.png"
            else:
                LOGO_URL = "https://devcommunifypublic.blob.core.windows.net/devcommunifynews/cflogofull.png"
            
        for variable in session_state_variables:
            if isinstance(variable, dict):
                for key in variable.keys():
                    initialize_session_state_variable(key, variable[key])
            
        st.set_page_config(
                page_title=PAGE_TITLE, page_icon=":earth_americas:", layout="wide", initial_sidebar_state="collapsed",
                menu_items={'Get Help': 'mailto:michael@justbuildit.com','Report a bug': 'mailto:michael@justbuildit.com',})    

        # Standard Session state    
        initialize_session_state_variable("show_session_state", False)
        initialize_session_state_variable("DevModeState", False) 
        initialize_session_state_variable("settings", {"divider-color": "gray",})
        initialize_session_state_variable("model_type_value", MODEL_DICT["Finance"])
        initialize_session_state_variable("temperature", .1)
        
        
        # Page Title Colors
        border_color = "#FFFFFF"
        text_color = "#FFFFFF"
        background_color = "#1D1D1D"
        
        # Display the page title and logo and top buttons
        st.markdown(f"""
                <div style="display: flex; align-items: start; width: 100%; padding: 10px; border: 1px solid {border_color}; border-radius: 10px; 
                height: 80px; background-color: {background_color}; margin-bottom: 20px;"> 
                <img src="{LOGO_URL}" alt="{PAGE_TITLE}" style="width: 80px; height: auto; margin: 10px 40px 5px 20px;">  
                <span style="flex: 1; font-size: 30px; margin: 2px 0px 10px 10px; font-weight: 400; text-align: top; align: right; white-space: nowrap; 
                overflow: hidden; color: {text_color}; text-overflow: ellipsis;">{PAGE_TITLE}</span>  </div>""", unsafe_allow_html=True)
                
        
        #View Session State Button
        view_ss = st.sidebar.button(f"Ses. State", use_container_width=True)
        if view_ss:
            if st.session_state.show_session_state:
                st.session_state.show_session_state = False
            else:
                st.session_state.show_session_state = True

        log_exp = st.expander("Extraction Log", expanded=False)
        
        # Display the session state
        if st.session_state.show_session_state:
            ss = st.expander("Session State Value", expanded=False)
            ss.write(st.session_state)
        
        
        # Enable the below to see border around the page and all the columns
        # st.markdown("""<code style="background-color: #FFFFFF; padding: 30px; border-radius: 6px;color: red;">Your HTML content here</code>""", unsafe_allow_html=True)

