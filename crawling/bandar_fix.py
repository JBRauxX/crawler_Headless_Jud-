

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
import time  # Import modul time untuk menambahkan delay

# Konfigurasi Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_KEY = '1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo'

# Autentikasi ke Google Sheets
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet("BANDAR")

def is_isp_block_page(html_content):
    """
    Deteksi apakah halaman yang diakses merupakan halaman blokir ISP.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    block_keywords = ['internetpositif', 'internetbaik', 'trustpositif', 'nawala']

    if any(keyword in html_content.lower() for keyword in block_keywords):
        return True
    return False

def check_website_accessibility(domain):
    """
    Periksa aksesibilitas website dan deteksi statusnya.
    """
    urls_to_try = [f"https://{domain}", f"http://{domain}"]
    
    for url in urls_to_try:
        try:
            with httpx.Client(verify=False, timeout=10.0, follow_redirects=True) as client:
                response = client.get(url)
                if response.status_code == 200:
                    if "godaddy" in response.text.lower():
                        return "Expired", "Tidak Ditemukan"
                    if is_isp_block_page(response.text):
                        return "Blokir", "nawala"
                    return "Aman", "Bisa Di Akses"
        except Exception:
            continue
    return "Expired", "Tidak Ditemukan"

def update_status_and_cekindo():
    """
    Perbarui status dan cekindo untuk setiap domain dalam Google Sheet.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    row = 3  # Mulai dari baris ke-3
    while True:
        no_value = sheet.cell(row, 1).value  # Ambil nilai dari kolom "A"
        if not no_value:  # Jika kolom "A" kosong, hentikan iterasi
            break

        link = sheet.cell(row, 2).value
        if not link:
            print(f"Row {row} skipped: No link found.")
            sheet.update_cell(row, 3, "Expired")
            sheet.update_cell(row, 5, "Tidak Ditemukan")
            row += 1
            continue

        domain = link.replace("https://", "").replace("http://", "").split("/")[0]
        print(f"\nMemeriksa domain: {domain}")
        status, cekindo = check_website_accessibility(domain)

        sheet.update_cell(row, 3, status)
        sheet.update_cell(row, 5, cekindo)  # Memperbarui kolom "E" (kolom ke-5)

        # Tambahkan warna pada cell (kecuali kolom D)
        color = {"Aman": (0.5, 1, 0.5), "Blokir": (1, 0.5, 0.5), "Expired": (0.8, 0.8, 0.8)}
        rgb = color.get(status, (1, 1, 1))
        sheet.format(f"C{row}:C{row}", {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}})
        sheet.format(f"E{row}:E{row}", {"backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}})

        print(f"Row {row} updated: Status={status}, Cekindo={cekindo}")
        row += 1
        time.sleep(2)  # Menunggu 2 detik sebelum melanjutkan

def update_check_time_and_date():
    """
    Perbarui waktu pemeriksaan terakhir di Google Sheet.
    """
    last_row = get_last_data_row()
    now = datetime.now()
    today = now.strftime("%y-%m-%d")
    current_time = now.strftime("%H:%M")

    sheet.update_cell(last_row + 2, 3, today)
    sheet.update_cell(last_row + 3, 3, current_time)
    print(f"Waktu pemeriksaan diperbarui: {today} {current_time}")

def get_last_data_row():
    """
    Mengambil baris terakhir yang berisi data pada kolom A di Google Sheets.
    """
    all_values = sheet.get_all_values()
    column_a_values = [row[0] for row in all_values if row[0]]
    return len(column_a_values)

def main():
    """
    Fungsi utama untuk menjalankan pembaruan status domain.
    """
    print("Memulai proses update...")
    update_status_and_cekindo()
    update_check_time_and_date()
    print("Proses selesai.")

main()
