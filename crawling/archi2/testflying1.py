import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3

# Konfigurasi Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'  # Ganti dengan path ke file kredensial Anda
SPREADSHEET_KEY = '1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo'  # Ganti dengan key Google Sheets Anda

# Autentikasi ke Google Sheets
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet("TOKE")  # Ganti nama sheet jika berbeda

# Fungsi untuk memastikan link memiliki protokol 'https://'
def ensure_https(link):
    if not link.startswith("http://") and not link.startswith("https://"):
        return f"https://{link}"
    return link

# Fungsi untuk mendapatkan jumlah baris terakhir yang berisi data di kolom "LINK WEBSITE"
def get_last_data_row():
    col_values = sheet.col_values(2)  # Kolom kedua adalah "LINK WEBSITE"
    return len([value for value in col_values if value.strip()])  # Menghitung baris non-kosong

# Fungsi untuk memperbarui status dan cekindo
def update_status_and_cekindo():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    last_row = get_last_data_row()  # Baris terakhir yang memiliki data di kolom "LINK WEBSITE"
    for i in range(3, last_row + 1):  # Iterasi mulai dari baris ke-3
        link = sheet.cell(i, 2).value  # Ambil nilai dari kolom kedua (LINK WEBSITE)
        if not link:
            continue  # Jika tidak ada link, lewati baris ini

        # Pastikan link memiliki protokol 'https://'
        full_link = ensure_https(link)
        print(f"Checking link: {full_link}")  # Cetak link yang sedang diperiksa

        try:
            response = requests.get(full_link, timeout=10, verify=False)
            if response.status_code == 200:
                status = "Aman"
                soup = BeautifulSoup(response.content, 'html.parser')
                cekindo = "Bisa di Akses" # Inisialisasi variabel cekindo
            else:
                status = "Blokir"
                cekindo = "nawala"
        except requests.exceptions.RequestException as e:
            status = "Blokir"
            cekindo = "nawala"
            print(f"Error accessing {full_link}: {e}")

        # Jika cekindo tidak ditemukan, biarkan kosong atau tetap None
        if cekindo is None:
            cekindo = ""  # Anda bisa memilih "" atau biarkan None untuk hasil kosong

        # Update kolom "STATUS" (kolom ke-3) dan "CEKINDO" (kolom ke-4)
        sheet.update_cell(i, 3, status)
        sheet.update_cell(i, 4, cekindo)
        print(f"Row {i} updated: Status={status}, Cekindo={cekindo}")

# Fungsi untuk memperbarui tanggal dan jam pengecekan
def update_check_time_and_date():
    last_row = get_last_data_row()  # Baris terakhir yang memiliki data di kolom "LINK WEBSITE"
    now = datetime.now()
    today = now.strftime("%y-%m-%d")  # Format tanggal
    current_time = now.strftime("%H:%M")  # Format waktu

    # Update "TANGGAL PENGECEKAN TERAKHIR" di baris setelah data terakhir
    sheet.update_cell(last_row + 2, 3, today)
    print(f"Tanggal diperbarui: {today}")

    # Update "JAM PENGECEKAN" di baris setelah "TANGGAL PENGECEKAN TERAKHIR"
    sheet.update_cell(last_row + 3, 3, current_time)
    print(f"Jam diperbarui: {current_time}")

# Fungsi utama
def main():
    print("Memulai proses update...")
    update_status_and_cekindo()
    update_check_time_and_date()
    print("Proses selesai.")

main()
