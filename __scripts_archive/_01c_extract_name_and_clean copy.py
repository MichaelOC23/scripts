# Standard Python Libraries
import os
import shutil

import sys
import re

import uuid
from tqdm.asyncio import tqdm_asyncio
import json
import math
from collections import Counter
import random

#Date / TIme
from datetime import datetime
import time


# PDF and Image Processing
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from markdown import markdown
from bs4 import BeautifulSoup
from pptx import Presentation
# from pptxpdf import convert
from PyPDF2 import PdfFileReader, PdfFileWriter
from pptx.enum.shapes import MSO_SHAPE_TYPE
from io import BytesIO

# Data Processing
import pandas as pd

# Async and Multiprocessing
from multiprocessing import Pool, cpu_count
import asyncio
import httpx

#Office Documents
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredPowerPointLoader, text
from langchain_community.document_loaders import UnstructuredExcelLoader
import langchain_core as core

# Import the custom Logger class
# from  _01b_extract_text_from_folder_recursively import extract_text_from_file as ext_advanced
from _class_logger import Logger




class TextExtractor:
    def __init__(self, model="gemini-1.5-flash", test_folder_path=None, force_rerun=False):
        self.logger = Logger(output_folder="_working", only_print_errors=True)
        self.logger.log(f"SysArg: {sys.argv}")

        API_KEY = os.environ.get("GOOGLE_API_KEY")
        MODEL = model
        self.URL = f'https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}'
        self.HEADERS = {'Content-Type': 'application/json'}
        self.RUNNING_TOKEN_COUNT =0
        
        self.entropy_threshold = 4.8 # Entropy is a measure of the randomness in a string of text (used to ignore serial numbers, etc.)

        self.test_folder_path = test_folder_path

        self.COMBINED_SUMMARY_FILE_PREFIX = "summary_combined_"
        self.CLEAN_TEXT_EXTRACTION_FILE_SUFFIX= "_clean"
        self.CLEAN_TEXT_EXTRACTION_FILE_TYPE= ".md"
        self.JSON_SUMMARY_FILE_SUFFIX= "_summary"
        self.JSON_SUMMARY_FILE_TYPE= ".json"
        self.SUMMARY_FILE_SUFFIX= "_summary"
        self.SUMMARY_FILE_TYPE= ".md"

        self.OVERWRITE_EXISTING_FILES = False
        self.pdf_types = ['.pdf']
        self.image_types = ['.jpg', '.jpeg', '.png', '.bmp', '.eps', '.tiff', 
                            '.webp', '.svg', '.ppm', '.sgi', '.iptc', '.pixar', '.psd', '.wmf']
        
        self.office_document_types = ['.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls']
        self.all_types = self.pdf_types + self.image_types + self.office_document_types
        self.pytesseract_executable_path = '/opt/homebrew/bin/tesseract'
        self.force_rerun = force_rerun

    def main(self):

        PATH_PARAMETER = sys.argv[1] if len(sys.argv) >= 2 else self.test_folder_path
        if len(sys.argv) >= 3 and sys.argv[2] == "force_rerun":
            self.force_rerun = True 
            
        pdf_files_to_process = []
        image_files_to_process = []
        officedocs_to_process = []
        
        if not os.path.exists(PATH_PARAMETER):
            self.logger.log(f"Error: Folder/File path not found: {sys.argv[1]}",color="RED")
            sys.exit(1)
        
        if os.path.isdir(PATH_PARAMETER):
            for root, dirs, files in os.walk(PATH_PARAMETER):
                for file in files:
                    if file.startswith("~"):
                        continue
                    if file.endswith(".pdf"):
                        pdf_files_to_process.append(os.path.join(root, file))
                    if file.endswith(tuple(self.image_types)):
                        image_files_to_process.append(os.path.join (root, file))
                    if file.endswith(tuple(self.office_document_types)):
                        officedocs_to_process.append(os.path.join(root, file))
        
        if os.path.isfile(PATH_PARAMETER) and not PATH_PARAMETER.startswith("~"):
            if file.endswith(".pdf"):
                pdf_files_to_process.append(os.path.join(root, file))
            if file.endswith(tuple(self.image_types)):
                image_files_to_process.append(os.path.join (root, file))
            if file.endswith(tuple(self.office_document_types)):
                officedocs_to_process.append(os.path.join(root, file))
        
        if len(pdf_files_to_process) == 0 and len(image_files_to_process) == 0 and len(officedocs_to_process) == 0:
            self.logger.log(f"No PDF, Image, or Office Doc files found to process given input: {sys.argv[1]}",color="YELLOW")
            sys.exit(0)     
        
        
        ##!# Process PDF files
        for file in pdf_files_to_process:
            try: 
                skip_extraction = False
                
                
                # get the important parts of the file path
                pdf_folder_path = os.path.dirname(file)
                pdf_file_name = os.path.basename(file)
                base_folder_path = file.replace("/_attachments", "").replace(f"/{pdf_file_name}", "")
                
                # Get the path of the folder where the file is located
                # Make sure the folders for attachments and working files exist
                if "_attachments" not in pdf_folder_path:
                    attachment_folder_path = os.path.join(base_folder_path, "_attachments")
                else:
                    attachment_folder_path = pdf_folder_path
                working_folder_path = os.path.join(base_folder_path, "_working")
                
                if not os.path.exists(attachment_folder_path):
                    os.makedirs(attachment_folder_path)
                if not os.path.exists(working_folder_path):
                    os.makedirs(working_folder_path)
                
                # Create the names for the raw_extract file and the clean_extract file
                raw_text_file = os.path.join(working_folder_path, pdf_file_name.replace(".pdf", "_raw.txt"))    
                clean_text_file = os.path.join(base_folder_path, pdf_file_name.replace(".pdf", self.CLEAN_TEXT_EXTRACTION_FILE_SUFFIX + self.CLEAN_TEXT_EXTRACTION_FILE_TYPE))
                
                # Check if the raw text file exists ... some part of the process may have already been run
                if os.path.isfile(raw_text_file) and not self.force_rerun:
                    self.logger.log(f"Raw Text file '{os.path.basename(raw_text_file)}' already exists. Skipping Extraction.",color="YELLOW")
                    with open(raw_text_file, 'r') as f:
                        standard_text = f.read()
                        skip_extraction = True
                
                # Check if the clean text file exists ... some part of the process may have already been run
                if os.path.isfile(clean_text_file) and not self.force_rerun:
                    self.logger.log(f"Cleaned file '{os.path.basename(clean_text_file)}' already exists. Skipping.",color="YELLOW")
                    # Move onto the next file
                    continue
                
                if not skip_extraction:
                    self.logger.log(f"Begin extracting text from '{os.path.basename(file)}'.")
                    raw_text, possible_title = self.pdf_to_text(file)
                    with open(raw_text_file, 'w') as f:
                        f.write(raw_text)
                    
                    standard_text = asyncio.run(self.standardize_extracted_text(raw_text))
                    self.logger.log(f"Successfully extracted and standardized text from '{os.path.basename(file)}'.", color="GREEN")
                    
                        # Combine all extracted text

                    
                clean_text = asyncio.run(self.clean_extracted_text(standard_text))
                self.logger.log(f"Successfully cleaned text from '{file}'.",color="GREEN")
                clean_text = clean_text.replace("####\n", "\n")
                clean_text = clean_text.replace("\n\n\n", "\n\n")
                clean_text = clean_text.replace("\n\n", "\n")
                clean_text = clean_text.replace("___", "")
                clean_text = clean_text.replace("\n####P", "\n#### P")
                clean_text = clean_text.replace("\n#### <font color=", "___\n#### <font color=")
                
                header = f"___"
                header = f"{header}\nTitle: {possible_title}"
                header = f"{header}\nFile: {pdf_file_name}"
                header = f"{header}\nFormat: {os.path.splitext(pdf_file_name)[1].upper()}"
                header = f"{header}\nCreatedOn: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
                header = f"{header}\nTags: [#PDF, #OCR]"
                header = f"{header}\n___"
                
                if not "_attachments" in file:
                    #Move the pdf file to the attachments folder
                    final_pdf_file_path = os.path.join(attachment_folder_path, pdf_file_name)
                    shutil.move(file, final_pdf_file_path)
                else:
                    final_pdf_file_path = file
                    
                clean_text = f"{header}\n\n##### {possible_title}\n\n![[_attachments/{pdf_file_name}]]\n{clean_text}"
                
                with open(clean_text_file, 'w') as f:
                    f.write(clean_text)
                    
                self.logger.log(f"Successfully cleaned and saved text to:\n\033[1;36m'{clean_text_file}'.",color="GREEN")
                
            
            except Exception as e:
                self.logger.log(f"Error: {e}",color="RED")
                continue
        self.logger.log("All PDF files processed.",color="PURPLE")
        
        ##!# Process Images files
        for file in image_files_to_process:
            try: 
                if "_attachments/images_" in file:
                    continue
            
                image_extension = os.path.splitext(file)[1] 
                file_name = os.path.basename(file)
                base_folder_path = file.replace("/_attachments", "").replace(f"/{file_name}", "")
                file_directory_name_only = os.path.dirname(file)
                clean_image_text_file = os.path.join(base_folder_path, file_name.replace(image_extension, "_clean.md"))
                
                if os.path.isfile(clean_image_text_file) and not self.force_rerun:
                    self.logger.log(f"Cleaned Image file '{clean_image_text_file}' already exists. Skipping.",color="YELLOW")
                    continue
                
                
                self.logger.log(f"Image file found: {file}",color="YELLOW") 
                image_raw_text = asyncio.run(self.image_to_text(file))
                clean_text = asyncio.run(self.clean_extracted_text(image_raw_text))
                possible_title = asyncio.run(self.try_and_get_document_title(clean_text))
                
                # Best efforts to clean up the text from OCR
                clean_text_lines = clean_text.split("\n")
                valid_lines = []
                invalid_lines = []
                
                for line in clean_text_lines:
                    if not line or line.strip() == "" or line.replace("#", "").strip() == "":
                        continue
                    plain_text = self.markdown_to_plain_text(line)
                    line_text_entropy = self.calculate_entropy(plain_text)
                    if line_text_entropy > self.entropy_threshold:
                        invalid_lines.append(line)
                    else:
                        valid_lines.append(line)
                        
                
                # Create the header for the markdown file
                header = f"___"
                header = f"{header}\nTitle: {possible_title}"
                header = f"{header}\nFile: {os.path.basename(file)}"
                header = f"{header}\nFormat: {os.path.splitext(file)[1].upper()}"
                header = f"{header}\nCreatedOn: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
                header = f"{header}\nTags: [#{image_extension}, #OCR, #IMAGE]"
                header = f"{header}\n___"
                
                if not "_attachments" in file_directory_name_only:
                    #Move the image file to the attachments folder
                    final_absolute_path = f"{file.replace(file_name, "_attachments")}/{file_name}"
                    shutil.move(file, final_absolute_path)
                
                final_text = f"{header}\n\n##### {possible_title}\n\n![[_attachments/{file_name}]]\n{"\n".join(valid_lines)}"
                
                with open(file.replace(image_extension, f"_clean.md"), 'w') as f:
                    f.write(final_text)
            
            except Exception as e:
                self.logger.log(f"Error: {e}",color="RED", force_print=True)
                continue
        self.logger.log("All Image files processed.",color="PURPLE")
        
        ##!# Process Office Docs files
        for file in officedocs_to_process:
            # try: 
                self.logger.log(f"Processing Offic Document: {file}",color="YELLOW") 
                
                
                # Extract the text (no cleaning necessary
                office_doc_text = asyncio.run(self.office_doc_to_text(file))
                # with open(clean_doc_text_file, 'w') as f:
                #     f.write(office_doc_text)
            # except Exception as e:
            #     self.logger.log(f"Error: {e}",color="RED", force_print=True)
            #     continue
        self.logger.log("All Office Docs processed.",color="PURPLE")
        
        self.logger.log("All documents processed.",color="GREEN", force_print=True)
    
    def process_image_pool(self, image):
        text = pytesseract.image_to_string(image)
        return text
    
    def pdf_to_text(self, file_path):
        
        # Convert PDF to a list of images
        images = convert_from_path(file_path)
        self.logger.log(f"Converted PDF to images.")
        # Determine the number of processes to use (you can adjust this)
        num_processes = min(cpu_count(), len(images))
        
        # Create a Pool of worker processes
        with Pool(processes=num_processes) as pool:
            # Map each image to a process
            results = pool.map(self.process_image_pool, images)
        
        if not results or len(results) == 0:
            self.logger.log(f"Error: No text extracted from '{file_path}'.",color="RED")
            return ""
            
        if len(results) == 1:
            starting_text =  results[0]
        elif len(results) > 1:
            starting_text = f"{results[0]}\n{results[1]}"   
        
        possible_title = asyncio.run(self.try_and_get_document_title(starting_text))
        


        #### <font color="#e36c09">{os.path.basename(file_path)}</font>
        

        all_text = ''
        for i, sentence in enumerate(results):
            
            # Append the, now formatted, sentences to the all_text and add page numbers to the top of each page
            all_text = f'{all_text}\n___ \n#### <font color="#92d050">Page {i + 1}</font> \n\n{sentence}\n'

        return all_text, possible_title

    def calculate_entropy(self, text):
        # Count the frequency of each character in the string
        frequencies = Counter(text)
        total_chars = len(text)

        # Calculate probabilities and entropy
        entropy = 0
        for freq in frequencies.values():
            prob = freq / total_chars
            if prob != 0:  # Handle the case where the probability is zero
                entropy -= prob * math.log2(prob)

        return entropy
    
    async def image_to_text(self, file_path ):
        
        # Get the file extension
        file_extension = os.path.splitext(file_path)[1] 
        
        # Check if the file extension is supported
        if file_extension not in self.image_types:
            msg = f"File type {file_extension} not supported for file {file_path}"
            self.log_it(msg, level='error')
            return file_path, False, msg
        
        # Configure the path to the tesseract executable
        pytesseract.pytesseract.tesseract_cmd = self.pytesseract_executable_path

        try:
            # Load the image
            image = Image.open(file_path)
            
            # Use Tesseract to do OCR on the image
            text = pytesseract.image_to_string(image)
            
            return text
            
        except Exception as e:
            msg = f"Error: {e}"
            self.log_it(msg, "ERROR")
            return msg
    
    async def standardize_extracted_text(self, ocr_text):
        
        # Identify extraction-created unnecessary line breaks (for preservation and later standardization)
        # Note: the below will remove the line breaks that are not part of any title
        # lines however we will restore those carefully 
        mutiple_line_breaks = f"{uuid.uuid4()}"
        ocr_text = ocr_text.replace("\n\n\n\n\n", mutiple_line_breaks)
        ocr_text = ocr_text.replace("\n\n\n\n", mutiple_line_breaks)
        ocr_text = ocr_text.replace("\n\n\n", mutiple_line_breaks)
        ocr_text = ocr_text.replace("\n\n", mutiple_line_breaks)
        # ocr_text = ocr_text.replace(". \n", mutiple_line_breaks)
        # ocr_text = ocr_text.replace(".  \n", mutiple_line_breaks)
        
        #Eliminate line brakes from mid-word wraps
        ocr_text = ocr_text.replace("- \n", "")
        ocr_text = ocr_text.replace("-\n", "")
        
        # Clean up double periods
        ocr_text = ocr_text.replace("..", ".  \n")  
        
        # Remove dangling periods (likely scanned image blips)
        ocr_text = ocr_text.replace("\n. ", "")
        ocr_text = ocr_text.replace("\n.", "")
        ocr_text = ocr_text.replace("# ", "")
        
        # Restore places that previously had multiple line breaks to have 1 line break
        standardized_text = ocr_text.replace(mutiple_line_breaks, "  \n")
        return standardized_text
    
    def markdown_to_plain_text(self, markdown_text):
        # Convert Markdown to HTML
        html = markdown(markdown_text)
        # Use BeautifulSoup to convert HTML to plain text
        soup = BeautifulSoup(html, "html.parser")
        plain_text = soup.get_text()
        return plain_text    
    
    def standardize_markdown_headers(self, markdown_text):
        # Scanned text has line break on every wrap of body text.  If a line break doe not conform to the
        # above patterns, the line break should likely be removed (unless it is a tile line)
        # Each text line has no \n (because of the split), but we will add them before and after titles
        
        multiple_line_breaks = f"{uuid.uuid4()}"
        #Retain multiple line breaks wherever they are ...
        markdown_text = markdown_text.replace("\n\n", multiple_line_breaks)
        markdown_text = markdown_text.replace("\n\n\n", multiple_line_breaks)
        
        text_lines = markdown_text.split("\n")
        title_indicators = ["######", "#####", "####", "###" "##", "#"]
            
        standardized_lines = []
        for line in text_lines:
            if not line or line.strip() == "":
                continue
            
            line = line.replace(".. ", ".  ")
            line = line.replace("# #", "####")

            for title_indicator in title_indicators:
                if title_indicator in line:
                    line = line.replace(title_indicator, f"\n####")
                    line = f"{line}\n"
                    line = line.replace(multiple_line_breaks, "\n")
                    standardized_lines.append(line)
                    continue        
        
        # Reassemble the sentence using spaces instead of \n
        # The  majority of paragraphs that had wrap-created line breaks mid sentence 
        # should be corrected now. 
        markdown_text = " ".join(line for line in standardized_lines if line and line.strip() != "" and line.replace("#", "").strip() != "")  
        return markdown_text

    async def fetch_gemini_response(self, prompt=None, data=None, timeout=15, return_data_on_error=False):
        
        return_value_on_error = None
        
        if return_data_on_error:
            return_value_on_error = data
        
        if not prompt:
            return return_value_on_error
        
        if data:
            prompt = f"{prompt}\n{data}"
        
        limits = httpx.Limits(max_keepalive_connections=None, max_connections=None)
        timeout = httpx.Timeout(timeout, read=timeout)
        KeepTrying = True
        TryCount = 0
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
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
        
        response = None
        
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            while KeepTrying and TryCount <= 3:
                TryCount += 1
                try:
                    response = await client.post(self.URL, headers=self.HEADERS, json=payload)
                    response.raise_for_status()
                except Exception as e:
                    tqdm_asyncio.write(f"Error: {e}")
                    if TryCount > 3:
                        KeepTrying = False
                        tqdm_asyncio.write(f"Error: Failed to get response after {TryCount} tries.")
                        return return_value_on_error
                    else:
                        tqdm_asyncio.write(f"Warning: Retrying request {TryCount}...")
                        await asyncio.sleep(5*TryCount)
                        continue
            
            
        try:
            result = response.json()
            self.RUNNING_TOKEN_COUNT += int(result.get('usageMetadata', {}).get('totalTokenCount', 0))
        
            if result['candidates'][0]['finishReason'] == 'RECITATION':
                tqdm_asyncio.write("Warning: Possible copyrighted or sensitive content detected. Returning original text.", color="ORANGE")
                return return_value_on_error  # Return original text if flagged
            else:    
                value_to_return = result['candidates'][0]['content']['parts'][0]['text']
                return value_to_return

        except Exception as e:
            tqdm_asyncio.write("Could not process the response.json() from Gemini.")
            if response:
                tqdm_asyncio.write(f"Value of result: \n${response} \n\n Error: {e}")
            return return_value_on_error
                
    async def extract_json_dict_from_llm_response(self, llm_response):
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
        start_idx = llm_response.find('{')
        end_idx = llm_response.rfind('}')

        if start_idx == -1 or end_idx == -1:
            return None

        try:
            # Extract the JSON string
            json_string = llm_response[start_idx:end_idx + 1]
            
            json_dict = try_to_json(json_string)
            if  isinstance(json_dict, dict) or isinstance(json_dict, list):
                return json_dict
            else:
                return None
        except Exception as e:
            return None

    async def create_prompt_to_clean_ocr_text(self):
            
        json_response_format = {"transformedtext": "the transformed text you create", "commentary": "Commentary you feel is necessary about how you did or did not clean the text."}

        instructions = f"""Transform the following OCR-extracted text into clean, readable MARKDOWN. 
        Return the MARKDOWN in the specified JSON format. The text is part of a longer document that was split on ". "
        please look for sentences with preceeding title text and apply reasonable line breaks and MARKDOWN "#" header formatting.

        1. Accuracy: Correct OCR errors, ensuring the text is accurate.
        2. Readability: Make the text clear and easy to understand.
        3. Structure: Preserve the original structure (e.g., lists, headings).
        4. Legal Context: If the document is a legal document, maintain the integrity of ALL legal language.
        5. Organization: Keep the names of these organizations as they are: Fincentric, Markit On Demand, Markit, S&P, Wall Street On Demand, JBI, Communify.
        6. Uncertain Words: If a word is unclear, mark it with a question mark in brackets [?].
        7. Make sure to maintain existing valid MARKDOWN and HTML formatting (if it is around the page numbers)
        
        Your response is being systematically integrated. Only return the MARKDOWN in the specified JSON in the format below:
        {json.dumps(json_response_format, indent=4)}
        

        OCR Text:"""

        return instructions
        
    async def spread_tasks(self, tasks, rate_limit):
        semaphore = asyncio.Semaphore(rate_limit)

        async def schedule_task(task):
            async with semaphore:
                result = await task
            return result

        # Gather all tasks with semaphore control
        results = await tqdm_asyncio.gather(
            *[schedule_task(task) for task in tasks]
        )
        return results

    async def clean_extracted_text(self, raw_text):
        async def extract_cleaned_text_from_gemini_response(prompt, data):
            def try_to_json(input_value):
                try:
                    return json.loads(input_value)
                except:
                    pass
                try:
                    return json.loads(f"[{input_value}]")
                except:
                    return input_value
            
            
            llm_response = await self.fetch_gemini_response(prompt, data, return_data_on_error=True)
            
            # Find the first '{' and the last '}'
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}')

            if start_idx == -1 or end_idx == -1:
                return None

            try:
                # Extract the JSON string
                json_string = llm_response[start_idx:end_idx + 1]
                
                json_dict = try_to_json(json_string)
                if  isinstance(json_dict, dict):
                    clean_text = json_dict.get('transformedtext', "No title found")
                    return clean_text
                else:
                    return None
            except Exception as e:
                return None
        
        # Example usage
        self.logger.log("Beginning to clean text with Gemini...", color="GREEN")

        sentences = raw_text.split(". ")  # Split into sentences
        self.logger.log(f"Split text into {len(sentences)} sentences.")

        prompt = await self.create_prompt_to_clean_ocr_text()
        
        cleaning_tasks = [extract_cleaned_text_from_gemini_response(prompt, sentence) for sentence in sentences if sentence and sentence.strip() != "" and len(sentence.strip()) > 1]
        rate_limit = 6  # Set the rate limit (e.g., X API calls per second)
        
        self.logger.log(f"Rate limit: {rate_limit} API calls per second.")
        start_time = datetime.now()
        self.logger.log(f"Starting time: {start_time}")
        cleaned_sentences = await self.spread_tasks(cleaning_tasks, rate_limit)
        end_time = datetime.now()
        time_delta_int = int((end_time - start_time).total_seconds())
        self.logger.log(f"Time taken: {time_delta_int} | {len(cleaned_sentences)} sentences. \n {self.RUNNING_TOKEN_COUNT} tokens used. {self.RUNNING_TOKEN_COUNT/len(cleaned_sentences)} average tokens per sentence. {self.RUNNING_TOKEN_COUNT/time_delta_int} average tokens per second.")
        
        text_only_sentence = [self.standardize_markdown_headers(sentence) for sentence in cleaned_sentences if sentence and sentence.strip() != ""]
        
        all_sentences = []
        
        for sentence in text_only_sentence:
            if sentence.strip().endswith("."):
                sentence = sentence[:-1]
            all_sentences.append(sentence)
                
        cleaned_text = ".  ".join(all_sentences)
        
        return cleaned_text

    async def try_and_get_document_title(self, some_text):
        
        json_response_format = {"title": "[Formal Title of Document]"}

        prompt = f"""Given the text below, which is the first part of a document or set of images, please attempt to obtain the formal title of the document or create one based on the content and return it in the specified JSON format.:
        
        ### Start of Text ###
        {some_text}
        ### End of Text ###
        
        Your response is being systematically integrated. Only return the title in the specified JSON format below:
        {json.dumps(json_response_format, indent=4)}"""
        try: 
        
            # Ask Gemini to get the title of the document
            response = await self.fetch_gemini_response(prompt)
            
            dict_response = await self.extract_json_dict_from_llm_response(response)
            if isinstance(dict_response, dict):
                return_text = dict_response.get('title', "No title found")
                return return_text
            else:
                return "No title found"
            result = response.json()
        
            
        except:
            self.logger.log("Warning: JSON format not detected. No title found", color="ORANGE")
            return "No title found"
    
    async def excel_to_text(self, excel_file_path):

        # Load the Excel file
        excel_data = pd.ExcelFile(excel_file_path)
        
        md_file_text = []
        for sheet_name in excel_data.sheet_names:
            # Write the sheet name
            md_file_text.append(f"# {sheet_name}\n")
            md_file_text.append(f"\n___\n\n")
            
            # Load the sheet into a DataFrame
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            # Format the header
            header = '| ' + ' | '.join([f'**{col}**' for col in df.columns]) + ' |\n'
            separator = '| ' + ' | '.join(['---' for _ in df.columns]) + ' |\n'
            
            md_file_text.append(header)
            md_file_text.append(separator)
            
            # Write the data rows
            for index, row in df.iterrows():
                row_values = []
                for value in row:
                    if isinstance(value, (int, float)):
                        row_values.append(f"{value}")
                    elif isinstance(value, datetime):
                        row_values.append(f"{value.strftime('%Y-%m-%d')}")
                    else:
                        row_values.append(f"{value}")
                row_str = '| ' + ' | '.join(row_values) + ' |\n'
                md_file_text.append(row_str)
            
            # Add space between sheets
            md_file_text.append('\n\n')
        return md_file_text
        
    async def office_doc_to_text(self, file_path):
        
        supported_doc_types = ['.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls']
        
        # Get the file extension
        file_extension = os.path.splitext(file_path)[1]
        
        # Check if the file extension is supported
        if file_extension not in supported_doc_types:
            msg = f"File type {file_extension} not supported for file {file_path}"
            self.log_it(msg, level='error')
            return file_path, False, msg
        
        # Get the approaciate document loader based on the file extension
        if file_extension in ['.docx', '.doc']:
            pass# doc_loader = UnstructuredWordDocumentLoader(file_path=file_path, mode="elements")
        
        if file_extension in ['.pptx', '.ppt']:
            from pptx2md import convert

            # Specify the path to the pptx file
            pptx_file = file_path

            # Convert the pptx file to markdown
            markdown_content = convert(pptx_file, title)

            # Optionally, write the markdown content to a file
            with open("output.md", "w") as md_file:
                md_file.write(markdown_content)
            # markdown_text = await self.create_dictionary_from_ppt([file_path])
            # doc_loader = UnstructuredPowerPointLoader(file_path=file_path, mode="elements")
        
        if file_extension in ['.xlsx', '.xls']:
            markdown_text = await self.excel_to_text(file_path)
        
        try:
            
            # Load the document 
            return markdown_text
        
        except Exception as e:
            msg = f"Error: {e}"
            self.log_it(msg, "ERROR")
            return file_path, False, msg
        
    
    
        
if __name__ == "__main__":
    test_folder = "/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/test_text_extraction"
    extractor = TextExtractor(test_folder_path=test_folder, force_rerun=True)
    extractor.main()
        