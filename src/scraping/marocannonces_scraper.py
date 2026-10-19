"""
MarocAnnonces.com scraper - corrected selectors
IT category: /maroc/offres-emploi-domaine-informatique-multimedia-internet-b309.html
Job items: div.holder > h3 > a
Pagination: ?pge=X
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd


class MarocAnnoncesScraper:
    def __init__(self):
        self.base_url = "https://www.marocannonces.com"
        # IT/Multimedia/Internet domain filter on the job listings category
        self.list_url = (
            "https://www.marocannonces.com/maroc/"
            "offres-emploi-domaine-informatique-multimedia-internet-b309.html"
        )
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.marocannonces.com/',
        }

    def fetch_page(self, url, params=None):
        """Fetch page content with retries."""
        for attempt in range(3):
            try:
                time.sleep(random.uniform(1.5, 3.0))
                r = requests.get(url, headers=self.headers, params=params, timeout=20)
                if r.status_code == 200:
                    enc = r.apparent_encoding or 'utf-8'
                    return r.content.decode(enc, errors='replace')
                elif r.status_code in (404, 403):
                    print(f"[MarocAnnonces] HTTP {r.status_code} on {url}")
                    return None
            except Exception as e:
                print(f"[MarocAnnonces] Error fetching {url}: {e}")
        return None

    def get_job_links(self, max_pages=10):
        """Scrape listing pages. Job listings are in div.holder h3 a."""
        job_links = set()

        for page in range(1, max_pages + 1):
            url = self.list_url
            if page > 1:
                url = url + f"?pge={page}"
            print(f"[MarocAnnonces] Scraping listing page {page}/{max_pages}...")

            html = self.fetch_page(url)
            if not html:
                print(f"[MarocAnnonces] Failed to fetch page {page}. Stopping.")
                break

            soup = BeautifulSoup(html, 'html.parser')

            # Job items are inside div.holder > h3 > a
            holders = soup.select('div.holder h3 a')
            if not holders:
                # Fallback: any link containing /annonces/ in href
                holders = [
                    a for a in soup.find_all('a', href=True)
                    if 'annonce' in a['href'] and 'categorie' in a['href']
                ]

            if not holders:
                print(f"[MarocAnnonces] No job links on page {page}. Stopping.")
                break

            before = len(job_links)
            for a in holders:
                href = a.get('href', '')
                if href and not href.startswith('http'):
                    href = self.base_url + '/' + href.lstrip('/')
                if href:
                    job_links.add(href)

            added = len(job_links) - before
            print(f"[MarocAnnonces] Page {page}: +{added} new links (total={len(job_links)})")

        print(f"[MarocAnnonces] Total unique links: {len(job_links)}")
        return list(job_links)

    def parse_job_detail(self, url):
        """Parse a single MarocAnnonces job ad page."""
        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # -- Title (h1) --
        h1 = soup.find('h1')
        title = h1.text.strip() if h1 else ""
        if not title:
            h2 = soup.find('h2')
            title = h2.text.strip() if h2 else ""

        # -- Default values --
        company = city = region = contract_type = experience = education = ""
        salary = date_published = sector = function_ = ""
        country = "Maroc"

        # -- Parse <li> tags with "Label : Value" pattern --
        # MarocAnnonces uses plain <li> for structured metadata
        for li in soup.find_all('li'):
            txt = li.text.strip()
            if ' : ' not in txt:
                continue
            label, _, value = txt.partition(' : ')
            label = label.strip().lower()
            value = value.strip()

            if 'domaine' in label or 'secteur' in label:
                sector = value
            elif 'fonction' in label:
                function_ = value
            elif 'contrat' in label:
                contract_type = value
            elif 'entreprise' in label or 'soci' in label:
                if not company:
                    company = value
            elif 'salaire' in label or 'remun' in label:
                salary = value
            elif "niveau" in label and "tude" in label:
                education = value
            elif 'ville' in label:
                city = value
            elif 'publi' in label or 'date' in label:
                date_published = value
            elif 'exp' in label:
                experience = value

        # Sector fallback: use function if sector empty
        if not sector and function_:
            sector = function_

        # -- Description from .detail div --
        desc_el = soup.select_one('.detail, .description, .ad-body, #detail')
        if desc_el:
            description = desc_el.get_text(separator='\n').strip()
        else:
            # Fallback: body text
            body = soup.find('body')
            description = body.get_text(separator='\n').strip()[:5000] if body else ""

        description = re.sub(r'\n{3,}', '\n\n', description)
        description = re.sub(r' {2,}', ' ', description)
        description = re.sub(r'\r', '', description)

        return {
            'titre_poste': title,
            'entreprise': company,
            'ville': city,
            'region': city,
            'pays': country,
            'type_contrat': contract_type,
            'experience_demandee': experience,
            'etude_demandee': education,
            'salaire': salary,
            'date_publication': date_published,
            'secteur': sector,
            'description': description,
            'url': url,
            'source': 'MarocAnnonces',
        }

    def scrape(self, max_pages=10):
        """Run the MarocAnnonces scraper and return a DataFrame."""
        links = self.get_job_links(max_pages)
        jobs = []
        print(f"[MarocAnnonces] Parsing {len(links)} job detail pages...")
        for i, link in enumerate(links):
            safe_link = link.encode('ascii', errors='ignore').decode('ascii')
            print(f"[MarocAnnonces] [{i+1}/{len(links)}] {safe_link}")
            job = self.parse_job_detail(link)
            if job and job.get('titre_poste'):
                jobs.append(job)
        print(f"[MarocAnnonces] Done. {len(jobs)} valid jobs collected.")
        return pd.DataFrame(jobs)
