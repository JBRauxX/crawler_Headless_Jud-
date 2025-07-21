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
sheet = gc.open_by_key(SPREADSHEET_KEY).worksheet("TOKE")

def is_isp_block_page(html_content, domain):
    """
    Deteksi apakah halaman yang diakses merupakan halaman blokir ISP.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Cek meta refresh
    meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
    if meta_refresh:
        content = meta_refresh.get('content', '').lower()
        if 'blockpage' in content or 'block' in content:
            print(f"Terdeteksi meta refresh ke blockpage: {content}")
            return True

    # Cek konten kosong atau minimal
    body = soup.find('body')
    if body:
        body_text = body.get_text(strip=True)
        if len(body_text) < 50:
            print("Terdeteksi body kosong atau minimal")
            return True

    # Cek domain blockpage yang umum
    known_block_domains = ['blockpage', 'internetpositif', 'nawala', 'trustpositif']
    page_links = [a.get('href', '').lower() for a in soup.find_all('a')]
    for link in page_links:
        if any(block_domain in link for block_domain in known_block_domains):
            print(f"Terdeteksi link ke domain pemblokiran: {link}")
            return True

    return False

def check_website_accessibility(domain):
    """
    Periksa aksesibilitas website dan deteksi apakah halaman blokir ISP muncul.
    """
    urls_to_try = [f"https://{domain}", f"http://{domain}"]
    
    for url in urls_to_try:
        try:
            with httpx.Client(verify=False, timeout=30.0, follow_redirects=True) as client:
                response = client.get(url)

                if response.status_code == 200:
                    if is_isp_block_page(response.text, domain):
                        print(f"Website {domain} terdeteksi sebagai halaman blokir")
                        return "Blokir", "nawala"
                    
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' in content_type:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        if soup.find():
                            body = soup.find('body')
                            if body and len(body.get_text(strip=True)) > 50:
                                print(f"Website {domain} berhasil diakses dengan konten valid")
                                return "Aman", "Bisa Di Akses"
        except Exception as e:
            print(f"Error mencoba {url}: {str(e)}")
    
    return "Blokir", "nawala"

def get_last_data_row():
    """
    Ambil nomor baris terakhir dengan data pada Google Sheet.
    """
    col_values = sheet.col_values(2)
    return len(col_values)

def update_status_and_cekindo():
    """
    Perbarui status dan cekindo untuk setiap domain dalam Google Sheet.
    """
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    last_row = get_last_data_row()
    
    for i in range(3, last_row + 1):
        link = sheet.cell(i, 2).value
        if not link:
            print(f"Row {i} skipped: No link found.")
            continue

        domain = link.replace("https://", "").replace("http://", "").split("/")[0]
        print(f"\nMemeriksa domain: {domain}")
        status, cekindo = check_website_accessibility(domain)
        
        sheet.update_cell(i, 3, status)
        sheet.update_cell(i, 4, cekindo)
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
