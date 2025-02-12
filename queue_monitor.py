import time
import dotenv
import os
from datetime import datetime
import subprocess
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

dotenv.load_dotenv()

# Spreadsheet IDs and Scope
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
QUEUE_RANGE = 'Form Responses!A2:J10'
COMPLETE_RANGE = 'Complete!A2:Z'
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class QueueStats:
    def __init__(self):
        self.total_requests = 0
        self.start_time = datetime.now()
        self.last_request_time = None

    def update(self, new_entries):
        self.total_requests += len(new_entries)
        self.last_request_time = datetime.now()


def send_notification(entry_id: str):
    """Send MacOS Notification"""
    net_id = entry_id.split('@')[0]
    apple_script = f'''display notification 
    "NetID: {net_id}" 
    with title "New Student in CS220 Queue" 
    sound name "Ping"
    '''
    subprocess.run(['osascript', '-e', apple_script])


def get_credentials():
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
    return creds


def get_timestamp(timestamp: str) -> str:
    """ Function to extract just the time from the timestamp in sheet """
    datetime_obj = datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S")
    time_str = datetime_obj.strftime("%H:%M:%S")
    return time_str


def monitor_queue():
    """Notification System"""
    creds = get_credentials()
    service = build("sheets", "v4", credentials=creds)

    # initialize QueueStats() class to track stats
    stats = QueueStats()
    print_status(stats)  # initial status

    # keep track of seen entries
    seen_entries = set()
    while True:
        try:
            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(spreadsheetId=SPREADSHEET_ID, range=QUEUE_RANGE)
                .execute()
            )
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return

            if not values or (len(values[0]) <= 2 and values[0] == ['FALSE', 'FALSE']):
                # queue is empty, wait and continue
                time.sleep(30)
                continue

            current_entries = set()
            for row in values:
                # skip empty or invalid rows
                if len(row) <= 2:
                    continue

                # create a unique identifier for each entry using email address and timestamp
                try:
                    timestamp = get_timestamp(row[2])
                    entry_id = f"{row[3]}-{timestamp}"
                    current_entries.add(entry_id)
                except (IndexError, ValueError) as e:
                    # skip malformed rows
                    continue

            new_entries = current_entries - seen_entries
            if new_entries:
                stats.update(new_entries) # update stats
                for entry_id in new_entries:
                    send_notification(entry_id)
                print_status(stats)

            # update seen_entries
            seen_entries = current_entries

            # print status every 5 minutes for fun
            if datetime.now().minute % 5 == 0:
                print_status(stats)

            time.sleep(30)  # check every 30 seconds

        except HttpError as e:
            print(f"HTTP Error: {e}")
            time.sleep(60)


def get_completed_entries():
    """Basic Usage of the Google Sheets API at the moment"""
    creds = get_credentials()

    try:
        service = build("sheets", "v4", credentials=creds)
        # calling sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=COMPLETE_RANGE)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Checked | Checked In At | Queued At | Student Name | Assignment | Called By")
        for row in values:
            if row[0] == 'TRUE':
                print(f"{row[0]} | {get_timestamp(row[1])} | {get_timestamp(row[2])} | {row[4]} | {row[5]} | {row[9]}")

    except HttpError as e:
        print(f"Error: {e}")


def print_status(stats: QueueStats):
    """Print current monitoring status"""
    print("=== Queue Monitor Status ===")
    print(f"Running since: {stats.start_time}")
    print(f"Total requests: {stats.total_requests}")
    if stats.last_request_time:
        print(f"Last request: {stats.last_request_time}")
    else:
        print("No requests yet")
    print("==========================\n")


if __name__ == '__main__':
    print("Starting Queue Monitoring...")
    monitor_queue()
    # get_completed_entries()
