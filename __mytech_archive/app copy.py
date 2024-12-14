
# Main App Libraries 
import streamlit as st
from _class_streamlit import streamlit_mytech, office_tools, office365_auth, create_new_grid
from streamlit_extras.stylable_container import stylable_container
import streamlit_shadcn_ui as ui
import streamlit_antd_components as sac
from google.cloud.firestore import FieldFilter 


stm = streamlit_mytech("Assistant", auth=True)
o365_auth = office365_auth()
stm.set_up_page(initial_sidebar_state='collapsed')

def display_session_state(Label='', filter=None):
    with st.expander(Label, expanded=False):
        for key, value in st.session_state.items():
            text = f'session_state: {key}: {value}'[:50]
            if filter:
                if filter in text:
                    st.write(text)
            else: st.write(text)

from _class_firebase import FirestoreStorage
fire_db = FirestoreStorage()

from streamlit_ace import st_ace, KEYBINDINGS, LANGUAGES, THEMES  # type: ignore
from streamlit_tags import st_tags # type: ignore


from _class_deepgram_final import deepgram_prerecorded_audio_transcription
dg = deepgram_prerecorded_audio_transcription()

import pandas as pd, requests, json, asyncio, numpy as np, os, uuid, traceback
from datetime import datetime
from PIL import Image, ImageDraw
from io import BytesIO
import cairosvg
from google.cloud import firestore
from pydub import AudioSegment
from io import BytesIO

import nest_asyncio
from functools import wraps


def handle_async_operation(async_func):
    """
    Decorator to properly handle async operations in Streamlit
    Ensures tasks are properly awaited and cleaned up
    """
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        try:
            # Get or create an event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Create and run the task with a timeout
            task = loop.create_task(async_func(*args, **kwargs))
            
            # Run the task and ensure it completes
            try:
                return loop.run_until_complete(task)
            except asyncio.CancelledError:
                st.error("Operation was cancelled")
                raise
            except Exception as e:
                st.error(f"Operation failed: {str(e)}")
                traceback.print_exc()
                raise
            finally:
                # Clean up any pending tasks
                pending = asyncio.all_tasks(loop)
                for t in pending:
                    if not t.done():
                        t.cancel()
                # Wait for all tasks to complete or be cancelled
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                
        except Exception as e:
            st.error(f"Failed to handle async operation: {str(e)}")
            traceback.print_exc()
            raise
            
    return wrapper




def format_pill_for_modal(value):
        
    format_dict = {
        "Complete" : ":material/check: Complete",
        "Incomplete": ":material/close_small: Incomplete",
        "Today" : ":material/clear_day: Today",
        "Next" : ":material/south_east: Next",
        "Later": ":material/timer_off: Later",
        True : ":material/star: Starred",
        False : ":material/pen_size_2:"
        }
    formatted_value = format_dict.get(value, value)
    return formatted_value



view_type_options = ['Kanban', 'Grid']
shadcn_path='pages_menu/shadcn'
show_settings=False
dev_mode=False
use_aggrid = True
if dev_mode: show_settings=True


if True:
    # Defaults (Topic Logo)
    if 'default_logo_url' not in st.session_state: st.session_state['default_logo_url'] =  "https://firebasestorage.googleapis.com/v0/b/toolsexplorationfirebase.appspot.com/o/logos%2Fdefault.svg?alt=media&token=cfee9595-c998-4be8-ba86-804a4330d204"
    
    #Firebase Session State Variables
    if 'collection' not in st.session_state: st.session_state['collection'] = 'action-activity'
    if 'project' not in st.session_state: st.session_state['project'] = 'toolsexplorationfirebase'
    if 'db' not in st.session_state: st.session_state['db'] = firestore.Client(project=st.session_state['project'])

    # UI Session State Variables
    if 'col_count' not in st.session_state: st.session_state['col_count'] = 2                       # Number of columns in each container
    if 'max_rows' not in st.session_state: st.session_state['max_rows'] = 20                        # Maximum number of rows
    if 'view_type' not in st.session_state: st.session_state['view_type'] = view_type_options[0]    # Kanban or Grid
    if 'containers' not in st.session_state: st.session_state['containers'] = {}                    # Dictionary to store container (row) references
    if 'slots' not in st.session_state: st.session_state['slots'] = {}                  
    if 'dirty_data' not in st.session_state: st.session_state['dirty_data'] = True    
    if 'show_labels' not in st.session_state: st.session_state['show_labels'] = 'collapsed' #       Whether to refresh data on next load
    if 'slot_filter' not in st.session_state: st.session_state['slot_filter'] = ['All']

    # Task Data Session State Variables
    if 'tasks_by_topic' not in st.session_state: st.session_state['tasks_by_topic'] = {}
    if 'non_blank_tasks_by_topic' not in st.session_state: st.session_state['non_blank_tasks_by_topic'] = {}
    if 'task_dict' not in st.session_state: st.session_state['task_dict'] = {}

    # Topic Data Detail Session State Variables
    if 'topic' not in st.session_state: st.session_state['topic'] = ''
    if 'topics' not in st.session_state: st.session_state['topics'] = []
    if 'topic_dict' not in st.session_state: st.session_state['topic_dict'] = {}
    if 'topics_dict' not in st.session_state: st.session_state['topics_dict'] = {}
    if 'topics_by_name_dict' not in st.session_state: st.session_state['topics_by_name_dict'] = {}

    # Note Data Detail Session State Variables
    if 'open_note_dict' not in st.session_state: st.session_state['open_note_dict'] = {}  
    if 'open_note_content' not in st.session_state: st.session_state['note_content'] = ''
    if 'open_note_container'not in st.session_state: st.session_state['open_note_container'] = None
    if 'note_dicts_dict_for_open_topic' not in st.session_state: st.session_state['note_dicts_dict_for_open_topic'] = {}
    if 'temp_note_content'not in st.session_state: st.session_state['temp_note_content'] = None
    if 'note_radio_987'not in st.session_state: st.session_state['note_radio_987'] = ''
    

    if 'note_editor_disabled' not in st.session_state: st.session_state['note_editor_disabled'] = False
    if 'ace_themes' not in st.session_state: st.session_state['ace_themes'] =  [ "chrome", "clouds", "iplastic", "solarized_light", "pastel_on_dark", "solarized_dark", "cobalt", "tomorrow_night_blue", "twilight"]
    if 'ace_theme' not in st.session_state: st.session_state['ace_theme'] =  "clouds"
    
    

    # grids and formats
    if 'topic_type_colors' not in st.session_state: st.session_state['topic_type_colors'] = {
        "Client":   "#00FFFF", "Internal": "#8A2BE2", "Partner": "#0000FF", "John": "#FF8C00", "Prospect":   "#FF00FF",
        "Personal": "#00FF00",  "TBD":      "#FFFF00"}
    

