import os
import time
import sys
import pandas as pd
from datetime import datetime
import httpx
import time
from notion_client import Client, errors
from notion_client.helpers import get_id

from notion_client.errors import APIResponseError
from typing import Dict, List, Union
import streamlit as st
from  _class_streamlit import streamlit_mytech
import logging 
import structlog
from pprint import pprint

logger = structlog.wrap_logger(
    logging.getLogger("notion-client"),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    )
notion = Client(auth=os.environ.get('NOTION_API_KEY'),logger=logger, log_level=logging.DEBUG)

def main():
    
    # users = notion.users.list()

    # for user in users.get("results"):
    #     name, user_type = user["name"], user["type"]
    #     emoji = "😅" if user["type"] == "bot" else "🙋‍♂️"
    #     print(f"{name} is a {user_type} {emoji}")
    
    parent_id, db_name = manual_inputs()
    # newdb = create_database(parent_id=parent_id, db_name=db_name)
    # print(f"\n\nDatabase {db_name} created at {newdb['url']}\n")
    next_example()



def get_id_by_name(page_or_db_name):
    results = notion.search(query=f"{page_or_db_name}").get("results")
    if results and len(results) > 1 :
        return [result["id"] for result in results][0]
    else:
        return []
    

def get_all_objects(search_filter = '', types = ["page", "database"]):
    result_dict = {}
    for type in types:
        response = notion.search(query=f"{search_filter}",filter={"value":f"{type}","property":"object"})
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


def next_example():
    
    # print (get_id_by_name("TestArea"))
    # print (get_id_by_name("Clients"))
    # print (get_id_by_name("ooglie"))
    # print "All in bold Cyan
    print("\033[1;32mAll\033[0m")
    pprint (get_all_objects())
    print("\033[1;32mTest\033[0m")
    pprint (get_all_objects("Client"))
    print("\033[1;32mClient\033[0m")
    pprint (get_all_objects("Client"))
    print("\033[1;32mPages\033[0m")
    pprint (get_all_objects(types=['page']))
    print("\033[1;32mDatabases\033[0m")
    pprint (get_all_objects("Client", types=['database']))
    print("\033[1;32mNoResults\033[0m")
    pprint (get_all_objects("ooglie"))
    


    # "filter": {
    #     "value": "database",
    #     "property": "object"
    # },
    
    
    # .get("results")
    # "property": "object", "value": "page"
    
    
    # Search for an item
    print("\nSearching for the word 'People' ")
    results = notion.search(query="Clients").get("results")
    print(len(results))
    result = results[0]
    print("The result is a", result["object"])
    pprint(result["properties"])
    
    database_id = result["id"]  # store the database id in a variable for future use


    
    
    # Create a new page
    your_name = "Michael"
    gh_uname = "Smith"
    
    
    
    
    
    
    new_page = {
        "Name": {"title": [{"text": {"content": your_name}}]},
        "Tags": {"type": "multi_select", "multi_select": [{"name": "python"}]},
        "GitHub": {
            "type": "rich_text",
            "rich_text": [
                {
                    "type": "text",
                    "text": {"content": gh_uname},
                },
            ],
        },
    }
    
    
    new_page =  {
  "parent": {
    "database_id": f"{database_id}"
  },
  "icon": {
    "emoji": "🥬"
  },
  "cover": {
    "external": {
      "url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Tuscankale.jpg"
    }
  },
  "properties": {
    "Name": {
      "title": [
        {
          "text": {
            "content": "Tuscan Kale"
          }
        }
      ]
    },
    "Description": {
      "rich_text": [
        {
          "text": {
            "content": "A dark green leafy vegetable"
          }
        }
      ]
    },
    "Food group": {
      "select": {
        "name": "Vegetable"
      }
    },
    "Price": {
      "number": 2.5
    }
  },
  "children": [
    {
      "object": "block",
      "type": "heading_2",
      "heading_2": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Lacinato kale"
            }
          }
        ]
      }
    },
    {
      "object": "block",
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": {
              "content": "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm.",
              "link": {
                "url": "https://en.wikipedia.org/wiki/Lacinato_kale"
              }
            }
          }
        ]
      }
    }
  ]
}
    
    
    
    notion.pages.create(parent={"page_id": database_id}, properties=new_page)
    print("You were added to the People database!")


    # Query a database
    name = input("\n\nEnter the name of the person to search in People: ")
    results = notion.databases.query(
        **{
            "database_id": database_id,
            "filter": {"property": "Name", "rich_text": {"contains": name}},
        }
    ).get("results")

    no_of_results = len(results)

    if no_of_results == 0:
        print("No results found.")
        sys.exit()

    print(f"No of results found: {len(results)}")

    result = results[0]

    print(f"The first result is a {result['object']} with id {result['id']}.")
    print(f"This was created on {result['created_time']}")


