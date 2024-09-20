import re
import os
import sys
import asyncio
import aiofiles
import httpx
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

TEST_VALUE = "/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes By Michael/Transcriptions/24.09.09"
TEST_SUMMARY_PATH = "/Users/michasmi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Notes by Michael/Transcriptions"

print(f"{sys.argv}")

async def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else TEST_VALUE  # Get file path from arguments
    summary_file_path = sys.argv[2] if len(sys.argv) > 2 else TEST_SUMMARY_PATH  # Get file path from arguments

    print(f"From publisher: Received file path: {file_path} \nSummary file path: {summary_file_path}")
    if not file_path or not os.path.isfile(file_path):
        err = f"Error: Summarization cannot proceed. Did not receive a valid file path for a deepgram transcription in json format. Value of json file path is: {file_path}"
        print(err)
        return err
    
    if not summary_file_path:
        err = f"Error: Summarization cannot proceed. Did not receive a valid file path to save the summary. Received {summary_file_path}"
        print(err)
        return err

    async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        json_transcription = await f.read()
    
    json_transcript = {}
    try:
        json_transcript = json.loads(json_transcription)
    except:
        err = f"Error: Invalid JSON format in JSON Trascription in {file_path}"
        print (err)
        return err 
    
    transcription_channels = json_transcript.get('results', {}).get('channels', [])
    if transcription_channels and len(transcription_channels) > 0:
        transcription_alternatives = transcription_channels[0].get('alternatives', [])
        if transcription_alternatives and len(transcription_alternatives) > 0:
            transcript_text = transcription_alternatives[0].get('transcript', '')
            

    summarized_transcription = await summarize_transcription_with_gemini(transcript_text)
    with open(summary_file_path, 'w') as f:
        f.write(f"{summarized_transcription} \n\n\n___  ##### Original Transcription\n{transcript_text}")
    
async def extract_json_dict_from_llm_response(content):
    def try_to_json(input_value):
        try:
            first_dict_attempt = json.loads(input_value)
            return first_dict_attempt
        except:
            return input_value
    
    try:
        json_dict = try_to_json(content)
        if isinstance(json_dict, dict) or isinstance(json_dict, list):
            return json_dict
    except Exception as e:
        pass
        print(f"Initial attempt to convert to JSON failed: {e}")
        print(f"The content is: {content}")
        print(f"Trying to extract JSON from the content without attempting to isolate it the json string did not succedd.")
        print(f"We will now attempt to extract the JSON string from the content.")
                
    

    # Find the first '{' and the last '}'
    start_idx = content.find('{')
    end_idx = content.rfind('}')

    if start_idx == -1 or end_idx == -1:
        return content

    try:
        # Extract the JSON string
        json_string = content[start_idx:end_idx + 1]
        
        json_dict = try_to_json(json_string)
        if  isinstance(json_dict, dict) or isinstance(json_dict, list):
            return json_dict
        else:
            print(f"After 2 attempts to obtain a dictionary from the response, both failed. Returning the content.")
            return content
    except Exception as e:
        print(f"After 2 attempts to obtain a dictionary from the response, both failed. Returning the content and providng the Error: {e}")
        return content
        
async def summarize_transcription_with_gemini(transcript_text):
    json_response_format={ 
                          "summary": "<Place the markdown summary here>", 
                          "commentary": "<Include your commentary about the summary process here>"
                          }
    
    instructions = f"""
    Please summarize the following meeting transcription, extracting key topics by type:
        * Action items
        * Follow-up items
        * Decisions
        * Factual statements
        * Opinions
        * Speculations
        * Objectives (short, medium, long-term)
        * Sales approaches
        * Product functions
        * Names, tiles, companies, roles and/or backgrounds of participants who provide said information

        Organize the summary by topic type using a markdown format with headers (e.g., "#### Factual Statements").

        Once you have summarized the transcription, please provide the summary and any commentary about the process in a JSON object with the following structure:

        ```json
        {json.dumps(json_response_format, indent=4)}
        ```
        
        Transcrioption Text:
        {transcript_text}
        """ 

    try:
        response = await fetch_gemini_json_response(instructions)
        hopefully_a_dict = await extract_json_dict_from_llm_response(response.text)
        if not response or not isinstance(hopefully_a_dict, dict):
            print("Error: Bad response from Gemini, trying again.")
            response = await fetch_gemini_json_response(instructions)
            hopefully_a_dict = await extract_json_dict_from_llm_response(response.text)
            if not response or not isinstance(hopefully_a_dict, dict):
                print("Error: Bad response from Gemini (on 2nd attempt)")
                sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        return instructions
    
    summary = f"{hopefully_a_dict.get('summary', hopefully_a_dict)} \n\n___  \n\n{hopefully_a_dict.get('commentary', '')} "
    
    return summary

async def fetch_gemini_json_response(prompt):
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        generation_config = {
                    "temperature": .5,
                    "top_p": 0.95,
                    "top_k": 34,
                    "max_output_tokens": 32000,
                    "response_mime_type": "application/json",
                    }
        response = model.generate_content(prompt, generation_config=generation_config,
                                          safety_settings={
                                              HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                              HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                              HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                              HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
                                              }
                                          )
        return response
            

if __name__ == '__main__':
    asyncio.run(main())
