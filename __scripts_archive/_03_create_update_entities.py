import os
import re
from datetime import datetime

def update_entities():
    # Client
    entity_list_name = "_Entities_Test"
    entity_folder_name = "Entities"
    # entity_list_name = "_Entities"
    vault_base_folder_path = "/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/"
    entity_list_folder_path = f"/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/{entity_list_name}"
    entity_folder_path = f"/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/{entity_folder_name}"

    
    upd_ent = UpdateEntities(vault_base_folder_path=vault_base_folder_path, entity_list_folder_path=entity_list_folder_path, entity_folder_path=entity_folder_path)
    upd_ent.update_entities()
    



class UpdateEntities:
    def __init__(self, vault_base_folder_path=None, entity_list_folder_path=None, entity_folder_path=None):

        self.vault_base_folder_path = vault_base_folder_path
        self.entity_list_folder_path = entity_list_folder_path
        self.entity_folder_path = entity_folder_path
        

    # Function to generate the markdown content
    def generate_markdown_header_dict(self, name, alias_list, entity_domain):
        today_date = datetime.today().strftime('%Y-%m-%d')
        yaml_header_dict = {
            "title": name,
            "date": today_date,
            "tags": {entity_domain},
            "aliases": alias_list,
            "relationship_type": {entity_domain},
            "status": "Active",
            "categories": "",
            "author": "Michael Smith",
            "file_name": f"{name}.md",
            "pages": 1,
        }
        return yaml_header_dict

    def parse_markdown_table(self, markdown_text):
        lines = markdown_text.strip().splitlines()
        
        # Extract header columns
        headers = [header.strip() for header in re.split(r'\s*\|\s*', lines[0]) if header.strip()]
        
        # Extract the rows and convert them to dictionaries
        table_data = []
        for row in lines[2:]:  # Skip the header and separator lines
            columns = [col.strip() for col in re.split(r'\s*\|\s*', row) if col.strip()]
            row_dict = dict(zip(headers, columns))
            
            # Handle Alias as a list by splitting on commas
            if 'Alias' in row_dict and row_dict['Alias']:
                row_dict['Alias'] = [alias.strip() for alias in row_dict['Alias'].split(', ')]
            
            table_data.append(row_dict)
        
        return table_data
    
    def update_entities(self):
        pass
    
    def get_entity_list_files(self):
        with open self.


if __name__ == '__main__':
    update_entities()
