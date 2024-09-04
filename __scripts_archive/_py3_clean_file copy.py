import os
import sys
import asyncio
import aiofiles
import httpx
import google.generativeai as genai
import logging

logging.basicConfig(level=logging.INFO)

TEST_FILE = "/Users/michasmi/Library/CloudStorage/OneDrive-JBIHoldingsLLC/WorkingMAS/ProjectSpring/3.5.3.2.9 OPRA/3.5.3.2.9.4 OPRA_MOD Distrib Declaration_Executed 20160112.pdf" 
SUMMARY_FILE_PREFIX = "all_product"
RAW_TEXT_EXTRACTION_FILE_SUFFIX= "_raw_extract.txt"
TEXT_EXTRACTION_FILE_SUFFIX= "_clean"
TEXT_EXTRACTION_FILE_TYPE= ".txt"
CLEAN_SUMMARY_FILE_SUFFIX= "_raw_extract_clean.json"

STATUS_MODE = True

async def main():
 

    if len(sys.argv) < 2:
        print("No file path argument was provided. Using defualt folder path.")
        file_path = TEST_FILE 

        
    if len(sys.argv) == 2 and sys.argv[1] != 'status':
        file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"The pdf file '{file_path}' does not exist Exiting")
        sys.exit(1)

    raw_extract_path = file_path.replace(".pdf", RAW_TEXT_EXTRACTION_FILE_SUFFIX)
    clean_extract_path = file_path.replace(".pdf", CLEAN_SUMMARY_FILE_SUFFIX)
    
    
    if not os.path.isfile(raw_extract_path):
        print(f"The raw text extraction file '{raw_extract_path}' does not exist Exiting")
    else:
        print(f"The raw text extraction file '{raw_extract_path}' exists")
        if os.path.isfile(clean_extract_path):
            print(f"The clean summary file '{clean_extract_path}' exists. Exiting")
            sys.exit(0)
        else:
            print(f"The clean summary file '{clean_extract_path}' does not exist. Creating it now.")
        

    # Clean the raw extracts and make them readable-ish text
    clean_dict = await clean_file(raw_extract_path)
    print(clean_dict)
    
async def clean_file(file_path):

    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        original_text = await f.read()
        clean_dict = await clean_with_gemini_extract(original_text, file_path)
    return clean_dict

async def clean_with_gemini_extract(prompt, orig_file_path, sleep_time=0, max_tokens=12000):
    async def fetch_gemini_response(url, headers, payload, timeout=30):  # Set timeout to 30 seconds
        limits = httpx.Limits(max_keepalive_connections=None, max_connections=None)
        timeout = httpx.Timeout(timeout, read=timeout)  # Set both connect and read timeouts
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
    
    async def call_google_gemini_api(prompt):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key: raise ValueError("Google API key not found in environment variables")

        url = f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}'
        headers = {'Content-Type': 'application/json'}

        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        result = await fetch_gemini_response(url, headers, payload)
        return result

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

    response = await call_google_gemini_api(prompt)
    cleaned_content = response['candidates'][0]['content']['parts'][0]['text']


    with open(new_file_path, "w") as file:
        file.write(cleaned_content)

    print(f"Cleaned content has been saved to: {new_file_path}")
    clean_dict = {"success": True, "input_path": orig_file_path, "output_path": new_file_path, "cleaned_content": cleaned_content}
    return clean_dict

if __name__ == '__main__':
    asyncio.run(main())