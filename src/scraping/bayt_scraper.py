"""
Bayt.com Morocco IT job scraper
URL: https://www.bayt.com/fr/maroc/jobs/it-jobs/
Bayt uses a clean HTML listing that is accessible.
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd


class BaytScraper:
    def __init__(self):
        self.base_url = "https://www.bayt.com"
        self.list_url = "https://www.bayt.com/fr/maroc/jobs/it-jobs/"
        self.headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept-Language': 'fr-FR,fr;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.bayt.com/',
        }

    def fetch_page(self, url):
        """Fetch page content with retries."""
        for attempt in range(3):
            try:
                time.sleep(random.uniform(1.5, 3.0))
                r = requests.get(url, headers=self.headers, timeout=20)
                if r.status_code == 200:
                    return r.text
                elif r.status_code in (403, 404):
                    print(f"[Bayt] HTTP {r.status_code} on {url}")
                    return None
            except Exception as e:
                print(f"[Bayt] Error fetching {url}: {e}")
        return None

    def get_job_links(self, max_pages=5):
        """Scrape job listing pages for IT jobs in Morocco."""
        job_links = set()
        base_list = self.list_url

        for page in range(1, max_pages + 1):
            if page == 1:
                url = base_list
            else:
                url = base_list + f"?page={page}"

            print(f"[Bayt] Scraping listing page {page}/{max_pages}...")
            html = self.fetch_page(url)
            if not html:
                break

            soup = BeautifulSoup(html, 'html.parser')

            # Bayt job cards: li[data-js-aid] or .media-heading a
            links = soup.select('li[data-js-aid] h2 a, .media-heading a, h3.jb-title a')

            if not links:
                # Generic fallback: any /fr/maroc/jobs/*-job link
                links = [
                    a for a in soup.find_all('a', href=True)
                    if re.search(r'/fr/maroc/jobs/[^/]+-job-\d+', a.get('href', ''))
                ]

            if not links:
                print(f"[Bayt] No job links on page {page}. Stopping.")
                break

            before = len(job_links)
            for a in links:
                href = a.get('href', '')
                if href and not href.startswith('http'):
                    href = self.base_url + href
                if href:
                    job_links.add(href)

            added = len(job_links) - before
            print(f"[Bayt] Page {page}: +{added} new links (total={len(job_links)})")

        print(f"[Bayt] Total unique links: {len(job_links)}")
        return list(job_links)

    def parse_job_detail(self, url):
        """Parse a single Bayt job detail page."""
        html = self.fetch_page(url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        # -- Title --
        h1 = soup.find('h1')
        title = h1.text.strip() if h1 else ""

        # -- Company --
        company = ""
        for selector in ['.at-tag-employer', 'span[itemprop="name"]', '.company-name']:
            el = soup.select_one(selector)
            if el:
                company = el.text.strip()
                break

        # -- Location --
        city = "Maroc"
        for selector in ['.at-tag-location', '[itemprop="addressLocality"]', '.location']:
            el = soup.select_one(selector)
            if el:
                city = el.text.strip()
                break

        contract_type = experience = education = salary = ""
        date_published = sector = ""
        country = "Maroc"

        # -- Structured DL/DT/DD blocks --
        dts = soup.select('dt')
        for dt in dts:
            label = dt.text.strip()
            dd = dt.find_next_sibling('dd')
            value = dd.text.strip() if dd else ""
            if re.search(r'[Cc]ontrat|[Tt]ype', label):
                contract_type = value
            elif re.search(r'[Ee]xp[eé]rience', label):
                experience = value
            elif re.search(r'[Ff]ormation|[Ee]tude|[Dd]ipl[oô]me', label):
                education = value
            elif re.search(r'[Ss]alaire|[Rr][eé]mun', label):
                salary = value
            elif re.search(r'[Ss]ecteur|[Ii]ndustrie', label):
                sector = value

        # -- Date --
        date_el = soup.select_one('time, [itemprop="datePosted"]')
        if date_el:
            date_published = date_el.get('datetime', '') or date_el.text.strip()

        # -- Description --
        desc_el = soup.select_one('[itemprop="description"], .jb-description, #j-desc')
        if desc_el:
            description = desc_el.get_text(separator='\n').strip()
        else:
            body = soup.find('body')
            description = body.get_text(separator='\n').strip()[:5000] if body else ""

        description = re.sub(r'\n{3,}', '\n\n', description)
        description = re.sub(r' {2,}', ' ', description)

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
            'source': 'Bayt',
        }

    def scrape(self, max_pages=5):
        """Run the Bayt Morocco scraper and return a DataFrame."""
        links = self.get_job_links(max_pages)
        jobs = []
        print(f"[Bayt] Parsing {len(links)} job detail pages...")
        for i, link in enumerate(links):
            print(f"[Bayt] [{i+1}/{len(links)}] {link}")
            job = self.parse_job_detail(link)
            if job and job.get('titre_poste'):
                jobs.append(job)
        print(f"[Bayt] Done. {len(jobs)} valid jobs collected.")
        return pd.DataFrame(jobs)
