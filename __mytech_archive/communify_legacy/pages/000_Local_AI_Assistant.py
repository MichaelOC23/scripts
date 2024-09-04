from openai import OpenAI
import streamlit as st

def get_instruction():
    ai_instruction = """

    ### Instruction:

    #### Introduction and Objective:

    You will be provided with a series of email texts.
    Your task is to read each email and determine if it contains information about a relevant meeting or event. If so, you will extract the details of the event and present them in a structured format.

    #### Criteria for Relevance:
    Identify emails that mention specific dates and times, locations (physical or virtual, like Zoom links), and a clear indication of a meeting or event. Exclude any emails that are promotional, newsletters, or spam. Make sure NOT to exclude message that are personal correspondence, relate The Center for Early Education, CEE, Communify or Just Build It.

    #### Extraction of Details:
    For each email that contains an event, extract the following details:
    - Event Title: The name or a brief description of the event or meeting.
    - Date and Time:  When the event is scheduled to occur.
    - Location: The physical address or online meeting link.
    - Organizer/Contact Information: If mentioned, include the name or email of the organizer.

    #### Response - Reporting Format - Present the extracted information in a structured format
    - Email Subject: [Subject of the Email]
    - Event Title: [Extracted Title
    - Date and Time: [Extracted Date and Time]
    - Location: [Extracted Location]
    - Organizer: [Extracted Organizer's Contact]
    - Additional Notes: [Any Other Relevant Details]

    #### Exclusion and Error Handling:
    If an email does not contain event information or falls under the categories to be excluded, simply note that it's 'No event details found. Handle any ambiguities or uncertainties in the email content by flagging them for manual review

    The emails are provided in the user messages.

    """ 
    return ai_instruction

def extract_events(email_text):
    # Point to the local server
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

    history = [
        {"role": "system", "content": get_instruction()},
        {"role": "user", "content": email_text},
    ]


    completion = client.chat.completions.create(
        model="local-model", # this field is currently unused
        messages=history,
        temperature=0.1,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content
            col2.markdown(new_message["content"])

    history.append(new_message)

    print()
    history.append({"role": "user", "content": input("> ")})
        
if __name__ == "__main__":

    st.title("LM Studio Chatbot")

    # Initialize the chat history with the instruction
    if "messages" not in st.session_state:
        history = [
        {"role": "system", "content": get_instruction()},
        {"role": "assistant", "content": "Please provide the email text."},            ]
        st.session_state["messages"] = history

    # Display the chat history / welcome message
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            st.chat_message(msg["role"]).write(msg["content"])
        
    
    # If the user provides a prompt, send it to the assistant and display the response
    if prompt := st.chat_input():

        #Connect to the local server
        client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
        
        # Add the user message to the chat history in the session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # write the user message to the chat
        st.chat_message("user").write(prompt)
        
        
        # Send the chat history to the assistant
        completion = client.chat.completions.create(
            model="local-model", # this field is currently unused
            messages=st.session_state.messages,
            temperature=0.1,
            stream=True,
            )
        
        message = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                message += chunk.choices[0].delta.content
                
        st.session_state.messages.append({"role": "assistant", "content": message})
        
        st.chat_message("assistant").write(message)
\
       
        
        
    
        # import streamlit as st
    # import shared.functions_common as oc2c
    # oc2c.configure_streamlit_page(Title="Calendar Event Finder (Local LM Studio)")


    # request = None

    # email = st.text_area("Email Body", key='query', height=200, help="Enter your email body here")

    # if st.button(label= "Submit",    key='submit'):
    #     request = email

    # col1, col2 = st.columns([1, 1])

    # with col1:
    #     st.write("You entered: ", email)

    # with col2:
    #     if request is not None:
    #         result = extract_events(request)
    #         st.header('Events', divider='rainbow')
    #         st.text(result)