import streamlit as st
import os

from navigation import _navigation
nav = _navigation() 

# Configure the page
st.set_page_config(page_title="Login",page_icon=":lock:", layout="centered", menu_items=None, initial_sidebar_state="collapsed")   

if nav.check_if_authenticated(): 
    pg = st.navigation(nav.menu)
    pg.run()


# Draw the screen
usr = st.text_input("User", key="_userid",)
pwd= st.text_input("Password",key="_pwd")
if st.button("Login", key="_login"):
    nav.auth_user(usr, pwd)
    st.rerun()  
    



        
