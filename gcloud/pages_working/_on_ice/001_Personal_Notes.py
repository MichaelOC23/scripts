import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import date, datetime, timedelta
from sqlalchemy import text


import classes._class_storage as Storage
import classes._class_streamlit as cs


# from helper.db import initialize_and_create_connection
# from helper.message import update_archived, update_pinned, generate_summary


class NoteManagement:
    def __init__(self):
        pass

    def initialize_and_create_connection(self, st):
        # Create the SQL connection to messages_db as specified in your secrets file.
        conn = st.connection("messages_db", type="sql", ttl=None)

        self.create_message_table(conn)
        self.create_project_table(conn)
        self.create_note_table(conn)

        # Flush the cache to ensure that the data is up to date
        st.cache_data.clear()

        return conn

    def create_message_table(self, conn):
        with conn.session as s:
            s.execute(text("""CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                role TEXT,
                project_id INTEGER,
                pinned BOOLEAN DEFAULT FALSE,
                archived BOOLEAN DEFAULT FALSE,
                timestamp DATETIME
            )"""))
            s.commit()

    def create_project_table(self, conn):
        with conn.session as s:
            s.execute(text("""CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                timestamp DATETIME
            )"""))
            s.commit()

    def create_note_table(self, conn):
        with conn.session as s:
            s.execute(text("""CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                date DATE,
                project_id INTEGER,
                timestamp DATETIME
            )"""))
            s.commit()
    
    def insert_message(self, conn, message, role="user", project_id=None):
        now = datetime.now()

        if project_id:
            with conn.session as s:
                s.execute(text(
                    "INSERT INTO messages (content, role, project_id, timestamp) VALUES (:message, :role, :project_id, :timestamp);"),
                    params=dict(message=message, role=role, project_id=int(project_id), timestamp=now)
                )
                s.commit()
        else:
            with conn.session as s:
                s.execute(text(
                    "INSERT INTO messages (content, role, timestamp) VALUES (:message, :role, :timestamp);"),
                    params=dict(message=message, role=role, timestamp=now)
                )
                s.commit()

    def insert_note(self, conn, content, project_id=None, date=None):
        now = datetime.now()

        if project_id:
            with conn.session as s:
                s.execute(text(
                    "INSERT INTO notes (content, project_id, timestamp) VALUES (:content, :project_id, :timestamp);"),
                    params=dict(content=content, project_id=int(project_id), timestamp=now)
                )
                s.commit()
        else:
            with conn.session as s:
                s.execute(text(
                    "INSERT INTO notes (content, date, timestamp) VALUES (:content, :date, :timestamp);"),
                    params=dict(content=content, date=date, timestamp=now)
                )
                s.commit()

    def update_pinned(self, conn, id, value):
        with conn.session as s:
            s.execute(text(
                "UPDATE messages SET pinned = :value WHERE id = :id;"),
                params=dict(value=value, id=id)
            )
            s.commit()

    def update_archived(self, conn, id, value):
        with conn.session as s:
            s.execute(text(
                "UPDATE messages SET archived = :value WHERE id = :id;"),
                params=dict(value=value, id=id)
            )
            s.commit()

    def convert_messages_to_log(self, conn, client, st, messages, has_ymd=False):
        events = []

        if len(messages) == 0:
            st.warning("No messages to export.")
            return

        for message in messages:
            if message["role"] == "user":
                if has_ymd:
                    events += "\n".join([message["timestamp"].strftime("%Y-%m-%d %H:%M:%S"), message["content"]])
                else:
                    events += "\n".join([message["timestamp"].strftime("%H:%M:%S"), message["content"]])

        return "\n\n".join(events)

    def generate_summary(self, conn, client, st, project_id=None, project_name=None, date=None):
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            message_history_all = st.session_state.messages.copy()
            message_history = list(filter(lambda m: not m["archived"], message_history_all))

            if project_id and project_name:
                history_log = self.convert_messages_to_log(conn, client, st, message_history, has_ymd=True)
                prompt = f"""The following text is a formatted log in the project named {project_name}. It may contain just memos or even fragmented words. Considering that, summarize it briefly. Do not use English unless the original text is written in it.
    ===
    Log:
    {history_log}
    ===
    Summary:
    """
            elif date:
                history_log = self.convert_messages_to_log(conn, client, st, message_history, has_ymd=False)
                prompt = f"""The following text is a formatted log in the journal on {date}. It may contain just memos or even fragmented words. Considering that, summarize it briefly. Do not use English unless the original text is written in it.
    ===
    Log:
    {history_log}
    ===
    Summary:
    """
            prompt_message = ({"role": "user", "content": prompt })

            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[prompt_message],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        if project_id:
            self.insert_note(conn, full_response, project_id=project_id)
        elif date:
            self.insert_note(conn, full_response, date=date)

