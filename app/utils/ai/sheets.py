import gspread
from google.oauth2.service_account import Credentials

# Авторизация через Service Account
def get_sheet(sheet_url: str, sheet_name: str):
    creds = Credentials.from_service_account_file("service_account.json")
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    data = sheet.get_all_records()
    return data