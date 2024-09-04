import streamlit as st
import os
import _menu
from navigation import _navigation





st.header("Test Dash")
st.write ("This is a test dash")



# def page3():
#     st.title("Third page")

# def page2():
#     st.title("Second page")

# pg = st.navigation({
#     "AI": [ 
#             st.Page("pages/AI/000_AI_Studio.py", title="First page", icon="🔥"),
#             st.Page(page2, title="Second page", icon=":material/favorite:")
#             ],
#     "Tools":[
#         st.Page(page3, title="Second page", icon=":material/favorite:")
#              ]
#     }
#                    )
# pg.run()


nav = _navigation()


used_paths = []
for folder in nav.folder_structure.keys():
    st.write(folder)
    folder_page_dict = nav.folder_structure[folder]
    for page in folder_page_dict.keys():
        page_dict = folder_page_dict[page]
        if page_dict.get('path') in used_paths:
            st.write("Duplicate path found: ", page_dict.get('path'))
            st.write(page.title)
        used_paths.append(page_dict.get('path'))
st.divider()
st.write(nav.folder_structure)
st.write("something else")


nav_dict = nav.create_menu()
pg = st.navigation(nav_dict)



pg.run()


