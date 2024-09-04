import os
import time
import pandas as pd
from datetime import datetime
import httpx
import time
from notion_client import Client, errors
from notion_client.errors import APIResponseError
from typing import Dict, List, Union
import streamlit as st
from  _class_streamlit import streamlit_mytech



class NotionDBManager:
    def __init__(self, token: str) -> None:
        self.notion = Client(auth=token)
        self.stm = streamlit_mytech()


    def create_property_schema(self, properties: Dict[str, str]) -> Dict:
        """
        Create a schema for the Notion database properties.
        :param properties: A dictionary where keys are property names and values are property types.
        :return: A dictionary representing the property schema.
        """
        property_schema = {}
        for name, type_ in properties.items():
            if type_ == "title":
                property_schema[name] = {"title": {}}
            elif type_ == "rich_text":
                property_schema[name] = {"rich_text": {}}
            elif type_ == "number":
                property_schema[name] = {"number": {"format": "number"}}
            elif type_ == "checkbox":
                property_schema[name] = {"checkbox": {}}
            elif type_ == "url":
                property_schema[name] = {"url": {}}
            elif type_ == "files":
                property_schema[name] = {"files": {}}
            else:
                raise ValueError(f"Unsupported property type: {type_}")
        return property_schema

    def create_database(self, parent_page_id: str, database_name: str, properties: Dict[str, str]) -> str:
        """
        Create a new database in Notion.
        :param parent_page_id: The UUID of the parent page where the database will be created.
        :param database_name: The name of the new database.
        :param properties: A dictionary of property names and types.
        :return: The ID of the created database.
        """
        property_schema = self.create_property_schema(properties)
        new_database = self.notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": database_name}}],
            properties=property_schema
        )
        return new_database["id"]

    def create_page(self, database_id: str, properties: Dict[str, Union[str, int, bool, List[Dict[str, str]]]]) -> str:
        """
        Create a new page (record) in the specified database.
        :param database_id: The ID of the database where the page will be created.
        :param properties: A dictionary of properties to define the page content.
        :return: The ID of the created page.
        """
        new_page = self.notion.pages.create(
            parent={"database_id": database_id},
            properties=properties
        )
        return new_page["id"]

    def update_page(self, page_id: str, properties: Dict[str, Union[str, int, bool, List[Dict[str, str]]]]) -> None:
        """
        Update an existing page (record) in the database.
        :param page_id: The ID of the page to update.
        :param properties: A dictionary of properties to update the page content.
        """
        self.notion.pages.update(page_id=page_id, properties=properties)

    def delete_page(self, page_id: str) -> None:
        """
        Delete a page (record) by archiving it.
        :param page_id: The ID of the page to archive (delete).
        """
        try:
            self.notion.pages.update(page_id=page_id, archived=True)
            print(f"Successfully archived page with ID: {page_id}")
        except errors.APIResponseError as e:
            if "Unsaved transactions" in str(e):
                print(f"Error archiving page with ID: {page_id}. Notion API encountered an internal error.")
            else:
                raise e  # Re-raise the exception if it's not the known issue

    def load_csv_to_database(self, csv_file: str, database_id: str, mapping: Dict[str, str], property_types: Dict[str, str]) -> None:
        """
        Load data from a CSV file into a Notion database.
        :param csv_file: The path to the CSV file.
        :param database_id: The ID of the target Notion database.
        :param mapping: A dictionary mapping CSV column names to Notion property names.
        :param property_types: A dictionary mapping Notion property names to their types.
        """
        df = pd.read_csv(csv_file)
        for _, row in df.iterrows():
            properties = {}
            for csv_column, notion_property in mapping.items():
                value = row[csv_column]
                prop_type = property_types[notion_property]  # Get the property type based on the Notion property name

                if prop_type == "title":
                    properties[notion_property] = {"title": [{"text": {"content": str(value)}}]}  # Ensure value is a string
                elif prop_type == "rich_text":
                    properties[notion_property] = {"rich_text": [{"text": {"content": str(value)}}]}  # Rich text handling
                elif prop_type == "checkbox":
                    properties[notion_property] = {"checkbox": bool(value)}
                elif prop_type == "number":
                    properties[notion_property] = {"number": value if pd.notna(value) else None}
                elif prop_type == "url":
                    properties[notion_property] = {"url": value}
                elif prop_type == "files":
                    properties[notion_property] = {
                        "files": [{"name": os.path.basename(value), "external": {"url": value}}]
                    }
                else:
                    raise ValueError(f"Unsupported property type: {prop_type}")

            self.create_page(database_id, properties)

    def list_pages_in_database(self, database_id: str) -> Dict[str, str]:
        """
        List all pages (records) in the specified database.
        :param database_id: The ID of the database to query.
        :return: A dictionary with page names as keys and page IDs as values.
        """
        pages = {}
        response = self.notion.databases.query(database_id=database_id)
        for result in response["results"]:
            title = result["properties"]["Name"]["title"][0]["text"]["content"] if result["properties"]["Name"]["title"] else "Untitled"
            pages[title] = result["id"]
        return pages

    def get_all_objects(self, search_filter = '', types = ["page", "database"]):
        result_dict = {}
        for type in types:
            response = self.notion.search(query=f"{search_filter}",filter={"value":f"{type}","property":"object"})
            if response and len(response.get("results", [])) > 0 :
                for result in response.get('results', []):
                    if result.get('in_trash', False):
                        continue
                    parent_type = result.get('parent', {}).get('type', '')
                    object_type = result.get("object", '')
                    if object_type == 'database':
                        name = result.get('description', '')
                    else:
                        name = result.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', '')
                    if not name or name == '' :
                        name=result.get('title', [{}])[0].get('text', {}).get('content', '')
                    result_dict[result["id"]] = {
                        "name": name,
                        "parent_type": parent_type,
                        "parent_id": result.get('parent', {}).get(parent_type, parent_type),
                        "url": result.get("url", ""),
                        "object": object_type,
                        "properties": f"{result.get("properties", {}).keys()}"
                    }
        return result_dict

    def get_first_id_search(self, search_filter = '', types = ["page", "database"]):
        results = self. get_all_objects(search_filter= search_filter, types =types )
        if results != {}:
            for key in results.keys():
                return key

    def inspect_database(self, db_id):
        response = self.call_api("databases.retrieve", db_id=db_id)
        return {
            "Name": response.get("title", [{"text": {"content": "No title"}}])[0]["text"]["content"],
            "ID": response["id"],
            "Properties": response.get("properties", {})
        }

    def display_databases_in_streamlit(self) -> None:
        self.stm.set_up_page(page_title_text="Notion Class Inspection", session_state_variables=[{"db":{}}]) 
        #Call list databases function, iterate through the dictionary and print each key value pair in 3 column streamlit row, the 3rd column is a button, which if pressed will call the inspect function with that database id and write it to the screen.
        databases = self.list_databases()
        name_col, id_col, button_col = st.columns(3)
        name_col.write("Database Name")
        id_col.write("Database ID")
        button_col.write("Inspect")
        def set_db_id():
            st.session_state["db"] = databases[key]
        for key in databases:
            name_col.write(key)
            id_col.write(databases[key])
            btn_inspect = button_col.button("Inspect", on_click = set_db_id, key=f"{databases[key]}")
        if st.session_state["db"]:
            inspection_dict = self.inspect_database(st.session_state["db"])
            st.subheader(f"Inspection of: {st.session_state["db"]}")
            st.write(inspection_dict)
    
    def get_database_properties(self, database_id: str) -> Dict[str, str]:
        """
        Retrieve the properties of a database.
        :param database_id: The ID of the database to inspect.
        :return: A dictionary with property names as keys and their types as values.
        """
        response = self.notion.databases.retrieve(database_id=database_id)
        properties = response.get('properties', {})
        return {name: prop['type'] for name, prop in properties.items()}

    def create_file_import_db(self, file_name="", page_content_list = [], icon_emoji = "📁", parent_id = "") -> str:
        
        title = [{"type": "text", "text": {"content": file_name}}]
        icon = {"type": "emoji", "emoji": f"{icon_emoji}"}
        parent = {"type": "page_id", "page_id": parent_id}
        
        properties = {
            # "Name": {"title": {}},  # This is a required property
            "Page": {"title": {}},
            "Page Image": {"files": {}},
            "Page Text": {"rich_text": {}},            
        }
        new_db = self.notion.databases.create(parent=parent, title=title, properties=properties, icon=icon)
        
        # page_content_list = [
        # [1, "https://b3699545.smushcdn.com/3699545/wp-content/uploads/2024/07/communify-fincentric-final-white.png?lossy=0&strip=1&webp=1",
        #     "some text here about from the image"],
        # [2, "https://b3699545.smushcdn.com/3699545/wp-content/uploads/2024/07/communify-fincentric-final-white.png?lossy=0&strip=1&webp=1",
        #     "some text here about from the image"]]
        
        new_db_id = new_db.get('id')
        for page in page_content_list:
            properties ={   "Page": {"title": [{"text": {"content": f"Page {page[0]:03} / {len(page_content_list):03}"}}]},
                            "Page Image": {"files": [{  "name": f"Page {page[0]} of {len(page_content_list)}",
                                                        "external": {"url": f"{page[3]}"}}]},
                            "Page Text": {"rich_text": [{"text": {"content": f"{page[2]}"} }] }}
            time.sleep(.33)
            self.notion.pages.create(parent={"database_id": new_db_id}, properties=properties)
        
        return True
        
                    # "Page": {"title": [{"text": {"content": "Tuscan Kale"}}]},
                    # "Description": {"rich_text": [{"text": {"content": "A dark green leafy vegetable"}}]},
                    # "Food group": {"select": {"name": "Vegetable"}},
                    # "Price": {"number": 2.5}},
        


            # "files": [{"name": "Project Alpha blueprint",
                        # "external": {"url": "https://www.figma.com/file/g7eazMtXnqON4i280CcMhk/project-alpha-blueprint?node-id=0%3A1&t=nXseWIETQIgv31YH-1"}}]


        
        
        
        
        
        
        properties = {
            # "Name": {"title": {}},  # This is a required property
            "Page": {"title": {}},
            "Page Image": {"files": {}},
            "Page Text": {"rich_text": {}},            
        }
        new_db = self.notion.databases.create(parent=parent, title=title, properties=properties, icon=icon)
        
        # page_content_list = [
        # [1, "https://b3699545.smushcdn.com/3699545/wp-content/uploads/2024/07/communify-fincentric-final-white.png?lossy=0&strip=1&webp=1",
        #     "some text here about from the image"],
        # [2, "https://b3699545.smushcdn.com/3699545/wp-content/uploads/2024/07/communify-fincentric-final-white.png?lossy=0&strip=1&webp=1",
        #     "some text here about from the image"]]
        
        new_db_id = new_db.get('id')
        for page in page_content_list:
            properties ={   "Page": {"title": [{"text": {"content": f"Page {page[0]:03} / {len(page_content_list):03}"}}]},
                            "Page Image": {"files": [{  "name": f"Page {page[0]} of {len(page_content_list)}",
                                                        "external": {"url": f"{page[3]}"}}]},
                            "Page Text": {"rich_text": [{"text": {"content": f"{page[2]}"} }] }}
            time.sleep(.33)
            self.notion.pages.create(parent={"database_id": new_db_id}, properties=properties)
        
        return True
        
                    # "Page": {"title": [{"text": {"content": "Tuscan Kale"}}]},
                    # "Description": {"rich_text": [{"text": {"content": "A dark green leafy vegetable"}}]},
                    # "Food group": {"select": {"name": "Vegetable"}},
                    # "Price": {"number": 2.5}},
        


            # "files": [{"name": "Project Alpha blueprint",
                        # "external": {"url": "https://www.figma.com/file/g7eazMtXnqON4i280CcMhk/project-alpha-blueprint?node-id=0%3A1&t=nXseWIETQIgv31YH-1"}}]



        

