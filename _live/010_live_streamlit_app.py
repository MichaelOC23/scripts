# Imports
import os
import threading
import traceback

import httpx
import streamlit as st
from _class_streamlit import streamlit_mytech
from _class_firebase import FirestoreStorage
from _class_aggrid import AggridUtils
import asyncio

stm = streamlit_mytech(theme='cfdark')
fire = FirestoreStorage()
# agu = AggridUtils(rowSelection="single", hide_by_default=True)

stm.set_up_page(page_title_text="Meeting Log",
                session_state_variables=[{"TransStatus": False}]) 
st.subheader("Select a Meeting:", divider=True)

header_dict = {
  "name": "Name", #"duration": "Duration", "created": "Date",
    #   "transcription_raw": "transcription_raw", #  #   "document_id": "Id",
    #   "speaker_names": "Speakers", "topics": "Topics", "summary": "Summary",
    #   "public_url": "public_url", #   "modified": "Modified", "modifiedon": "modifiedon", #   "createdon": "createdon", 
 }
if not 'transcription_records' in st.session_state:
    st.session_state["transcription_records"] = fire.get_transcription_records_sync()

df_leftnav = st.session_state['transcription_records'][['name']]

scol, vcol = st.columns([3,7])

def on_nav_grid_select():
    print(st.session_state["nav_grid"].selection)
    if len(st.session_state["nav_grid"].selection.rows) >0:
        nav_grid_row = st.session_state["nav_grid"].selection.rows[0]
        st.session_state["selected_document_id"] = st.session_state['transcription_records'].index[nav_grid_row]
    else:
        st.session_state['selected_document_id'] = None


with scol:
    st.dataframe(df_leftnav, on_select=on_nav_grid_select,
                 use_container_width=True, hide_index=True, 
                 height=(len(st.session_state['transcription_records'])+1)*30, 
                 key='nav_grid', selection_mode="single-row")
    # agu.create_default_grid(st.session_state['transcription_records'], header_dict )
    # agu.display_grid(st.session_state["transcription_records"])

with vcol:
    bt1, title,  bt2, bt3 = st.columns ([1, 10,1,1])

    
    with bt1:
        st.button('Edit', key='Edit', use_container_width=True, type='primary')    
    with bt2:
        st.button('Save', key='Save', use_container_width=True)
    with bt3:   
        st.button('Cancel', key='Cancel',  use_container_width=True)
    st.divider()
    if 'selected_document_id' in st.session_state and st.session_state['selected_document_id'] is not None:
        doc = asyncio.run(fire.get_full_transcription(st.session_state["selected_document_id"]))
        st.write(doc)



