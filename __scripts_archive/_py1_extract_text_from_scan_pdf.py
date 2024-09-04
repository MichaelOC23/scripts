import os
import sys
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

DEFAULT_FILE_PATH = "/Users/michasmi/Prod-Cust-Serv/Customer-Contract-3.5.1.1 Bank of America Merill Lynch (BAML)/3.5.1.1.1.6 20070522_Merrill Lynch Application Development and Hosting Agreement.pdf"
RAW_TEXT_EXTRACTION_FILE_SUFFIX= "_raw_extract.txt"

def main():
    FILE_PATH = sys.argv[1] if len(sys.argv) == 2 else DEFAULT_FILE_PATH
    # # Check for a sys argument
    # if len(sys.argv) != 2:
    #     print(f"Usage: python extract_text_from_scan_pdf.py <input_pdf_path>")
    # if not DEFAULT_FILE_PATH:
    #     sys.exit(1)
    
    if not os.path.exists(FILE_PATH):
        print(f"Error: File not found: {sys.argv[1]}")
        sys.exit(1)
    

    output_text_file = FILE_PATH.replace(".pdf", RAW_TEXT_EXTRACTION_FILE_SUFFIX)
    
    print(f"Extracting text from {FILE_PATH}")

    pdf_to_text(FILE_PATH, output_text_file)
    
    print(f"Text extracted and saved to {output_text_file}")
    


def pdf_to_text(pdf_path, output_text_file):
    """
    Extracts text from a PDF file that contains images using OCR and writes the text to an output file.

    Parameters:
    pdf_path (str): The path to the PDF file.
    output_text_file (str): The path to the output text file.
    """
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    all_text = ""
    
    for i, image in enumerate(images):
        # Perform OCR on each image
        text = pytesseract.image_to_string(image)
        all_text += text + "\n"
    
    # Write the extracted text to the output file
    with open(output_text_file, 'w') as f:
        f.write(all_text)

if __name__ == "__main__":
    main()
    