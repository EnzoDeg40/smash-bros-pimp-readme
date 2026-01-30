
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

BASE_URL = "https://www.smashbros.com"
DOWNLOAD_FOLDER = "fighters"
MAX_FIGHTER_ID = 99
MAX_404 = 3  # On arrête après 3 images manquantes consécutives

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_fighter_name(page_url):
    """Récupère le nom du fighter depuis la page via la CSS."""
    try:
        html = requests.get(page_url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("link", rel="stylesheet", href=True):
            href = link["href"]
            if href.startswith("/assets_v2/css/fighter/"):
                # Récupère le nom du fighter depuis le nom du fichier CSS
                return href.split("/")[-1].replace(".css", "")
    except Exception as e:
        print(f"Erreur récupération fighter sur {page_url} : {e}")
    return None

def download_image(url, folder):
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, url.split("/")[-1])
        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Téléchargé : {filename}")
        return True
    except Exception as e:
        print(f"Erreur téléchargement {url} : {e}")
        return False

# --- MAIN ---
for fighter_id in range(1, MAX_FIGHTER_ID + 1):
    fighter_id_str = str(fighter_id).zfill(2)
    page_url = f"{BASE_URL}/fr_FR/fighter/{fighter_id_str}.html"

    fighter_name = get_fighter_name(page_url)
    if not fighter_name:
        print(f"Fighter {fighter_id_str} introuvable, skip")
        continue

    print(f"\nFighter {fighter_name} ({fighter_id_str})")

    folder_path = os.path.join(DOWNLOAD_FOLDER, fighter_name)
    consecutive_404 = 0
    img_index = 1

    while consecutive_404 < MAX_404:
        if img_index == 1:
            img_url = f"{BASE_URL}/assets_v2/img/fighter/{fighter_name}/main.png"
        else:
            img_url = f"{BASE_URL}/assets_v2/img/fighter/{fighter_name}/main{img_index}.png"
        success = download_image(img_url, folder_path)
        if not success:
            consecutive_404 += 1
        else:
            consecutive_404 = 0
        img_index += 1
