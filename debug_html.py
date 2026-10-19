"""Debug script to inspect actual HTML structure of working sites."""
import requests
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
}

# --- 1. Test Rekrute with new URL ---
print("=" * 60)
print("REKRUTE - Testing new URLs")
print("=" * 60)

rekrute_urls = [
    "https://www.rekrute.com/offres.html?s=3&p=1&o=1",  # Category 3 = IT
    "https://www.rekrute.com/offres/emploi/informatique-electronique.html",
    "https://www.rekrute.com/offres.html",
]

for url in rekrute_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"URL: {url}")
        print(f"Status: {r.status_code} | Length: {len(r.text)} chars")
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Try to find job links
            all_links = soup.find_all('a', href=True)
            job_links = [a['href'] for a in all_links if '/offre-emploi-' in a.get('href', '') or '/emploi/' in a.get('href', '')]
            print(f"  -> Potential job links: {len(job_links)}")
            if job_links:
                print(f"  -> Sample: {job_links[:3]}")
            # Print title tags of anchors to understand structure
            print(f"  -> Page title: {soup.title.text.strip() if soup.title else 'N/A'}")
        print()
    except Exception as e:
        print(f"Error: {e}\n")
    time.sleep(2)

# --- 2. Inspect MarocAnnonces structure ---
print("=" * 60)
print("MAROCANNONCES - Inspect HTML structure")
print("=" * 60)

ma_url = "https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-internet-b309.html"
r = requests.get(ma_url, headers=headers, timeout=15)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    print(f"Status: 200 | Length: {len(r.text)}")
    
    # Find all links on page
    all_a = soup.find_all('a', href=True)
    job_links = [a['href'] for a in all_a if '/maroc/annonces/' in a.get('href', '')]
    print(f"Links with /maroc/annonces/: {len(job_links)}")
    print(f"Sample: {job_links[:5]}")
    
    # Check for listing items
    items = soup.select('li.holder')
    print(f"\n'li.holder' items: {len(items)}")
    
    items2 = soup.select('.ann-title')
    print(f"'.ann-title' items: {len(items2)}")
    
    items3 = soup.select('h2.ann-title')
    print(f"'h2.ann-title' items: {len(items3)}")
    
    # Show raw portion of html to understand structure
    print("\n--- RAW HTML SNIPPET (first 3000 chars after body tag) ---")
    body = soup.find('body')
    if body:
        # Find the listings section
        main_content = str(body)[:5000]
        print(main_content)

# --- 3. Test Rekrute with session / cookies ---
print("\n" + "=" * 60)
print("REKRUTE - Session test")
print("=" * 60)

session = requests.Session()
session.headers.update(headers)

# First hit homepage to get cookies
r0 = session.get("https://www.rekrute.com/", timeout=15)
print(f"Homepage: {r0.status_code}")
time.sleep(2)

r1 = session.get("https://www.rekrute.com/offres.html?s=3&p=1&o=1", timeout=15)
print(f"IT jobs page: {r1.status_code} | Length: {len(r1.text)}")
if r1.status_code == 200:
    soup = BeautifulSoup(r1.text, 'html.parser')
    print(f"Title: {soup.title.text.strip() if soup.title else 'N/A'}")
    links = soup.find_all('a', href=True)
    job_links = [a['href'] for a in links if '/offre-emploi-' in a.get('href', '')]
    print(f"Job links found: {len(job_links)}")
    if job_links:
        print(f"Sample: {job_links[:3]}")
    # Show body text snippet
    print(f"Body text snippet: {soup.get_text()[:500]}")
