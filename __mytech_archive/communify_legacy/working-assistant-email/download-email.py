import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import shared.functions_gmail as gmail
import shared.functions_constants as constants
import base64
from bs4 import BeautifulSoup
from googleapiclient.discovery import build




def main(run_id1):
    """Hello this is it"""
    gmail.get_emails_full_contents(run_id1)
    #send_sms()

if __name__ == '__main__':
    # Usage:
    run_id = constants.UNIQUE_DATE_TIME_STRING()
    print(f'Run ID: {run_id}')  # Output: Unique run ID of 12 characters
    main(run_id)
    