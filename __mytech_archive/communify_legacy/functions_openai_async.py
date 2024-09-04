import imp
import aiohttp
import asyncio
import os
import json
import functions_constants as con

from datetime import datetime
from openai import OpenAI
import requests
import streamlit as st

# gets OPENAI_API_KEY from your environment variables
client = OpenAI()

#! asynch
import asyncio
from concurrent.futures import ThreadPoolExecutor
llm_executor = ThreadPoolExecutor(max_workers=10)


# client = AsyncOpenAI(
#     # This is the default and can be omitted
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

async def ask_llm (prompt, data_val=None, model=None, temperature=None, max_tokens=None, system_message=None, provider=None, item_id=None):
    response_message = ''
    tokens_used = 0 

    start_time = datetime.now()

    if model is None:
        model = con.MODEL_GPT4_TURBO
        model = con.MODEL_MISTRAL_LOCAL

    if temperature is None:
        temperature = con.DEFAULT_TEMPERATURE
    
    if max_tokens is None:
        max_tokens = con.DEFAULT_MAX_TOKENS
    
    if system_message is None:
        system_message = con.DEFAULT_SYSTEM_PROMPT
    
    if data_val is None:
        data_val = ""
    
    if provider == None:
        # provider = con.DEFAULT_PROVIDER
        provider = 'PROVIDER_OPENAI_PYCLI'
    
    #! asynch
    loop = asyncio.get_running_loop()

    def sync_request():
        
        #? OPENAI WHISPER
        #? GPT4All
        #? GOOGLE NANO

        #? LOCAL MISTRAL 7B
        if provider == 'PROVIDER_LOCAL_MISTRAL7B':
            con.log_it(f"Using {provider} to ask LLM", "LLM")
            try:
                # Example: reuse your existing OpenAI setup


                # Point to the local server
                client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Always answer in rhymes."},
                              {"role": "user", "content": f"{prompt}\n{data_val}"}],
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                    )

                response_message = chat_completion.choices[0].message.content
                print(response_message)
            except Exception as e:
                response_message = f"Error: {str(e)}"

        #? OPENAI PYTHON CLIENT
        if provider == 'PROVIDER_OPENAI_PYCLI':
            con.log_it(f"Using {provider} to ask LLM", "LLM")
            
            try: 
                chat_completion = client.chat.completions.create(  
                    messages=[{"role": "user", "content": f"{prompt}\n{data_val}"}],
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )  
                response_message = chat_completion.choices[0].message.content
            except Exception as e:
                response_message = f"Error:\n {str(e)} \n\n Full reponse" #:\n {chat_completion}"
                

        #? OPENAI HTTP API
        if provider == 'PROVIDER_OPENAI_HTTP':
            header = {'Authorization': f'Bearer {os.environ.get("OPENAI_API_KEY")}'}
            data = {
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "messages": [
                        {
                            "role": "system",
                            "content": con.DEFAULT_SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": f"{prompt}\n\n{data_val}"
                        }
                                    ]
                    }
            try:
                response = requests.post(con.OPENAI_COMPLETION_ENDPOINT, headers=header, json=data)
                response_json = response.json()
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    response_message = response_json['choices'][0]['message']['content']  # Access the message
                else:
                    response_message = f'{provider}_ERROR: VALID response WITHOUT choices or error json nodes received. Response is below: \n\n {json.dumps(response_json)}'    
            except Exception as e:
                response_message = f"Error: {str(e)}"
        return response_message
    
    #! asynch
    response_message = await loop.run_in_executor(llm_executor, sync_request)            
    response_time = f'{provider} | Run-time {(datetime.now() - start_time).total_seconds()} seconds) | Began: {start_time.strftime("%H:%M:%S")} | Complete: {datetime.now().strftime("%H:%M:%S")}'
    print(response_time)
    # st.sidebar.write(response_time)
    return response_message    

async def test_pvp():
    tasks = []
    
    prompts = [
        "translate English to French: 'Hello, how are you?'",
        "translate English to Spanish: 'What time is it?'",
        "translate English to German: 'Where is the nearest restaurant?'"
        # Add more prompts as needed
    ]


    prompts = [
        "Please introduce yourself.",
        "What is artificial intelligence?", 
        "Where was Justin Bieber born?"
        # Add more prompts as needed
    ]
    # Schedule all tasks to run concurrently
    for prompt in prompts:
        task = asyncio.create_task(ask_llm(prompt, None, None, 0.0))
        tasks.append(task)  
    
    responses = await asyncio.gather(*tasks)
    full_response = '\n'.join(responses)
    
    #print(full_response)

if __name__ == "__main__":
    asyncio.run(test_pvp())
