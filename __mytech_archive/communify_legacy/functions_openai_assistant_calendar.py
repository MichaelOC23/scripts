 # Importing required packages
import streamlit as st
import time
from openai import OpenAI


# Set your OpenAI API key and assistant ID here
assistant_id    = "asst_zqC1QIHOAXN7zVjuq5KXbYGQ"

# Set openAi client , assistant ai and assistant ai thread
@st.cache_resource
def load_openai_client_and_assistant():
    client          = OpenAI()
    my_assistant    = client.beta.assistants.retrieve(assistant_id)
    thread          = client.beta.threads.create()

    return client , my_assistant, thread

client,  my_assistant, assistant_thread = load_openai_client_and_assistant()

# check in loop  if assistant ai parse our request
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

# initiate assistant ai response
def get_assistant_response(user_input=""):

    message = client.beta.threads.messages.create(
        thread_id=assistant_thread.id,
        role="user",
        content=user_input,
    )

    run = client.beta.threads.runs.create(
        thread_id=assistant_thread.id,
        assistant_id=assistant_id,
    )

    run = wait_on_run(run, assistant_thread)

    # Retrieve all the messages added after our last user message
    messages = client.beta.threads.messages.list(
        thread_id=assistant_thread.id, order="asc", after=message.id
    )

    return messages.data[0].content[0].text.value


if __name__ == "__main__":
    import shared.functions_common as oc2c
    oc2c.configure_streamlit_page(Title="Calendar Event Finder (Assistant)")


    request = None
    st.title("🍕 Papa Johns Pizza Assistant 🍕")

    email = st.text_area("Email Body", key='query', height=200, help="Enter your email body here")

    if st.button(label= "Submit",    key='submit'):
        request = email

    colw1, colw2 = st.columns([1, 1])

    with colw1:
        st.write("You entered: ", email)

    with colw2:
        if request is not None:
            result = get_assistant_response(request)
            st.header('Events', divider='rainbow')
            st.text(result)