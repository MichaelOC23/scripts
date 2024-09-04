


import base64
import json
import os
import subprocess
import requests
import csv
from datetime import datetime
import streamlit as st
import asyncio
import nats


import streamlit as st

PROJECT_PATH = '/Users/michasmi/code/platform/Src/Api'
WATCHLIST_CSV_PATH = '/Users/michasmi/code/data/sources/privateasset.csv'
NATS_COMMANDS_JSON = '/Users/michasmi/code/platform/Src/Api/Utils/NatsCommands.json'

class NatsClass:
    def __init__(self, nats_base_url='https://localhost:5001/api', project_path=PROJECT_PATH):
       
        self.encoded_credentials = base64.b64encode(b'platform:local').decode('utf-8')
        self.register_payload = { "Email": "123@456.com","Name": "123 string", "Password": "123abcDEF!!!"}
        self.login_payload = {"Email": "123@456.com", "Password": "123abcDEF!!!"}
        self.base_url = nats_base_url
        self.headers = {'accept': 'application/json','Content-Type': 'application/json'}
        self.nats_token = self.nats_authenticate()
        self.project_path = project_path

    def convert_date_format(self, date_str):
        # Parse the date string
        date_obj = datetime.strptime(date_str, '%m/%d/%y')
        # Convert to the desired format
        formatted_date = date_obj.strftime('%Y-%m-%d')
        return formatted_date

    def convert_text_num_to_num(self, textnum):
        # Parse the date string
        try:
            if textnum is None or textnum == '':
                decimal_to_return = float(0)
            return float(textnum)
        except ValueError:
            decimal_to_return = float(0)

    def csv_to_dict(self, csv_file_path, key_column='AttributeName'):
        result_dict = {}
        with open(csv_file_path, mode='r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            print(reader.fieldnames)
            rownum=0
            for row in reader: # Assuming 'AttributeName' is the name of the column to be used as the key
                rownum = rownum+1
                printrow = {}
                printrow.update(row)
                
                #! FIXME: This should be a look up to the business mode to see what the field types are
                if 'privateasset' in csv_file_path:
                    printrow['AcquisitionDate'] = self.convert_date_format(row['AcquisitionDate'])
                    printrow['AcquisitionCost'] = self.convert_text_num_to_num(row['AcquisitionCost'])
                    printrow['UnitsHeld'] = self.convert_text_num_to_num(row['UnitsHeld'])
                    
                # Convert dictionary to JSON string with double quotes
                row_string_escaped = json.dumps(printrow)
                row_string_simple = row_string_escaped.replace('\\"', '"')
                result_dict[rownum] = row_string_simple
            
        return result_dict

    def nats_authenticate(self):
        
        user_registration = requests.post(
            f'{self.base_url}/auth/register',
                    headers=self.headers,
                    json=self.register_payload,
                    verify=False
                )

        nats_login_response = requests.post(
            'https://localhost:5001/api/auth/login',
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': f'Basic {self.encoded_credentials}'
            },
            json=self.login_payload,
            verify=False
        )
        nats_login_json = nats_login_response.json()

        # Extract Token and NatsJwt
        self.nats_token = nats_login_json.get('Token')

        # Export the values as environment variables
        os.environ['NATS_TOKEN'] = self.nats_token
        
        return self.nats_token

    def take_action(self,  action_dict={"service":"", "verb":"", "request_dict":[]}, csv_path='', ):
        
        success_list = []
        error_list = []
        
        def nats_request(action_dict, request):
            try:
                # Send the request via nats (adjust the command as needed) "cd {PROJECT_PATH} && 
                nats_command = f'cd {self.project_path} && nats req {action_dict["service"]}.{action_dict["verb"]} \'{request}\' -H "Project:CMS" -H Token:{self.nats_token}'
                response = subprocess.run(nats_command, shell=True)
                return {"success": True, "content": f"Success: {request}", "response": response, "nat_command": nats_command}
            except Exception as e:
                error_dict = {"success": False, "content": f"Error: {e}", "nat_command": nats_command}
                print(f"\033[4;31m Error: {error_dict}\033[0m")
                return 
        
        if csv_path is not None and csv_path != '':
            request_dict = self.csv_to_dict(csv_path)
            for key in request_dict.keys():  
                request = request_dict[key]
                response = nats_request(action_dict, request)
                if response['success']:success_list.append(response)
                else: error_list.append(response)
                
        if action_dict.get('request_dict', '') != [] and isinstance(action_dict.get('request_dict', ''), list):
            for request in action_dict['request_dict']:
                response = nats_request(action_dict, request)
                if response['success']:success_list.append(response)
                else: error_list.append(response)
        
        return {"success": success_list, "error": error_list}
    
nats_inst = NatsClass()
# result_dict = nats_inst.take_action({"service":"privateasset", "verb":"create"}, csv_path=WATCHLIST_CSV_PATH)
result_dict = nats_inst.take_action({"service":"privateasset", "verb":"query", "request_dict":['{"SymTicker": "MSFT","RecordContext":"WATCHLIST", "ComputePersonalGainLoss": true}']})
print(result_dict)