helper = NoteManagement()

#
# Initialization
# 

cs.set_up_page(page_title_text="Personal Notes", jbi_or_cfy="jbi", light_or_dark="dark", 
    session_state_variables=[{'page_file_path': __file__}],
                            connect_to_dj=False)

conn = helper.initialize_and_create_connection(st)


#
# Side bar
#

st.sidebar.header("Journal")

# NOTE: Journal - daily / weekly / monthly
is_filtered_by_date = st.sidebar.checkbox("Filter by date")
date_selected = st.sidebar.date_input("Dates", "today")

st.sidebar.divider()

st.sidebar.header("Project")

# NOTE: Project - open / closed / archived
is_filtered_by_project = st.sidebar.checkbox("Filter by project")

with st.sidebar.expander("Create new project"):
    with st.form("new_project", border=False):
        project_name_input = st.text_input("Project name")
        project_submit_button = st.form_submit_button("Create")

    if project_submit_button and project_name_input:
        with conn.session as s:
            s.execute(text(
                "INSERT INTO projects (name, timestamp) VALUES (:name, :timestamp);"),
                params=dict(name=project_name_input, timestamp=datetime.now())
            )
            s.commit()

# Sort descending by timestamp
projects = conn.query("SELECT * FROM projects ORDER BY timestamp DESC")

if not projects.empty:
    st.session_state.projects = projects.to_dict(orient="records")
else:
    st.session_state.projects = []

# filter messages by project
project_id_selected = st.sidebar.radio("Projects", [project["id"] for project in st.session_state.projects], format_func=lambda id: projects.get(projects.id == id, {}).get("name", "").values[0])

# Area - other tag

# Resource - closed tag

st.sidebar.divider()


is_filtered_by_pinned = st.sidebar.checkbox("📌 Show only pinned")
is_filtered_by_archived = st.sidebar.checkbox("🗑️ Show also archived")

st.sidebar.divider()

#
# Settings
#

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

with st.sidebar.expander("Settings", expanded=False):
    # openai_api_key = st.text_input("OpenAI API key", value=st.secrets["OPENAI_API_KEY"])
    st.session_state["openai_model"] = st.text_input("OpenAI model", value=st.session_state["openai_model"])

client = OpenAI()

#
# Main content
#

if is_filtered_by_project and project_id_selected:
    st.title(projects.get(projects.id == project_id_selected, {}).get("name", "").values[0])
elif is_filtered_by_date and date_selected:
    st.title(date_selected.strftime("%Y/%m/%d"))
# elif len(st.session_state.selected_tags) > 0:
#     st.title(" ".join(st.session_state.selected_tags))
else:
    st.title("Notes")


# Summary

# Sort descending by timestamp
notes = conn.query("SELECT * FROM notes ORDER BY timestamp DESC")

# filter notes
if not notes.empty:
    if is_filtered_by_project and project_id_selected:
        notes = notes[notes.project_id == project_id_selected]
    elif is_filtered_by_date and date_selected:
        notes = notes[notes.date == date_selected.strftime("%Y-%m-%d")]
    else:
        notes = notes[0:0]

    st.session_state.notes = notes.to_dict(orient="records")
else:
    st.session_state.notes = []


# Query and display the data you inserted
if is_filtered_by_date and date_selected:
    messages = conn.query("SELECT * FROM messages WHERE timestamp >= :today AND timestamp < :next", params={"today": date_selected, "next": date_selected + timedelta(days=1)})
else:
    messages = conn.query("SELECT * FROM messages")

# Convert the 'timestamp' column to a datetime type
messages['timestamp'] = pd.to_datetime(messages['timestamp'])

# Populate project by project_id
messages['project'] = messages["project_id"].apply(lambda id: (conn.query("SELECT * FROM projects WHERE id = :id", params={"id": id}).iloc[0].to_dict() if not conn.query("SELECT * FROM projects WHERE id = :id", params={"id": id}).empty else None) if id else None)

if not messages.empty:
    if is_filtered_by_project:
        messages = messages[messages.project.apply(lambda project: project["id"] == project_id_selected if project else False)]
    if is_filtered_by_pinned:
        messages = messages[messages.pinned == True]
    if not is_filtered_by_archived:
        messages = messages[messages.archived == False]

    st.session_state.messages = messages.to_dict(orient="records")
