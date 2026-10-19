"""
Rekrute.com scraper - corrected selectors (v2)
URL: https://www.rekrute.com/offres.html?s=3&p={page}&o=1
Detail page structure:
  - Title: h1
  - Company: img[title] containing 'Krunchy' or 'Feel Good' → text after ' - '
  - Fields: unlabeled <li> tags in order:
      [0] experience (e.g. "Intermédiaire (3 à 5 ans)")
      [1] city (e.g. "Casablanca et région - Maroc")
      [2] education (e.g. "Bac +2 Minimum - Autre")
      [3] contract (e.g. "CDI")
      [4] télétravail (optional)
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd

# Experience level keywords for classification hint
_EXP_KEYWORDS = [
    'débutant', 'junior', 'intermédiaire', 'confirmé', 'senior',
    'ans d', 'an d', 'ans d\'expérience', 'expérience requise',
    r'\d+\s*à\s*\d+\s*ans'
]
_CONTRACT_TYPES = ['cdi', 'cdd', 'stage', 'freelance', 'interim', 'intérim',
                   'alternance', 'apprentissage', 'vié']
_EDU_KEYWORDS = ['bac', 'master', 'licence', 'ingénieur', 'doctorat',
                 'dut', 'bts', 'école', 'formation']


class RekruteScraper:
    def __init__(self):
        self.base_url = "https://www.rekrute.com"
        self.list_url = "https://www.rekrute.com/offres.html"
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.rekrute.com/',
        }

    def fetch_page(self, url, params=None):
        """Fetch page with retries; returns properly decoded HTML string."""
        for attempt in range(3):
            try:
                time.sleep(random.uniform(1.5, 3.0))
                r = requests.get(url, headers=self.headers, params=params, timeout=20)
                if r.status_code == 200:
                    # Use apparent_encoding to handle latin/utf-8 correctly
                    enc = r.apparent_encoding or 'utf-8'
                    return r.content.decode(enc, errors='replace')
                elif r.status_code in (403, 404):
                    print(f"[Rekrute] HTTP {r.status_code} on {url}")
                    return None
            except Exception as e:
                print(f"[Rekrute] Error (attempt {attempt+1}): {e}")
        return None

    def get_job_links(self, max_pages=10):
        """Return unique IT job detail URLs from Rekrute."""
        job_links = set()
        for page in range(1, max_pages + 1):
            params = {'s': '3', 'p': str(page), 'o': '1'}
            print(f"[Rekrute] Listing page {page}/{max_pages}...")
            html = self.fetch_page(self.list_url, params=params)
            if not html:
                break

            soup = BeautifulSoup(html, 'html.parser')
            page_links = [
                a['href']
                for a in soup.find_all('a', href=True)
                if '/offre-emploi-' in a['href'] and '#' not in a['href']
            ]
            if not page_links:
                print(f"[Rekrute] No links on page {page}. Stopping.")
                break

            before = len(job_links)
            job_links.update(page_links)
            print(f"[Rekrute] Page {page}: +{len(job_links)-before} new (total={len(job_links)})")

        full_links = []
        for lnk in job_links:
            if not lnk.startswith('http'):
                lnk = self.base_url + lnk
            full_links.append(lnk)

        print(f"[Rekrute] Total unique links: {len(full_links)}")
        return full_links

    def _is_experience(self, text):
        t = text.lower()
        return any(re.search(p, t) for p in _EXP_KEYWORDS)

    def _is_contract(self, text):
        t = text.lower()
        return any(k in t for k in _CONTRACT_TYPES)

    def _is_education(self, text):
        t = text.lower()
        return any(k in t for k in _EDU_KEYWORDS)

    def _is_city(self, text):
        # City entries typically contain "Maroc" or known Moroccan cities
        return 'maroc' in text.lower() or 'casablanca' in text.lower()

    def parse_job_detail(self, url):
        """Parse a Rekrute job detail page."""
        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # -- Title --
        h1 = soup.find('h1')
        title = h1.text.strip() if h1 else ""

        # -- Company (from img title: "Entreprises X - CompanyName") --
        company = ""
        for img in soup.find_all('img', title=True):
            t = img.get('title', '').strip()
            if t and ' - ' in t and any(
                k in t for k in ['Krunchy', 'Feel Good', 'Love my Job']
            ):
                company = t.split(' - ', 1)[-1].strip()
                break
        # Fallback: look for company in text near "recrute"
        if not company:
            for img in soup.find_all('img', title=True):
                t = img.get('title', '').strip()
                if t and t != '' and 'Entreprises' not in t and 'Rekrute' not in t:
                    company = t.strip()
                    break

        # -- Fields from unlabeled <li> tags --
        # Rekrute detail page uses plain <li> tags (no class) for metadata
        city = experience = education = contract_type = ""
        country = "Maroc"
        salary = date_published = sector = ""

        # Collect all plain <li> texts (short ones, not nav items)
        li_texts = [
            li.get_text(separator=' ').strip()
            for li in soup.find_all('li')
            if li.get_text(separator=' ').strip()
            and len(li.get_text(separator=' ').strip()) < 200
            and not li.find('ul')  # skip nested lists
        ]

        for lt in li_texts:
            lt_clean = lt.strip()
            if not lt_clean:
                continue
            # Experience: e.g. "Intermédiaire (3 à 5 ans)", "Débutant", "Senior"
            if not experience and self._is_experience(lt_clean):
                # Remove the "- Autre" or "- Maroc" suffix if present
                experience = lt_clean.split(' - ')[0].strip()
            # Contract: e.g. "CDI", "CDD", "Stage"
            elif not contract_type and self._is_contract(lt_clean):
                contract_type = lt_clean.split(' - ')[0].strip()
            # Education: e.g. "Bac +2 Minimum - Autre"
            elif not education and self._is_education(lt_clean):
                education = lt_clean.split(' - ')[0].strip()
            # City: e.g. "Casablanca et région - Maroc"
            #   or "1 poste(s) sur Casablanca et région - Maroc"
            elif not city and self._is_city(lt_clean):
                # Strip leading "N poste(s) sur " prefix
                city = re.sub(r'^\d+\s+poste\(s\)\s+sur\s+', '', lt_clean, flags=re.I)
                # Strip " et région - Maroc" suffix
                city = re.sub(r'\s+et\s+r[ée]gion.*$', '', city, flags=re.I)
                city = re.sub(r'\s*-\s*Maroc\s*$', '', city, flags=re.I).strip()

        # -- Date --
        date_el = soup.select_one('time, .date, .post-date')
        if date_el:
            date_published = date_el.get('datetime', '') or date_el.text.strip()
        if not date_published:
            m = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', soup.text)
            if m:
                date_published = m.group(1)

        # -- Description --
        desc_parts = []
        for blc in soup.select('.blc'):
            txt = blc.text.strip()
            # Rekrute sections start with these headings
            if any(txt.startswith(h) for h in ['Entreprise', 'Poste', 'Profil', 'Culture', 'Missions']):
                desc_parts.append(txt)

        if desc_parts:
            description = "\n\n".join(desc_parts)
        else:
            desc_el = soup.select_one('.jobdescription, .post-content')
            if desc_el:
                description = desc_el.get_text(separator='\n').strip()
            else:
                body = soup.find('body')
                description = body.get_text(separator='\n').strip()[:6000] if body else ""

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
            'source': 'Rekrute',
        }

    def scrape(self, max_pages=10):
        """Run full Rekrute scrape and return DataFrame."""
        links = self.get_job_links(max_pages)
        jobs = []
        print(f"[Rekrute] Parsing {len(links)} detail pages...")
        for i, link in enumerate(links):
            print(f"[Rekrute] [{i+1}/{len(links)}] {link}")
            job = self.parse_job_detail(link)
            if job and job.get('titre_poste'):
                jobs.append(job)
        print(f"[Rekrute] Done. {len(jobs)} valid jobs.")
        return pd.DataFrame(jobs)
