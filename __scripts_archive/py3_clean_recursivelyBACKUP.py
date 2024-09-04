import os
import sys
import asyncio
import aiofiles
import aiohttp
import fnmatch
import httpx
import json
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

DEFAULT_START_DIRECTORY = "/Users/michasmi/Library/CloudStorage/OneDrive-JBIHoldingsLLC/WorkingMAS/ProjectSpring" 
SUMMARY_FILE_PREFIX = "all_product"
RAW_TEXT_EXTRACTION_FILE_SUFFIX= "_raw_extract.txt"
TEXT_EXTRACTION_FILE_SUFFIX= "_clean"
TEXT_EXTRACTION_FILE_TYPE= ".txt"
CLEAN_SUMMARY_FILE_SUFFIX= "_clean_summary.json"

STATUS_MODE = True

async def main():
    
    # def add_title_to_txt_files(start_folder):
    #     for root, _, files in os.walk(start_folder):
    #         folder_name = os.path.basename(root)
    #         for file_name in files:
    #             if file_name.endswith('.txt'):
    #                 file_path = os.path.join(root, file_name)
    #                 add_title_to_file(file_path, folder_name, file_name)

    # def add_title_to_file(file_path, folder_name, file_name):
    #     title_line = f"Document File Name-Title: {folder_name} {file_name}\n"
    #     try:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             content = file.readlines()
            
    #         content.insert(0, title_line)

    #         with open(file_path, 'w', encoding='utf-8') as file:
    #             file.writelines(content)
            
    #         print(f"Title added to {file_path}")
    #     except Exception as e:
    #         print(f"Failed to add title to {file_path}: {e}")

    # add_title_to_txt_files(DEFAULT_START_DIRECTORY)
    

    print("Starting the cleaning process")
    def display_files_partially_processed(start_folder):
        file_status = {}
        full_file_list = []
        # Create a file with all the files in the folder
        with open("all_files.txt", "a") as f:
            for root, _, files in os.walk(start_folder):
                for file in files:
                    f.write(f"{os.path.join(root, file)}\n")
                    full_file_list.append(os.path.join(root, file))
        

        for root, _, files in os.walk(start_folder):
            for file in files:

                if file.endswith('.pdf') or file.endswith('.docx'):
                    
                    if "20060801" in file:
                        pass
                    
                    file_path = os.path.join(root, file)
                    file_str = f"{file_path}"
                    file_key = f"{file_path}"
                    
                    file_status[file_str] = {}
                    file_status[file_str]['raw_extract'] = False
                    file_status[file_str]['clean_text'] = False
                    file_status[file_str]['summary'] = False
                    
                    file_str = f"{file_str}".replace('.pdf', "PLACEHOLDER").replace(".docx", "PLACEHOLDER")
                    
                    raw = file_str.replace('PLACEHOLDER', RAW_TEXT_EXTRACTION_FILE_SUFFIX)
                    print(raw)
                    if raw in full_file_list:
                        file_status[file_key]['raw_extract'] = True
                    clean = file_str.replace('PLACEHOLDER', f"{TEXT_EXTRACTION_FILE_SUFFIX}{TEXT_EXTRACTION_FILE_TYPE}")
                    print(clean)
                    if clean in full_file_list:
                        file_status[file_key]['clean_text'] = True
                    summ = file_str.replace('PLACEHOLDER', CLEAN_SUMMARY_FILE_SUFFIX)
                    print(summ)
                    if summ in full_file_list:
                        file_status[file_key]['summary'] = True    
                        
        
        # Print the status of the files using red for missing files and green for present files
        for file, status in file_status.items():
            status_text = f"{file}: \n"
            for key, value in status.items():
                if value == True:
                    status_text += f"\t{key}: \033[92mPresent\033[0m   "
                    status_flag = f"{key}: Present"
                else:
                    status_text += f"\t{key}: \033[91mMissing\033[0m   "                
                    status_flag = f"{key}: Missing"
                
            status_text += f"\n"
            if "Missing" in status_text:
                print(status_text)
        with open('file_status.json', 'w') as f:
            f.write(json.dumps(file_status, indent=4))
        return file_status

    if len(sys.argv) < 2:
        print("No folder path argument was provided. Using defualt folder path.")
        folder_path = DEFAULT_START_DIRECTORY
        
     
    # Check for an argument to display the status of the files in the folder
    if len(sys.argv) > 1 and sys.argv[1] == 'status' or STATUS_MODE:
        file_status = display_files_partially_processed(DEFAULT_START_DIRECTORY)
        folder_path = DEFAULT_START_DIRECTORY
        
    
    if len(sys.argv) == 2 and sys.argv[1] != 'status':
        folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' does not exist or is not a folder. Exiting")
        sys.exit(1)
   
    cleaning_needed_list = []
    for file in file_status.keys():
        if not file_status[file]['clean_text']:
            file = file.replace(".pdf", RAW_TEXT_EXTRACTION_FILE_SUFFIX).replace(".docx", RAW_TEXT_EXTRACTION_FILE_SUFFIX)
            cleaning_needed_list.append(file)
    
    # Clean the raw extracts and make them readable-ish text
    clean_dicts = await clean_files(cleaning_needed_list)
    print(clean_dicts)
    
