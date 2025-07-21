import requests

def cek_status(url):
    try:
        response = requests.get(url, timeout=10)
        if "Nawala" in response.text or "Internet Sehat" in response.text:
            print(f"Situs {url} diblokir (konten mendeteksi blokir).")
        else:
            print(f"Situs {url} dapat diakses (Status: {response.status_code}).")
    except requests.exceptions.RequestException as e:
        print(f"Situs {url} mungkin diblokir (Error: {e}).")

cek_status("https://playsbo.fun")
