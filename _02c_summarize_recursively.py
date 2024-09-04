import os
import sys
import asyncio
import aiohttp
import fnmatch
import httpx
import json
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

DEFAULT_START_DIRECTORY = "/Users/michasmi/Prod-Cust-Serv" 
SUMMARY_FILE_PREFIX = "all_product"
RAW_TEXT_EXTRACTION_FILE_SUFFIX= "_raw_extract.txt"
TEXT_EXTRACTION_FILE_SUFFIX= "_clean"
TEXT_EXTRACTION_FILE_TYPE= ".txt"
CLEAN_SUMMARY_FILE_SUFFIX= "_clean_summary.json"

STATUS_MODE = True

def main():
    if len(sys.argv) < 2:
        print("No folder path argument was provided. Using defualt folder path.")
        folder_path = DEFAULT_START_DIRECTORY
        
    from extract_text_from_folder_recursively import extract_text_from_file 
    extractor = extract_text_from_file()
    
    # Check for an argument to display the status of the files in the folder
    if len(sys.argv) > 1 and sys.argv[1] == 'status' or STATUS_MODE:
        file_status = display_files_partially_processed(DEFAULT_START_DIRECTORY)
        folder_path = DEFAULT_START_DIRECTORY
        
    
    if len(sys.argv) == 2 and sys.argv[1] != 'status':
        folder_path = sys.argv[1]

    if not os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' does not exist or is not a folder. Exiting")
        sys.exit(1)

    summaries_list = []
    # Begins the asynchronous process of summarizing the text in the folder
    logging.info(f"Extracting text from the folder: {folder_path}")
    
    
    # # Get the input/output paths for the files to be summarized
    # raw_file_path_extracts = asyncio.run(extractor.recursive_text_extractor(folder_path, RAW_TEXT_EXTRACTION_FILE_SUFFIX))
    
    # cleaning_needed_list = []
    # for file in file_status. keys():
    #     if not file_status[file]['clean_text']:
    #         file.replace(".pdf", RAW_TEXT_EXTRACTION_FILE_SUFFIX).replace(".docx", RAW_TEXT_EXTRACTION_FILE_SUFFIX)
    #         cleaning_needed_list.append(file)
    
    # # Clean the raw extracts and make them readable-ish text
    # clean_dicts = asyncio.run(clean_files(cleaning_needed_list))
    
    list_of_file_paths = asyncio.run(get_files_paths_to_summarize(folder_path))
    
    # Summarize the text in the files that were found
    summaries_list = asyncio.run(summarize_list_of_files(list_of_file_paths))
    if summaries_list and len(summaries_list) > 0:
        with open('all_summaries.json', 'w') as f:
            json.dump(summaries_list, f, indent=4)

async def fetch_gemini_response(client, url, headers, payload):

    response = await client.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

async def call_google_gemini_api(prompt):

    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key: raise ValueError("Google API key not found in environment variables")

    url = f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}

    # Define the payload
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient() as client:
        result = await fetch_gemini_response(client, url, headers, payload)
        return result




async def clean_files(file_path_list):
    clean_tasks = []
    count = 0
    for file_path in file_path_list:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            original_text = f.read()
            clean_tasks.append(asyncio.create_task(clean_with_gemini_extract(original_text, file_path, count)))
            count += 1
    clean_dicts = await asyncio.gather(*clean_tasks)
    return clean_dicts

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

async def clean_with_gemini_extract(prompt, orig_file_path, sleep_time = 0, max_tokens=12000):
        
        await asyncio.sleep(sleep_time*2)
        
        dir_path = os.path.dirname(orig_file_path)
        filename = os.path.splitext(os.path.basename(orig_file_path))[0]
        new_file_path = os.path.join(dir_path, f"{filename}{TEXT_EXTRACTION_FILE_SUFFIX}{TEXT_EXTRACTION_FILE_TYPE}")
        bad_file_path = os.path.join(dir_path, f"{filename}_ERROR_{TEXT_EXTRACTION_FILE_SUFFIX}{TEXT_EXTRACTION_FILE_TYPE}")
        
        
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
            cleaned_content = response.text
        
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response: {response}")
            bad_dict = {"success": False, "comment": "ERRORCLEANING", "input_path": orig_file_path, "Error_Response": f"{response.text}", "partial_cleaned_content": f"{cleaned_parts}"}
            with open(f"{new_file_path}", "w") as f:
                json.dump(bad_dict, f, indent=4)
            print(bad_dict)
            return bad_dict
            
        with open(new_file_path, "w") as file:
            file.write(cleaned_content)

        print(f"Cleaned content has been saved to: {new_file_path}")
        clean_dict = {"success": True, "input_path": orig_file_path, "output_path": new_file_path, "cleaned_content": cleaned_content}
        return clean_dict


            
