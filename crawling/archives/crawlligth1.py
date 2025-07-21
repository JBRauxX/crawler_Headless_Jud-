import httpx
from bs4 import BeautifulSoup
import re
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_url(url):
    """Validasi format URL menggunakan regex."""
    regex = re.compile(
        r'^(?:http|https)://'
        r'(?:\S+(?::\S*)?@)?'
        r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6}'
        r'(?::\d{1,5})?(?:/[^/#?]*)?$', re.IGNORECASE)
    return re.match(regex, url) is not None

def check_website(url):
    """Memeriksa status HTTP, pengalihan, dan meta refresh dari sebuah URL."""
    try:
        # Tambahkan protokol jika tidak ada
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        # Validasi URL
        if not is_valid_url(url):
            logging.error("URL tidak valid. Mohon periksa kembali.")
            return

        logging.info(f"Memeriksa situs: {url}")
        
        # Membuat client HTTPX
        timeout = httpx.Timeout(connect=5, read=10)
        with httpx.Client(follow_redirects=True, verify=False, timeout=timeout) as client:
            response = client.get(url)
            status_code = response.status_code
            logging.info(f"Kode respon HTTP untuk {url}: {status_code}")

            # Status HTTP
            if status_code == 200:
                print(f"Situs {url} dapat diakses.")
            elif status_code in [403, 451]:
                print(f"Situs {url} diblokir (status code: {status_code}).")
            else:
                print(f"Situs {url} mengarah ke status: {status_code}.")

            # Periksa pengalihan
            if response.history:
                print(f"Situs {url} mengalami pengalihan ke {response.url}.")
            else:
                print(f"Tidak ada pengalihan untuk situs {url}.")

            # Analisis konten HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Periksa elemen penting
            title = soup.title.string if soup.title else "Tidak ada judul"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc['content'] if meta_desc else "Tidak ada deskripsi"
            print(f"Judul: {title}")
            print(f"Deskripsi: {description}")

            # Deteksi meta refresh
            meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if meta_refresh:
                content = meta_refresh.get('content', '')
                if 'url=' in content.lower():
                    redirect_url = content.split('url=')[1]
                    print(f"Meta refresh ditemukan, pengalihan ke: {redirect_url}")
                else:
                    print("Meta refresh ditemukan, tetapi tidak ada URL pengalihan.")
            else:
                print("Tidak ada meta refresh yang terdeteksi.")

            # Cetak potongan HTML (opsional)
            print("\nPotongan Konten HTML:")
            print(soup.prettify()[:500])  # Cetak hanya 500 karakter pertama
    
    except httpx.RequestError as e:
        logging.error(f"Gagal mengakses {url}: {str(e)}")
    except Exception as e:
        logging.error(f"Kesalahan tidak terduga: {str(e)}")

# Contoh penggunaan
check_website('tokemantap.com')
