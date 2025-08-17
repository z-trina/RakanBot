# Service account: rakanspreadsheet@stoked-legend-467903-m4.iam.gserviceaccount.com
from google.oauth2 import service_account
from googleapiclient.discovery import build

import os, sys

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)

SERVICE_ACCOUNT_FILE = resource_path('Service_account_rakan.json')

'''
# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'Service_account_rakan.json'
'''

# Create credentials using the service account file
credentials = service_account.Credentials.from_service_account_file(
    filename=SERVICE_ACCOUNT_FILE
)

# Build the Sheets API client
service_sheets = build('sheets', 'v4', credentials=credentials)

GOOGLE_SHEETS_ID = '1W5poT1Wp9lhpPruzMrm_QXqZu5owjT23w0uHXbe1hSU'

worksheet_name = 'Sheet1!'
cell_range_insert = 'A1' 

'''
values = [
    ['03/17', '2000', 'Insurance', 'Transportation']
]
'''


def save_to_google_sheets(values): 
    # Columns: Name, Discord Name, Discord ID, State, School, Gender, Used Discord, Form, Timestamp
    value_range_body = {
        'majorDimension': 'ROWS',
        'values': values
    }

    service_sheets.spreadsheets().values().append(
        spreadsheetId=GOOGLE_SHEETS_ID,
        valueInputOption='USER_ENTERED',
        range=worksheet_name + cell_range_insert,
        body=value_range_body
    ).execute()


# save_to_google_sheets([['Name', 'ID', 'State', 'School']]) 
