
from google.oauth2 import service_account
from google.cloud import firestore, secretmanager
from pathlib import Path
import os, asyncio, json



class SecretUpdater:
    def __init__(self):
        pass
    
    async def get_multiple_secrets(self, secret_id_list, project_id='toolsexplorationfirebase',  version_id="latest"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f"{Path.home()}/.config/google-cloud-toolsexplorationfirebase.json"
        secret_payload_dict = {}
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
        credential_file_path = f"{Path.home()}/.config/google-cloud-toolsexplorationfirebase.json"
        
        with open (credential_file_path, 'r') as f:
            try: json.loads (f.read())
            except Exception as e: print(f"Invalid credential file: {e}")
        
        credentials = service_account.Credentials.from_service_account_file(f"{Path.home()}/.config/google-cloud-toolsexplorationfirebase.json")
        db = firestore.Client(credentials=credentials, project="toolsexplorationfirebase")
        doc_ref = db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict()

    async def update_local_secret_file(self):
        env_variable_dict = await self.get_document_by_id('variable_key_list', 'settings')
        env_variable_list = env_variable_dict.get('names', [])
        list_of_secret_dicts = await self.get_multiple_secrets(env_variable_list)
        home_directory_str = str(Path.home())
        secrets_file_path = f"{home_directory_str}/.config/secrets.sh"
        dot_env_file_path = f"{home_directory_str}/.config/.env"    

        with open(secrets_file_path, 'w') as source_script:
            with open (dot_env_file_path, 'w') as dot_env_file:
                source_script.write("#!/bin/bash")
                for env_variable in list_of_secret_dicts.keys():
                    try:
                        value = json.loads(list_of_secret_dicts.get(env_variable, ''))
                        value=json.dumps(value).replace('"', '\"')
                        print(f'exporting {env_variable} as json')
                    except Exception as e:
                        value = list_of_secret_dicts.get(env_variable, '')
                        print(f'exporting {env_variable} as string')
                    
                    source_script.write(f'\nexport {env_variable}="{value}"')
                    dot_env_file.write(f'\n{env_variable}={value}')
                dot_env_file.write(f'\n{'STREAMLIT_THEME_PRIMARYCOLOR'}={os.environ.get('STREAMLIT_THEME_PRIMARYCOLOR', '')}')
                dot_env_file.write(f'\n{'STREAMLIT_THEME_BACKGROUNDCOLOR'}={os.environ.get('STREAMLIT_THEME_BACKGROUNDCOLOR', '')}')
                dot_env_file.write(f'\n{'STREAMLIT_THEME_SECONDARYBACKGROUNDCOLOR'}={os.environ.get('STREAMLIT_THEME_SECONDARYBACKGROUNDCOLOR', '')}')
                dot_env_file.write(f'\n{'STREAMLIT_THEME_TEXTCOLOR'}={os.environ.get('STREAMLIT_THEME_TEXTCOLOR', '')}')
                dot_env_file.write(f'\n{'STREAMLIT_LOGO_URL'}={os.environ.get('STREAMLIT_LOGO_URL', '')}')
                dot_env_file.write(f'\n{'STREAMLIT_ICON_URL'}={os.environ.get('STREAMLIT_ICON_URL', '')}')
                dot_env_file.write(f'\n{'STREAMLIT_PAGE_ICON'}={os.environ.get('STREAMLIT_PAGE_ICON', '')}')
                source_script.write(f'\necho -e "secrets loaded successfully"')
        
        
if __name__ == "__main__":

    secret_updater = SecretUpdater()
    asyncio.run(secret_updater.update_local_secret_file())
    