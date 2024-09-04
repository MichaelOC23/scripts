import _class_streamlit
import asyncio
storage = _class_streamlit.PsqlSimpleStorage()
import csv
import json
import re


fields = [
    "Organization CRD#",
    "SEC#",
    "Primary Business Name",
    "Legal Name",
    "Main Office Street Address 1",
    "Main Office Street Address 2",
    "Main Office City",
    "Main Office State",
    "Main Office Country",
    "Main Office Postal Code",
    "Main Office Telephone Number",
    "Chief Compliance Officer Name",
    "Chief Compliance Officer Other Titles",
    "Chief Compliance Officer Telephone",
    "Chief Compliance Officer E-mail",
    "SEC Status Effective Date",
    "Website Address",
    "Entity Type",
    "Governing Country",
    "Total Gross Assets of Private Funds"
    ]


def clean_key(key):
    key = key.strip()
    key = key.replace("#", "")
    # Remove characters that are not alphanumeric or underscores
    return re.sub(r'\W|^(?=\d)', '_', key)

def format_readable_json(json_data):
    return_list = []
    for key in json_data:
        if key != "PartitionKey" and key != "RowKey":
            if json_data.get(key, "") != "":
                if json_data.get(key, "0") != "0":
                    if json_data.get(key, 0) != 0:
                        return_list.append(f"{key}: {json_data[key]}") 
    return "\n".join(return_list) 

def csv_to_json(csv_file_path, json_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # Clean the headers
        cleaned_headers = [clean_key(header) for header in csv_reader.fieldnames]
        data = [dict(zip(cleaned_headers, row.values())) for row in csv_reader]
        
        data_az = []
        for row in data:
            row_az = {}
            row_az["PartitionKey"] = "PROSPECT"
            row_az["RowKey"] = row.get("Organization_CRD", "NoCRD")
            row_az["FilingData"]=format_readable_json(row)
            for f in fields:
                f = clean_key(f)
                row_az[f] = row.get(f, "")
            data_az.append(row_az)
        
    
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data_az, json_file, indent=4)
    
    return data_az


folder = "/Users/michasmi/Downloads/"
# Example usage
# csv_file_path = f"{folder}{"test.csv"}"

# csv_file_path = f"{folder}{"not_exempt.csv"}"
# json_file_path = f"{folder}{"not_exempt.json"}"

csv_file_path = f"{folder}{"ia050324-exempt.csv"}"
json_file_path = f"{folder}{"ia050324-exempt.json"}"

json_data = csv_to_json(csv_file_path, json_file_path)
# asyncio.run(storage.add_update_or_delete_some_entities("prospects", json_data))
pass
pass
print("done")
