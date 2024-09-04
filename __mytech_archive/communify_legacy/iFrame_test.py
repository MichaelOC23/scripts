import streamlit as st
import streamlit.components.v1 as components
import shared.functions_common as oc2c
import os
oc2c.configure_streamlit_page("Multi-LLM-Chainlit-App-Test-Page", "wide")


b2_URL = "http://localhost:5011/"  # Replace with the URL of your Chainlit app
b7_URL = "http://localhost:5012/"  # Replace with the URL of your Chainlit app
mistral_URL = "http://localhost:5013/"  # Replace with the URL of your Chainlit app

st.title("My Chainlit App in Streamlit")

# Adjust the height as needed
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.subheader ("Gemma 2b")
    components.iframe(src=b2_URL, height=600) 

with col2:
    st.subheader ("Gemma 7b")
    components.iframe(src=b7_URL, height=600)

with col3:
    st.subheader ("Mistral 7b")
    components.iframe(src=mistral_URL, height=600)
    