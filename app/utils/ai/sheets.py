import logging

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Авторизация через Service Account
def get_sheet_all_data(sheet_url: str, sheet_name: str):
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_url(sheet_url)
    logger.debug(sheet_name)
    sheet = sh.worksheet(sheet_name)
    data = sheet.get_all_records()
    logger.debug("DATA FROM SHEET")
    logger.debug(data)
    return data


def get_sheet_all_values(sheet_url: str, sheet_name: str):
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sh = client.open_by_url(sheet_url)
    sheet = sh.worksheet(sheet_name)
    data = sheet.get_all_values()
    text = "\n".join(
        " ".join(cell for cell in row if cell)
        for row in data
        if any(row)
    )
    logger.debug("DATA FROM SHEET")
    logger.debug(text)
    return text