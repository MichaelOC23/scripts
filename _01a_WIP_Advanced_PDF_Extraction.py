# To read PDFs
# import tkinter


# To analyze PDF layouts and extract text
from cv2 import log
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure

import asyncio
import aiohttp
import math

#Office Documents
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredPowerPointLoader, text
from langchain_community.document_loaders import UnstructuredExcelLoader
import langchain_core as core

# To extract text from tables in PDF
import pdfplumber
import PyPDF2

# To extract the images from the PDFs
from PIL import Image
from pdf2image import convert_from_path

# To perform OCR to extract text from images 
import pytesseract 

# Standard Python libraries
import os
from pathlib import Path

import re
import sys
import fnmatch

# from cv2 import log
import math
from collections import Counter

# Add the parent directory to sys.path
import tempfile
import json
import subprocess

#Extraction of text from images
import pytesseract
from PIL import Image

from datetime import datetime




class extract_text_from_file:
    def __init__(self, keep_it_simple=True):
        self.parent_dir = str(Path(__file__).resolve().parent.parent)
        self.entropy_threshold = 4.8 # Entropy is a measure of the randomness in a string of text (used to ignore serial numbers, etc.)
        self.prior_values_set = set() 

        self.office_document_types = ['.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls']
        self.pdf_types = ['.pdf']
        self.gif_types = ['.gif']
        self.image_types = ['.jpg', '.jpeg', '.png', '.bmp', '.eps', '.tiff', 
                            '.webp', '.svg', '.ppm', '.sgi', '.iptc', '.pixar', '.psd', '.wmf']
        
        
        self.all_types = self.office_document_types + self.pdf_types + self.image_types + self.gif_types
        self.all_types = [".pdf"]
        #Construction of the dictionary which will drive the structure of the JSON to be output
        self.text_structures = ['by_page', 'all_pages', 'useful', 'ignored']
        self.text_styles = ['max_font_size', 'formats_concat']
        self.text_element_types = ['element_type']
        self.new_files_for_append = set()
        self.pytesseract_executable_path = '/opt/homebrew/bin/tesseract'
        self.all_extracts_dict = {}
        self.all_extracts_path = ''
        
    def create_empty_record(self):
        import datetime
        import uuid
        return {
        
                "id": str(uuid.uuid4()),
                "timestamp": datetime.datetime.now().isoformat(),
                "content": "",
                "source": "",
                "filename": "",
                "last_modified": "",
                "page_count": -1,
                "type":"",
                "categories": [],
                "languages": [],
                "filetype": "",
                "collection": "",
                "tags": []
                }
        
    def safe_remove(self, file_path):
        try:
            # Attempt to remove the file
            os.remove(file_path)
        except FileNotFoundError:
            # If the file does not exist, just pass
            pass
        except Exception as e:
            # Handle other possible exceptions (e.g., permission issues)
            print(f"Error while deleting file: {e}")

    def log_it(self, message, level='info'):
        if level == 'info':
            pass
        # print(message)
        elif level != 'info':
            pass
        # print(f"\033[96m{level.upper()}: {message}\033[00m")

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
    
    def get_file_extension(self, file_path):
            # Split the path and get the extension part
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()
            return file_extension
    
    def create_key_safe_path(self, file_path):
        # Get the home directory for the current user to remove it from the file path
        home_dir = os.path.expanduser('~')
        
        # Remove the user-specific part from the path
        if file_path.startswith(home_dir):
            file_path = file_path[len(home_dir):]  # Remove the home directory part

        # Replace spaces with underscores and remove characters that are not allowed in JSON keys
        file_path = file_path.replace(' ', '_')
        file_path = re.sub(r'[^\w\s_-]', '', file_path)  # Keep alphanumeric, underscores, hyphens

        return file_path
    
    def save_json_to_file(self, doc_dict, output_path, mode='replace', file_path=None):
        try:
            
            if not output_path:
                # get the name of the file and replace the extension with .json and put it in the output folder
                output_path = file_path.replace(self.get_file_extension(file_path), '.json')
                print(f"Output Path: {output_path}")
    
            # Create a safe path for the JSON file
            safe_path = self.create_key_safe_path(file_path)
            
            if mode == "replace":
                self.safe_remove(output_path)
            
            # Only erase the first time the file is appended
            if mode == "appendasnew":
                if os.path.exists(output_path) and output_path not in self.new_files_for_append:
                    self.safe_remove(output_path)
                    self.new_files_for_append.add(output_path)
                mode = "append"
            
            self.all_extracts_dict[safe_path] = doc_dict
            
            if output_path != self.all_extracts_path:
                if os.path.exists(output_path) and mode == "append":
                    pass
                    with open(output_path, 'r') as f:
                        # current_document = f.read()
                        # current_doc_dict = json.loads(current_document)
                        # current_doc_dict[safe_path] = doc_dict
                        f.close()
                        
                    with open(output_path, 'w') as f:
                        # f.write(json.dumps(current_doc_dict, indent=4))
                        # self.new_files_for_append.add(output_path)
                        f.close()
                
                else:
                    pass
                    with open(output_path, 'w') as f:
                        # Create a dictionary with the safe path as the key
                        # dict_to_save = {}
                        # dict_to_save[safe_path] = doc_dict
                        # f.write(json.dumps(dict_to_save, indent=4))
                        # self.new_files_for_append.add(output_path)
                        f.close()
            return True, output_path
            
        except Exception as e:
            return False, f"Error: saving file:{output_path}    {e}"

    def extract_json_from_pdf(self, pdf_path, output_path=None, mode="replace", entropy_threshold=4.8 ):
        

        def _create_empty_dict():
            pdf_text = {}

            for structure_item in self.text_structures:
                pdf_text[structure_item] = []
            
            pdf_text['by_page'] = {}

            pdf_text['by_style'] = {}
            for style_item in self.text_styles:
                pdf_text['by_style'][style_item] = {}
                
            pdf_text['by_element_type'] = {}
            for element_type in self.text_element_types:
                pdf_text['by_element_type'][element_type] = []
            
            pdf_text['all_text'] = []

            return pdf_text

        def _add_element_dict_to_json(pdf_text, element_dict):
            if element_dict.get('text', '') == '':
                return pdf_text
            
            pdf_text['all_text'].append(element_dict.get('text', ''))
            
            #structure by_page
            page_str = element_dict['page']
            if element_dict['page'] not in pdf_text['by_page']:
                pdf_text['by_page'][page_str] = []
            pdf_text['by_page'][page_str].append(element_dict)
            
            #structure all_pages
            pdf_text['all_pages'].append(element_dict)
            
            #structure useful/ignored
            pdf_text[element_dict['ignored_or_useful']].append(element_dict)
            
            #style by_style
            for style_item in self.text_styles:
                if element_dict[style_item] not in pdf_text['by_style'][style_item]:
                    pdf_text['by_style'][style_item][element_dict[style_item]] = []
                pdf_text['by_style'][style_item][element_dict[style_item]].append(element_dict)
                
            #element_type by_element_type
            for element_type in self.text_element_types:
                if element_dict[element_type]  not in pdf_text['by_element_type'][element_type]:
                    pdf_text['by_element_type'][element_type]= []
                pdf_text['by_element_type'][element_type].append(element_dict)
            
            # print(f"Added element to JSON: {page_str} {element_dict['text']}")
            return pdf_text

        def _text_extraction(element):
            
            try: 
                # Extracting the text from the in-line text element
                extracted_text = element.get_text()
                if extracted_text == None or extracted_text == '':
                    return (None, None, None)
                
                # Find the formats of the text
                # Initialize the list with all the formats that appeared in the line of text
                font_name = []
                font_size = []
                font_name_and_size = []
                
                max_font_size = 0
                
                # Iterating through each character in each line of text
                #capture the font name and size for each character
                for text_line in element:
                    if isinstance(text_line, LTTextContainer):
                        # Iterating through each character in the line of text
                        for character in text_line:
                            if isinstance(character, LTChar):
                                # Append the font name of the character
                                font_name.append(character.fontname)

                                # Append the font size of the character
                                # Rounding because interpreted font sizes can vary slightly (and this is meaningless for this purpose)
                                font_size_rounded = int(round(character.size, 0))
                                font_size.append(font_size_rounded)
                                
                                # Append a string of fontname and size to line_formats
                                font_name_and_size.append(f'{font_size_rounded:04d}_{character.fontname};')
                                
                # Find the unique font sizes and names in the line
                formats_per_line = list(set(font_name_and_size))

                # Find the maximum font size in the line
                
                if len(font_size) > 0:
                    max_font_size = max(font_size)
                
                # Return a tuple with the text in each line along with its format
                return (extracted_text, formats_per_line, max_font_size)    
            except Exception as e:
                print(f"Error: {e}")
                return (None, None, None)

        def _table_converter(table):
            table_string = ''
            # Iterate through each row of the table
            for row_num in range(len(table)):
                row = table[row_num]
                # Remove the line breaker from the wrapped texts
                cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
                # Convert the table into a string 
                table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')

                # Adding the clean and dirty row to the list of prior values:
                if isinstance(row, list):
                    self.prior_values_set.add(" ".join([item for item in row if item is not None]).strip())
                    self.prior_values_set.add(" ".join(cleaned_row).strip())
                else:
                    self.prior_values_set.add(row)
                    self.prior_values_set.add(cleaned_row)
            
            # Removing the last line break
            table_string = table_string[:-1]

            

            return table_string

        def _extract_nested_dict_from_pdf(pdf_path):

            # pdf_path = 'example.pdf'

            pages_where_tables_processed = set()

            # Initialize the dictionary that is the final output of this function
            pdf_text = _create_empty_dict()
            
            # PDF Plumber is a specialized librar for extracting tables from PDFs
            # better to open it once here then on every table below
            plumbed_pdf = pdfplumber.open(pdf_path) 

            # We extract the pages from the PDF
            #? PDFMiner for loop
            self.log_it(f"Extracting text from PDF: {pdf_path}")
            extracted_pages = list(extract_pages(pdf_path))

            self.log_it(f"PDF Length: {len(extracted_pages)}")
            for pagenum, page in enumerate(extracted_pages):

                # Find all the elements and create a list of tuples with the y coordinate and the element
                # The y coordinate is the top of the element measured from the bottom of the page
                # The greater the y coordinate the higher the element is in the page
                page_elements = [(element.y1, element) for element in page._objs]
                self.log_it(f"Page {pagenum} has {len(page_elements)} elements")
                
                
                # Sort all the elements as they appear in the page 
                # The elements are sorted from the top of the page to the bottom (largest y coordinate to smallest  y coordinate)
                sorted_elements = sorted(page_elements, key=lambda a: a[0], reverse=True)
            

                # Iterate through each element in the page (sorted) to extract the text
                sorted_elements = list(enumerate(sorted_elements))
                for i, sorted_element in sorted_elements:
                    self.log_it(f"Page {pagenum} Element {i} of {len(sorted_elements)} percent complete: {round((i/len(sorted_elements))*100, 2)}%")
                    # Extract the element from the tuple
                    element = sorted_element[1]

                    # Initialize the variable needed for tracking the extracted text from the element
                    element_text = []

                    # Initialize the variables needed for tracking the concatenated formats
                    formats_per_line = []
                    formats_per_line.append("None")
                    max_font_size = 0

                    # initialize a variable to store the page number as a string
                    page_number_str = f'Page_{pagenum:04d}' 
                    
                    # Get the y value for the element in the current iteration
                    y_value= int(round(sorted_element[0],0))
                            
                    # Check the elements for images (if so OCR them)
                    if isinstance(element, LTFigure):

                        # Since there is an image, we will need to crop it out of the PDF,
                        # convert the cropped pdf to an image, and then OCR the image

                        # create a PDF file object
                        pdfFileObj = open(pdf_path, 'rb')
                        
                        # create a PDF reader object (pdfReaded) which is used for cropping images (if there are any)
                        pdfReaded = PyPDF2.PdfReader(pdfFileObj)

                        # This object is used to crop the image from the PDF (if there are any images)
                        pageObj = pdfReaded.pages[pagenum]
                        
                        text_element_type = "image_ocr"

                        # Crop the image from the PDF
                        # Get the coordinates to crop the image from the PDF
                        [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
            
                        # Crop the page using coordinates (left, bottom, right, top)
                        pageObj.mediabox.lower_left = (image_left, image_bottom)
                        pageObj.mediabox.upper_right = (image_right, image_top)
            
                        # Create a PDF writer object that will be used to save the cropped PDF to a new file
                        cropped_pdf_writer = PyPDF2.PdfWriter()
                        try: 
                            cropped_pdf_writer.add_page(pageObj)
                        except Exception as e:
                            print(f"Error: {e}")
                            continue
            
                        # Save the cropped PDF to a new file
                        # cropped_file_path = os.path.join(self.temp_folder, f'{page_number_str}_y{y_value}_cropped_pdf_of_image.pdf')
                        
                        with tempfile.TemporaryDirectory() as temp_dir:
                            cropped_pdf_file_path = os.path.join(temp_dir, f'{page_number_str}_y{y_value}_cropped_pdf_of_image.pdf')
                            cropped_pdf_writer.write(cropped_pdf_file_path)
                            
                            # with open(cropped_file_path, 'wb') as cropped_pdf_file:
                            #      cropped_pdf_writer
                            #      cropped_pdf_writer.write(cropped_pdf_file)
                            # use PdftoImage to convert the cropped pdf to an image
                            images = convert_from_path(cropped_pdf_file_path)
                            image = images[0]
                            image_file_path = os.path.join(temp_dir, f'{page_number_str}_y{y_value}_image_of_cropped_pdf.png')  
                            image.save(image_file_path, "PNG")
                            
                            # Extract the text from the image
                            # Read the image
                            img = Image.open(image_file_path)
                            # Extract the text from the image
                            extracted_text = pytesseract.image_to_string(img)

                        # Add the extracted text to the list of text elements
                        if extracted_text != None and extracted_text != '':
                            element_text.append(extracted_text)
                        
                        # Closing the pdf file object
                        pdfFileObj.close()

                    # Check the elements for tables
                    if isinstance(element, LTRect):
                        text_element_type = "rich_text" 
                        
                        if page_number_str not in pages_where_tables_processed:
                            #! .pages is a list containing one pdfplumber.Page instance per page loaded.
                            pdf_plumber_page = plumbed_pdf.pages[pagenum]
                            
                            # Find the number of tables on the page
                            tables_list = pdf_plumber_page.find_tables()

                            # Check if there are tables on the page
                            if len(tables_list) > 0:

                                # if there are tables on the page, extract the table
                                i = 0
                                for table in tables_list:
                                    table_raw_data = pdf_plumber_page.extract_tables()[i]
                                    formatted_table = _table_converter(table_raw_data)
                                    if formatted_table != None and formatted_table != '':
                                        element_text.append(formatted_table)
                                    i+=1
                                    text_element_type = "table_grid"
                            
                            pages_where_tables_processed.add(page_number_str)
                            

                    
                    # Check if the element is a text element (rich text)
                    if isinstance(element, LTTextContainer):
                        
                        text_element_type = "rich_text" 

                        # Use the function to extract the text and format for each text element
                        (extracted_text, formats_concatenated, font_size) = _text_extraction(element)

                        if extracted_text != None and extracted_text != '':
                            element_text.append(extracted_text)
                            formats_per_line = formats_concatenated
                            max_font_size = font_size

                            self.prior_values_set.add(extracted_text)
                    
                    #combine the list of formats into a single string if there is more than one.
                    if isinstance(formats_per_line, list):
                        all_line_formats = '_'.join(formats_per_line)
                    else:
                        all_line_formats = formats_per_line


                    #detailed json for 2nd pass (wich needs to break out the document into nested sections)
                    line_text = {}
                    line_text['text'] = " ".join(element_text) #the text in element
                    line_text['text_as_list'] = []
                    line_text['text_as_list'].append(element_text) #the text in element
                    line_text['formats_concat'] = all_line_formats #the font size appended to font name
                    line_text['max_font_size'] = max_font_size #the max font size across all chars in the element
                    line_text['element_type'] = text_element_type
                    line_text['page'] = page_number_str # either text_from_body (has a format/font/size) or text_from_image / text from table (which don't have formats/fonts/sizes)
                    line_text['y_value'] = y_value # the y value of the element
                    
                    #The entropy calculation is the likelihood, based on the commonness of proximity of letters of the 
                    #text being a real sentence (or nonsense, likes a serial number)
                    line_text_entropy = self.calculate_entropy(line_text['text'])
                    line_text['entropy'] = round(line_text_entropy, 1)
                    line_text['self.entropy_threshold'] = self.entropy_threshold
                
                
                    structure = 'useful'
                    ignore_reason = ''
                    #determine if the text is useful or ignored based on the entropy threshold
                    
                    if line_text['text'] == None or line_text['text'] == '':
                        structure = 'ignored'
                        ignore_reason = 'Empty or None'
                        
                        if line_text_entropy < self.entropy_threshold:
                            structure = 'ignored'
                            ignore_reason = f'Exceed Entropy Threshold of {self.entropy_threshold}'
                    
                            if line_text['text'] in self.prior_values_set:
                                structure = 'ignored'
                                ignore_reason = 'Duplicate'
                    
                    line_text['ignored_or_useful'] = structure
                    line_text['ignore_reason'] = ignore_reason
                    
                    self.prior_values_set.add(line_text['text'])
                    
                    #add the element to the json
                    pdf_text = _add_element_dict_to_json(pdf_text, line_text)
            
            return pdf_text
            
        # Note/Reminder: Tested entropy_thresholds: 2.1-5.5. 4.8 seems to be the best for this purpose. 
        # It captures the most useful text and ignores the most noise.
        
        self.entropy_threshold = entropy_threshold
        supported_doc_types = ['.pdf']
        
        # Get the file extension
        file_extension = self.get_file_extension(pdf_path)
        
        # Check if the file extension is supported
        if file_extension not in supported_doc_types:
            msg = f"File type {file_extension} not supported for file {pdf_path}"
            self.log_it(msg, level='error')
            return pdf_path, False, msg
        
        try:
            pdf_text = _extract_nested_dict_from_pdf(pdf_path=pdf_path)
            save_result, output_path = self.save_json_to_file(pdf_text, output_path=output_path, mode=mode, file_path=pdf_path)

            return output_path, save_result, pdf_text
        
        except Exception as e:
            msg = f"Error: {e}"
            self.log_it(msg, "ERROR")
            return pdf_path, False, msg
        
    def extract_json_from_office_doc(self, file_path, output_path=None, mode="replace", entropy_threshold=4.8 ):
        """
        Extracts JSON data from an office document (docx, doc, pptx, ppt, xlsx, xls).

        Args:
            file_path (str): The path to the office document file.
            output_path (str, optional): The path to save the extracted JSON file. If not provided, the JSON file will be saved in the same directory as the input file. Defaults to None.
            mode (str, optional): The mode for extracting elements from the document. Defaults to "replace". Can also be "append" to append to an existing JSON file or appendasnew to create a new JSON file with a new name and append to it.
            entropy_threshold (float, optional): The entropy threshold for filtering elements. Defaults to 4.8.

        Returns:
            tuple: A tuple containing the path to the extracted JSON file, a boolean indicating if the extraction was successful, and the extracted JSON data.

        Raises:
            None

        """
        
        def create_dictionary_from_ppt(ppt_documents):
            # Dictionary to store the converted documents
            ppt_dict = {}

            for doc in ppt_documents:
                # Generate a key-safe filename from the original filename in the metadata
                filename = doc.metadata['filename']
                safe_key = re.sub(r'[^\w]', '_', filename)  # Replace non-word characters with underscore

                # Create a list under this filename if it does not already exist
                if safe_key not in ppt_dict:
                    ppt_dict[safe_key] = []

                # Each document's content and metadata can be stored in a dictionary
                doc_info = {
                    'content': doc.page_content,
                    'metadata': doc.metadata
                }

                # Append this document's information to the list associated with the filename
                ppt_dict[safe_key].append(doc_info)

            return ppt_dict

        supported_doc_types = ['.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls']
        
        # Get the file extension
        file_extension = self.get_file_extension(file_path)
        
        # Check if the file extension is supported
        if file_extension not in supported_doc_types:
            msg = f"File type {file_extension} not supported for file {file_path}"
            self.log_it(msg, level='error')
            return file_path, False, msg
        
        # Get the approaciate document loader based on the file extension
        if file_extension in ['.docx', '.doc']:
            doc_loader = UnstructuredWordDocumentLoader(file_path=file_path, mode="elements")
        if file_extension in ['.pptx', '.ppt']:
            doc_loader = UnstructuredPowerPointLoader(file_path=file_path, mode="elements")
        if file_extension in ['.xlsx', '.xls']:
            doc_loader = UnstructuredExcelLoader(file_path=file_path, mode="elements")
        
        try:
            
            # Open the document and extract the JSON data from the document elements
            doc_doc_objs = doc_loader.load()
            
            if file_extension in ['.pptx', '.ppt']:
                doc_dict = create_dictionary_from_ppt(doc_doc_objs)

            else:    
                # turn the document objects into a dictionary
                doc_dict = core.load.dump.dumpd(doc_doc_objs)
                
            save_result, output_path = self.save_json_to_file(doc_dict, output_path=output_path, mode=mode, file_path=file_path)

            return output_path, save_result, doc_dict
        
        except Exception as e:
            msg = f"Error: {e}"
            self.log_it(msg, "ERROR")
            return output_path, False, msg
        
    def extract_json_from_image(self, file_path, output_path=None, mode="replace", entropy_threshold=4.8 ):
        
        # Get the file extension
        file_extension = self.get_file_extension(file_path)
        
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
            
            # Extract detailed information
            # image_cv = cv2.imread(file_path)
            # data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Create a structured dictionary to store text and its box coordinates
            text_dict = {}
            
            text_dict['text'] = text
            if output_path:
                save_result, output_path = self.save_json_to_file(text_dict, output_path=output_path, mode=mode, file_path=file_path)
                return output_path, save_result, text_dict
            else:
                return None, None, text
        
        except Exception as e:
            msg = f"Error: {e}"
            self.log_it(msg, "ERROR")
            return output_path, False, msg
        
    async def extract_json_from_files(self, file_path_list, output_path=None, mode="replace", entropy_threshold=4.8 ):
        
        # Check if the file path is a list
        if not isinstance(file_path_list, list):
            file_path_list = [file_path_list]
        
        if output_path is not None:
            self.all_extracts_path = output_path
        
        for file_path in file_path_list:
            # Get the file extension
            file_name = os.path.basename(file_path)
            start_time = datetime.now()
            print(f"Beginning raw extraction for file: {file_name} at {start_time}")
            file_extension = self.get_file_extension(file_path)
            
            if file_extension in self.office_document_types:
                output_path, save_result, pdf_text = self.extract_json_from_office_doc(file_path, output_path, mode, entropy_threshold)
            elif file_extension in self.pdf_types:
                output_path, save_result, pdf_text = self.extract_json_from_pdf(file_path, output_path, mode, entropy_threshold)
                
            elif file_extension in self.image_types:
                output_path, save_result, pdf_text = self.extract_json_from_image(file_path, output_path, mode, entropy_threshold)
            else:
                msg = f"File type {file_extension} not supported for file {file_path}"
                self.log_it(msg, level='error')
                continue
            # Save the file as a json dumps file in the file path with a cleaned file name a unqiue identifier and the .json extension
                # Do this by replacing the full filename with the cleaned filename 
            raw_extract_file_path = file_path.replace(file_extension, '_raw_extract.txt')
            with open(raw_extract_file_path, "w") as f:
                full_text_extract = " ".join(pdf_text['all_text'])
                f.write(full_text_extract)
                f.close()
            
            print(f"Completed raw extraction for file: {file_name} at {datetime.now()} time to complete was {datetime.now() - start_time}")

            print(f"Beginning the cleaning process for {file_name} at {datetime.now()}")
            await self.clean_extract(full_text_extract, file_path)
            print(f"Completed the cleaning process for {file_name} at {datetime.now()}. Total time to complete was {datetime.now() - start_time}")
    
    async def clean_extract(self, prompt, orig_file_path, max_tokens=12000):
        instructions = """Please transform the following OCR-extracted text into a clean, readable version that closely matches the original document.
        1). Accuracy and Readability: Strive to correct any OCR errors, ensuring the text is readable and as accurate as possible.
        2). Structure: Reconstruct sentence structures, headers, and footnotes appropriately.
        3). Legal Context: This is a legal document, so maintain the integrity of the legal language.
        4). Common Names: Preserve the names of organizations: Fincentric, Markit On Demand, Markit, S&P, and Wall Street On Demand. Do not alter these names.
        5). Uncertain Words: If a word is unclear and is critical to the meaning of the sentence indicate uncertainty with a question mark in brackets [?].
        Note I understand there may be some inaccuracies due to the quality of the OCR, but please make your best effort to ensure the text is as close to the original as possible.
        """
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        # Split the prompt into smaller parts
        prompt_parts = [prompt[i:i+max_tokens] for i in range(0, len(prompt), max_tokens)]
        
        cleaned_parts = []
        for part in prompt_parts:
            request_final = f"{instructions}\n\n{part}"
            request_json = json.dumps({
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": request_final}],
                "temperature": 0.1
            })
            endpoint = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, headers=headers, data=request_json) as response:
                    response_json = await response.json()
                    with open(orig_file_path.replace(self.get_file_extension(orig_file_path), 'json_response.json'), "w") as f:
                        json.dump(response_json, f, indent=4)
                        #   print(f"Raw response: {response_json}")

                    if "choices" in response_json:
                        content = response_json["choices"][0]["message"]["content"]
                    else:
                        content = response_json.get("error", {}).get("message", "Unknown error")

                    cleaned_parts.append(content)

        # Combine the cleaned parts into a single string
        cleaned_content = "\n".join(cleaned_parts)

        dir_path = os.path.dirname(orig_file_path)
        filename = os.path.splitext(os.path.basename(orig_file_path))[0]
        new_file_path = os.path.join(dir_path, f"{filename}_clean.txt")

        with open(new_file_path, "w") as file:
            file.write(cleaned_content)

        print(f"Cleaned content has been saved to: {new_file_path}")
    
    async def recursive_text_extractor(self, directory, file_suffix='_raw_extract.txt'):
        
        file_list = []
        raw_file_path_extracts = []
        for root, _, files in os.walk(directory):
            for file in files:
                if any(fnmatch.fnmatch(file, f"*{ext}") for ext in self.all_types):
                    file_path = os.path.join(root, file)
                    folder_path = os.path.dirname(file_path)
                    raw_extract_file_path = file_path.replace(self.get_file_extension(file_path), file_suffix)
                    raw_file_path_extracts.append (raw_extract_file_path)
                    if not os.path.exists(raw_extract_file_path):
                        file_list.append(asyncio.create_task(self.extract_json_from_files(file_path, raw_extract_file_path)))
        await asyncio.gather(*file_list)
        return
        
            
def main():
    if len(sys.argv) < 2:
        print("No folder path was provided.")
        sys.exit(1)

    folder_path = sys.argv[1]

    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' does not exist or is not a folder.")
        sys.exit(1)

    print(f"Extracting text from the folder: {folder_path}")
    extractor = extract_text_from_file()
    asyncio.run(extractor.recursive_text_extractor(folder_path))



if __name__ == '__main__':
    main()
    

    

