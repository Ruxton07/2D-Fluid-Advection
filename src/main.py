"""
Shows basic usage of the Apps Script API.
Call the Apps Script API to create a new script project, upload a file to the
project, and log the script's URL to the user.
"""

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import src.simulation as sim
import src.Prototype2 as p2


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1NapEbwM5uHI1JoR1sZo8Qzd5WGt84tHy3jl_P5IljRM"
GRID_RANGE = "Grid!A1:AN40"
print(f"Using range: {GRID_RANGE}")

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        sim.main(creds, SPREADSHEET_ID, GRID_RANGE)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
