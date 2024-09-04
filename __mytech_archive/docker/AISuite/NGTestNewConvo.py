
import json
import requests

def get(retries):
    bot_id = "7N1aMJqEGbWm"
    conversation_id = "wMvbm3LO0eYA"
    default_table_folder = "Oy5eVO25WaEP"
    base_url = "https://getcody.ai/api/v1"
    api_key = "gX8NGF0KtNw6BTx5PqQJapYwyhxKia7vHmJgrywCa98df424"
    headers = {'Authorization': f'Bearer {api_key}','Content-Type': 'application/json'}

    def extract_questions(data):
        try: 
            
            question_dict = {
                    "Q1": data.get("Q1",""),
                    "Q2": data.get("Q2",""),
                }
            
        except Exception as e:
            ERROR_REASONS.append(f"Error extracting questions. Function: {"extract_questions"}  data: {data}: Error Message: {e}")
            
        
        return question_dict
    
    def getContent(response_dict):
    
        data = response_dict.get("data",{})

        if data.get("failed_responding",True):
            return False
        
        try: 
            
            content = extract_json_dict_from_llm_response(data.get("content",""))

            resp = {
                "Commentary" : content.get("commentary",""),
                "Questions" : extract_questions(content)
            }
            return resp
        except Exception as e:
            ERROR_REASONS.append(f"Error extracting json from llm response. Function: {"getContent"}  response_dict: {response_dict}: Error Message: {e}")
    
    def extract_json_dict_from_llm_response(content):
        
        # Find the first '{' and the last '}'
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            return None

        try: 
            # Extract the JSON string
            json_string = content[start_idx:end_idx+1]
            
            # Load and return the JSON as a dictionary
            return json.loads(json_string)
        
        except Exception as e:
            ERROR_REASONS.append(f"Error extracting json from llm response. Function: {"extract_json_dict_from_llm_response"}  Content: {content}: Error Message: {e}")
    






    # Body of get(retries) function
    try:
        
        json_data = {"name": 'CommSectorInsights', "bot_id": bot_id}
        c_response = requests.post("{}/conversations".format(base_url), headers=headers, json=json_data)
        c_response_dict = c_response.json()
        convo_id = c_response_dict.get('data', {}).get('id', '')
         
        message_content = "My porfolio contains the following industry sector allocations: " + ", ".join(Tickers) + ".  Would you help me analyze my portfolio?"
        
        data = {
            "content": message_content,
            "conversation_id": convo_id
            }
        
        response = requests.post(f"{base_url}/messages", headers=headers, json=data)
        
        response_dict = response.json()
        CODY_RESPONSE

        content = getContent(response_dict)
    
    except Exception as e:
        ERROR_REASONS.append(f"Error extracting or formatting json from llm response. Function: {"get(retries)"}  Tickers {Tickers}: Error Message: {e}")
    
    return content

# Main body of python function begins here
TICKERS_FOR_TESTING = ['NVDA', 'CSCO']
TEST_MODE = False
VALUE_TO_RETURN = ""
ERROR_REASONS = []
CODY_RESPONSE = ""

Tickers = ['NVDA', 'CSCO']
# Get the Tickers from the input provided by python framework
# Assumption: if no tickers are provided, we will use the default tickers, as this must be a local running test.
try:
    # Tickers_Input is not used, this line is used to test the existence of the Tickers input value
    Tickers_Input = Tickers
except Exception as e:
    pass
    Tickers = TICKERS_FOR_TESTING
    TEST_MODE = True
    error = f"Error: Tickers value not received.  Operating in TEST_MODE with default Tickers: {TICKERS_FOR_TESTING}." 
    ERROR_REASONS.append(error)


try: 
    VALUE_TO_RETURN = get(0)
except Exception as e:
    pass
    ERROR_REASONS.append(f"Error in main body of python function. Error Message: {e}")

result = {
    "Success": True,
    "TestMode": TEST_MODE,
    "Reasons": ERROR_REASONS,
    "Value": VALUE_TO_RETURN,
    "received_input": Tickers
}

print(result)