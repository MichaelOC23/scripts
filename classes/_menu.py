import streamlit as st
import os


def show_authenticated_menu():
    pass# Show a navigation menu for authenticated users
    # with st.sidebar:
    #     st.text("Navigation")
        # st.page_link("pages/000_gmtc_charts.py", label="GMTC Chart Design Area")
    # st.switch_page("pages/000_gmtc_charts.py")

def check_session_state():
    # Check if Streamlit is running in development mode
    if os.environ.get("STREAMLIT_DEV_MODE", "FALSE") == "TRUE": 
        return True
    
    # Set the role to None if it doesn't exist in Session State
    st.session_state.role = None if 'role' not in st.session_state else st.session_state.role
    if st.session_state.role != 'user': return None
    else: show_authenticated_menu()
    return True
    

def auth_user(user, password):
    if user is None or user.strip() == "": return None    
    if password is None or password.strip() == "": return None   
    if "communify" in user or "justbuildit" in user:
        if "Heavy95!" in password: return 'user'
        
