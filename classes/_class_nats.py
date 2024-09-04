import asyncio
import nats
import requests
import base64
import os
import json
import csv
from urllib3.exceptions import InsecureRequestWarning
import urllib3



# Suppress the warning for unverified HTTPS requests (optional, for development only)
urllib3.disable_warnings(InsecureRequestWarning)

PROJECT_PATH = '/Users/michasmi/code/mytech'
WATCHLIST_CSV_PATH = '/Users/michasmi/code/data/sources/privateasset.csv'
NATS_DEV_LOCAL_UIDPWD = 'platform:local'
NATS_REGISTRATION_UIDPWD = '123@456.com:123abcDEF!!!'

class Nats:
    def __init__(self, nats_base_url='https://localhost:5001/api', project_path=PROJECT_PATH):
        self.encoded_credentials = base64.b64encode(NATS_DEV_LOCAL_UIDPWD.encode('utf-8')).decode('utf-8')
        self.register_payload = {"Email": "123@456.com", "Name": "123 string", "Password": "123abcDEF!!!"}
        self.login_payload = {"Email": "123@456.com", "Password": "123abcDEF!!!"}
        self.base_url = nats_base_url
        self.headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
        self.nats_token = os.environ.get('NATS_TOKEN', "NO TOKEN") #self.nats_authenticate()
        self.project_path = project_path

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

        self.nats_token = nats_login_json.get('Token')
        os.environ['NATS_TOKEN'] = self.nats_token
        
        return self.nats_token

    async def send_request(self, nc, action_dict, request, semaphore):
        async with semaphore:
            try:
                subject = f"{action_dict['service']}.{action_dict['verb']}"
                headers = {
                    "Project": "CMS",
                    "Token": self.nats_token
                }
                response = await nc.request(subject, json.dumps(request).encode(), headers=headers, timeout=10)
                return {"success": True, "content": response.data.decode(), "nat_command": f"{subject}: {request}"}
            except Exception as e:
                error_dict = {"success": False, "content": f"Error: {e}", "nat_command": f"{subject}: {request}"}
                print(f"\033[4;31m Error: {error_dict}\033[0m")
                return error_dict

    async def take_action(self, action_dict={"service": "", "verb": "", "data": {}}, csv_path=''):
        success_list = []
        error_list = []

        
        nc = await nats.connect("nats://localhost:4222")
        
        concurrency_limit = 100
        semaphore = asyncio.Semaphore(concurrency_limit)

        if csv_path:
            request_dict = self.csv_to_dict(csv_path)
            tasks = [
                self.send_request(nc, action_dict, json.loads(request), semaphore) for request in request_dict.values()
            ]
            responses = await asyncio.gather(*tasks)
            for response in responses:
                if response['success']:
                    success_list.append(response)
                else:
                    error_list.append(response)

        if action_dict.get('request_dict'):
            for request in action_dict['request_dict'].values():
                response = await self.send_request(nc, action_dict, request, semaphore)
                if response['success']:
                    success_list.append(response)
                else:
                    error_list.append(response)

        await nc.close()

        return {"success": success_list, "error": error_list}

if __name__ == "__main__":
    async def test():
        nc = await nats.connect(servers=f"nats://127.0.0.1:4222")
    
    
    nats_instance = Nats()
    asyncio.run(nats_instance.take_action({"service": "privateasset", "verb": "create"}, csv_path=WATCHLIST_CSV_PATH))
    