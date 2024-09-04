# import _class_storage
import asyncio
# storage = _class_storage.az_storage()
import csv
import json
import re
import os
from bs4 import BeautifulSoup
import csv


description_folder = os.path.join("/Users/communify/", "desc")


if not os.path.exists(description_folder):
    print("Error: Folder does not exist")
    exit()

def extract_text_from_html(html_body):
        soup = BeautifulSoup(html_body, 'html.parser')
        return soup.get_text(separator=' ', strip=True)

def extract_all_text():
    #Iterate through all files in the folder
    files = os.listdir(description_folder)
    file_count = len(files)
    on_file = 0
    for file in files:
        on_file += 1    
        if file.endswith(".html"):
            print("Processing file: " + file + "Percent done: " + str(on_file/file_count))
            with open(description_folder + "/" + file, 'r') as f:
                html_text = f.read()
                text = extract_text_from_html(html_text)
            with open(f"{description_folder}/{file.replace(".html", ".txt")}", 'w') as f:
                f.write(text)
                
    
    
def extract_description_from_text():
    
    
    def extract_text_between_delimiters(text, start_delimiter, end_delimiter):
        
        try:
            start_index = text.index(start_delimiter) + len(start_delimiter)
            end_index = text.index(end_delimiter, start_index)
            return text[start_index:end_index]
        except ValueError:
            # Return an empty string if delimiters are not found
            return ""
    
    #Iterate through all files in the folder
    files = os.listdir(description_folder)
    file_count = len(files)
    on_file = 0
    output_list = []
    
    for file in files:
        on_file += 1

        if file.endswith(".txt"):
            print(f"Processing file: {file} |||| Percent complete: {round((on_file/file_count)*100,1)}%")
            with open(description_folder + "/" + file, 'r') as f:
                text = f.read()
                start_delimiter = " Description "
                end_delimiter = "Corporate Governance"
                try:
                    start_index = text.index(start_delimiter) + len(start_delimiter)
                    end_index = text.index(end_delimiter, start_index)
                    CompDesc = text[start_index:end_index]
                    output_list.append([file.split(".")[0], CompDesc])
                except Exception as e:
                    print(f"Failed to extract description from file: {file} with error: {e}")
                    continue
            with open("ticker-desc.csv", mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                for row in output_list:
                    writer.writerow(row)
                
                    
                
extract_description_from_text()
    
    