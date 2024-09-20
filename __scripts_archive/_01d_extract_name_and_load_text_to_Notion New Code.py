import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient
from notion_client import Client

# Azure Storage configuration
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "document-images"


def upload_to_azure(self, file_path):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    
    blob_name = os.path.basename(file_path)
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data)

    return blob_client.url

def get_or_create_folder_entry(self, folder_name):
    query = {
        "database_id": self.folders_database_id,
        "filter": {
            "property": "Name",
            "title": {
                "equals": folder_name
            }
        }
    }
    
    results = self.notion.databases.query(**query)
    
    if results["results"]:
        return results["results"][0]["id"]
    else:
        new_page = self.notion.pages.create(
            parent={"database_id": self.folders_database_id},
            properties={
                "Name": {"title": [{"text": {"content": folder_name}}]}
            }
        )
        return new_page["id"]

def add_content_to_document_page(self, page_id, notion_image_text_list):
    content_blocks = []
    
    for page_num, image_path, text in notion_image_text_list:
        image_url = self.upload_to_azure(image_path)
        
        content_blocks.extend([
            {
                "type": "divider",
                "divider": {}
            },
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": f"Page {page_num}"}}]
                }
            },
            {
                "type": "column_list",
                "column_list": {
                    "children": [
                        {
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "type": "image",
                                        "image": {
                                            "type": "external",
                                            "external": {
                                                "url": image_url
                                            }
                                        }
                                    }
            ]
            }
                        },
                        {
                            "type": "column",
                            "column": {
                                "children": [
                                    {
                                        "type": "paragraph",
                                        "paragraph": {
                                            "rich_text": [{"type": "text", "text": {"content": text}}]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ])
    
    self.notion.blocks.children.append(page_id, children=content_blocks)

def process_image_text_list(pdf_path, notion_image_text_list):
    folder_name = Path(pdf_path).parent.name
    document_name = Path(pdf_path).name
    
    # folder_id = self.get_or_create_folder_entry(folder_name)
    # pdf_url = upload_to_azure(pdf_path)
    # document_page_id = self.create_document_entry(self, folder_id, document_name, pdf_url)
    # self.add_content_to_document_page(document_page_id, notion_image_text_list)

