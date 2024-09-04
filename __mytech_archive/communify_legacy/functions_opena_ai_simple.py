
# This file contains a simple wrapper for the OpenAI API.
from asyncore import loop
from venv import create
from flask import request
import functions_constants as con     
import _api_request_parallel_processor as parallel_processor   
from enum import Enum
from typing import Union
import os
import json
import asyncio

class Response_Return_Format(Enum):
    LIST_OF_RESPONSES = 1 #List / Array of responses
    FILE_PATH_OF_RESPONSES = 2 # File path to the responses (in jsonl format)
    MERGED_SINGLE_RESPONSE = 3 # a String ... a Single response that is the concatenation of all the responses (concatenated with a newline)
    REQUEST_JSON_ONLY = 4 # a JSON file with the request data only (i.e. no response data). This is useful for debugging and re-running requests

def create_request_row(prompt_val, data_val=None, model=None, temperature=None, max_tokens=None, system_message=None):
    if model is None:
        model = con.MODEL_DEFAULT

    if temperature is None:
        temperature = con.DEFAULT_TEMPERATURE
    
    if max_tokens is None:
        max_tokens = con.DEFAULT_MAX_TOKENS
    
    if system_message is None:
        system_message = con.DEFAULT_SYSTEM_PROMPT
    
    if data_val is not None:
        prompt_val = f"{prompt_val}\n\n{data_val}"
    
    request_data_row = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages":     [
                                {
                                    "role": "system",
                                    "content": json.dumps(system_message)
                                },
                                {
                                    "role": "user",
                                    "content": json.dumps(prompt_val)
                                }
                            ]
                        }
    return json.dumps(request_data_row)






def ask_gpt_via_multi_prompt_file(request_input_file_path_str, response_return_format=None, response_output_file_path_str=None, max_tokens_per_min_flt=None, max_requests_per_min_flt=None):
    """ 
    Ask GPT-4-Turbo a question using a prompt file. 
    Note, this assumes a valid prompt file with one prompt per line in jsonl format._api
    You can find an example prompt file in the file __api_request_parallel_processor.py
    """
    

    if response_return_format is None:
        response_return_format = Response_Return_Format.MERGED_SINGLE_RESPONSE

    if max_tokens_per_min_flt is None:
        max_tokens_per_min_flt = float(200000)
    
    if max_requests_per_min_flt is None:
        max_requests_per_min_flt = float(1500)

    #if the response_output_file_path_str is None, then create a unique file name based on the name and location of the input file path
    if response_output_file_path_str is None:
        response_output_file_path_str = f'{request_input_file_path_str.split(".jsonl")[0]}_responses_{con.UNIQUE_DATE_TIME_STRING()}.jsonl'

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    try: 

        
        #? OPENAI VERSION
        result =  loop.run_until_complete(parallel_processor.process_api_requests_from_file(
                                                            requests_filepath=request_input_file_path_str,
                                                            save_filepath=response_output_file_path_str,
                                                            request_url=con.OPENAI_BASE_URL,
                                                            api_key=con.OPENAI_API_KEY,
                                                            max_requests_per_minute=float(max_requests_per_min_flt),
                                                            max_tokens_per_minute=float(max_tokens_per_min_flt),
                                                            token_encoding_name="cl100k_base",
                                                            max_attempts=int(5),
                                                            logging_level=int(20),
                                                            api_endpoint = con.OPENAI_COMP_ENDPOINT
                                                              ))
         
        
        #? MISTRAL LOCAL VERSION                                                   
        # result =  loop.run_until_complete(parallel_processor.process_api_requests_from_file(
        #                                                     requests_filepath=request_input_file_path_str,
        #                                                     save_filepath=response_output_file_path_str,
        #                                                     request_url=con.MISTRAL_BASE_URL,
        #                                                     #request_url=con.MISTRAL_BASE_URL,
        #                                                     api_key=con.OPENAI_API_KEY,
        #                                                     max_requests_per_minute=float(max_requests_per_min_flt),
        #                                                     max_tokens_per_minute=float(max_tokens_per_min_flt),
        #                                                     token_encoding_name="cl100k_base",
        #                                                     max_attempts=int(5),
        #                                                     logging_level=int(20),
        #                                                     api_endpoint = con.MISTRAL_COMP_ENDPOINT
        #                                                     ))
        
                                                                                
                                                        
    except Exception as e:
        #Log the result of a failed request and response
        con.log_it(f"Error saving responses to {response_output_file_path_str}: {str(e)}", "LLM")
        return None
    
    #!### FILE PATH TO RESPONSES ###
    if response_return_format == Response_Return_Format.FILE_PATH_OF_RESPONSES:
        return response_output_file_path_str

    #Get all the responses from the jsonl file (i.e. strip the responses from the json response that is the structure of each row )
    with open(response_output_file_path_str, "r") as f:
        responses = f.readlines()
        #get the vaule of choices[0].message.content from each response in teh jsonl file
        response_text_list = []
        for response in responses:
            response_json = json.loads(response)
            try:
                response_message = json.dumps(response_json[1]['choices'][0]['message']['content'])
                response_text_list.append(response_message)
            except:
                try:
                    #reading the json in the response failed ... check if it is a standard error message    
                    response_message = json.dumps(f"RESPONSE_ERROR: {response_json['error']['message']}")
                    response_text_list.append(response_message)
                    con.log_it(f"Error reading response: {response_json['error']['message']}", "LLM")
                except Exception as e:
                    #capture the error basically, as it is corrupt/non-standard json
                    response_message = json.dumps(f"RESPONSE_ERROR: {str(e)}")
                    response_text_list.append(response_message)
                    con.log_it(f"Error reading response: {str(e)}", "LLM")
    
    #!### LIST OF RESPONSES ###
    if response_return_format == Response_Return_Format.LIST_OF_RESPONSES:
        con.log_it(f"Returning list of responses", "LLM")
        #Return the list of responses generated above
        return response_text_list

    #!### MERGED SINGLE RESPONSE ###
    if response_return_format == Response_Return_Format.MERGED_SINGLE_RESPONSE:
        #Return a single response that is the concatenation of all the responses generated above (concatenated with a newline)
        return_text =  "\n".join(response_text_list)    
        return return_text

