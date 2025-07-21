import gspread
from oauth2client.service_account import ServiceAccountCredentials
import httpx
from datetime import datetime
import urllib3

# Konfigurasi Google Sheets API
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_KEY = '1PuWqIQg2YxKSSV_c3OA3KOtLrb35zGSLkktE_lBU3wo'

# Autentikasi ke Google Sheets
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet("OPEL")

def is_isp_block_page(html_content):
    """
    Deteksi apakah halaman yang diakses merupakan halaman blokir ISP.
    """
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
        except httpx.RequestError:
            continue
    return "Expired", "Tidak Ditemukan"

def get_last_data_row():
    """
    Mengambil baris terakhir dengan data valid di kolom A.
    Berhenti pada baris pertama yang kosong.
    """
    column_a_values = sheet.col_values(1)  # Ambil semua nilai di kolom A
    for i, value in enumerate(column_a_values):
        if not value:  # Berhenti saat menemukan baris kosong
            return i  # Mengembalikan indeks baris terakhir yang valid
    return len(column_a_values)  # Jika tidak ada nilai kosong

def update_status_and_cekindo():
    """
    Perbarui status dan cekindo untuk setiap domain dalam Google Sheet menggunakan pewarnaan berdasarkan status.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    last_row = get_last_data_row()  # Baris terakhir dengan data di kolom A

    update_data = []  # Menyimpan data yang akan diperbarui dalam batch

    for i in range(3, last_row + 1):  # Mulai dari baris 3 hingga baris terakhir
        link = sheet.cell(i, 2).value  # Ambil nilai dari kolom B
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

    if update_data:
        try:
            # Update data dalam batch
            sheet.batch_update(update_data)

            # Apply formatting after updating the data
            for i in range(3, last_row + 1):
                status = sheet.cell(i, 3).value  # Get the status from the updated column C
                # Warna berdasarkan status
                color = {
                    "Aman": (0.5, 1, 0.5),  # Hijau
                    "Blokir": (1, 0.5, 0.5),  # Merah
                    "Expired": (0.8, 0.8, 0.8)  # Abu-abu
                }
                rgb = color.get(status, (1, 1, 1))  # Default putih jika status tidak terdefinisi

                # Format warna background berdasarkan status
                sheet.format(f'C{i}:D{i}', {
                    "backgroundColor": {"red": rgb[0], "green": rgb[1], "blue": rgb[2]}
                })
                print(f"Row {i} updated: Status={status}, Cekindo={cekindo}")
        except gspread.exceptions.APIError as e:
            print(f"Error during batch update: {e}")

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

def main():
    """
    Fungsi utama untuk menjalankan pembaruan status domain.
    """
    print("Memulai proses update...")
    update_status_and_cekindo()
    update_check_time_and_date()
    print("Proses selesai.")

main()
