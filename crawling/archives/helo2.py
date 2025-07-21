import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# File credential JSON dari Google Cloud
credentials_file = "credentials.json"

# Scope akses untuk Google Sheets dan Google Drive
scopes = ["https://www.googleapis.com/auth/spreadsheets", 
          "https://www.googleapis.com/auth/drive"]

# Autentikasi
credentials = Credentials.from_service_account_file(credentials_file, scopes=scopes)
client = gspread.authorize(credentials)

# URL spreadsheet
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo/edit#gid=0"

# Membuka spreadsheet berdasarkan URL
spreadsheet = client.open_by_url(spreadsheet_url)

# Mendapatkan semua sheet
sheets = spreadsheet.worksheets()

# Membaca data dari tiap sheet ke dalam pandas DataFrame
all_sheets_data = {}

for sheet in sheets:
    sheet_name = sheet.title
    print(f"Memproses sheet: {sheet_name}")

    try:
        # Membaca semua data mentah dari sheet
        raw_data = sheet.get_all_values()

        if not raw_data:  # Jika sheet kosong
            print(f"Sheet {sheet_name} kosong, melewatkan...")
            continue

        # Pastikan baris pertama adalah header
        if len(raw_data) < 1 or not any(raw_data[0]):
            print(f"Sheet {sheet_name} tidak memiliki header yang valid, melewatkan...")
            continue

        # Konversi ke DataFrame
        df = pd.DataFrame(raw_data[1:], columns=raw_data[0])  # Baris pertama sebagai header
        all_sheets_data[sheet_name] = df
        print(f"Berhasil memproses sheet: {sheet_name}")
        print(df.head())  # Preview data

    except Exception as e:
        print(f"Error saat memproses sheet {sheet_name}: {e}")

# Menampilkan ringkasan semua sheet yang berhasil dibaca
print("\nRingkasan sheet yang berhasil diproses:")
for sheet_name, df in all_sheets_data.items():
    print(f"- {sheet_name}: {len(df)} baris")

# Contoh: Mengakses DataFrame dari sheet tertentu
if "NamaSheet" in all_sheets_data:
    print(all_sheets_data["NamaSheet"].head())
