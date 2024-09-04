import json
import requests

def get(retries):
    bot_id = "7N1aMJqEGbWm"
    conversation_id = "wMvbm3LO0eYA"
    default_table_folder = "Oy5eVO25WaEP"
    base_url = "https://getcody.ai/api/v1"
    api_key = "gX8NGF0KtNw6BTx5PqQJapYwyhxKia7vHmJgrywCa98df424"
    headers = {'Authorization': 'Bearer {}'.format(api_key), 'Content-Type': 'application/json'}

    def extract_questions(data):
        try:
            question_dict = {
                "Q1": data.get("Q1", ""),
                "Q2": data.get("Q2", ""),
            }
        except Exception as e:
            ERROR_REASONS.append("Error extracting questions. Function: {}  data: {}: Error Message: {}".format("extract_questions", data, e))

        return question_dict

    def getContent(response_dict):
        data = response_dict.get("data", {})

        if data.get("failed_responding", True):
            return False

        try:
            content = extract_json_dict_from_llm_response(data.get("content", ""))

            resp = {
                "Commentary": content.get("commentary", ""),
                "Questions": extract_questions(content)
            }
            return resp
        except Exception as e:
            ERROR_REASONS.append("Error extracting json from llm response. Function: {}  response_dict: {}: Error Message: {}".format("getContent", response_dict, e))

    def extract_json_dict_from_llm_response(content):
        # Find the first '{' and the last '}'
        start_idx = content.find('{')
        end_idx = content.rfind('}')

        if start_idx == -1 or end_idx == -1:
            return None

        try:
            # Extract the JSON string
            json_string = content[start_idx:end_idx + 1]

            # Load and return the JSON as a dictionary
            return json.loads(json_string)
        except Exception as e:
            ERROR_REASONS.append("Error extracting json from llm response. Function: {}  Content: {}: Error Message: {}".format("extract_json_dict_from_llm_response", content, e))

    # Body of get(retries) function
    try:
        message_content = "My portfolio contains the following industry sector allocations: " + ", ".join(Tickers) + ".  Would you help me analyze my portfolio?"

        data = {
            "content": message_content,
            "conversation_id": conversation_id
        }

        response = requests.post("{}/messages".format(base_url), headers=headers, json=data)

        response_dict = response.json()

        content = getContent(response_dict)
    except Exception as e:
        ERROR_REASONS.append("Error extracting or formatting json from llm response. Function: {}  Tickers {}: Error Message: {}".format("get(retries)", Tickers, e))

    return content

# Main body of python function begins here
TICKERS_FOR_TESTING = ['NVDA', 'CSCO']
TEST_MODE = False
VALUE_TO_RETURN = ""
ERROR_REASONS = []
CODY_RESPONSE = ""

Tickers = TICKERS_FOR_TESTING

try:
    VALUE_TO_RETURN = get(0)
except Exception as e:
    pass
    ERROR_REASONS.append("Error in main body of python function. Error Message: {}".format(e))

result = {
    "Success": True,
    "TestMode": TEST_MODE,
    "Reasons": ERROR_REASONS,
    "Value": VALUE_TO_RETURN,
    "received_input": Tickers
}