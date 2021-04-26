import os
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

from apiclient import discovery
from google.oauth2 import service_account

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SHEET_NAME = os.environ["SHEET_NAME"]

def get_google_service():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file('google_secret.json', scopes=scopes)
    return discovery.build('sheets', 'v4', credentials=creds, cache_discovery=False)

def get_rows_to_update(service, case_id):
    case_ids = get_case_ids(service, unique=False)
    return [i+1 for i, x in enumerate(case_ids) if x == case_id]

def update_rows(service, info, rows):
    for row in rows:
        paste_range = f"{SHEET_NAME}!AN{row}:AV{row}"
        body = {'values': [info]}
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=paste_range,
            valueInputOption="RAW", body=body
        ).execute()
    return result

def get_case_ids(service, unique=True):
    case_id_range = f"'{SHEET_NAME}'!S:S"
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=case_id_range
    ).execute()
    values = result.get('values', [])
    return list(set([x[0] for x in values if (x != ['0'] and x != [])])) if unique else [x[0] if len(x)==1 else '' for x in values]
