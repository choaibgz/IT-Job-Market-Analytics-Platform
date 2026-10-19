import requests
from bs4 import BeautifulSoup
import sys

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

sites = {
    'Rekrute': 'https://www.rekrute.com/offres-emploi-informatique-electronique.html',
    'Emploi.ma': 'https://www.emploi.ma/recherche-jobs-maroc/informatique',
    'MarocAnnonces': 'https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-internet-b309.html'
}

for name, url in sites.items():
    print(f"Testing {name} at {url}...")
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {r.status_code}")
        print(f"Response Length: {len(r.text)} characters")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            print(f"Title: {soup.title.text.strip() if soup.title else 'No Title'}")
            # Show a snippet of the page
            print("First 200 chars of body:")
            body_text = soup.body.get_text() if soup.body else ""
            print(body_text.strip()[:200].replace('\n', ' '))
        else:
            print(f"Failed to fetch {name}")
    except Exception as e:
        print(f"Error connecting to {name}: {e}")
    print("-" * 50)
