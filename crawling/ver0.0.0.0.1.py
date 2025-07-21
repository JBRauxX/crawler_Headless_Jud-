import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import time

# Konfigurasi Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_KEY = '1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo'

# Autentikasi
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)
spreadsheet = gc.open_by_key(SPREADSHEET_KEY)

def process_sheet(sheet):
    # Fungsi untuk sheet selain "SEMUA ALTERNATIF"
    last_row = len(sheet.col_values(2))  # Kolom "LINK WEBSITE"
    for i in range(3, last_row + 1):
        link = sheet.cell(i, 2).value
        if not link:
            continue
        # Update status dan cekindo
        sheet.update_cell(i, 3, "Aman")
        sheet.update_cell(i, 4, "Bisa diakses")
        print(f"Row {i} in sheet {sheet.title} updated")

def process_semi_tubular_sheet(sheet):
    # Fungsi khusus untuk sheet "SEMUA ALTERNATIF"
    last_row = len(sheet.col_values(1))
    for i in range(2, last_row + 1):
        status = sheet.cell(i, 5).value
        if not status or status.strip().lower() != "valid":
            sheet.update_cell(i, 5, "Valid")
            print(f"Row {i} in sheet {sheet.title} updated: Status Indo set to 'Valid'")

def main():
    while True:
        now = datetime.now()
        target_times = [datetime(now.year, now.month, now.day, hour) for hour in [8, 13, 18]]
        next_target = min([t for t in target_times if t > now], default=target_times[0] + timedelta(days=1))
        print(f"Next update scheduled at: {next_target}")
        
        sleep_time = (next_target - now).total_seconds()
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        sheets = spreadsheet.worksheets()
        for sheet in sheets:
            if sheet.title == "SEMUA ALTERNATIF":
                process_semi_tubular_sheet(sheet)
            else:
                process_sheet(sheet)
        print("All sheets processed. Waiting for the next cycle...")

main()
