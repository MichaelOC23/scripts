import re
import os
import sys
import asyncio
import aiofiles
import httpx
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

TEST_VALUE = "/Users/michasmi/Library/CloudStorage/OneDrive-JBIHoldingsLLC/WorkingMAS/ProjectSpring/3.5.1.17 Charles Schwab-CUSTOMER/3.5.1.17.53 SchwabMSA.pdf"

def replacement(match):
    # Match object: group(0) is the entire match, group(1) is the part before the first \n, group(2) is the first \n
    line_with_hashes = match.group(1)
    newline = match.group(2)
    # Replace "##" with "|##| |"
    modified_line = line_with_hashes.replace("##", "|##| |")
    # Replace the first \n after the line with \n\n
    return f"{modified_line}{newline}\n\n"
    
async def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else TEST_VALUE  # Get file path from arguments

    if not file_path or not os.path.isfile(file_path):
        print("Error: Please provide a valid file path.")
        return

    raw_extract_path = file_path.replace(".pdf", "_raw_extract.txt")
    clean_extract_path = file_path.replace(".pdf", "_clean.md")

    if not os.path.isfile(raw_extract_path):
        print(f"Error: Raw extract file '{raw_extract_path}' not found.")
        return

    if os.path.isfile(clean_extract_path):
        print(f"Cleaned file '{clean_extract_path}' already exists. Skipping.")
        return

    await clean_file(raw_extract_path, clean_extract_path)

async def clean_file(raw_path, clean_path):
    async with aiofiles.open(raw_path, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = await f.read()

    sentences = raw_text.split(". \n")  # Split into sentences
    cleaned_sentences = await asyncio.gather(*[clean_with_gemini(sentence) for sentence in sentences])
    raw_text_file_name = os.path.basename(raw_path)
    # Pattern to find lines with "##" and the following newline
    # pattern = re.compile(r"(.*##.*?)(\n)")
    
    # Join sentences back together, adding periods back where needed
    for sentence in cleaned_sentences:
        if not sentence:
            sentence = '\n'
        else:
            prefix = ''
            if sentence.startswith(". "):
                prefix = "\n"
            sentence = sentence.strip()
            if sentence != '' and sentence[-1] != '.':
                sentence += '.  '
            sentence = sentence.replace("\n\n\n", "\n\n")
            sentence = sentence.replace("\n\n", "||||")
            sentence = sentence.replace("\n", " ")
            sentence = sentence.replace("||||", "\n\n")
    
    text_only_sentence = [sentence for sentence in cleaned_sentences if sentence]
    cleaned_text = ".  \n".join(text_only_sentence)
    
    # Add a link to the original PDF at the top of the cleaned text
    cleaned_text = f"![[{raw_text_file_name.replace("_raw_extract.txt", ".pdf")}#height=750]]\n\n {cleaned_text}"
    async with aiofiles.open(clean_path, 'w', encoding='utf-8') as f:
        await f.write(cleaned_text)

    print(f"Cleaned content saved to: {clean_path}")

async def extract_json_dict_from_llm_response(content):
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

async def clean_with_gemini(text):
    api_key = 'AIzaSyCIEV24Isgy-MZElHSfOg1SNg0wX7TqxoI'
    

    url = f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}'
    headers = {'Content-Type': 'application/json'}
    
    json_response_format = {"transformedtext": text, "commentary": "Commentary you feel is necessary about how you did or did not clean the text."}

    instructions = f"""Transform the following OCR-extracted text into clean, readable MARKDOWN and return the MARKDOWN in the specified JSON format.:

    1. Accuracy: Correct OCR errors, ensuring the text is accurate.
    2. Readability: Make the text clear and easy to understand.
    3. Structure: Preserve the original structure (e.g., lists, headings).
    4. Legal Context: Maintain the integrity of the legal language.
    5. Organizations: Keep the names of these organizations as they are: Fincentric, Markit On Demand, Markit, S&P, Wall Street On Demand.
    6. Uncertain Words: If a word is unclear, mark it with a question mark in brackets [?].
    
    Your response is being systematically integrated. Only return the MARKDOWN in the specified JSON in the format below:
    {json.dumps(json_response_format, indent=4)}
    

    OCR Text:
    """ + text  # Concatenate instructions with text

    payload = {
        "contents": [{"parts": [{"text": instructions}]}],
        "safetySettings": [
        {"category": "HARM_CATEGORY_HATE_SPEECH",
         "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
         "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
         "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT",
         "threshold": "BLOCK_NONE"},
        ]
        }



    async def fetch_gemini_response(url, headers, payload, timeout=180):
        limits = httpx.Limits(max_keepalive_connections=None, max_connections=None)
        timeout = httpx.Timeout(timeout, read=timeout)
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response

    response = await fetch_gemini_response(url, headers, payload)
    result = response.json()
    
    if result['candidates'][0]['finishReason'] == 'RECITATION':
        print("Warning: Possible copyrighted or sensitive content detected. Returning original text.")
        return text  # Return original text if flagged
    else:
        print("Text cleaned successfully.")
        try: 
            hopefully_a_dict = await extract_json_dict_from_llm_response(result['candidates'][0]['content']['parts'][0]['text'])
            if isinstance(hopefully_a_dict, dict):
                return_text = hopefully_a_dict['transformedtext']
                return return_text
            else:
                return hopefully_a_dict
        except:
            print("Warning: JSON format not detected. Returning original")
            print(f"${result}")
            return text
        
    



if __name__ == '__main__':
    asyncio.run(main())
