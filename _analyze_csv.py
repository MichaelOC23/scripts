import sys
import csv
import re
import pandas as pd

def analyze_csv(csv_path):
    # Define pattern to detect special characters (excluding ., ,, /, $, @, &, -, :, ;, %, _)
    special_char_pattern = re.compile(r'[^a-zA-Z0-9_ /$@&-:;%,.]+')

    def check_special_characters(text):
        return special_char_pattern.findall(text)

    def detect_encoding(file_path):
        encodings = ['utf-8', 'latin1', 'ISO-8859-1']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as file:
                    file.read()
                return enc
            except UnicodeDecodeError:
                continue
        raise ValueError("Cannot determine file encoding")

    encoding = detect_encoding(csv_path)

    with open(csv_path, 'r', newline='', encoding=encoding) as csvfile:
        reader = csv.reader(csvfile)

        # Get header row
        headers = next(reader)

        # Check for duplicate headers
        if len(headers) != len(set(headers)):
            print("Warning: Duplicate headers detected.")
            duplicates = set([header for header in headers if headers.count(header) > 1])
            print(f"Duplicate headers: {duplicates}")

        # Check for special characters in headers
        for i, header in enumerate(headers):
            special_chars = check_special_characters(header)
            if special_chars:
                print(f"Header '{header}' in column {i+1} contains special characters: {''.join(special_chars)}")

        # Process each row
        for row_number, row in enumerate(reader, start=1):
            # Check if row length matches header length
            if len(row) != len(headers):
                print(f"Row {row_number + 1} has a mismatch in number of columns (expected {len(headers)}, got {len(row)}).")

            for col_index, value in enumerate(row):
                # Treat every column value as a string
                value_str = str(value)

                # Check for special characters in the value
                special_chars = check_special_characters(value_str)
                if special_chars:
                    print(f"Row {row_number + 1}, Column {headers[col_index]}: Found special characters in value '{value_str}': {''.join(special_chars)}")

                # Check for invisible characters in what should be empty strings
                if value_str.strip() == '' and len(value_str) > 0:
                    print(f"Row {row_number + 1}, Column {headers[col_index]}: Found invisible characters in what appears to be an empty string")

                # Check for NaN values
                if value_str.lower() == 'nan':
                    print(f"Row {row_number + 1}, Column {headers[col_index]}: Found NaN value")

    # Additional checks using pandas
    try:
        df = pd.read_csv(csv_path, encoding=encoding)
    except pd.errors.ParserError as e:
        print(f"Pandas parsing error: {e}")
        return

    # Check for mixed data types in columns
    for col in df.columns:
        if df[col].apply(type).nunique() > 1:
            print(f"Column '{col}' contains mixed data types.")

    # Check for trailing delimiters (extra empty columns)
    if len(df.columns) != len(headers):
        print("Warning: Detected trailing delimiters leading to extra columns.")
    
    # Check for inconsistent newlines (rows with unexpected line breaks)
    with open(csv_path, 'r', encoding=encoding) as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if '\n' in line[:-1] or '\r\n' in line[:-2]:
                print(f"Line {i+1} contains inconsistent newline characters.")

    print("CSV analysis complete.")

def compare_files(file_a_path, file_b_path):
    # Read file A
    with open(file_a_path, 'r', encoding='utf-8') as file_a:
        content_a = file_a.read()
    
    # Read file B
    with open(file_b_path, 'r', encoding='utf-8') as file_b:
        content_b = file_b.read()
    
    # Create sets of characters from both files
    set_a = set(content_a)
    set_b = set(content_b)
    
    # Find characters that are in A but not in B
    diff_characters = set_a - set_b
    
    # Print the results
    if diff_characters:
        print("Characters in file A that are not in file B:")
        for char in diff_characters:
            # Display non-printable characters in their hexadecimal form
            if char.isprintable():
                print(f"'{char}'")
            else:
                print(f"'\\x{ord(char):02x}'")
    else:
        print("All characters in file A are also in file B.")

# Example usage
# file_a_path = '/Users/michasmi/code/mytech/docker/Utils/scripts/gmtc/account_holdings.csv'
# file_b_path = '/Users/michasmi/code/mytech/docker/Utils/scripts/gmtc/account_transactions.csv'
# compare_files(file_a_path, file_b_path)

if len(sys.argv) != 2:
    print("Usage: python _analyze_csv.py <csv_path>")
    sys.exit(1)
csv_path = sys.argv[1] if len(sys.argv) > 1 else '/Users/michasmi/code/mytech/docker/Utils/scripts/gmtc/holdings_out.csv'
analyze_csv(csv_path)