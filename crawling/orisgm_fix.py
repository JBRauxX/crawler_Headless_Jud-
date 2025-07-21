import gspread
from oauth2client.service_account import ServiceAccountCredentials
import httpx
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
import time

# Konfigurasi Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_KEY = '1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo'

# Autentikasi ke Google Sheets
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet("ORISGAMING")

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
                    if is_isp_block_page(response.text):
                        return "Blokir", "nawala"
                    return "Aman", "Bisa Di Akses"
        except Exception:
            continue
    return "Expired", "Tidak Ditemukan"

def get_last_data_row():
    """
    Ambil nomor baris terakhir dengan data pada Google Sheet.
    """
    col_values = sheet.col_values(2)
    return len(col_values)

def get_website_count():
    """
    Ambil jumlah website yang akan diperiksa (berdasarkan nilai "LINK WEBSITE").
    Gunakan default jika nilai tidak valid atau kosong.
    """
    try:
        link_website = sheet.cell(1, 2).value  # Asumsi "LINK WEBSITE" ada di baris pertama, kolom kedua
        if link_website and link_website.isdigit():
            return int(link_website)  # Menggunakan nilai yang valid
        else:
            print("Nilai 'LINK WEBSITE' kosong atau tidak valid. Menggunakan default (semua baris).")
            return get_last_data_row() - 2  # Menggunakan jumlah data yang ada, dikurangi 2 untuk header
    except Exception as e:
        print(f"Error saat mengambil nilai 'LINK WEBSITE': {e}")
        return get_last_data_row() - 2  # Menggunakan jumlah data yang ada jika error

def update_status_and_cekindo():
    """
    Perbarui status dan cekindo untuk setiap domain dalam Google Sheet menggunakan batch update.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    last_row = get_last_data_row()
    update_data = []  # Menyimpan data yang akan diperbarui dalam batch

    website_count = get_website_count()  # Ambil jumlah website yang akan diperiksa
    rows_to_check = min(website_count, last_row - 2)  # Jangan melebihi baris data yang ada

    for i in range(3, 3 + rows_to_check):  # Mulai dari baris 3, batasi jumlah sesuai website_count
        link = sheet.cell(i, 2).value
        if not link:
            print(f"Row {i} skipped: No link found.")
            update_data.append({
                'range': f'C{i}:D{i}',
                'values': [["Expired", "Tidak Ditemukan"]]
            })
            continue

        domain = link.replace("https://", "").replace("http://", "").split("/")[0]
        print(f"\nMemeriksa domain: {domain}")
        status, cekindo = check_website_accessibility(domain)
        
        update_data.append({
            'range': f'C{i}:D{i}',
            'values': [[status, cekindo]]
        })

        # Tambahkan jeda untuk menghindari pembatasan API Google
        time.sleep(2)  # Jeda 2 detik per baris

    if update_data:
        # Update data dalam batch
        sheet.batch_update(update_data)
        print(f"{len(update_data)} rows updated in batch.")
        time.sleep(5)  # Jeda setelah batch update untuk menghindari batasan API

        # Apply formatting after updating the data
        for i in range(3, 3 + rows_to_check):
            status = sheet.cell(i, 3).value  # Get the status from the updated column C
            color = {"Aman": (0.5, 1, 0.5), "Blokir": (1, 0.5, 0.5), "Expired": (0.8, 0.8, 0.8)}
            rgb = color.get(status, (1, 1, 1))

            # Format the row background color based on the status
            sheet.format(f"C{i}:D{i}", {
                "backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}
            })

            print(f"Row {i} updated: Status={status}, Cekindo={cekindo}")

def update_check_time_and_date():
    """
    Perbarui waktu pemeriksaan terakhir di Google Sheet.
    """
    last_row = get_last_data_row()
    now = datetime.now()
    today = now.strftime("%y-%m-%d")
    current_time = now.strftime("%H:%M")

    sheet.update_cell(last_row + 2, 3, today)
    time.sleep(2)  # Jeda setelah memperbarui tanggal
    sheet.update_cell(last_row + 3, 3, current_time)
    time.sleep(2)  # Jeda setelah memperbarui waktu
    print(f"Waktu pemeriksaan diperbarui: {today} {current_time}")

def main():
    """
    Fungsi utama untuk menjalankan pembaruan status domain.
    """
    print("Memulai proses update...")
    update_status_and_cekindo()
    update_check_time_and_date()
    print("Proses selesai.")

main()
