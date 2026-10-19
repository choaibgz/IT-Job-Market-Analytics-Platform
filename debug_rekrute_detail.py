"""Deep-dive debug of Rekrute detail page structure."""
import requests
from bs4 import BeautifulSoup
import chardet
import time

headers = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.rekrute.com/',
}

# Get a real IT job link from Rekrute
r = requests.get("https://www.rekrute.com/offres.html?s=3&p=1&o=1", headers=headers, timeout=20)
soup_list = BeautifulSoup(r.content, 'html.parser')
links = [
    a['href'] for a in soup_list.find_all('a', href=True)
    if '/offre-emploi-' in a['href'] and '#' not in a['href']
]
print(f"Links on listing page: {len(links)}")
detail_url = "https://www.rekrute.com" + links[0]
print(f"Testing detail: {detail_url}\n")

time.sleep(2)

# Fetch with raw bytes to detect encoding
r2 = requests.get(detail_url, headers=headers, timeout=20)
raw_bytes = r2.content

# Detect encoding
detected = chardet.detect(raw_bytes)
print(f"Detected encoding: {detected}")
print(f"Response encoding: {r2.encoding}")
print(f"Apparent encoding: {r2.apparent_encoding}")

# Parse with detected encoding
enc = r2.apparent_encoding or 'utf-8'
html = raw_bytes.decode(enc, errors='replace')
soup = BeautifulSoup(html, 'html.parser')

print(f"\nTitle (h1): {soup.find('h1').text.strip() if soup.find('h1') else 'NOT FOUND'}")

# --- Company ---
print("\n--- COMPANY CANDIDATES ---")
for img in soup.find_all('img', title=True)[:10]:
    print(f"  img[title]: '{img['title']}'  class={img.get('class','')}")

for sel in ['.company', '.entreprise', '.recruteur', 'a.company', 'h2.company',
            '[itemprop=name]', '.info-wrapper', '.recruiter-info']:
    els = soup.select(sel)
    if els:
        print(f"  '{sel}': '{els[0].text.strip()[:60]}'")

# --- Structured fields ---
print("\n--- ALL <li> CONTENT ---")
for li in soup.find_all('li'):
    txt = li.text.strip()
    if txt and len(txt) < 150:
        print(f"  <li> [{li.get('class','')}]: '{txt[:100]}'")

# --- Spans and strongs ---
print("\n--- STRONGS & SPANS WITH LABELS ---")
for tag in soup.select('strong, span, label'):
    txt = tag.text.strip()
    if any(k in txt for k in ['Région', 'Ville', 'Contrat', 'Expérience', 'Secteur',
                               'Formation', 'Salaire', 'Poste', 'Fonction']):
        parent = tag.parent
        sibling = tag.next_sibling
        print(f"  <{tag.name}>[{tag.get('class','')}]: '{txt}' | parent={parent.name}[{parent.get('class','')}]")
        if sibling:
            print(f"     next_sibling: '{str(sibling).strip()[:60]}'")

# --- DL / DT / DD ---
print("\n--- DL/DT/DD PAIRS ---")
for dt in soup.select('dt'):
    dd = dt.find_next_sibling('dd')
    print(f"  DT: '{dt.text.strip()[:60]}' | DD: '{dd.text.strip()[:60] if dd else 'N/A'}'")

# --- Tables ---
print("\n--- TABLE ROWS ---")
for tr in soup.select('tr')[:20]:
    tds = [td.text.strip() for td in tr.select('td, th')]
    if tds:
        print(f"  TR: {tds[:4]}")

# --- Classes containing 'info' or 'detail' or 'post' ---
print("\n--- KEY DIV CLASSES ---")
for div in soup.find_all('div')[:80]:
    cls = div.get('class', [])
    cls_str = ' '.join(cls)
    if any(k in cls_str for k in ['info', 'detail', 'post', 'job', 'desc', 'content', 'field', 'side']):
        txt_preview = div.text.strip()[:80].replace('\n', ' ')
        print(f"  div.{cls_str}: '{txt_preview}'")

# --- Check charset meta tag ---
meta_charset = soup.find('meta', charset=True) or soup.find('meta', {'http-equiv': 'Content-Type'})
print(f"\nMeta charset: {meta_charset}")