# Gets all the unprocessed files in the folder recursively

def get_file_extension(file_path):
    """Helper function to get the file extension."""
    return os.path.splitext(file_path)[1]

async def get_files_paths_to_summarize(start_directory):
    list_of_file_paths = []

    # Walk through the directory structure
    for root, _, files in os.walk(start_directory):
        for file in files:
            # Check if the file is of the required type and has the specific suffix
            if file.endswith("_clean.txt"):
                file_path = os.path.join(root, file)
                
                # Construct the path for the expected summary file
                summary_extract_path = os.path.join(root, file.replace(get_file_extension(file_path), '_clean_summary.json'))
                print(summary_extract_path)  # Debug print statement
                
                # If the summary file does not exist, add the file to the list
                if not os.path.exists(summary_extract_path):
                    path_dict = {"input_path": file_path, "output_path": summary_extract_path}
                    list_of_file_paths.append(path_dict)

    return list_of_file_paths


async def summarize_list_of_files(list_of_file_paths): 
    summary_tasks = []
    for file_path in list_of_file_paths:
        input_file_path = file_path['input_path']
        output_file_path = file_path['output_path']
        with open(input_file_path, 'r') as f:
            original_text = f.read()
            summary_tasks.append(asyncio.create_task(get_gemini_summary(original_text, output_file_path)))
    list_of_summaries = await asyncio.gather(*summary_tasks)
    return list_of_summaries

#Summarizes the text of one document    
async def get_gemini_summary(text_to_summarize, summary_extract_path):
    
    def extract_json_dict_from_llm_response(content):
        def try_to_json(input_value):
            try:
                return json.loads(input_value)
            except:
                pass
            try:
                return json.loads(f"[{input_value}]")
            except:
                return input_value
        
        # Find the first '{' and the last '}'
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            return None

        try:
            # Extract the JSON string
            json_string = content[start_idx:end_idx + 1]
            
            json_dict = try_to_json(json_string)
            if  isinstance(json_dict, dict) or isinstance(json_dict, list):
                return json_dict
            else:
                return None
        except Exception as e:
            return None
    
    
    
    
    
    data_structure = {
        "Title": "Example Document Title",
        "Date": "2024-01-01",
        "Related Product": "Product Name",
        "Summary": "A 3 paragraph summary of the document's content.",
        "Committed Fees": "$10,000",
        "Renewal Date": "2025-01-01",
        "Parties Involved": ["Party A", "Party B"],
        "Key Terms": ["Term 1", "Term 2", "Term 3"],
        "Document Type": "Client Contract",
        "Is Addendum": False,
        "Effective Date": "2024-02-01",
        "Duration": "1 year",
        "Amendments": ["Amendment 1", "Amendment 2"],
        "References to Other Documents": ["Document 1", "Document 2"],
        "Unusual Legal Terms": ["Term 1", "Term 2"],
        "Your Commentary": "Any additional commentary or notes you have on the document."
    } 

    prompt = f"""
    Please summarize the following collection of business documents, ensuring that the output is formatted strictly as JSON 
    without any additional commentary or text. The JSON should include the following fields:

    • Title: The title of the document.
    • Date: The execution, publish or other main date of the document.
    • Summary: A concise summary of the document.
    • Committed Fees: Any fees committed in the document.
    • Renewal Date: The renewal date mentioned in the document.
    • Parties Involved: The main parties involved in the document.
    • Key Terms: The key terms and conditions outlined in the document.
    • Document Type: The type of document (e.g., client contract, vendor contract, etc.).
    • Effective Date: The date when the document or agreement becomes effective.
    • Duration: The duration for which the document or agreement is valid.
    • Amendments: Any amendments or changes to previous agreements mentioned.
    • References to Other Documents: Any references to other documents or agreements.
    • Unusual Legal Terms:  Any unusual or non-standard legal terms mentioned. Major concerns would be: "Most Favored Nation" or "Termination at Will" 
                            or other terms that put future fees at risk. Penalties that exceed the value of the contract. Commitments to deliver services 
                            or build product that is not clearly defined. 
    • Your Commentary: Any additional commentary or notes you have on the document. Pretend you are Fincentric (also known as Market on Demand, MoD, Wall Street on Demand, WSOD, and S&P),
                        would are the terms of a contract or document disadvantageous? Are there any terms that are particularly advantageous? If thie text is not a contract, please comment on
                        how the document could be improved or what the document is missing.
    Response structure should be a single JSON dictionary as follows:
    {json.dumps(data_structure, indent=4)}

    Document Types should be limited to the following (unless it is something completely different):
    Client Contract, Vendor Contract, API Documentation, Channel Partner Agreement, Product Fact Sheet, Pitch Deck, 
    Internal Presentation, Client Presentation, or Client Account Plan. If the document type is an addendum please 
    use the main document's type and mark the "Is Addendum" field as true.
    
    If a field is not present in the document and cannot be inferred, please put "None" as the Value.
    
    ## Document Text ##
    {text_to_summarize}
    ## End of Document Text ##
    """

    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(prompt,
        generation_config=genai.types.GenerationConfig(
            candidate_count=1,
            temperature=0.2))
    
    valid_dict = extract_json_dict_from_llm_response(response.text)
    if valid_dict:
        with open(summary_extract_path, 'w') as f:
            json.dump(valid_dict, f, indent=4)
        return valid_dict
    else:
        with open(summary_extract_path, 'w') as f:
            f.write(response.text)
        return response.text