async def clean_files(file_path_list):
    clean_tasks = []
    count = 0
    for file_path in file_path_list:
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_text = await f.read()
                clean_tasks.append(asyncio.create_task(clean_with_gemini_extract(original_text, file_path, count)))
                count += 1
        except Exception as e:
            print(f"Error: {e}")
            print(f"File: {file_path}")
            continue
    clean_dicts = await asyncio.gather(*clean_tasks)
    return clean_dicts

async def clean_with_gemini_extract(prompt, orig_file_path, sleep_time=0, max_tokens=12000):
    async def fetch_gemini_response(url, headers, payload):
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
    
    async def call_google_gemini_api(prompt):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key: raise ValueError("Google API key not found in environment variables")

        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}'
        headers = {'Content-Type': 'application/json'}

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        result = await fetch_gemini_response(url, headers, payload)
        return result

    await asyncio.sleep(sleep_time*2)
    response = ""
    dir_path = os.path.dirname(orig_file_path)
    filename = os.path.splitext(os.path.basename(orig_file_path))[0]
    new_file_path = os.path.join(dir_path, f"{filename}{TEXT_EXTRACTION_FILE_SUFFIX}{TEXT_EXTRACTION_FILE_TYPE}")
    cleaned_parts = []

    instructions = """Please transform the following OCR-extracted text into a clean, readable version that closely matches the original document.
    1). Accuracy and Readability: Strive to correct any OCR errors, ensuring the text is readable and as accurate as possible.
    2). Structure: Reconstruct sentence structures, headers, and footnotes appropriately.
    3). Legal Context: This is a legal document, so maintain the integrity of the legal language.
    4). Common Names: Preserve the names of organizations: Fincentric, Markit On Demand, Markit, S&P, and Wall Street On Demand. Do not alter these names.
    5). Uncertain Words: If a word is unclear and is critical to the meaning of the sentence indicate uncertainty with a question mark in brackets [?].
    Note I understand there may be some inaccuracies due to the quality of the OCR, but please make your best effort to ensure the text is as close to the original as possible.
    """
    try:
        response = await call_google_gemini_api(prompt)
        cleaned_content = response['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response: {response}")
        try:
            rtext = f"{response}"
        except:
            rtext = "No response"
        bad_dict = {"success": False, "comment": "ERRORCLEANING", "input_path": orig_file_path, "Error_Response": f"{rtext}", "partial_cleaned_content": f"{cleaned_parts}"}
        with open(f"{new_file_path}", "w") as f:
            json.dump(bad_dict, f, indent=4)
        print(bad_dict)
        return bad_dict

    with open(new_file_path, "w") as file:
        file.write(cleaned_content)

    print(f"Cleaned content has been saved to: {new_file_path}")
    clean_dict = {"success": True, "input_path": orig_file_path, "output_path": new_file_path, "cleaned_content": cleaned_content}
    return clean_dict

if __name__ == '__main__':
    asyncio.run(main())