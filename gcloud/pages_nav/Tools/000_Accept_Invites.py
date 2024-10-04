

import streamlit as st
from _class_streamlit import streamlit_mytech   
stm = streamlit_mytech(theme='cfdark')
stm.set_up_page(page_title_text="Meeting Acceptance",
                session_state_variables=[], )
    
if st.button('Accept'):
    from _class_o365_communify import MS_GraphAPI_Calendar 
    o365 = MS_GraphAPI_Calendar()
    st.session_state['log'] = o365.process_meeting_invites()

if 'log' in st.session_state:
    for item in st.session_state['log']:
        st.markdown(f'- {item}' )
        