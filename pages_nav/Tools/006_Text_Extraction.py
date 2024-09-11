

from gettext import find
import streamlit as st
import os
from streamlit_elements import elements, mui, html, editor, lazy, sync
from sympy import div
import functions_excel as excel


st.set_page_config(layout="wide")
st.header('Text and Word Extraction tools')
base_path = '/Volumes/code/vscode/cool-tools/'
excel_file_path = f'{base_path}model-json/data_draft_001.xlsx'
export_path = f'{base_path}model-json/'
st.session_state['excel_file_path'] = excel_file_path
st.session_state['excel_range'] = "'consolidated copy 2'!E:E"

fullVocabFilePath = os.path.join(base_path, "Vocab", 'vocab-finance.txt')
with open(fullVocabFilePath, 'r') as f:
    content = f.read().upper()
    content = content.replace('{', '').replace('}', '').replace("'", '').replace('\n', '').replace(' ', '') #Remove unnecessary characters
    content_list = content.split(',')
    # Convert the list into a set
    full_vocab = set(content_list)


# with elements("monaco_editors"):

#     # Streamlit Elements embeds Monaco code and diff editor that powers Visual Studio Code.
#     # You can configure editor's behavior and features with the 'options' parameter.
#     #
#     # Streamlit Elements uses an unofficial React implementation (GitHub links below for
#     # documentation).

#     from streamlit_elements import editor

#     if "content" not in st.session_state:
#         st.session_state.content = "Default value"

#     mui.Typography("Content: ", st.session_state.content)

#     def update_content(value):
#         st.session_state.content = value

#     editor.Monaco(
#         height=300,
#         defaultValue=st.session_state.content,
#         onChange=lazy(update_content)
#     )

#     mui.Button("Update content", onClick=sync())

#     editor.MonacoDiff(
#         original="Happy Streamlit-ing!",
#         modified="Happy Streamlit-in' with Elements!",
#         height=300,
#     )

# with elements("multiple_children"):

#         # You have access to Material UI icons using: mui.icon.IconNameHere
#         #
#         # Multiple children can be added in a single element.
#         #
#         # <Button>
#         #   <EmojiPeople />
#         #   <DoubleArrow />
#         #   Hello world
#         # </Button>

#     mui.Button(
#             mui.icon.EmojiPeople,
#             mui.icon.DoubleArrow,
#             "Button with multiple children"
#         )

#         # You can also add children to an element using a 'with' statement.
#         #
#         # <Button>
#         #   <EmojiPeople />
#         #   <DoubleArrow />
#         #   <Typography>
#         #     Hello world
#         #   </Typography>
#         # </Button>

#     with mui.Button:
#             mui.icon.EmojiPeople()
#             mui.icon.DoubleArrow()
#             mui.Typography("Button with multiple children")

#     with elements("nested_children"):

#         # You can nest children using multiple 'with' statements.
#         #
#         # <Paper>
#         #   <Typography>
#         #     <p>Hello world</p>
#         #     <p>Goodbye world</p>
#         #   </Typography>
#         # </Paper>

#         with mui.Paper:
#                 with mui.Typography:
#                     html.p("Hello world")
#                     html.p("Goodbye world")


#         # with mui.Paper(elevation=3, variant="outlined", square=True):
#         mui.TextField(
#             label="My text input",
#             defaultValue="Type here",
#             variant="outlined",
#         )

#             # If you must pass a parameter which is also a Python keyword, you can append an
#             # underscore to avoid a syntax error.
#             #
#             # <Collapse in />

#         mui.Collapse(in_=True)

def generate_and_sort_substrings(input_str, min_length=1):
    length = len(input_str)
    substrings = []

    # Generate substrings of at least min_length
    print(f'Value of input/length {input_str}/{length}')
    for i in range(length):
        for j in range(i + min_length, length + 1):
            substrings.append(input_str[i:j])
    
    #make sure the list is unique
    substrings = list(set(substrings))

    # Sort the substrings by length, longest first
    sorted_substrings = sorted(substrings, key=len, reverse=True)
    
    return sorted_substrings


# Example usage
# data = read_excel_data('path_to_your_workbook.xlsx', 'Sheet1', 'A1:C3')


# Function to find words from the vocab in the input string
def find_words_upper(initial_string, vocab_set_upper):
    if not initial_string:
        return []
    
    substrings = generate_and_sort_substrings(initial_string,3)
    
    for substring in substrings:
        if substring in vocab_set_upper:
            # Identify the pre and post substring parts
            pre_substring = initial_string[:initial_string.find(substring)].strip()
            post_substring = initial_string[initial_string.find(substring) + len(substring):].strip()

            beginning = ''
            end = ''    
            if len(pre_substring.strip()) >0:
                beginning = find_words_upper(pre_substring, vocab_set_upper= vocab_set_upper)
            
            if len(post_substring.strip()) >0:
                end = find_words_upper(post_substring, vocab_set_upper= vocab_set_upper)

            return f"{beginning} {substring} {end}"

    # If no substring is found in the vocabulary
    return initial_string

processing_tab1, testing_tab2 = st.columns(2)

with processing_tab1:
    st.subheader('Extract Text', divider='green')
    excel_file_path = st.text_input ('Excel File Path', st.session_state['excel_file_path'], key='Excel_File_Path')
    excel_range1 = st.text_input ('Range', st.session_state['excel_range'], key='Range')
    
    if st.button("Extract and Display Excel Data", key="Display_Excel_Data"):
        excel_data = excel.read_excel_data(excel_file_path, excel_range1)
        st.write(excel_data)

    if st.button("Extract and Process Excel Data", key="Process_Excel_Data"):
        excel_data = excel.read_excel_data(excel_file_path, excel_range1)
        proper_names = []
        for item in excel_data:
            proper_names.append(find_words_upper(item[0], full_vocab))
        st.write(proper_names)



with testing_tab2:
    st.subheader('Test Substring Extraction', divider = 'orange')
    gibberish = st.text_input ('Word', 'word')

    if st.button("Test Substring Extraction"):
        substring_list = generate_and_sort_substrings(gibberish, 3)
        st.write(substring_list)

    if st.button("Test Word Extraction"):
        result = find_words_upper(gibberish, full_vocab)
        st.write(result)