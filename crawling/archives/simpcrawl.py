import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL awal (dengan skema protokol)
#url = 'https://cia.cia88group.org/'
#url = 'https://opelgame.com'
#url = 'https://opeljitu.com'
#url = 'https://orisoriginal.com'
#url = 'https://bandartotovip.com'
#url = 'https://tokeasik.com'
#url = 'https://playsbo.fun'
url = 'https://tokemantap.com'
#url = 'https://tokesetia.com'

try:
    # Mengunduh konten halaman
    response = requests.get(url, timeout=10, verify=False)
    
    # Mencetak status kode HTTP
    print(f"Status Code: {response.status_code}")
    
    # Jika request berhasil, lanjutkan parsing
    if response.status_code == 200:
        # Parsing HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Mencari semua tautan di halaman
        links = [a['href'] for a in soup.find_all('a', href=True)]

        # Menampilkan daftar tautan
        print("Links found on the page:")
        for link in links:
            print(link)
    else:
        print("Failed to retrieve the page.")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
