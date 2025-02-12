import dotenv
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

dotenv.load_dotenv()

# Spreadsheet IDs and Scope
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE = 'Complete!A2:Z'
SHEET_ID = os.environ.get("COMPLETE_ID")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def main():
    """Basic Usage of the Google Sheets API at the moment"""
    creds = None
    # token.json stores the user's access and refresh tokens
    # created automatically when auth flow completes for the first time
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # if there are no (valid) credentials available, user must log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # save credentials for next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)
        # calling sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Checked In At | Queued At | Student Name | Assignment | Called By")
        for row in values:
            if row[1]:
                print(f"{row[1]} | {row[2]} | {row[4]} | {row[5]} | {row[9]}")

    except HttpError as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
