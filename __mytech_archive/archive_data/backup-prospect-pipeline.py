
##############################################
######    PROSPECT DATA PIPELINE     #########
##############################################

class prospect_data_pipeline:
    def __init__(self):
        self.log_folder = LOG_FOLDER
        self.company =""
        self.location = ""
        self.CRD = ""
        self.llm_model = 'llama3'
        self.llm_base_url='http://localhost:11434/v1'
        self.llm_model_api_key='Local-None-Needed'
        
        self.embeddings_model = 'mxbai-embed-large'
        self.embeddings_base_url='http://localhost:11434/v1'
        self.embeddings_model_api_key='Local-None-Needed'
        
        self.scrape_session_history = {}

        self.embeddings_model='mxbai-embed-large'
        self.google_api_key = os.environ.get('GOOGLE_API_KEY', 'No Key or Connection String found')
        self.google_general_cx = os.environ.get('GOOGLE_GENERAL_CX', 'No Key or Connection String found')
        self.titles_list = [
                # "Founder",
                # "Managing Partner",
                # "Chairman",
                # "Chief Executive Officer (CEO)"
                "Wealth Management CEO",
                "Head of Wealth Management",
                # "Head of Private Banking",
                # "Head of Client Services",
                # "Head of Client Relations",
                # "Head of Client Experience",
                # "Head of Client Engagement",
                # "Head of Client Success",
                # "Chief Investment Officer (CIO)",
                # "Chief Financial Officer (CFO)",
                # "President",
                # "Managing Director",
                # "Partner",
                # "Executive Vice President (EVP)",
                # "Chief Strategy Officer (CSO)",
                # "Regional Managing Director",
                "Principal"]
    
    def process_prospect_main(self, propsect_data):
        
        new_prospect_dict = asyncio.run(self.async_process_prospect(propsect_data))
        asyncio.run(storage.add_update_or_delete_some_entities("prospects", [new_prospect_dict], alternate_connection_string=storage.jbi_connection_string))
    
    def is_valid_url(self, may_be_a_url):
        try:
            result = urlparse(may_be_a_url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False    
    
    def get_base_url(self, url):
        try: 
            parsed_url = urlparse(url)            
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            return base_url
        except:
            return ""
    
    def get_domain(self, url):
        try: 
            parsed_url = urlparse(url)        
            domain_parts = parsed_url.netloc.split('.')
            domain = '.'.join(domain_parts[-2:]) if len(domain_parts) > 1 else parsed_url.netloc

            return domain
            
        except:
            return ""

    def generate_unique_key_for_url(self, url):
        # Create a SHA-256 hash object
        hash_object = hashlib.sha256()
        
        # Encode the URL to bytes and update the hash object
        hash_object.update(url.encode('utf-8'))
        
        # Get the hexadecimal representation of the hash
        unique_key = hash_object.hexdigest()
        
        return unique_key
    
    # Enable override of default values for configuration options that are set in __init__
    def optional_config(self, log_folder=None, llm_model=None, llm_base_url=None, llm_model_api_key=None, embeddings_model=None, embeddings_base_url=None, embeddings_model_api_key=None, google_api_key=None, google_general_cx=None):
        if log_folder:
            self.log_folder = log_folder
        if llm_model:
            self.llm_model = llm_model
        if llm_base_url:
            self.llm_base_url = llm_base_url
        if llm_model_api_key:
            self.llm_model_api_key = llm_model_api_key
        if embeddings_model:
            self.embeddings_model = embeddings_model
        if embeddings_base_url:
            self.embeddings_base_url = embeddings_base_url
        if embeddings_model_api_key:
            self.embeddings_model_api_key = embeddings_model_api_key
        if google_api_key:
            self.google_api_key = google_api_key
        if google_general_cx:
            self.google_general_cx = google_general_cx
    
    async def async_process_prospect(self, propsect_data):
        def extract_N_urls_from_markdown(markdown, N=5):
            # Split the markdown into lines
            lines = markdown.split('\n')
            
            # Find lines that start with '### '
            h3_lines = [line for line in lines if line.startswith('### ')]
            
            # Regular expression to extract URLs from markdown links
            url_pattern = re.compile(r'\(https*://[^\s\)]+')
            
            # List to store the extracted URLs
            urls = []
            urls.append({"Type":"Markdown", "all-google-results": markdown})
            
            # Extract URLs from the first 5 H3 lines
            for line in h3_lines[:N]:
                # Find all URLs in the line
                found_urls = url_pattern.findall(line)
                # If a URL is found, clean it and add to the list
                if found_urls:
                    # Remove the opening parenthesis from the URL
                    clean_url = found_urls[0][1:]
                    clean_dict = {"Type":"google", "Link": clean_url}
                    urls.append(clean_dict)
            
            return urls
        
        
        def scrape_google_web(search_query):
            try:
                def clean_search_string(search_query):
                    # Remove characters that are not suitable for a URL search query
                    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.~ ")
                    cleaned_string = ''.join(c for c in search_query if c in allowed_chars)
                    return cleaned_string
                
                def create_google_search_url(search_string):
                    # Clean the search string
                    cleaned_string = clean_search_string(search_string)
                    # Encode the search string for use in a URL
                    encoded_string = urllib.parse.quote_plus(cleaned_string)
                    # Construct the final Google search URL
                    google_search_url = f"https://www.google.com/search?q={encoded_string}"
                    return google_search_url
                
                url = create_google_search_url(search_query)
                
                response = requests.get(url)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract the HTML content of the body
                    body_html = soup.find('body')
                    if body_html:
                        body_html = str(body_html)
                        # Convert HTML to Markdown
                        h = html2text.HTML2Text()
                        # Configure options (optional)
                        h.ignore_links = False  # Ignore links 
                        h.ignore_images = True # Ignore images
                        h.body_width = 0  # Don't wrap lines

                        markdown_text = h.handle(body_html)
                        return markdown_text
                    else:
                        print("No body tag found.")
                else:
                    print(f"Failed to retrieve the page. Status code: {response.status_code}")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        def search_google_api(query):
            # Uses the configured (non image) CSE to search for results. Returns page 1
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            search_results = (service.cse().list(q=query,cx=f"{self.google_general_cx}",).execute())
            
            
            
            results = []
            for result in search_results.get('items', []):
                thumb_list = result.get('pagemap', {}).get('cse_thumbnail', [])
                image_list = result.get('pagemap', {}).get('cse_image', [])
                metatag_list = result.get('pagemap', {}).get('metatags', [])
                
                #Below is my view on prioritizing images and content
                primary_result_image = ""
                primary_site_image = ""
                for image in image_list:
                    if 'src' in image:
                        if self.is_valid_url(image.get('src', '')):
                            primary_result_image = image.get('src', '')
                            
                if primary_result_image == "":
                    for thumb in thumb_list:
                        if primary_result_image != "":
                            continue
                        else:
                            if 'src' in thumb:
                                if self.is_valid_url(thumb.get('src', '')):
                                    primary_result_image = thumb.get('src', '')
                                    
                
                if primary_result_image =="":
                    for meta in metatag_list:
                        if primary_result_image != "":
                            continue
                        else:
                            if 'og:image' in meta:
                                if self.is_valid_url(meta.get('og:image', '')):
                                    primary_result_image = meta.get('og:image', '')
                    
                if primary_site_image == "":
                    if result.get('link', '') != "":
                        base_url = self.get_base_url(result.get('link', ''))
                        if base_url != "":
                            primary_site_image = f"{base_url}/favicon.ico"
                    primary_site_image = f"https://www.google.com/s2/favicons?domain_url={self.get_domain(result.get('link', ''))}"
                    
                    if primary_site_image == "":                
                        for meta in metatag_list:
                            if primary_site_image != "":
                                continue
                            else:
                                if 'og:url' in meta:
                                    if self.is_valid_url(meta.get('og:url', '')):
                                        base_url = self.get_base_url(meta.get('og:url', ''))
                                        if base_url != "":
                                            primary_site_image = f"{base_url}/favicon.ico"
                
                
                result_dict = {
                    "Type" : "google",
                    "Query" : query,
                    "Site" : base_url,
                    "Summary" : result.get('htmlSnippet', result.get('snippet', '')),
                    "Page_Content": "",
                    "Link" : result.get('link', ''),
                    "Title": result.get('title', ''),
                    "primary_result_image" : primary_result_image,
                    "primary_site_image" : primary_site_image
                }
                
                results.append(result_dict)
            
            return results
            
        def search_you_rag_content_api(query):
            ydc_list = []
            for doc in yr.get_relevant_documents(query):
                text_val = f"<strong>{doc.type}</strong>: {doc.page_content}"
                ydc_list.append(text_val)
            return ydc_list
        
        #! Step 1 in pipeline: Get the company and location #################################################################
        self.company = propsect_data.get('Legal_Name''')
        self.location = f"{propsect_data.get('Main_Office_City', '')}, {propsect_data.get('Main_Office_State', '')}"
        self.CRD = propsect_data.get('Organization_CRD', '')
        
        #! Step 2 in pipeline: Get all relevant search results #################################################################
        search_results = []
        for title in self.titles_list:
            
            search_query = f'person {title} at {self.company} in {self.location}?'
            
            #?---> Note: FREE SCRAPING (COSTS NO MONEY) (could be blocked by google)
            google_web_scrape_results = scrape_google_web(search_query)
            url_list = extract_N_urls_from_markdown(google_web_scrape_results)
            search_results.extend(url_list)
            

            #?---> Note: THESE TWO LINES OF CODE !WORK! (THEY JUST COST MONEY)
            # google_results = search_google_api(search_query)
            # search_results.extend(google_results)
            
            print(f"Successfully got google search results for query '{search_query}'")
            
            you_results = search_you_rag_content_api(search_query)
            search_results.extend(you_results)
            print(f"Successfully got you.com results for query '{search_query}'")
            
            with open(f"{self.CRD}{title}search_results.json", "w") as f:
                f.write(json.dumps(search_results, indent=4))
        
        #! Step 3 in pipeline: Scrape all search results #################################################################
        async def async_scrape_single_url(url):
            def extract_text_from_html(html_body):
                soup = BeautifulSoup(html_body, 'html.parser')
                return soup.get_text(separator=' ', strip=True)

            def is_a_valid_url(may_be_a_url):
                try:
                    result = urlparse(may_be_a_url)
                    return all([result.scheme, result.netloc])
                except ValueError:
                    return False
            
            if url == "" or not is_a_valid_url(url):
                return "Invalid or missing URL"
                
            
            else:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    try:
                        await page.goto(url)
                        await page.wait_for_selector('body')
                        body = await page.content()
                        body_text = extract_text_from_html(body)
                        
                        return body_text
                    
                    except Exception as e:
                        error_message = f"Error getting full webpage for {url}: {str(e)}"
                        return error_message
                    
                    finally:
                        await browser.close()
        
        search_results_for_llm = []
        for result in search_results:            
            if isinstance(result, dict):
                type = result.get('Type', '')   
                if type == 'google':
                    url = result.get('Link', '')
                    
                    # Check if the URL has already been scraped
                    url_key = self.generate_unique_key_for_url(url)
                    if url_key in self.scrape_session_history:
                        body_text = self.scrape_session_history[url_key]
                    else:
                        # Scrape the URL and store the result
                        body_text = await async_scrape_single_url(url)
                        
                        # Store the result in the session history
                        self.scrape_session_history[url_key] = body_text
                    
                    result['Page_Content'] = body_text
                    search_results_for_llm.append(result)
                    print(f"Successfully scraped {url}")
                    
                    
        
        #! Step 4 in pipeline: prepare embeddings #################################################################
        def prepare_text(data):
            
            # Flatten the JSON data into a single string
            text = json.dumps(data, ensure_ascii=False)
            
            # Normalize whitespace and clean up text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split text into chunks by sentences, respecting a maximum chunk size
            sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
            chunks = []
            current_chunk = ""
            for sentence in sentences:
                
                # Check if the current sentence plus the current chunk exceeds the limit
                if len(current_chunk) + len(sentence) + 1 < 1000:  # +1 for the space
                    current_chunk += (sentence + " ").strip()
                else:
                    # When the chunk exceeds 1000 characters, store it and start a new one
                    chunks.append(current_chunk)
                    current_chunk = sentence + " "
            if current_chunk:  # Don't forget the last chunk!
                chunks.append(current_chunk)
            
            text_to_embed_list = []
            for chunk in chunks:
                # Write each chunk to its own line
                text_to_embed_list.append(chunk.strip() + "\n")  # Two newlines to separate chunks
            
            return text_to_embed_list
        
        #! Step 5 in pipeline: organize everything into a package #################################################################
        package = {}
        package['Prospect']= propsect_data
        package['Search_Results'] = search_results_for_llm
        package['Text_To_Embed'] = prepare_text(search_results_for_llm)
        
        #! Step 6 in pipeline: get the embeddings #################################################################
        # Parse command-line arguments
        parser = argparse.ArgumentParser(description="Ollama Chat")
        parser.add_argument("--model", default=self.llm_model, help="Ollama model to use (default: llama3)")
        args = parser.parse_args()

        # Configuration for the Ollama API client
        client = OpenAI(
            base_url=self.llm_base_url,
            api_key=self.llm_model_api_key
        )

        # Generate embeddings for the vault content using Ollama
        vault_embeddings = []
        for content in package['Text_To_Embed']:
            response = ollama.embeddings(model=self.embeddings_model, prompt=content)
            vault_embeddings.append(response["embedding"])

        # Convert to tensor and print embeddings
        vault_embeddings_tensor = torch.tensor(vault_embeddings) 
        print(f"Successfully got embeddings for the vault content for {self.company}.")
        print("Embeddings for each line in the vault:")
        print(vault_embeddings_tensor)
        
        
        #! Step 7 in pipeline: get the prompt, get relevant embeddings and ask Ollama #################################################################
        
        def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
            if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
                return []
            # Encode the rewritten input
            input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
            
            # Compute cosine similarity between the input and vault embeddings
            cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
            
            # Adjust top_k if it's greater than the number of available scores
            top_k = min(top_k, len(cos_scores))
            
            # Sort the scores and get the top-k indices
            top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
            
            # Get the corresponding context from the vault
            relevant_context = [vault_content[idx].strip() for idx in top_indices]
            
            return relevant_context

           #! Step 7 in pipeline: get the prompt         
        
        # Function to interact with the Ollama model
        def ollama_chat(user_input, system_message, vault_embeddings, vault_content, ollama_model, conversation_history):
           
            # Get relevant context from the vault
            relevant_context = get_relevant_context(user_input, vault_embeddings_tensor, vault_content, top_k=3)
            if relevant_context:
                # Convert list to a single string with newlines between items
                context_str = "\n".join(relevant_context)
                print("Context Pulled from Documents: \n\n" + CYAN + context_str + RESET_COLOR)
            else:
                print(CYAN + "No relevant context found." + RESET_COLOR)
            
            # Prepare the user's input by concatenating it with the relevant context
            user_input_with_context = user_input
            if relevant_context:
                user_input_with_context = context_str + "\n\n" + user_input
            
            # Append the user's input to the conversation history
            conversation_history.append({"role": "user", "content": user_input_with_context})
            
            # Create a message history including the system message and the conversation history
            messages = [
                {"role": "system", "content": system_message},
                *conversation_history
            ]
            
            
            # Send the completion request to the Ollama model
            response = client.chat.completions.create(
                model=self.llm_model,
                messages=messages
            )
            
            # Append the model's response to the conversation history
            conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
            
            # Return the content of the response from the model
            return response.choices[0].message.content
            
        def get_prompt(PersonTitle, Company):
            prompts = {"GetInfo": ''' {

                    "Instructions": [
                        "Below is an Example_JSON_Data_Record for a contact at a wealth management firm. Use the Example_JSON_Data_Record as a guide to populate the Empty_JSON_Data_Template with information about the person holding the RoleTitle specified in the Empty_JSON_Data_Template.",
                        "Use only the information provided with this prompt. Do not use any external sources. If you are not able to populate a value, leave it as an empty string.",
                        "Return only the Empty_JSON_Data_Template in your response. Do not return any other commentary or text. Your response is being systematically integrated and the assumption is that the Empty_JSON_Data_Template is the only output of your code.",
                        "Your response must be in valid JSON format beginning with: {\"Contact_JSON_Data\": {<The template you populate>} }"
                    ],
                    "Example_and_Template": {
                        "Example_JSON_Data_Record": {
                            "RoleTitle": "Chief Investment Officer (CIO)"
                            "PersonName": "John Doe",
                            "Company": "XYZ Wealth Management",
                            "Email": "John@xyzwealth.com",
                            "Phone": "555-555-5555",
                            "LinkedIn": "https://www.linkedin.com/in/johndoe",
                            "Background": "John Doe is the Chief Investment Officer at XYZ Wealth Management. He has over 20 years of experience in the financial services industry and specializes in investment management and portfolio construction. John holds a CFA designation and is a graduate of the University of ABC with a degree in Finance. He is passionate about helping clients achieve their financial goals and is committed to providing personalized investment solutions tailored to their needs.",
                            "PhotoURLs": ["https://www.xyzwealth.com/johndoe.jpg", "https://www.xyzwealth.com/johndoe2.jpg"],
                            "Location": "New York, NY",
                            "Interests": ["Cars", "Golf", "Travel"],
                            "OtherInfo": ["John is an avid golfer and enjoys spending time with his family and friends.", "He is also a car enthusiast and loves to travel to new destinations."]
                        },
                        
                        "Empty_JSON_Data_Template": {
                            "RoleTitle": " ''' + PersonTitle + ''' ",
                            "PersonName": "",
                            "Company": " ''' + Company + ''' ",
                            "Email": "",
                            "Phone": "",
                            "LinkedIn": "",
                            "Background": "",
                            "PhotoURLs": ["", ""],
                            "Location": "",
                            "Interests": ["", "", ""],
                            "OtherInfo": ["", "", ""]
                        }
                    }
                    }

                    Critical reminder: "Your response must be in valid JSON format beginning with: 
                    {
                        \"Contact_JSON_Data\": {<The populated template>}
                    }'''
                    
            }
            return prompts


            # @st.cache
        
        # ANSI escape codes for colors
        PINK = '\033[95m'
        CYAN = '\033[96m'
        YELLOW = '\033[93m'
        NEON_GREEN = '\033[92m'
        RESET_COLOR = '\033[0m'
        
        # Conversation loop
        conversation_history = []
        system_message = "You are a helpful assistant that is an expert at extracting the most useful information from a given text."

        key_contacts  = []
        for title in self.titles_list:
            user_input = get_prompt(title, self.company)
            response = ollama_chat(user_input, system_message, vault_embeddings_tensor, package['Text_To_Embed'], args.model, conversation_history)
            print(NEON_GREEN + "Response: \n\n" + response + RESET_COLOR)
            key_contacts.append(response)
        
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
        package['Prospect'][key_contacts] = json.dumps(key_contacts)
        package['Prospect']['pipeline_version'] = "1"
        package['Prospect']['pipeline_as_of'] = current_date_time
        
        #! Step 8 in pipeline: return the package
        return package['Prospect']
            
@app.route('/prospectpipeline', methods=['POST'])
def process_pipeline_all_prospects():
    
    
    storage = _class_streamlit.PsqlSimpleStorage()
    prospect_list = asyncio.run(storage.get_all_prospects())
    print(f"Successfully got prospect list with count '{len(prospect_list)}'")
    
    pipeline = prospect_data_pipeline()
    
    for prospect in prospect_list:
        FIXME = pipeline.process_prospect_main(prospect)
        
