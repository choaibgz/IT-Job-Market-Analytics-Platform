"""Targeted debug for MarocAnnonces + Rekrute detail page structure."""
import requests
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'fr-FR,fr;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
}

# ---- MarocAnnonces: scan all hrefs ----
print("=" * 60)
print("MAROCANNONCES - All href patterns")
print("=" * 60)

r = requests.get(
    "https://www.marocannonces.com/maroc/offres-emploi-informatique-multimedia-internet-b309.html",
    headers=headers, timeout=15
)
soup = BeautifulSoup(r.text, 'html.parser')
all_links = [a['href'] for a in soup.find_all('a', href=True)]
print(f"Total links on page: {len(all_links)}")

# Group by prefix pattern
from collections import Counter
prefixes = Counter()
for l in all_links:
    parts = l.split('/')
    prefix = '/'.join(parts[:3]) if len(parts) >= 3 else l
    prefixes[prefix] += 1

print("\nLink prefix frequency:")
for prefix, count in prefixes.most_common(20):
    print(f"  {count:3d}x  {prefix}")

# Look for patterns that might be job listings
print("\nLinks containing 'annonce' or 'emploi':")
for l in all_links:
    if 'annonce' in l.lower() or 'offre' in l.lower():
        print(f"  {l}")

# Find <li> and <article> elements
print(f"\nTotal <li> tags: {len(soup.find_all('li'))}")
print(f"Total <article> tags: {len(soup.find_all('article'))}")
print(f"Total <div class=...> with 'item' in class: {len(soup.select('[class*=item]'))}")
print(f"Total <div class=...> with 'ann' in class: {len(soup.select('[class*=ann]'))}")
print(f"Total <h2> tags: {len(soup.find_all('h2'))}")
print(f"Total <h3> tags: {len(soup.find_all('h3'))}")

# Show first 10 h2/h3 and their parent
print("\nFirst 10 h2/h3 tags:")
for tag in (soup.find_all('h2') + soup.find_all('h3'))[:10]:
    print(f"  <{tag.name}> '{tag.text.strip()[:60]}' parent={tag.parent.name} parent_class={tag.parent.get('class','')}")

# ---- Rekrute: check correct IT category URL ----
print("\n" + "=" * 60)
print("REKRUTE - Validate s=3 is IT jobs")
print("=" * 60)

time.sleep(2)
r2 = requests.get("https://www.rekrute.com/offres.html?s=3&p=1&o=1", headers=headers, timeout=15)
soup2 = BeautifulSoup(r2.text, 'html.parser')
# Get all job links (no duplicates, no #matching4K)
links2 = list(set([
    a['href'] for a in soup2.find_all('a', href=True)
    if '/offre-emploi-' in a.get('href', '') and '#' not in a.get('href', '')
]))
print(f"Clean job links found: {len(links2)}")
print(f"Sample: {links2[:5]}")

# Now check pagination - what does page 2 look like?
time.sleep(2)
r3 = requests.get("https://www.rekrute.com/offres.html?s=3&p=2&o=1", headers=headers, timeout=15)
soup3 = BeautifulSoup(r3.text, 'html.parser')
links3 = list(set([
    a['href'] for a in soup3.find_all('a', href=True)
    if '/offre-emploi-' in a.get('href', '') and '#' not in a.get('href', '')
]))
print(f"\nPage 2 clean job links: {len(links3)}")

# Check a Rekrute detail page structure
if links2:
    detail_url = "https://www.rekrute.com" + links2[0]
    print(f"\n--- Rekrute Detail Page: {detail_url} ---")
    time.sleep(2)
    r_detail = requests.get(detail_url, headers=headers, timeout=15)
    soup_d = BeautifulSoup(r_detail.text, 'html.parser')
    print(f"Status: {r_detail.status_code}")
    
    # Find title
    h1 = soup_d.find('h1')
    print(f"H1: {h1.text.strip() if h1 else 'Not found'}")
    
    # Find company
    company_candidates = soup_d.select('.info-wrapper, .company-info, .company, .recruteur, img[title]')
    for c in company_candidates[:5]:
        print(f"Company candidate ({c.name}.{c.get('class','')}): {c.text.strip()[:60] if c.text else c.get('title','')}")
    
    # Find info list items
    lis = soup_d.select('li')
    print(f"\nTotal <li> tags in detail: {len(lis)}")
    for li in lis[:20]:
        txt = li.text.strip()
        if any(k in txt for k in ['Région', 'Ville', 'Contrat', 'Expérience', 'Secteur', 'Salaire', 'Fonction']):
            print(f"  [INFO LI] {txt[:100]}")
    
    # Find spans with key labels
    for span in soup_d.find_all('span')[:50]:
        txt = span.text.strip()
        if any(k in txt for k in ['Région', 'Ville', 'Contrat', 'Expérience', 'Secteur', 'Salaire', 'Fonction']):
            print(f"  [SPAN] {txt[:100]}")
