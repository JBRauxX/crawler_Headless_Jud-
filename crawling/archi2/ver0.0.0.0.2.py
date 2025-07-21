import gspread
from oauth2client.service_account import ServiceAccountCredentials
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

# Konfigurasi Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_KEY = '1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo'

# Autentikasi ke Google Sheets
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)

# Fungsi untuk mendeteksi halaman blokir ISP
def is_isp_block_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    keywords = ['internetpositif', 'internetbaik', 'trustpositif']
    return any(keyword in html_content.lower() for keyword in keywords)

# Fungsi untuk memeriksa aksesibilitas website
def check_website_accessibility(domain):
    urls_to_try = [f"https://{domain}", f"http://{domain}"]
    for url in urls_to_try:
        try:
            with httpx.Client(verify=False, timeout=30.0, follow_redirects=True) as client:
                response = client.get(url)
                if response.status_code == 200:
                    if is_isp_block_page(response.text):
                        return "Blokir", "nawala"
                    return "Aman", "Bisa Diakses"
        except Exception as e:
            print(f"Error mencoba {url}: {str(e)}")
    return "Blokir", "nawala"

# Fungsi untuk memperbarui status dan cekindo pada setiap sheet di Google Spreadsheet
def update_status_and_cekindo():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
    sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]

    for sheet_name in sheet_names:
        # Lewati sheet "SHARE-LINK" dan "SEMUA ALTERNATIF"
        if sheet_name in ["SHARE-LINK", "SEMUA ALTERNATIF"]:
            print(f"Sheet {sheet_name} dilewati.")
            continue

        print(f"\nMemproses sheet: {sheet_name}")
        worksheet = spreadsheet.worksheet(sheet_name)
        rows = worksheet.get_all_values()

        # Pastikan header sesuai
        if len(rows) < 1 or rows[0][:3] != ['LINK WEBSITE', 'STATUS', 'CEKINDO']:
            print(f"Header di sheet {sheet_name} tidak sesuai atau kosong. Lewati.")
            continue

        for index, row in enumerate(rows[1:], start=2):  # Mulai dari baris kedua
            link = row[0] if len(row) > 0 else ""
            if not link:
                print(f"Baris {index} dilewati: Tidak ada link.")
                continue

            domain = link.replace("https://", "").replace("http://", "").split("/")[0]
            print(f"Memeriksa domain: {domain}")
            status, cekindo = check_website_accessibility(domain)

            worksheet.update_cell(index, 2, status)  # Kolom STATUS
            worksheet.update_cell(index, 3, cekindo)  # Kolom CEKINDO
            print(f"Baris {index} diperbarui: Status={status}, Cekindo={cekindo}")

# Fungsi untuk memperbarui waktu pemeriksaan terakhir
def update_check_time_and_date():
    now = datetime.now()
    today = now.strftime("%y-%m-%d")
    current_time = now.strftime("%H:%M")

    spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
    sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]

    for sheet_name in sheet_names:
        # Lewati sheet "SHARE-LINK" dan "SEMUA ALTERNATIF"
        if sheet_name in ["SHARE-LINK", "SEMUA ALTERNATIF"]:
            print(f"Sheet {sheet_name} dilewati.")
            continue

        worksheet = spreadsheet.worksheet(sheet_name)
        last_row = len(worksheet.col_values(1)) + 1
        worksheet.update_cell(last_row, 2, today)
        worksheet.update_cell(last_row + 1, 2, current_time)
        print(f"Waktu pemeriksaan diperbarui untuk sheet {sheet_name}: {today} {current_time}")

# Fungsi utama
if __name__ == "__main__":
    print("Memulai proses update...")
    update_status_and_cekindo()
    update_check_time_and_date()
    print("Proses selesai.")