def ask_gpt_list_of_prompts(prompt_list, data_list=None, response_return_format=None, response_file_path=None, max_tokens_per_min_flt=None, max_requests_per_min_flt=None, max_tokens=None, model=None, temperature=None, system_prompt=None):
    
    unique_id = con.UNIQUE_DATE_TIME_STRING()

    if data_list != None:
        if len(data_list) != len(prompt_list):
            return "ERROR: data_list must be None or the same length as prompt_list"
        
    if data_list != None:
        for prompt, data in zip(prompt_list, data_list):
            prompt_list = f"{prompt}\n\n{data}"
    
    if response_file_path is None:
        response_file_path = os.path.join(con.TEMP_FOLDER_PATH, f"response_{unique_id}.json")
    
    # Receive a list so have to generate this path reasonably
    request_file_path = os.path.join(con.TEMP_FOLDER_PATH, f"request_{unique_id}.json")
    
    if model is None:
        model = con.MODEL_DEFAULT # should be GPT-4-Turbo

    if temperature is None:
        temperature = con.DEFAULT_TEMPERATURE # 0 = flat; .9 = very creative, but may stray from the prompt; 1 = very creative, but will stray from the prompt; 1.2 = extremely creative, but will often stray from the prompt; 1.5 = extremely creative, but will often stray from the prompt; 2 = very, very creative, but will often stray from the prompt; 3 = extremely creative, but will often stray from the prompt; 4 = extremely creative, but will often stray from the prompt; 5 = extremely creative, but will often stray from the prompt; 10 = extremely creative, but will often stray from the prompt; 100 = extremely creative, but will often stray from the prompt; 1000 = extremely creative, but will often stray from the prompt; 10000 = extremely creative, but will often stray from the prompt; 100000 = extremely creative, but will often stray from the prompt; 1000000 = extremely creative, but will often stray from the prompt; 10000000 = extremely creative, but will often stray from the prompt;
    
    if max_tokens is None:
        max_tokens = con.DEFAULT_MAX_TOKENS # 100 is a sentence or two question w/ a question or two response; for grammer checking this needs to be aligned with chunk size
    
    if system_prompt is None:
        system_prompt = con.DEFAULT_SYSTEM_PROMPT #Default is "You are a helpful assistant."
    
    if response_return_format is None:
        response_return_format = Response_Return_Format.MERGED_SINGLE_RESPONSE
    
    #! request_data_structure
    REQUEST_JSON_LIST = []
    with open(request_file_path, 'w') as f:
        for each_prompt in prompt_list:    
            request_data_row = create_request_row(each_prompt, model=model, temperature=temperature, max_tokens=max_tokens, system_message=system_prompt)
            REQUEST_JSON_LIST.append(request_data_row) 
            f.write(request_data_row)
        f.close()

    
    #!### REQUEST_JSON_ONLY ###
    if response_return_format == Response_Return_Format.REQUEST_JSON_ONLY:
        return REQUEST_JSON_LIST
    
    #!Process the request file
    response = ask_gpt_via_multi_prompt_file(request_file_path, response_return_format, response_file_path, max_tokens_per_min_flt, max_requests_per_min_flt)
    
    #!### MERGED_SINGLE_RESPONSE ##
    if response_return_format == Response_Return_Format.MERGED_SINGLE_RESPONSE:
        if isinstance(response, str):
            return response
    
    #!### FILE PATH TO RESPONSES ###
    if response_return_format == Response_Return_Format.FILE_PATH_OF_RESPONSES:
        if isinstance(response, str):
            if os.path.exists(response):
                return response

def ask_gpt_single_prompt(prompt, data_list=None, response_return_format=None, response_file_path=None, max_tokens_per_min_flt=None, max_requests_per_min_flt=None, max_tokens=None, model=None, temperature=None, system_prompt=None):
    prompt_list = []
    loop = asyncio.get_event_loop()
    if response_return_format is None:
        response_return_format = Response_Return_Format.MERGED_SINGLE_RESPONSE
    prompt_list.append(prompt)
    response = ask_gpt_list_of_prompts(prompt_list, data_list, response_return_format, response_file_path, max_tokens_per_min_flt, max_requests_per_min_flt, max_tokens, model, temperature, system_prompt)
    return response

#def create_request_file_from_prompt_list(prompt_list, data_value=None, request_file_path=None, model=None, temperature=None, max_tokens=None, system_prompt=None):


def test_simple_gpt():
    # Ensure 'ask_gpt_with_multi_prompt_file' is an async function
    result1 = ask_gpt_via_multi_prompt_file("archive/test.jsonl")
    print(result1)
    result2 = ask_gpt_single_prompt("Who is your mama, mother or person who you see as your role model?")
    print(result2)
    result3 = ask_gpt_list_of_prompts(["What is the color blue","What is the color green"],  max_tokens=10, response_return_format=Response_Return_Format.MERGED_SINGLE_RESPONSE,)
    print(result3)

if __name__ == "__main__":
    test_simple_gpt()