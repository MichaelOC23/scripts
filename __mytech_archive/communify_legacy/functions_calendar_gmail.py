
import functions_constants as con
from googleapiclient.discovery import build
import datetime
import json
import functions_opena_ai_simple as gpt
import re

# Get the credentials
creds = con.get_gmail_access_token()

# Build the service
service = build('calendar', 'v3', credentials=creds)

def clean_key(input_string):
    # Replace any non-alphanumeric and non-underscore characters with an empty string
    cleaned_string = re.sub(r'[^a-zA-Z0-9_]', '', input_string)
    return cleaned_string

def create_event(event_text, Calendar_Id='primary'):
    if not event_text or event_text == None or event_text == "":
      return "ERROR: No event text provided"
    
    if isinstance(event_text, str):
      event_text = [event_text]
    
    if not isinstance(event_text, list):
      return "ERROR: event_text must be a string or a list of strings"
    
    return_value = create_events(event_text, Calendar_Id=Calendar_Id)
    
    return return_value

def create_events(event_text, Calendar_Id='primary'):

  #Get the prompt
  with open(con.PROMPT_FILE_PATH_CREATE_GOOGLE_CALENDAR_EVENT, 'r') as f:
      prompt = f.read()
      f.close()
  

  Current_Date_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  prompt = prompt.replace('<Current-Date-Time>', Current_Date_Time)
  prompt = f"{prompt} \n\n {event_text} \n\n ### END TRANSCRIBED REQUESTS ###"
  con.log_it(f'Prompt: {prompt}')

  #Ask GPT
  print(f'Sending to Chat GPT')
  time_start = datetime.datetime.now()
  response = gpt.ask_gpt_single_prompt(prompt, model=con.MODEL_GPT3, temperature=0.1,)
  con.log_it(f'receivedresponse from GPT in {datetime.datetime.now()-time_start}')

  if response == None:
    return "ERROR: GPT3 returned None"

  #Clean up the markdown that is standard when GPT3 returns a response with code
  response = response.replace('"```json','')
  response = response.replace('```"','')
  response = bytes(response, "utf-8").decode("unicode_escape")
  response = response.replace("\n"," ")
  #remove the leading and trailing quotes
  response = response[1:-1]



  response_dict = json.loads(response)

  log_dict = {}

  for event in response_dict:
    # Insert the event
    #created_event = service.events().insert(calendarId='rtt9gi02nk109kr86mvegkiot8@group.calendar.google.com', body=event).execute()
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (created_event.get('htmlLink')))
    kev_value = event_text
    if isinstance(event_text, list):
       key_value = "".join(event_text)
    log_dict[clean_key(key_value)] = event

  return log_dict  




if __name__ == '__main__':
  #print("Tests are below, but commented out")
  event_text = "Dinner with sam tomorrow at 6:30 at Louie's italian"
  returnval = create_event(event_text)
  con.log_it(f'returnval: {returnval}')

  # for event_text in event_list:
  #   returnval = create_events(event_text)
  #   with open(f'temp/event_log{event_run}.json', 'a') as outfile:
  #     json.dump(returnval, outfile)
  #     outfile.write(',\n')


  # event_list = [
  #   "Coffee with Maria next Monday at 9am at Starbucks on Main Street",
  #   "Team meeting on Wednesday at 3pm in Conference Room B",
  #   "Lunch with Alex and Jordan, Friday 1pm, The Greenhouse Cafe",
  #   "Doctor's appointment on 23rd March at 10:30am at City Medical Center",
  #   "Project review with the IT department, April 5th, 2pm, Zoom",
  #   "Birthday party for Ella, April 12th, 5pm, at my house",
  #   "Golf with clients, next Thursday, 8am, Oakwood Golf Course",
  #   "Dentist appointment, March 28th, 11am, Pearl Dental",
  #   "Yoga class with Emily, Sunday, 4pm, Lotus Yoga Studio",
  #   "Dinner at The French Bistro, 7pm, next Saturday with the Smiths",
  #   "Haircut, May 6th, 9:30am, Bella's Hair Salon",
  #   "Marketing seminar, April 15th, 1pm-4pm, Downtown Conference Hall",
  #   "Networking event, Tuesday, 6pm, The Riverside Hotel",
  #   "Parent-teacher meeting, 16th April, 2:30pm, Lincoln High School",
  #   "Guitar lesson, every Friday, 6pm, Dave's Music Academy",
  #   "Plumbing repair, March 22nd, 10am-12pm, my apartment",
  #   "Hiking trip, next Sunday, 8am, meet at Trailhead Park",
  #   "Book club, April 10th, 7pm, Emily's house",
  #   "Vet appointment for Max, April 3rd, 2pm, City Pet Clinic",
  #   "Grocery shopping, Saturday, 11am, Main Street Supermarket",
  #   "Dinner with Kevin, next Tuesday, 8pm, Ocean View Restaurant",
  #   "Gardening workshop, March 27th, 10am, Community Center",
  #   "Car service, April 8th, 9am, QuickFix Auto Garage",
  #   "Piano recital, April 20th, 5pm, Town Hall Auditorium",
  #   "Coffee catch-up, next Wednesday, 10am, Central Park Cafe",
  #   "Annual general meeting, April 17th, 3pm-5pm, Corporate HQ",
  #   "Soccer practice, every Thursday, 4pm, Eastside Sports Field",
  #   "Dance class with Sarah, Monday, 7pm, Starlight Dance Studio",
  #   "Library visit, April 1st, 2pm, Downtown Library",
  #   "Brunch with college friends, April 13th, 11am, SunnySide Brunch Spot"
  #     ]
  # 
  