# Replace 'your_notion_api_key' with your actual Notion API key or set it as an environment variable
if __name__ == "__main__":
    notion_api_key = os.getenv('NOTION_API_KEY', 'your_notion_api_key')


    notion = Client(auth=os.environ.get('NOTION_API_KEY'))
    notionDbMgr = NotionDBManager(os.getenv('NOTION_API_KEY'))
    import json
    page = notion.pages.retrieve(page_id="96edc3216e7248d583bfd0772ba045f4")
    blocks = notion.blocks.retrieve(block_id="96edc3216e7248d583bfd0772ba045f4")
    
    with open('page.json', 'w') as f:
        json.dump(page, f)
    
    with open('blocks.json', 'a') as f:
        blocks = notion.blocks.retrieve(block_id="96edc3216e7248d583bfd0772ba045f4")
        for block in blocks:
            block_content = notion.blocks.retrieve(block['id'])
            f.write(json.dumps(block_content, indent=4))
            f.write('\n\n')
            

    
    print (json.dumps(blocks, indent =4 ))
    print(page)
    
    
    def create_two_col():
        # Initialize the Notion client
        # The ID of the page where you want to add the columns
        parent_page_id = notionDbMgr.get_first_id_search("[Client Imports]")
         # Define the structure of the page content
        blocks = [
            # Header Block
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "[Client Imports]"}
                        }
                    ]
                }
            },
            # Text Block
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Here is some text at the top. Below starts the two columns"}
                        }
                    ]
                }
            },
            # Divider Block
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            # Columns List
            {
                "object": "block",
                "type": "column_list",
                "column_list": {}
            }
        ]

        # Append the blocks to the page
        try:
            response = notion.blocks.children.append(block_id=parent_page_id, children=blocks)
            column_list_id = response['results'][-1]['id']
        except Exception as e:
            print("Error creating main blocks: ", e)
            exit()

        # Define the columns
        columns = [
            {
                "object": "block",
                "type": "column",
                "column": {},
                "children": [
                    {
                        "object": "block",
                        "type": "image",
                        "image": {
                            "type": "external",
                            "external": {"url": "https://transcriptionpersonal.blob.core.windows.net/notionattachments/0259bea5-5755-4f9e-8c38-dc1c4414d771.png"}
                        }
                    }
                ]
            },
            {
                "object": "block",
                "type": "column",
                "column": {},
                "children": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {"content": "Here is the text that is in the 2nd column"}
                                }
                            ]
                        }
                    }
                ]
            }
        ]

        # Append columns to the column list
        try:
            notion.blocks.children.append(block_id=column_list_id, children=columns)
            print("Note created successfully in Notion.")
        except Exception as e:
            print("Error creating columns: ", e)
            exit()

    
    
    create_two_col()
    
    
    parent_id = notionDbMgr.get_first_id_search("[Client Imports]")
    new_db_id = notionDbMgr.create_file_import_db("Testdb", [], "📮", parent_id)
    print(new_db_id)
    
    
    # notionDbMgr.display_databases_in_streamlit()
    # database_id = "db_1234"
    # response = notion.databases.query(database_id=database_id)
    # page = notion.pages.retrieve(page_id=response["results"][0]["id"])


    exit()    
    notion = NotionDBManager(os.getenv('NOTION_API_KEY'))
    
    
    if False:
        token = os.getenv("NOTION_API_KEY")
        manager = NotionDBManager(token)

        # 1. Retrieve a valid parent page ID by listing top-level pages
        top_level_pages = manager.list_top_level_pages()
        if not top_level_pages:
            raise Exception("No top-level pages found in the workspace.")
        
        parent_page_id = next(iter(top_level_pages.values()))  # Get the first page ID
        print(f"Using parent page ID: {parent_page_id}")

        # 2. Create the database with all the necessary properties at the outset
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_note_id = manager.create_database(
            parent_page_id=parent_page_id,
            database_name=f"Test Note {timestamp}",
            properties={
                "Name": "title",             # Title type
                "Employee Number": "number", # Number type
                "Is Active": "checkbox",     # Checkbox type
                "Website": "url",            # URL type
                "Resume": "files",           # Files type
                "Profile Image": "files"     # Files type
            }
        )
        print(f"Created Test Note database with ID: {test_note_id}")



        # 3. Add one of each property type to the Test Note
        properties = {
            "Name": {"title": [{"text": {"content": "Record 1"}}]},  # Title type
            "Employee Number": {"number": 123},                      # Number type
            "Is Active": {"checkbox": True},                         # Checkbox type
            "Website": {"url": "https://example.com"},               # URL type
            "Resume": {"files": [{"name": "test.pdf", "external": {"url": f"file://{os.getcwd()}/test.pdf"}}]},  # Files type
            "Profile Image": {"files": [{"name": "test.png", "external": {"url": f"file://{os.getcwd()}/test.png"}}]}  # Files type
        }

        page_id = manager.create_page(database_id=test_note_id, properties=properties)
        print(f"Created page with ID: {page_id}")

        # 4. Update the properties with new values
        updated_properties = {
            "Name": {"title": [{"text": {"content": "Updated Name"}}]},  # Updated title
            "Employee Number": {"number": 456},                          # Updated number
            "Is Active": {"checkbox": False},                            # Updated checkbox
            "Website": {"url": "https://updated.com"},                   # Updated URL
            "Resume": {"files": [{"name": "test-updated.pdf", "external": {"url": f"file://{os.getcwd()}/test.pdf"}}]},  # Updated file
            "Profile Image": {"files": [{"name": "test-updated.png", "external": {"url": f"file://{os.getcwd()}/test.png"}}]}  # Updated image
        }

        manager.update_page(page_id=page_id, properties=updated_properties)
        print(f"Updated page with ID: {page_id}")

    ## Create the database (step 5)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db_id = manager.create_database(
            parent_page_id=parent_page_id,
            database_name=f"Test Database {timestamp}",
            properties={
                "Name": "title",             # Title type
                "Employee Number": "number", # Number type
                "Is Active": "checkbox",     # Checkbox type
                "Website": "url",            # URL type
                "Resume": "files",           # Files type
                "Profile Image": "files"     # Files type
            }
        )
        print(f"Created database with ID: {db_id}")

        # Verify the properties
        db_properties = manager.get_database_properties(db_id)
        print("Database Properties:", db_properties)

        # 6. Add 3 records to the database
        record1_id = manager.create_page(database_id=db_id, properties={"Name": {"title": [{"text": {"content": "Record 1"}}]}})
        record2_id = manager.create_page(database_id=db_id, properties={"Name": {"title": [{"text": {"content": "Record 2"}}]}})
        record3_id = manager.create_page(database_id=db_id, properties={"Name": {"title": [{"text": {"content": "Record 3"}}]}})
        print(f"Created records with IDs: {record1_id}, {record2_id}, {record3_id}")

        # 7. Delete one record
        manager.delete_page(page_id=record2_id)
        print(f"Deleted record with ID: {record2_id}")

        # 8. Update one record
        manager.update_page(page_id=record1_id, properties={"Name": {"title": [{"text": {"content": "Record 1 Updated"}}]}})
        print(f"Updated record with ID: {record1_id}")

        # 9. Retrieve and print properties of the updated record using list_pages_in_database
        pages = manager.list_pages_in_database(db_id)
        for name, pid in pages.items():
            if name == "Record 1 Updated":
                # Directly use the Notion API client's pages.retrieve method
                record_properties = manager.call_api('pages.retrieve', pid)['properties']
                
                # Now print the properties
                print("Record 1 Updated Properties:")
                print(f"Text Property: {record_properties['Name']['title'][0]['text']['content']}")
                print(f"Number Property: {record_properties['Employee Number']['number']}")
                print(f"Checkbox Property: {record_properties['Is Active']['checkbox']}")
                print(f"URL Property: {record_properties['Website']['url']}")

        # 10. Create a simple CSV and save it
        csv_data = {
            "Employee Name": ["Alice", "Bob", "Charlie"],
            "Employee Age": [30, 40, 25],
            "Is Active": [True, False, True],
            "Website": ["https://alice.com", "https://bob.com", "https://charlie.com"],
            "Resume Link": ["https://example.com/alice.pdf", "https://example.com/bob.pdf", "https://example.com/charlie.pdf"],
            "Image Link": ["https://example.com/alice.jpg", "https://bob.com/bob.jpg", "https://charlie.com/charlie.jpg"]
        }
        df = pd.DataFrame(csv_data)
        csv_file = "test_upload.csv"
        df.to_csv(csv_file, index=False)

        # 11. Create a new database for CSV upload
        csv_db_id = manager.create_database(
            parent_page_id=parent_page_id,
            database_name=f"CSV Upload {timestamp}",
            properties={
                "Name": "title",
                "Employee Number": "number",
                "Is Active": "checkbox",
                "Website": "url",
                "Resume": "files",
                "Profile Image": "files"
            }
        )
        print(f"Created CSV Upload database with ID: {csv_db_id}")

        # 12. Construct property types dictionary
        property_types = {
            "Name": "title",
            "Employee Number": "number",
            "Is Active": "checkbox",
            "Website": "url",
            "Resume": "files",
            "Profile Image": "files"
        }

        # Map the CSV columns to Notion properties and upload the CSV data
        csv_mapping = {
            "Employee Name": "Name",
            "Employee Age": "Employee Number",
            "Is Active": "Is Active",
            "Website": "Website",
            "Resume Link": "Resume",
            "Image Link": "Profile Image"
        }

        # Upload CSV data
        manager.load_csv_to_database(csv_file, csv_db_id, csv_mapping, property_types=property_types)
        print(f"CSV data uploaded to database with ID: {csv_db_id}")
