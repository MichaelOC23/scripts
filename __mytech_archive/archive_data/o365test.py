import json
import os
import sys
import requests





GRAPH_ENDPOINT = 'https://graph.microsoft.com/v1.0'


access_token = os.environ.get('JBI_MSFT_ACCESS_TOKEN')


if access_token != "":
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(f'{GRAPH_ENDPOINT}/me/contacts', headers=headers)
    
    if response.status_code == 200:
        messages = response.json()
        print(json.dumps(messages, indent=4))
    
    else:
        print(f"Failed to fetch messages: {response.status_code} {response.text}")
else:
    print(f"Failed to obtain access token")


endpoints = {
  "Email": [
    {"Get messages": "GET /me/messages"},
    {"Send a message": "POST /me/sendMail"},
    {"Get a specific message": "GET /me/messages/{id}"},
    {"Create a new message": "POST /me/messages"}
  ],
  "Calendar": [
    {"Get calendar events": "GET /me/events"},
    {"Create a new event": "POST /me/events"},
    {"Get a specific event": "GET /me/events/{id}"},
    {"Update an event": "PATCH /me/events/{id}"},
    {"Delete an event": "DELETE /me/events/{id}"}
  ],
  "Tasks (To-Do)": [
    {"Get tasks": "GET /me/todo/lists/{listId}/tasks"},
    {"Create a new task": "POST /me/todo/lists/{listId}/tasks"},
    {"Get a specific task": "GET /me/todo/lists/{listId}/tasks/{taskId}"},
    {"Update a task": "PATCH /me/todo/lists/{listId}/tasks/{taskId}"},
    {"Delete a task": "DELETE /me/todo/lists/{listId}/tasks/{taskId}"}
  ],
  "Contacts": [
    {"Get contacts": "GET /me/contacts"},
    {"Create a new contact": "POST /me/contacts"},
    {"Get a specific contact": "GET /me/contacts/{id}"},
    {"Update a contact": "PATCH /me/contacts/{id}"},
    {"Delete a contact": "DELETE /me/contacts/{id}"}
  ]
}