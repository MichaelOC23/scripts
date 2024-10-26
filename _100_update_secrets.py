from google.cloud import firestore
from google.cloud import secretmanager
from pathlib import Path
import asyncio
import json


class SecretUpdater:
    def __init__(self):
        pass
    
    async def get_multiple_secrets(self, secret_id_list, project_id='toolsexplorationfirebase',  version_id="latest"):
        secret_payload_dict = {}
        # Create the Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        for secret_id in secret_id_list:
            try:
                name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
                response = client.access_secret_version(request={"name": name})
                secret_payload_value = response.payload.data.decode("UTF-8")
                secret_payload_dict[secret_id]= secret_payload_value
            except Exception as e:
                print(f'ERROR -- Secret ID not found in Secret Manager: {e}')
                continue
        return secret_payload_dict
    
    async def get_document_by_id(self, document_id, collection_name=None):
        db = firestore.Client()
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict()

    async def update_local_secret_file(self):
        env_variable_dict = await self.get_document_by_id('variable_key_list', 'settings')
        env_variable_list = env_variable_dict.get('names', [])
        list_of_secret_dicts = await self.get_multiple_secrets(env_variable_list)
        home_directory_str = str(Path.home())
        secrets_file_path = f"{home_directory_str}/.config/secrets.sh"    

        with open(secrets_file_path, 'w') as file:
            file.write("#!/bin/bash")
            for env_variable in list_of_secret_dicts.keys():
                if "FIREBASE" in env_variable:
                    pass
                try:
                    value = json.loads(list_of_secret_dicts.get(env_variable, ''))
                    value=json.dumps(value).replace('"', '\"')
                    print(f'exporting {env_variable} as json')
                except Exception as e:
                    value = list_of_secret_dicts.get(env_variable, '')
                    print(f'exporting {env_variable} as string')
                file.write(f'\n\nexport {env_variable}="{value}" \n\n#______________________________________________________________________')
        
        
if __name__ == "__main__":

    secret_updater = SecretUpdater()
    asyncio.run(secret_updater.update_local_secret_file())
    