if dev_mode: display_session_state('Start', 'topic')
#! ################################                
#? #####      SHARED    ###########
#! ################################
if True: 
    def admin():
        st.sidebar.markdown(" ###### Setting / Admin")
        if st.sidebar.button("Search RIA Database"):
            rias = st.session_state['db'].collection(st.session_state['collection']).limit(20).stream()
            rias_dict = {}
            for ria in rias:
                ria_dict = ria.to_dict()
                rias_dict[ria.id]=ria_dict

    @st.dialog("Settings", width='large')
    def view_settings():
        if st.button("Load default topics"):
            load_default_topics()
        if st.button("Close", type='primary'):
            st.rerun()


#! ########################################                
#? #####      TASK FUNCTIONS    ###########
#! ########################################
if True: 
    def filter_slots():
        filter_options = list(st.session_state['topic_type_colors'].keys())
        if 'All' in st.session_state['slot_segment_filter']:
            st.session_state['slot_segment_filter'] = filter_options
            st.session_state['slot_filter'] = ['All']
            return
        
        if 'None' in st.session_state['slot_segment_filter']:
            st.session_state['slot_segment_filter'] = []
            st.session_state['slot_filter'] = ['None']
            return
        
        st.session_state['slot_filter'] = st.session_state['slot_segment_filter']
        return

    def display_task_header():
        st.subheader("Priority Actions")
        header = st.container(border = False)
        filter_col, col_num_col, create_task = header.columns([7, 2, 1], vertical_alignment='center', gap='medium')
        if create_task.button("", key="topicbutton", use_container_width=True, type="primary", icon=':material/view_object_track:'): create_topic()
        if create_task.button("", key="create_task_header_button", use_container_width=True, type="primary", icon=':material/add:'): new_task_modal()
        if st.sidebar.button("", key="settings_button", use_container_width=True, type="primary", icon=':material/settings:'): view_settings()
        col_num_col.number_input(label="# of Columns",min_value=2, max_value=5,  key="col_count", label_visibility='collapsed',) # col_num_col.slider("Columns", 1,5,label_visibility='collapsed', key="col_count")
        col_num_col.segmented_control(label="segment", options=view_type_options, selection_mode='single', key='view_type', label_visibility='collapsed')
        filter_col.segmented_control(label="Type", options=['All', 'None']+list(st.session_state['topic_type_colors'].keys()),key="slot_segment_filter", label_visibility='collapsed',selection_mode="multi", on_change=filter_slots)
        filter_col.segmented_control(label="Status", default='All', options=["All", 'Starred', 'Today', 'Open', 'Next', 'Not Now', 'Closed'], key="slot_status_filter", label_visibility='collapsed',selection_mode="single", on_change=filter_slots)

    def create_task_ui(col_count, containers, slots, topics):
        # Dynamically create "n" containers with unique keys
        slot_num = 0
        row_count = min(
            int(round((len(topics)/col_count)+.5,0)), st.session_state['max_rows'])
        for i in range(1, row_count + 1):
            key = f"r{i}"  # Unique key for each container
            containers[key] = st.container(border=False)  # Create the container and store it

            # Create columns (slots) within each container
            if col_count == 1: slot1 = containers[key].columns(col_count)
            elif col_count == 2: slot1, slot2 = containers[key].columns(col_count)
            elif col_count == 3: slot1, slot2, slot3 = containers[key].columns(col_count)
            elif col_count == 4: slot1, slot2, slot3, slot4 = containers[key].columns(col_count)
            elif col_count == 5: slot1, slot2, slot3, slot4, slot5 = containers[key].columns(col_count)
            elif col_count == 6: slot1, slot2, slot3, slot4, slot5, slot6 = containers[key].columns(col_count)
            
            if col_count >=1: slots[f"s.{(slot_num + 1)}"] = slot1
            if col_count >=2: slots[f"s.{(slot_num + 2)}"] = slot2
            if col_count >=3: slots[f"s.{(slot_num + 3)}"] = slot3
            if col_count >=4: slots[f"s.{(slot_num + 4)}"] = slot4
            if col_count >=5: slots[f"s.{(slot_num + 5)}"] = slot5
            if col_count >=6: slots[f"s.{(slot_num + 6)}"] = slot6
            slot_num += col_count
        st.session_state['slots'] = slots
        st.session_state['containers'] = containers

    def display_tasks_kanban():
        topic_num = 0
        for topic_doc_id, topic_dict in st.session_state['tasks_by_topic'].items():
            
            sf = st.session_state['slot_filter']
            if 'None' in sf:
                break
            if not 'All' in sf:
                topic_type = st.session_state['topics_dict'][topic_doc_id].get('type', '')
                if not topic_type in sf: 
                    continue
            topic_num+=1
                
            topic_title = st.session_state['topics_dict'].get(topic_doc_id, {}).get('topic', None)
            if not topic_title:
                missing_topic_dict = get_topic_by_name('TBD')
                topic_title = missing_topic_dict.get('topic', 'TBD')
                topic_doc_id = missing_topic_dict.get('document_id', 'TBD')
                for taskid, task_dict in topic_dict.items():
                    task_dict['topic_list'].append(topic_doc_id)
                    # asyncio.run(fire_db.upsert_merge(task_dict.get('document_id', ''),  st.session_state['collection'], task_dict))
                st.rerun()
            obj_for_with = st.session_state['slots'][f"s.{topic_num}"]
            
            with obj_for_with:
                key_value = f"t.{topic_num}{uuid.uuid4()}"
                
                # The box that containst the topic title, drill in button, and list of tasks        
                task_container = st.container(border=True, key=f"t.{topic_num}{uuid.uuid4()}")
                with task_container:
                    
                    # 2-Column header for the container that contains the tipic tile and dill in button
                    topic_name_col, topic_drill_in_col = task_container.columns([75,10])
                    with topic_name_col: sac.divider(label=topic_title.upper(), size='sm', align='center ', variant='dashed', color="#003366")
                    
                    drill_topic = topic_drill_in_col.button(label="", 
                                              key=key_value, 
                                              use_container_width=False,
                                              type='secondary',
                                              on_click=set_topic_for_drill_in_display,
                                              kwargs={"topic_document_id": topic_doc_id},
                                              icon=":material/arrows_more_up:",# icon=":material/arrow_outward:",
                                              )
                    if drill_topic:
                        st.rerun()
                    

                                                
                    
                    # Display as many tasks as there are in the topic
                    task_num=0
                    for taskid, task_dict in topic_dict.items():
                        task_num+=1
                        t_text, t_pills = task_container.columns([5,5])
                        with t_text:
                            ui.checkbox(default_checked=task_dict.get('isComplete', False), label=task_dict.get('text', ''),key=f"{taskid}|{topic_num}1")

                            # input_value = ui.input(default_value=task_dict.get('text', ''), type='text',  key=f"{taskid}|{topic_num}1")

    def display_tasks_as_grid():
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame.from_dict(st.session_state['task_dict'], orient="index")
        df_topics = pd.DataFrame.from_dict(st.session_state['topics_dict'], orient="index")
        
        if len(df) ==0 or len(df_topics) ==0:
            return
        
        df_topics = df_topics.rename(columns={"topic": "Topic Name", "type": "Type"})
        df = df.rename(columns={"text": "Action", "created": "Created", "modified": "Modified", "status": "Status", "today": "Today", "starred": "Starred"})
        
        df_topics = df_topics[["document_id", "Topic Name", "Type"]]
        df = df.merge(df_topics, left_on="topic", right_on="document_id", how="left")
        df.set_index("document_id", inplace=True)

        
        df = df[["Topic Name", "Type", "Action", "Created", "Modified", "Today", "Status", "Starred"]]
        # st.write(df)
        
        if use_aggrid:
            new_aggrid = create_new_grid()
            override = {"Today": {"width": 15}, "Open": {"width": 15}}
            grid_options = new_aggrid.create_default_grid(df, col_dict = override)
            new_aggrid.display_grid(df, grid_options=grid_options)
        
        else: 
            columns_to_display = ['Topic', 'Action', 'Open', 'Today', 'Starred']
            edited_df = st.data_editor(
                                    df, 
                                    # column_config=column_config, 
                                    hide_index=True, 
                                    use_container_width=True,  
                                    num_rows='dynamic', 
                                    key="wmIL_data_grid")

            # Show the edited DataFrame for demonstration
            st.write(edited_df)
    
    @st.dialog("Add New Aciton", width='large')
    def new_task_modal():
        
        task_text = st.text_area("Action Details")
        topic_list = st.multiselect("Topics", st.session_state['topics'])

        c, s, l, t = st.columns(4)
        with c: isComplete = ui.checkbox(default_checked=False, label='Complete',key=f"{uuid.uuid4()}")
        with s: isStarred = ui.checkbox(default_checked=False, label='Starred',key=f"{uuid.uuid4()}")
        with l: isLater = ui.checkbox(default_checked=False, label='Later',key=f"{uuid.uuid4()}")
        with t: isToday = ui.checkbox(default_checked=False, label='Today',key=f"{uuid.uuid4()}")

        cancel_btn, save_btn = st.columns(2)

        if cancel_btn.button(label="Cancel", key = "cancel_button", use_container_width=True):
            st.rerun()
            
        if save_btn.button(label="Save", key="save_button", type="primary", use_container_width=True):
            create_new_task(topic_name_list=topic_list, text=task_text, isComplete=isComplete, isStarred=isStarred, isToday=isToday, isLater=isLater, taskid=None)
            st.rerun()
    
    def create_new_task(topic_name_list, text='', isComplete=False, isStarred=False, isToday=False, isLater=False, taskid=None):
        
        if not taskid: taskid = f"{uuid.uuid4()}"
        topic_document_id_list = []
        
        if isinstance(topic_name_list, list):
            for topic_name in topic_name_list:
                topic_document_id_list.append(st.session_state['topics_by_name_dict'][topic_name])
        else:
            topic_document_id_list = [st.session_state['topics_by_name_dict'][topic_name_list]]


        task= { 
            'document_id': taskid, 
            'topic_list': topic_document_id_list,
            'text':text,
            'isComplete': isComplete,
            'isStarred': isStarred,
            'isToday': isToday,
            'type': 'task',
            'isLater': isLater,
            'modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "isPublic": False
            }
        
        asyncio.run(fire_db.upsert_merge(taskid,st.session_state['collection'], task))
        return task

    def get_topic_by_name(topic_name):
        for topic_doc_id in st.session_state['topics_dict'].keys():
            if topic_name == st.session_state['topics_dict'][topic_doc_id].get('type', ''):
                return st.session_state['topics_dict'][topic_doc_id]

        return None

    @handle_async_operation
    async def refresh_tasks(record_limit=500):
        if st.session_state['dirty_data']:
            
            entitled_task_dict = await fire_db.get_recent_documents_from_collection(
                    collection_name=st.session_state['collection'], 
                    record_limit=record_limit, 
                    convert_string_dates_in_dict_list_to_datetime=True, filters={"type": "task", "owner": "task"}
                    )


            # Gather the dictionaries from the query result
            for document_id, task_dict in entitled_task_dict.items():
                for topic_document_id in task_dict.get('topic_list', []):
                
                    if topic_document_id not in st.session_state['tasks_by_topic'].keys():
                        st.session_state['tasks_by_topic'][topic_document_id] ={}
                        st.session_state['non_blank_tasks_by_topic'][topic_document_id] ={}
                    
                    st.session_state['tasks_by_topic'][topic_document_id][task_dict['document_id']]= task_dict
                    st.session_state['task_dict'][task_dict.get('document_id', 'NO ID')] = task_dict
                    if task_dict.get('text', '').strip() != '':
                        st.session_state['non_blank_tasks_by_topic'][topic_document_id][task_dict['document_id']]= task_dict

            st.session_state['dirty_data'] = False

    #? CALL-BACK
    def update_task(task_document_id, updated_task_dict: dict ):
        
        if not task_document_id or task_document_id == '':
            st.error("update task called but no key was passed to identify the task.")
        
        if task_document_id in st.session_state['task_dict'].keys():
            task_to_update = st.session_state['task_dict'][task_document_id]
        
        for key, value in updated_task_dict:
            task_to_update[key] = value
        
        asyncio.run(fire_db.upsert_merge(task_document_id,st.session_state['collection'],task_to_update))
        
        
        
