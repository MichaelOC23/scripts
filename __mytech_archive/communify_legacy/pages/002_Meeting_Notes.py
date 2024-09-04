import streamlit as st 
import functions_common as oc2c
import os
oc2c.configure_streamlit_page("Meeting Notes")
from streamlit_monaco import st_monaco


st.sidebar.markdown(st.session_state)

#Get the current user
User = oc2c.get_current_user()

#Create a session state for the current user
if User not in st.session_state: st.session_state[User] = {}

#Get the folder to store all notes in
NOTE_FOLER_PATH = os.environ.get('NOTE_FOLER_PATH')

#Start with no open notes
if "NoteState" not in st.session_state[User] or st.session_state[User]['NoteState'] == "None": 
    st.session_state[User]['NoteState'] = "None"
    st.session_state[User]['SavingState'] = "None"
    st.session_state[User]['NoteTitle'] = "Create or Open a Note"
    st.session_state[User]['NoteContent'] = ""
    st.session_state[User]['NoteType'] = ""
    st.session_state[User]['NotePath'] = ""

SubHeader = st.subheader(st.session_state[User]['NoteTitle'],divider=True)

with st.container(height=72, border=True,):
    b1, b2, b3, b4, b5, b6 = st.columns([1,1,1,3,.5,1])
    New_Note_Button = b1.button("New", key="Create New Note",type="secondary", use_container_width=True)
    Open_Note_Button = b2.button("Open", key="Open Note",type="secondary", use_container_width=True)
    Save_and_Close_Button = b3.button("Close", key="Close",type="secondary", use_container_width=True)
    Discard_Work_Button = b6.button(":red[Discard]", key="Discard Work",type="secondary", use_container_width=True,)   


if New_Note_Button or st.session_state[User]['SavingState'] == "Saving":
    st.session_state[User]['SavingState'] = "Saving"
    with st.container(border=False,):
        col1, col2, = st.columns([1,5])
        with col1.container(border=True,):
            NewNoteName = col1.text_input("New Note Name", key="New Note Name",)
            file_type_radio = col1.radio("File Type", ["txt", "json", "py"], key="File Type")
            if file_type_radio or st.session_state[User]['SavingState'] == "Saving":
                st.session_state[User]['SavingState'] == "Saving"
                if col1.button("Save", key="Save Note",type="primary", use_container_width=False):
                    st.session_state[User]['NoteTitle'] = f'{NewNoteName}.{file_type_radio}'
                    st.session_state[User]['NotePath'] = f"{NOTE_FOLER_PATH}/{NewNoteName}.{file_type_radio}"
                    with open(st.session_state[User]['NotePath'], "w") as file:
                        if file_type_radio == "json":
                            file.write("{}")
                        else:
                            file.write("")
                    st.session_state[User]['NoteState'] = "Open"
                    st.session_state[User]['SavingState'] = "None"
                        
if st.session_state[User]['NoteState'] == "Open":
    Note_col1, Preview_col2, = st.columns([1,1])
    with Note_col1:
        save_close = st.button("Save and Close", key="Save and Close",type="primary", use_container_width=False)
        content = st_monaco(value="## Type your notes in text or markdown here",
                                height="1000px",
                                language="markdown",
                                lineNumbers=False,
                                minimap=False,
                                theme="vs-dark",
                                )
        st.session_state[User]['NoteContent'] = content
        with open(st.session_state[User]['NotePath'], "w") as file:
            file.write(content)
        if save_close or st.session_state[User]['NoteState'] == "None":
            st.session_state[User]['NoteState'] = "None"
            st.stop()
        with Preview_col2:
            st.markdown(content)


    
 
# content = st_monaco(
#     value="// First line\nfunction hello() {\n\talert('Hello world!');\n}\n// Last line",
#     height="1000px",
#     language="markdown",
#     lineNumbers=False,
#     minimap=False,
#     theme="vs-dark",
# )
# print(content)



# if st.button("Get content"):
#     st.markdown(content)





# st.markdown("""
#             <style>
#                 div[data-testid="column"] {
#                     width: fit-content !important;
#                     flex: unset;
#                     justify-content: flex-end; /* Align children to the end (bottom) */
#                     border:1px solid red;

#                 }
#                 div[data-testid="column"] * {
#                     width: fit-content !important;
#                     justify-content: flex-end; /* Align children to the end (bottom) */
#                 }
#             </style>
#             """, unsafe_allow_html=True)



# col1, col2, col3 = st.columns(3)

# with col1:
#     """
#     ## Column 1 
#     Lorem ipsum dolor sit amet, consectetur adipiscing elit, 
#     sed do eiusmod tempor incididunt ut labore et dolore 
#     magna aliqua. Volutpat sed cras ornare arcu dui vivamus.
#     """
# with col2:
#     """
#     ## Column 2
#     Stuff aligned to the right
#     """
#     st.button("➡️")
# with col3:
#     """
#     ## Column 3
#     This column was untouched by our CSS 
#     """
#     st.button("🐈")


# st.markdown(
#     """
#     <style>
#         div[data-testid="column"]:nth-of-type(1)
#         {
#             border:1px solid red;
#         } 

#         div[data-testid="column"]:nth-of-type(2)
#         {
#             border:1px solid blue;
#             text-align: end;
#         } 
#     </style>
#     """,unsafe_allow_html=True
# )
