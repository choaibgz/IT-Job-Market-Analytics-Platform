"""Debug MarocAnnonces using the same selectors as the working scraper."""
import sys
sys.path.insert(0, '.')
import requests
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Referer': 'https://www.marocannonces.com/',
}

list_url = "https://www.marocannonces.com/maroc/offres-emploi-domaine-informatique-multimedia-internet-b309.html"
r_list = requests.get(list_url, headers=headers, timeout=20)
enc = r_list.apparent_encoding or 'utf-8'
soup_list = BeautifulSoup(r_list.content.decode(enc, errors='replace'), 'html.parser')

print(f"Status: {r_list.status_code}")
print(f"Total links: {len(soup_list.find_all('a', href=True))}")

# Use same selector as the working scraper
holders = soup_list.select('div.holder h3 a')
print(f"div.holder h3 a: {len(holders)}")

# Fallback: categorie/annonce links
fallback = [a for a in soup_list.find_all('a', href=True)
            if 'annonce' in a.get('href','') and 'categorie' in a.get('href','')]
print(f"Fallback (annonce in href): {len(fallback)}")

if fallback:
    detail_href = fallback[0]['href']
    detail_url = "https://www.marocannonces.com/" + detail_href.lstrip('/')
    print(f"\nDetail URL: {detail_url}")
    
    time.sleep(2)
    r_det = requests.get(detail_url, headers=headers, timeout=20)
    enc2 = r_det.apparent_encoding or 'utf-8'
    html = r_det.content.decode(enc2, errors='replace')
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\nH1: {soup.find('h1').text.strip() if soup.find('h1') else 'NONE'}")
    
    print("\n--- ALL <li> ---")
    for li in soup.find_all('li'):
        txt = li.text.strip()
        if txt and len(txt) < 200 and not li.find('ul'):
            print(f"  [{li.get('class','')}] '{txt[:100]}'")
    
    print("\n--- TABLE CELLS ---")
    for td in soup.find_all('td'):
        txt = td.text.strip()
        if txt and len(txt) < 200:
            print(f"  [{td.get('class','')}] '{txt[:100]}'")
    
    print("\n--- SPANS ---")
    for span in soup.find_all('span')[:50]:
        txt = span.text.strip()
        if txt and len(txt) < 150:
            print(f"  .{span.get('class','')} '{txt[:100]}'")
    
    print("\n--- KEY DIVs ---")
    for div in soup.find_all('div'):
        cls = ' '.join(div.get('class', []))
        if any(k in cls for k in ['info', 'detail', 'field', 'meta', 'attr', 'crit', 'prop', 'label']):
            txt = div.text.strip()[:120].replace('\n', ' ')
            print(f"  .{cls}: '{txt}'")
    
    print("\n--- BODY TEXT ---")
    print(soup.get_text()[:3000])
else:
    print("No IT job links found!")
    # Show all links for debugging
    all_links = [a['href'] for a in soup_list.find_all('a', href=True)]
    print(f"All link samples: {all_links[:20]}")
