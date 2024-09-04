import os
import sys
import csv
import filecmp
from pathlib import Path
import re

class ApplyTags:
    def __init__(self, tag_map_csv_path=None, start_folder_path=None, remove_existing_tags=False):
        if not tag_map_csv_path or not os.path.exists(tag_map_csv_path) or not start_folder_path or not os.path.exists(start_folder_path):
            print(f"Invalid tag map CSV or start folder path. Exiting.")
            return
        
        self.tag_csv_path = tag_map_csv_path
        self.start_folder_path = start_folder_path
        base_tag_folder = os.path.dirname(tag_map_csv_path)
        self.HISTORY_FILE_PATH = os.path.join(base_tag_folder, ".tag_history", 'tags.csv')
        self.REMOVE_EXISTING_TAGS = remove_existing_tags  # Set to True to remove all existing tags before applying new ones
        
    def load_tags(self, csv_path):
        tags = []
        with open(csv_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    tags.append((row[0].strip().replace('"',''), row[1].strip().replace('"','')))
        return tags

    def save_tag_history(self, csv_path, history_path):
        Path(history_path).parent.mkdir(parents=True, exist_ok=True)
        with open(history_path, 'w', newline='') as csvfile:
            reader = csv.reader(open(csv_path))
            writer = csv.writer(csvfile)
            for row in reader:
                writer.writerow(row)

    def apply_tags(self, content, tags, remove_existing):
        content = content.replace('---', '*```*')
        content_parts = content.split('```')
        
        processed_parts = []
        for part in content_parts:
            processed_part = part
            if not 'CreatedOn' in part and not '[!info]'  in part:
                for search_string, tag in tags:
                    if remove_existing:
                        processed_part = self.remove_tag(processed_part, tag)
                    processed_part = processed_part.replace(search_string, f"{tag} {search_string}")
                processed_parts.append(processed_part)
            else:
                processed_parts.append(part)
            
        new_content = '```'.join(processed_parts)
        new_content = new_content.replace('*```*', '---')
        
        return new_content

    def remove_tag(self, content, tag):
        return content.replace(f"{tag} ", "")

    def process_file(self, file_path, tags, remove_existing):
        with open(file_path, 'r') as file:
            content = file.read()
        print(f"Processing file: {file_path}")
        updated_content = self.apply_tags(content, tags, remove_existing)

        with open(file_path, 'w') as file:
            file.write(updated_content)

    def process_folder(self, folder_path, tags, remove_existing):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".md") or file.endswith(".txt"):
                    self.process_file(os.path.join(root, file), tags, remove_existing)

    def main(self):
        start_path = sys.argv[1] if len(sys.argv) > 1 else self.start_folder_path
        if not start_path or not os.path.exists(start_path):
            print(f"Path {start_path} does not exist. Exiting.")
            return

        csv_path = self.tag_csv_path
        
        history_path = self.HISTORY_FILE_PATH

        if not os.path.exists(csv_path):
            print(f"No tags.csv found at {csv_path}. Exiting.")
            return

        tags = self.load_tags(csv_path)
        if not os.path.exists(history_path) or not filecmp.cmp(csv_path, history_path, shallow=False):
            if os.path.exists(history_path):
                print("Tags have changed. Applying updates...")
            else:
                print("No tag history found. Applying tags for the first time...")
            
            remove_existing = self.REMOVE_EXISTING_TAGS
            if os.path.isdir(start_path):
                self.process_folder(start_path, tags, remove_existing)
            else:
                self.process_file(start_path, tags, remove_existing)
            
            self.save_tag_history(csv_path, history_path)
        else:
            print("No changes detected in tags.csv. No updates applied.")

if __name__ == "__main__":
    
    test_folder_path = "/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/test_tagging"
    csv_path = "/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/test_tagging/tags.csv"
    reapply_tags = True
    TagManager = ApplyTags(csv_path, test_folder_path, reapply_tags)
    TagManager.main()