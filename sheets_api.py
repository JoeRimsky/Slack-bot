import pickle, os.path, yaml
import pandas as pd
import numpy as np
import setup_logger
from tabulate import tabulate
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

data_logger = setup_logger.Logger(log='data_logs',file_name='/home/jrimsky8854/rtm_bot/logs/data_logs.log')

def connect_to_api(scopes):
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds,cache_discovery=False)

    return service

def get_data(username, message, service, spreadsheet_id, sheet_range, optional_range=None):
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=sheet_range).execute()
    values = result.get('values', [])
    data_logger.log_data(username, message, values, 'INFO')
    df = pd.DataFrame(values)

    master = convert_data(df)

    if optional_range:
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                    range=optional_range).execute()
        values = result.get('values', [])
        df = pd.DataFrame(values)

        master = convert_data(df) + "\n\n" + master

    return master

def convert_data(df):
    master_table = ""
    df_list = np.split(df, df[df.isnull().all(1)].index)
    for df in df_list:
        df = df.dropna(how='all')
        if not master_table:
            master_table += tabulate(df, tablefmt="pretty", showindex="never", colalign=("right","center"))
        else:
            master_table = master_table + "\n\n" + tabulate(df, tablefmt="pretty", showindex="never", colalign=("right","center"))

    return master_table