else:
    st.session_state.messages = []


st.session_state.is_project_open = True

if len(st.session_state.notes) > 0:
    if (is_filtered_by_project and project_id_selected) or (is_filtered_by_date and date_selected):
        st.info(st.session_state.notes[0]["content"])
elif not is_filtered_by_date and not is_filtered_by_project:
    pass
    # st.info("_HiddenSource の秘伝のタレは、創業以来継ぎ足すことで、深い味わいを生み出しています。_")
    # st.info("""
    #         Welcome to HiddenSource! This is a chat-like memo app that helps you keep track of your daily activities. You can:
    #         - Filter by date to journal your day
    #         - Filter by project to separate your concerns
    #         - 📌 Pin a message to find it quickly later
    #         - 🗑️ Archive a message to hide it anywhere
    #         - Generate a summary of your activities using OpenAI's GPT-3.5/4
    # """)
elif len(st.session_state.messages) == 0:
    st.info("No activities found.")


#AI Summary Button
if len(st.session_state.messages) > 0:
    if is_filtered_by_project and project_id_selected and len(st.session_state.notes) > 0:
        st.session_state.is_project_open = st.checkbox("Reopen to add a memo", False)
        button_generate_summary = st.button("Generate Summary")
    elif is_filtered_by_date and date_selected and date_selected is not date.today():
        button_generate_summary = st.button("Generate Summary")
    else:
        button_generate_summary = False

    if button_generate_summary:
        if is_filtered_by_project and project_id_selected:
            helper.generate_summary(conn, client, st, project_id=project_id_selected, project_name=projects.get(projects.id == project_id_selected, {}).get("name", "").values[0])
        elif is_filtered_by_date and date_selected:
            helper.generate_summary(conn, client, st, date=date_selected)


# Display Notes (Messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["timestamp"]:
            id = message["id"]
            # If date is selected, show only time. Otherwise, show date and time.
            then = message["timestamp"].time() if is_filtered_by_date and date_selected else message["timestamp"]
            then = then.replace(microsecond=0)
            st.markdown(f"`{then}`\t`#{id}`")
        st.markdown(message["content"])

        col_pinned, col_archived = st.columns(2)
        checkbox_pinned = col_pinned.checkbox("📌 ", value=message["pinned"], key=f"pinned-{message['id']}")
        if message["pinned"] != checkbox_pinned:
            helper.update_pinned(conn, message["id"], checkbox_pinned)
        checkbox_archived = col_archived.checkbox("🗑️", value=message["archived"], key=f"archived-{message['id']}")
        if message["archived"] != checkbox_archived:
            helper.update_archived(conn, message["id"], checkbox_archived)

# Chat input
post = ""
if (not is_filtered_by_date or date_selected == date.today()) and st.session_state.is_project_open:
    post = st.chat_input("Enter your memo here")

if post:
    now = datetime.now()

    with st.chat_message("user"):
        st.markdown(f"`{now.strftime('%H:%M:%S')}`")
        st.markdown(post)

        col_pinned, col_archived = st.columns(2)
        checkbox_pinned = col_pinned.checkbox("📌 ", value=False, key="pinned-new-message-id", disabled=True)
        checkbox_archived = col_archived.checkbox("🗑️", value=False, key="archived-new-message-id", disabled=True)

    st.session_state.messages.append({"content": post, "timestamp": now, "role": "user", "project_id": project_id_selected, "archived": False, "pinned": False})

    # Insert some data with conn.session
    if is_filtered_by_project and project_id_selected:
        with conn.session as s:
            s.execute(text(
                "INSERT INTO messages (content, role, project_id, timestamp) VALUES (:message, :role, :project_id, :timestamp);"),
                params=dict(message=post, role="user", project_id=int(project_id_selected), timestamp=now)
            )
            s.commit()
    else:
        with conn.session as s:
            s.execute(text(
                "INSERT INTO messages (content, role, timestamp) VALUES (:message, :role, :timestamp);"),
                params=dict(message=post, role="user", timestamp=now)
            )
            s.commit()

if is_filtered_by_project and project_id_selected and len(st.session_state.messages) > 0 and st.session_state.is_project_open:
    button_close_and_generate_summary = st.button("Close and generate Summary")
    if button_close_and_generate_summary:
        if is_filtered_by_project and project_id_selected:
            helper.generate_summary(conn, client, st, project_id=project_id_selected, project_name=projects.get(projects.id == project_id_selected, {}).get("name", "").values[0])
        elif is_filtered_by_date and date_selected:
            helper.generate_summary(conn, client, st, date=date_selected)