#Supporting function to get the file extension
def get_file_extension(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower()

#Supporting function to extract JSON from text
def extract_json_dict_text(content):
        def try_to_json(input_value):
            try:
                return json.loads(input_value)
            except:
                pass
            try:
                return json.loads(f"[{input_value}]")
            except:
                return input_value
        
        # Find the first '{' and the last '}'
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            return None

        try:
            # Extract the JSON string
            json_string = content[start_idx:end_idx + 1]
            
            json_dict = try_to_json(json_string)
            if  isinstance(json_dict, dict) or isinstance(json_dict, list):
                return json_dict
            else:
                return None
        except Exception as e:
            return None
 
def create_csv_json_combined_file(start_folder, output_file):
    """
    Recursively iterates through folders from a start folder, reads all files ending with '_clean.txt',
    and writes their contents into a single output file in the base folder.

    Parameters:
    start_folder (str): The folder to start the search from.
    output_file (str): The path of the output file to write the combined content to.
    """
    all_dict = {}
    import csv

    for root, _, files in os.walk(start_folder):
        for file in files:
            if file.endswith(CLEAN_SUMMARY_FILE_SUFFIX):
                file_path = os.path.join(root, file)
                directory_path = os.path.dirname(file_path)
                directory_name = os.path.basename(directory_path)
                with open(file_path, 'r') as infile:
                    file_dict = extract_json_dict_text(infile.read())

                    all_dict.update({ f"{directory_name}|{file}": file_dict})
                    # content = {f"{file}": { "content": infile.read()}}
                    # all_dict.update(content)

    
    with open(output_file, 'w') as outfile:
        outfile.write(json.dumps(all_dict, indent=4))
    column_titles = list(next(iter(all_dict.values())).keys())
    with open(output_file, 'w', newline='') as csvfile:
        # Create a CSV DictWriter object
        writer = csv.DictWriter(csvfile, fieldnames=['key'] + column_titles)
        
        # Write the header row
        writer.writeheader()
    
    # Write each key-value pair to the CSV file
        for key, value in all_dict.items():
            # Add the 'key' to the value dictionary
            row = {'key': key}
            if value is None: value = ''
            row.update(value)
            writer.writerow(row)
                    
if __name__ == '__main__':
    main()
    
    
    