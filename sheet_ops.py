import os
import sys
sys.path.append('/opt')
sys.path.append('package')
sys.path.append('package/bin')

from apiclient import discovery
from google.oauth2 import service_account

SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

def get_google_service():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file('google_secret.json', scopes=scopes)
    return discovery.build('sheets', 'v4', credentials=creds, cache_discovery=False)

def get_rows_to_update(service, case_id):
    case_id_range = "'FED FILINGS 2020-2021'!A:A"
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=case_id_range
    ).execute()
    values = result.get('values', [])

    return [i+1 for i, x in enumerate(values) if x[0] == case_id]

def update_rows(service, info, rows):
    first_row = rows[0]
    num_rows = len(rows)
    last_row = first_row + num_rows - 1
    paste_range = f"'FED FILINGS 2020-2021'!O{first_row}:V{last_row}"
    body = {'values': [info]*num_rows}
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=paste_range,
        valueInputOption="RAW", body=body
    ).execute()
    return result

def get_case_ids(service):
    case_id_range = "'FED FILINGS 2020-2021'!A:A"
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=case_id_range
    ).execute()
    values = result.get('values', [])

    return list(set([x[0] for x in values]))