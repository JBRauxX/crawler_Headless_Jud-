import httpx
from bs4 import BeautifulSoup

def check_website(url):
    try:
        # Tambahkan 'http://' jika protokol tidak ada
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        with httpx.Client(follow_redirects=True, verify=False) as client:
            response = client.get(url, timeout=10)
            status_code = response.status_code
            print(f"Kode respon HTTP untuk {url}: {status_code}")
            
            if status_code == 200:
                print(f"Situs {url} dapat diakses.")
            elif status_code in [403, 451]:
                print(f"Situs {url} diblokir (status code: {status_code}).")
            else:
                print(f"Situs {url} mengarah ke status: {status_code}.")
            
            # Periksa jika ada pengalihan
            if response.history:
                print(f"Situs {url} mengalami pengalihan ke {response.url}.")
            else:
                print(f"Tidak ada pengalihan untuk situs {url}.")
            
            # Analisis konten HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
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

            # Cetak HTML yang didapat (opsional)
            print("\nKonten HTML yang diperoleh:")
            print(soup.prettify())
    
    except httpx.RequestError as e:
        print(f"Gagal mengakses {url}: {str(e)}")
    except Exception as e:
        print(f"Kesalahan tidak terduga: {str(e)}")

# Contoh penggunaan
check_website('tokemantap.com')