def manual_inputs(parent_id="", db_name="") -> tuple:
    """
    Get values from user input
    """
    if parent_id == "":
        is_page_ok = False
        while not is_page_ok:
            input_text = "https://www.notion.so/Test-Page-5710016a76a940baa1b65f401b1de22c"
            # Checking if the page exists
            try:
                if input_text[:4] == "http":
                    parent_id = get_id(input_text)
                    print(f"\nThe ID of the target page is: {parent_id}")
                else:
                    parent_id = input_text
                notion.pages.retrieve(parent_id)
                is_page_ok = True
                print("Page found")
            except Exception as e:
                print(e)
                continue
    while db_name == "":
        db_name = "tuna"

    return (parent_id, db_name)


def create_database(parent_id: str, db_name: str) -> dict:
    """
    parent_id(str): ID of the parent page
    db_name(str): Title of the database
    """
    print(f"\n\nCreate database '{db_name}' in page {parent_id}...")
    properties = {
        "Name": {"title": {}},  # This is a required property
        "Description": {"rich_text": {}},
        "In stock": {"checkbox": {}},
        "Food group": {
            "select": {
                "options": [
                    {"name": "🥦 Vegetable", "color": "green"},
                    {"name": "🍎 Fruit", "color": "red"},
                    {"name": "💪 Protein", "color": "yellow"},
                ]
            }
        },
        "Price": {"number": {"format": "dollar"}},
        "Last ordered": {"date": {}},
        "Store availability": {
            "type": "multi_select",
            "multi_select": {
                "options": [
                    {"name": "Duc Loi Market", "color": "blue"},
                    {"name": "Rainbow Grocery", "color": "gray"},
                    {"name": "Nijiya Market", "color": "purple"},
                    {"name": "Gus's Community Market", "color": "yellow"},
                ]
            },
        },
        "+1": {"people": {}},
        "Photo": {"files": {}},
    }
    title = [{"type": "text", "text": {"content": db_name}}]
    icon = {"type": "emoji", "emoji": "🎉"}
    parent = {"type": "page_id", "page_id": parent_id}
    return notion.databases.create(
        parent=parent, title=title, properties=properties, icon=icon
    )





def get_and_print_database_ids():
        # Initialize Notion client
        notion = Client(auth=os.environ.get('NOTION_API_KEY'))
        
        def call_api(method: str, *args, **kwargs):
            """
            General method to call Notion API methods.
            Supports nested attributes (e.g., 'databases.retrieve') and includes a 0.33 second pause before each call.
            """
            time.sleep(0.33)  # Pause for 0.33 seconds before making the API call

            parts = method.split(".")
            api_method = notion

            for part in parts:
                if hasattr(api_method, part):
                    api_method = getattr(api_method, part)
                else:
                    raise AttributeError(f"API method {method} is deprecated or does not exist")

            try:
                return api_method(*args, **kwargs)
            except APIResponseError as e:
                print(f"APIResponseError: {e.message}")
                print(f"More info: {e.code} - {e.status}")
                raise
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                raise

        def list_databases():
            try:
                databases = call_api("pages.list")
                return [db['id'] for db in databases['results']]
            except AttributeError as e:
                print(f"Error: {str(e)}")
                return []
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                return []

        # Get database IDs
        db_ids = list_databases()
        
        # Print out each database ID
        if db_ids:
            for db_id in db_ids:
                print(f"Database ID: {db_id}")
        else:
            print("No databases found or an error occurred.")
if __name__ == "__main__":
    main()