#! ########################################                
#? #####      TOPIC FUNCTIONS    ###########
#! ########################################
if True:
    
    #! DISPLAYING TOPICS
    def clear_topic():
        async_save_content(st.session_state['temp_note_content'])  # Call async save function
        st.session_state['topic'] = ''
        st.session_state['topic_dict'] = {}
        clear_note()

    
    def display_topic():
        
        def format_note_radio(value):
            try:
                return st.session_state['note_dicts_dict_for_open_topic'][value].get('note_title', 'No title')
            except:
                return "No Title"
        

            
        if not st.session_state['open_note_dict'] or st.session_state['open_note_dict'] =={}:
            if len(st.session_state['note_dicts_dict_for_open_topic'].keys()) >0:
                first_note_document_id = list(st.session_state['note_dicts_dict_for_open_topic'].keys())[0]
                st.session_state['open_note_dict'] = st.session_state['note_dicts_dict_for_open_topic'][first_note_document_id]
        
        
        
        fd = st.session_state['topic_dict']
            
        #! TOPIC Subheader
        logo_sidebar_sh_col, details_col, = st.columns([1.5,8.5]) 
        name_sh_col, syn_sh_col, types_sh_col, back_to_tasks_button_col = details_col.columns( [4,2,2,2], vertical_alignment='top')
        back_to_tasks_button_col.button(label="Back to Dashboard", key=f'{uuid.uuid4()}', on_click=clear_topic, use_container_width=True, icon=":material/keyboard_double_arrow_left:")                 
        logo_url = fd.get('logo', '')
        
        if not logo_url or logo_url == '': logo_sidebar_sh_col.image(st.session_state['default_logo_url'] ,use_container_width=True)
        else:
            formatted_image = format_image( logo_url)
            logo_sidebar_sh_col.image(formatted_image,use_container_width=True)
        name_sh_col.subheader( fd.get('topic', 'No Topic Details . . .'))
        name_sh_col.markdown(f"**Synonyms:** {', '.join(fd.get('alt_topics', ['No synonyms']))}")
        # with syn_sh_col:
        #     fd['alt_topics'] = st_tags(label='Synonyms', text='Press enter to add more', value=fd.get('alt_topics', []), maxtags = 10, key='focus_tags_syn')
        
        #! Note Section Header
        note_buttons_container = st.container(border=True)
        nbtn1, nbtn2, nbtn3, nbtn4 = note_buttons_container.columns( [4,1,1,1])
        
        #! Note Selector Menu
        if len(st.session_state['note_dicts_dict_for_open_topic'].keys())>0:
            nbtn1.radio(
                label="Select Note",
                options=st.session_state['note_dicts_dict_for_open_topic'].keys(), 
                horizontal=True,
                format_func=format_note_radio, on_change=set_display_note_callback, 
                args=("note_radio_987",),
                key='note_radio_987', label_visibility='collapsed'
                )
        
        
        #! New Note Button
        nbtn4.button(
            label='New Note', 
            key="add_note_for_topic_button", use_container_width=True,
            on_click=create_new_note_for_topic, icon=':material/add_notes:',
            kwargs={'topic_document_id': fd.get('document_id')},
            type='secondary')
        
            
        
        
        
        return note_buttons_container

    def format_image(url, object_color=None, background_color=None, corner_radius=8):
        """
        Modify an image's colors while preserving transparency and adding rounded corners.
        
        Args:
            url (str): URL of the image (SVG or PNG)
            object_color (tuple): RGB or RGBA tuple for the main object color
            background_color (tuple, optional): RGB or RGBA tuple for background color. Defaults to None.
            corner_radius (int, optional): Radius for rounded corners. Defaults to 8.
        
        Returns:
            PIL.Image: Modified image with new colors and rounded corners
        """
        # Download and open the image
        if not object_color: object_color = (255, 255, 255)
        if not url or url == '':
            url = "https://firebasestorage.googleapis.com/v0/b/toolsexplorationfirebase.appspot.com/o/logos%2Fdefault.svg?alt=media&token=cfee9595-c998-4be8-ba86-804a4330d204"
        
        response = requests.get(url)

        is_svg = (
            'image/svg' in response.headers.get('content-type', '').lower() or 
            url.lower().endswith('.svg')
        )
        
        if is_svg:
            # Convert SVG to PNG in memory
            png_data = cairosvg.svg2png(bytestring=response.content)
            img = Image.open(BytesIO(png_data))
        else:
            # Handle PNG directly
            img = Image.open(BytesIO(response.content))
        
        # Convert to RGBA if not already
        img = img.convert('RGBA')
        
        # Convert to numpy array for faster processing
        data = np.array(img)
        
        # Create alpha mask (1 where pixels are not fully transparent)
        alpha_mask = data[:, :, 3] > 0
        
        # Create new image array with same shape
        new_data = np.zeros_like(data)
        
        # Set object color for non-transparent pixels
        if len(object_color) == 3:
            object_color = (*object_color, 255)  # Add alpha channel if not provided
        new_data[alpha_mask] = object_color
        
        # Set background color for transparent pixels if provided
        if background_color is not None:
            if len(background_color) == 3:
                background_color = (*background_color, 255)  # Add alpha channel if not provided
            new_data[~alpha_mask] = background_color
        else:
            # Keep transparent pixels transparent
            new_data[~alpha_mask, 3] = 0
        
        # Convert back to PIL Image
        modified_img = Image.fromarray(new_data)
        
        # Create rounded corners mask
        mask = Image.new('L', modified_img.size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle mask
        width, height = modified_img.size
        draw.rounded_rectangle([(0, 0), (width-1, height-1)], 
                            radius=corner_radius, 
                            fill=255)
        
        # Apply rounded corners
        output = Image.new('RGBA', modified_img.size, (0, 0, 0, 0))
        output.paste(modified_img, mask=mask)
        
        return output
   
    #? CALL-BACK (This is the callback for the diagonal up arrow)
    def set_topic_for_drill_in_display(topic_document_id):
        st.session_state['topic'] = st.session_state['topics_dict'].get(topic_document_id, {}).get('topic', None)
        st.session_state['topic_dict'] = st.session_state['topics_dict'].get(topic_document_id, {})
    
    
    #! GETTING TOPICS
    @handle_async_operation
    async def refresh_topics(record_limit=100):
        if st.session_state['dirty_data']:
            # Query Firestore, ordered by 'timestamp' descending, limited to 'count'
            current_user = await fire_db.get_current_user()
            myquery = (st.session_state['db'].collection('topics')
                       .limit(record_limit)
                       .where(filter=FieldFilter('owner', "==", current_user))
                       .where(filter=FieldFilter('isPublic', "==", False))
                       )
            
            # myquery = myquery.where(filter=('isPublic', "==", False))
            myresults = myquery.stream()
            
            public_query = (st.session_state['db'].collection('topics')
                       .limit(record_limit)
                       .where(filter=FieldFilter('isPublic', "==", True))
                       )
            
            public_results = public_query.stream()
            

            # Gather the dictionaries from the query result
            st.session_state['topics'] = []
            for item in myresults:
                topic = item.to_dict()
                st.session_state['topics_dict'][topic.get('document_id')] = topic
                st.session_state['topics_by_name_dict'][topic['topic']] = topic.get('document_id')
                st.session_state['topics'].append(topic.get('topic', 'NO TOPIC NAME'))
            
            for item in public_results:
                topic = item.to_dict()
                st.session_state['topics_dict'][topic.get('document_id')] = topic
                st.session_state['topics_by_name_dict'][topic['topic']] = topic.get('document_id')
                st.session_state['topics'].append(topic.get('topic', 'NO TOPIC NAME'))
            
            
            st.session_state['topics'] = list(set(st.session_state['topics']))
 
    
    #! CREATING TOPICS
    @st.dialog("Create Topic", width='small')
    def create_topic():
        
        new_topic = st.text_input('Topic Name', key='topic_diag')
        if st.button("Create Topic", type='primary'):
            if new_topic and new_topic != '' and new_topic not in st.session_state['topics']:
                
                new_topic_dict = create_empty_topic_dict(new_topic)
                st.session_state['topics_dict'][new_topic_dict.get('document_id')]=new_topic_dict
                st.session_state['topics'].append(new_topic)
                # asyncio.run(fire_db.upsert_merge(new_topic_dict.get('document_id'), 'topics', new_topic_dict))
                                
                st.rerun()
            
            elif new_topic in st.session_state['topics']: st.warning(f"Topic '{new_topic}' already exists.")
            
            else: st.warning("Invalid topic")
        st.session_state['topics'].sort()
        st.divider()
        md_body = f"#### Existing Topics:   - {'   - '.join(st.session_state['topics'])}"
        md_body = md_body.replace('   -',   '\n   -')
        st.markdown(md_body)
        
    def create_empty_topic_dict(topic):
        new_topic_document_id = f"{uuid.uuid4()}"
        
        return {
                "document_id": new_topic_document_id,
                "topic": topic,
                "created": datetime.now(),
                "modified": datetime.now(),
                "logo": "",
                "status": 'Open',
                'type': 'topic',
                "color": '',
                "type": '',
                "tags": [],
                "alt_topics": [],
                "note_dict_list": [],
                "isPublic": False
                }

    @handle_async_operation
    async def handle_wrapper_load_default_topics(default_topic_list):
        
        progress_text = "Loading initial topics and tasks . . . "
        my_bar = st.progress(0, text=progress_text)

        count = 0
        st.success("Topics Created")
        my_bar.empty()
        for topic_dict in default_topic_list:
            count +=1
            my_bar.progress(count/len(default_topic_list), text=f"Loading topic and taks for {topic_dict.get('topic')}")
            empty_topic_dict = create_empty_topic_dict(topic_dict['topic'])
            empty_topic_dict.update(topic_dict)
            await fire_db.upsert_merge(empty_topic_dict.get('document_id'), 'topics', empty_topic_dict,)
    
    #? Default Data
    def load_default_topics():
    
        default_topic_list = [
            {"isPublic": True, "topic": "Royal Bank of Canada (RBC)", "ticker": "RY", "type": "Client"},
            {"isPublic": True, "topic": "Missing Type"},
            {"isPublic": True, "topic": "Bank of America Merrill Lynch (BAML)", "ticker": "BAC", "type": "Client"},
            {"isPublic": True, "topic": "Charles Schwab (& TD)", "ticker": "SCHW", "type": "Client"},
            {"isPublic": True, "topic": "Empower Retirement", "ticker": "EMP", "type": "Client"},
            {"isPublic": True, "topic": "Morgan Stanley", "ticker": "MS", "type": "Client"},
            {"isPublic": True, "topic": "Bank of Montreal (BMO)", "ticker": "BMO", "type": "Client"},
            {"isPublic": True, "topic": "J.P. Morgan", "ticker": "JPM", "type": "Client"},
            {"isPublic": True, "topic": "Fidelity", "ticker": "", "type": "Client"},
            {"isPublic": True, "topic": "National Australia Bank (NAB)", "ticker": "NAB.AX", "type": "Client"},
            {"isPublic": True, "topic": "Teachers Insurance and Annuity (TIAA)", "ticker": "", "type": "Client"},
            {"isPublic": True, "topic": "Bank of New York Mellon", "ticker": "BK", "type": "Client"},
            {"isPublic": True, "topic": "Wells Fargo", "ticker": "WFC", "type": "Client"},
            {"isPublic": True, "topic": "TD Waterhouse", "ticker": "TD", "type": "Client"},
            {"isPublic": True, "topic": "Financial Times (FT)", "ticker": "", "type": "Client"},
            {"isPublic": True, "topic": "MetLife", "ticker": "MET", "type": "Client"},
            {"isPublic": True, "topic": "Capital Group", "ticker": "", "type": "Client"},
            {"isPublic": True, "topic": "Refinitiv", "ticker": "", "type": "Client"},
            {"isPublic": True, "topic": "ASX", "ticker": "ASX.AX", "type": "Client"},
            {"isPublic": True, "topic": "Banco Santander", "ticker": "SAN", "type": "Client"},
            {"isPublic": True, "topic": "Commonwealth Bank of Australia", "ticker": "CBA.AX", "type": "Client"},

            {"isPublic": True, "topic": "Broadridge", "ticker": "", "type": "Prospect"},
            {"isPublic": True, "topic": "Wellington", "ticker": "", "type": "Prospect"},
            {"isPublic": True, "topic": "Glenmede", "ticker": "", "type": "Prospect"},
            {"isPublic": True, "topic": "Edward Jones", "ticker": "", "type": "Prospect"},
            {"isPublic": True, "topic": "Psalm Capital", "ticker": "", "type": "Prospect"},
            {"isPublic": True, "topic": "The London Co. (TLC)", "ticker": "", "type": "Prospect"},

            {"isPublic": True, "topic": "WealthTechs", "ticker": "", "type": "Partner"},
            {"isPublic": True, "topic": "Morningstar", "ticker": "", "type": "Partner"},
            
            {"isPublic": True, "topic": "TBD", "type": "TBD"},

            {"topic": "Ruth", "type": "Ruth"},
            {"topic": "Internal", "type": "Internal"},
            {"topic": "Expenses", "type": "Internal"},
            {"topic": "WC Part 2", "type": "Internal"},
            {"topic": "John", "type": "John"},
            {"topic": "Personal", "type": "Personal"},
            
        ]
        
        handle_wrapper_load_default_topics(default_topic_list)
            


#! ########################################                
#? #####      NOTE FUNCTIONS    ###########
#! ########################################
if True:
    
    # Note Data Detail Session State Variables
    # if 'open_note_dict' not in st.session_state: st.session_state['open_note_dict'] = {}  
    # if 'open_note_content' not in st.session_state: st.session_state['note_content'] = ''
    
    #! CREATING AND UPDATING NOTES
    @handle_async_operation
    async def handle_wrapper_convert_string_dates_to_datetime(any_dictionary):
        return_dictionary_list = await fire_db.convert_string_dates_to_datetime([any_dictionary])
        if len(return_dictionary_list)>0:
            return return_dictionary_list[0]
        else: 
            return any_dictionary
    
    def create_empty_note(topic_document_id, topic_title, note_document_id):

        
        note_dict = {"note_title" : f"{topic_title} Note",
                    "document_id": note_document_id,
                    "note_date":  datetime.now(),
                    "created": datetime.now(),
                    "modified": datetime.now(),
                    "template": "simple",
                    "note_md": "",
                    'type':'note',
                    "subject": "",
                    "attendees": "",
                    "task_document_ids": [],
                    "topic_document_id": topic_document_id,
                    "tags": [],
                    "summary": {},
                    "isPublic": False
                    }
        
        return note_dict
    
    @handle_async_operation
    async def create_new_note_for_topic(topic_document_id):
        new_note_document_id = f"{uuid.uuid4()}"
        empty_note_dict = create_empty_note(topic_document_id=topic_document_id, topic_title=f"{st.session_state['topic'].replace('Note', '').strip()} Note", note_document_id=new_note_document_id)
        await fire_db.insert_dictionary( collection_path=st.session_state['collection'], data_dictionary=empty_note_dict, document_id=new_note_document_id)
        st.session_state['open_note_dict'] = empty_note_dict
        st.session_state['open_note_content'] = empty_note_dict.get('note_md')
        pass
    
    @handle_async_operation
    async def async_save_content(content):
        try: 
            # print(f"{st.session_state['open_note_dict'].get('document_id', None)} | {st.session_state['collection']} | \n\n {st.session_state['open_note_dict']} | \n\n {content}" )
            open_note_document_id = st.session_state['open_note_dict'].get('document_id', None)
            if open_note_document_id:
                st.session_state['open_note_dict']['note_md'] =  content
                result = await fire_db.insert_dictionary(collection_path=st.session_state['collection'],
                                                         data_dictionary=st.session_state['open_note_dict'],
                                                         document_id=open_note_document_id)
                st.session_state["note_content"] = content
                print(result)
            return True
        except Exception as e:
            st.error(f"FAILED TO SAVE NOTE. ERROR: {e}")
            st.session_state['note_editor_disabled'] = True
            st.info('Note editor has been disabled to prevent loss of work.')
            return False

    @handle_async_operation
    async def refresh_notes_for_topic(topic: str, record_limit=50):

        if topic and topic != '':
            topic_doc_id = st.session_state['topics_by_name_dict'].get(topic, {})
            st.session_state['note_dicts_dict_for_open_topic'] = await fire_db.get_recent_documents_from_collection(
                        collection_name=st.session_state['collection'], 
                        record_limit=record_limit, 
                        convert_string_dates_in_dict_list_to_datetime=True, filters={"type": "note", "topic_document_id": topic_doc_id}
                        )

    #! DISPLAYING NOTES
    
    def clear_note():
        st.session_state['open_note_dict'] = {}  
        st.session_state['note_content'] = ''
        st.session_state['open_note_container'] = None
        st.session_state['note_editor_disabled'] = False
    
    def set_display_note_callback(session_state_key):
        note_document_id = st.session_state.get(session_state_key)
        set_display_note(note_document_id)
    
    def set_display_note(note_document_id=None):
        if not note_document_id and st.session_state['topic_dict'].get('notes_dict_list', []) != []:
            note_document_id = st.session_state['topic_dict'].get('notes_dict_list')[0]

        st.session_state['open_note_dict'] = {}
        st.session_state['open_note_dict'].update(st.session_state['note_dicts_dict_for_open_topic'].get(note_document_id))
        note_md_dict = asyncio.run(fire_db.get_document_by_id(note_document_id,st.session_state['collection']))
        st.session_state['open_note_dict']['note_md']=note_md_dict.get('note_md', '')
        st.session_state['open_note_content'] = note_md_dict.get('note_md', '')
        display_open_note()
    
    
    def display_open_note():
        
        st.session_state['open_note_dict'] = handle_wrapper_convert_string_dates_to_datetime(st.session_state['open_note_dict'])
        
        note_col = st.session_state['open_note_container']
        
        # Define the ui to show the note header    
        top_row = note_col.container(border=True)
        nc1, nc2, nc3 = top_row.columns([6,2,2],vertical_alignment='bottom')
        
        st.session_state['open_note_dict']['note_title'] = nc1.text_input("Title / Date", 
                        value=st.session_state.get('open_note_dict', {}).get('note_title', ''), 
                        key=f"note_title")
        
        date_box, size_box, wrap_box = nc1.columns([1,3,1])
        
        
        st.session_state['open_note_dict']['note_date'] = date_box.date_input (
                        label="Date", 
                        value=st.session_state.get('open_note_dict', {}).get('note_date', ''),  
                        key=f"note_date", 
                        format="YYYY.MM.DD", 
                        label_visibility='collapsed')

        # additional note settings
        nc3.selectbox("Theme", st.session_state['ace_themes'], key="ace_theme", )
        wrap = wrap_box.checkbox("Wrap enabled", value=True, key="wrapcheck")
        note_height = size_box.radio('Note Area', options=['Small','Medium', 'Large'],key="note_height",horizontal=True, label_visibility='collapsed') 
        note_height_dict = {"Small": 5, "Medium": 20, "Large": 40 }
                
        with note_col:
            st.session_state['temp_note_content'] = st_ace(
                value=st.session_state["note_content"],
                placeholder="Type notes here . . .",
                language="markdown",
                theme=st.session_state['ace_theme'],
                keybinding="vscode",
                font_size=18,
                tab_size=4,
                show_gutter=True,
                show_print_margin=False,
                wrap=wrap,
                auto_update=True,
                readonly=st.session_state['note_editor_disabled'],
                min_lines=note_height_dict[note_height],
                key='ace_editor',
            )
            
            save_status_message = st.empty()

        # Check for changes and trigger async save
        if st.session_state['temp_note_content'] and st.session_state['temp_note_content'] != st.session_state["note_content"]:
            save_status_message.caption("*Saving changes...*")
            async_save_content(st.session_state['temp_note_content'])  # Call async save function
            save_status_message.caption ("Saved")
            
        # Display the saved content
        st.subheader("Saved Content:")
        st.markdown(st.session_state["note_content"])





#! ##############################################                
#! ##########      MAIN LOGIC    ################
#! ##############################################
if True:

    def display_task_dashboard_page():    
        if st.session_state['topic'] and st.session_state['topic'] != '':
            if st.session_state['topic_dict'] =={}: 
                st.session_state['topic_dict'] = st.session_state['topics_by_name_dict'].get(st.session_state['topic'], None)
                if not st.session_state['topic_dict']:
                    st.error(f'Missing topic dictionary for topic {st.session_state['topic_dict']}.  Cannot proceed.')
                    st.stop()

            # Screen is in #!    <<<<<<    TOPIC MODE    >>>>>>>>>
            refresh_notes_for_topic(st.session_state['topic'])
            st.session_state['open_note_container'] = display_topic()
            
            if st.session_state['open_note_dict'] and st.session_state['open_note_dict'] != {} and st.session_state['topic'] and st.session_state['topic'] != '' and st.session_state['open_note_container'] :
                display_open_note()
            
            
        else:
            # Screen is in #! <<<<<<    TASK MODE    >>>>>>>>>
            refresh_topics()
            refresh_tasks()
            
            
            # Tasks as Grid
            if st.session_state['view_type'] == 'Grid': 
                display_task_header()
                display_tasks_as_grid()
            
            # Tasks as Kanban
            else: #Create UI Objects on UI to display task slots / displays taks
                display_task_header()
                create_task_ui(st.session_state['col_count'], 
                            st.session_state['containers'], 
                            st.session_state['slots'], 
                            st.session_state['topics_dict'])
                display_tasks_kanban()

    def display_file_uplaod_audio():
        st.session_state['audio_file_list'] = st.session_state['audio_file_uploader_col'].file_uploader(label="Upload Audio Recording",
                                type=dg.AUDIO_PATH_EXTENSIONS, 
                                accept_multiple_files=True, key = "uploader_for_prerec_audio" )

    def display_transcribe_prerecorded_audio():
        if not 'audio_file_list' in st.session_state: st.session_state['audio_file_list'] = None
        if not 'audio_file_uploader_col' in st.session_state: st.session_state['audio_file_uploader_col'] = None
        if not 'new_recordings_to_transcribe_dict' in st.session_state: st.session_state['new_recordings_to_transcribe_dict'] = {}
        
        st.markdown("#### :blue[Transcribe Recorded Audio]")
        st.divider()
        
        st.session_state['audio_file_uploader_col'], result_col = st.columns([3,5])
        display_file_uplaod_audio()
        
        docs_dict = asyncio.run(fire_db.get_recent_uploaded_documents('recorded-audio-files'))
        docs_df = pd.DataFrame.from_dict(docs_dict, orient='index')

        
        if len(docs_dict.items()) >0:
            result_col.dataframe(docs_df, hide_index=True)
            
        
        # Process each uploaded file
        if st.session_state['audio_file_list']:
            for uploaded_file in st.session_state['audio_file_list']:


                # file_obj=None,     # Source file object for a in memory file/object
                # destination_blob_name=None, #name of the file in storage
                # collection_path=None, #sub-folder path in storage for the file
                # upload_dict=None, # record of the uploaded file to upload to firestore
                # bucket_name = None # bucket name of overall storage container

                # Read the uploaded file into memory
                file_obj = uploaded_file.getvalue()

                
                upload_dict = {
                    "file_path": uploaded_file.name,
                    "file_name": uploaded_file.name,
                    "file_title": uploaded_file.name,
                    'collection_path':'recorded-audio-files',
                    "file_size": uploaded_file.size,
                    "file_type": uploaded_file.type,
                    "bucket_name": 'recorded-audio-transcriptions-json',
                    "destination_blob_name": uploaded_file.file_id,
                    "status": "upload_initiated",
                }

                # Convert M4A to MP3 using pydub

                # Load M4A file into AudioSegment
                audio = AudioSegment.from_file(BytesIO(file_obj), format="m4a")
                
                # Create MP3 file in memory
                mp3_buffer = BytesIO()
                audio.export(mp3_buffer, format="mp3")
                mp3_buffer.seek(0)  # Reset buffer position to the beginning

                # asyncio.run(fire_db.upload_file(file_obj=mp3_buffer, collection_path='recorded-audio-files',  destination_blob_name=uploaded_file.file_id,upload_dict=upload_dict))
                
                # Display success message
                st.success(f"Converted {uploaded_file.name} to MP3 format and uploaded the file.")
                st.rerun()
                
            st.session_state['audio_file_list'] = []

            
            pass

    def display_email_page():    

        access_token = o365_auth.get_current_access_token()
        if not access_token: return []
        
        ot = office_tools(access_token)
        
        email_dict_list = ot.get_emails()    
        email_df = pd.DataFrame(email_dict_list)
        email_df.set_index('id', inplace=True)
        
        if use_aggrid:
            new_aggrid = create_new_grid()
            # override = {"Today": {"width": 15}, "Open": {"width": 15}}
            grid_options = new_aggrid.create_default_grid(email_df) #, col_dict = override)
            new_aggrid.display_grid(email_df, grid_options=grid_options)
            
            # ui.table(data=email_df, maxHeight=300)
            # st.write(ui.table)

            
        else: 
            ui.table(data=email_df, maxHeight=300)
            st.write(ui.table)


            edited_df = st.data_editor(
                                data=email_df,
                                hide_index=True, 
                                use_container_width=True,
                                num_rows='dynamic',
                                key="emaildata_grid2",)
            
    shadcn_page_list=os.listdir(shadcn_path)

    pages = {
        "Efficiency": [
            st.Page(display_task_dashboard_page, title="Task Dashboard", url_path="Task_Dashboard"),
            st.Page(display_transcribe_prerecorded_audio, title="Transcribe Recording", url_path="transcribe_pre_recorded_audio"),
            st.Page(display_email_page, title="Email", url_path = "email_recent"),
        
            ],
        "Tools": [
            st.Page("PAGES_MENU/antdapp.py", title="AntD Components", url_path = "antd"),
            st.Page("PAGES_MENU/streamlit_ui_1.py", title="Streamlit #1", url_path = "ST1"),
            st.Page("PAGES_MENU/streamlit_ui_2.py", title="Streamlit #1", url_path = "ST2"),
            # st.Page("trial.py", title="Try it out"),
            ],
        
        "Shadcn": 
            [st.Page(f"pages_menu/shadcn/{file}", title=f"{file}", url_path = f"shadcn_{file}") for file in shadcn_page_list if '.py' in file]
        }

    pg = st.navigation(pages)
    pg.run()

    # Display selected note
    

    if dev_mode: display_session_state('End', 'topic')


