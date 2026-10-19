import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd

class EmploiMaScraper:
    def __init__(self):
        self.base_url = "https://www.emploi.ma"
        # Search page for IT / Web jobs
        self.search_url = "https://www.emploi.ma/recherche-jobs-maroc"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
        }

    def fetch_page(self, url, params=None):
        """Fetch page content with retries and timeout."""
        for attempt in range(3):
            try:
                time.sleep(random.uniform(1.5, 3.0))
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    return None
            except Exception as e:
                print(f"Error fetching {url}: {e}")
        return None

    def get_job_links(self, max_pages=15):
        """Scrape the main pages to find individual job detail links."""
        job_links = []
        for page in range(0, max_pages):
            # Emploi.ma uses page=X starting from 0 or 1. Let's send page=X
            params = {
                'key': 'informatique',
                'page': page
            }
            print(f"[Emploi.ma] Scraping search page {page+1}/{max_pages}...")
            html = self.fetch_page(self.search_url, params=params)
            if not html:
                break
            
            soup = BeautifulSoup(html, 'html.parser')
            # Look for job links containing '/offre-emploi-maroc/' or similar in href
            links = soup.find_all('a', href=True)
            
            page_links = []
            for link in links:
                href = link.get('href')
                # Check for job detail URL pattern
                if '/offre-emploi-maroc/' in href or 'offre-emploi-' in href:
                    if not href.startswith('http'):
                        href = self.base_url + href
                    # Make sure it's not a generic listing or category
                    if href not in page_links:
                        page_links.append(href)
            
            if not page_links:
                print(f"[Emploi.ma] No job links found on page {page+1}.")
                # If we don't find any links, we try category URL directly as fallback
                fallback_url = f"https://www.emploi.ma/recherche-jobs-maroc/informatique?page={page}"
                html = self.fetch_page(fallback_url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href')
                        if '/offre-emploi-maroc/' in href or 'offre-emploi-' in href:
                            if not href.startswith('http'):
                                href = self.base_url + href
                            page_links.append(href)
                
                if not page_links:
                    break
                    
            page_links = list(set(page_links))
            job_links.extend(page_links)
            print(f"[Emploi.ma] Found {len(page_links)} job links on page {page+1}.")
            
            # Check for next page indicator
            next_btn = soup.select('.pager-next, a[href*="page="]')
            if not next_btn:
                # If no next page links, stop
                break
                
        job_links = list(set(job_links))
        print(f"[Emploi.ma] Total unique job links collected: {len(job_links)}")
        return job_links

    def parse_job_detail(self, url):
        """Scrape and parse a single job offer detail page."""
        html = self.fetch_page(url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get Job Title
        title_el = soup.find('h1')
        title = title_el.text.strip() if title_el else ""
        if not title:
            title_el = soup.select_one('.job-ad-title, .title')
            title = title_el.text.strip() if title_el else ""
            
        # Get Company
        company = ""
        company_el = soup.select_one('.company-title, .company-name, .company')
        if company_el:
            company = company_el.text.strip().replace("Entreprise :", "").strip()
        if not company:
            # Look in the text for "Entreprise :"
            comp_match = re.search(r'Entreprise\s*:\s*([^\n]+)', soup.text, re.IGNORECASE)
            if comp_match:
                company = comp_match.group(1).strip()

        # Initialize default values
        city = ""
        region = ""
        country = "Maroc"
        contract_type = ""
        experience = ""
        education = ""
        salary = ""
        date_published = ""
        sector = ""
        
        # Parse table/details on page
        # Emploi.ma pages often have rows in a table or list
        # <tr><td class="field-label">Type de contrat :</td><td class="field-value">CDI</td></tr>
        labels = soup.select('.field-label, td, th, strong')
        for label in labels:
            text = label.text.strip()
            # Find next sibling or parent's sibling for value
            sibling = None
            if label.next_sibling:
                sibling = label.next_sibling.text.strip()
            
            if "Région de :" in text or "Ville :" in text or "Localisation :" in text:
                val = label.find_next('td') or label.find_next('span')
                city = val.text.strip() if val else (sibling if sibling else "")
            elif "Type de contrat :" in text:
                val = label.find_next('td') or label.find_next('span')
                contract_type = val.text.strip() if val else (sibling if sibling else "")
            elif "Expérience requise :" in text or "Niveau d'expérience :" in text:
                val = label.find_next('td') or label.find_next('span')
                experience = val.text.strip() if val else (sibling if sibling else "")
            elif "Niveau d'études :" in text or "Niveau d'étude requis :" in text:
                val = label.find_next('td') or label.find_next('span')
                education = val.text.strip() if val else (sibling if sibling else "")
            elif "Secteur d'activité :" in text:
                val = label.find_next('td') or label.find_next('span')
                sector = val.text.strip() if val else (sibling if sibling else "")
            elif "Salaire :" in text:
                val = label.find_next('td') or label.find_next('span')
                salary = val.text.strip() if val else (sibling if sibling else "")
                
        # Clean extracted fields
        city = re.sub(r'\s+', ' ', city).strip()
        contract_type = re.sub(r'\s+', ' ', contract_type).strip()
        experience = re.sub(r'\s+', ' ', experience).strip()
        education = re.sub(r'\s+', ' ', education).strip()
        sector = re.sub(r'\s+', ' ', sector).strip()

        # Date of publication
        date_match = re.search(r'\b\d{2}/\d{2}/\d{4}\b', soup.text)
        if date_match:
            date_published = date_match.group(0)

        # Full Description
        description_parts = []
        for sec in ['job-ad-description', 'job-description', 'post-description', 'details-offre', 'field-item']:
            sec_els = soup.select(f'.{sec}, #{sec}, [class*="{sec}"]')
            for el in sec_els:
                description_parts.append(el.text.strip())
                
        if not description_parts:
            body_el = soup.find('body')
            if body_el:
                description_parts.append(body_el.text.strip())
                
        description = "\n\n".join(description_parts)
        description = re.sub(r'\n+', '\n', description)
        description = re.sub(r' +', ' ', description)
        
        return {
            'titre_poste': title,
            'entreprise': company,
            'ville': city,
            'region': region if region else city,
            'pays': country,
            'type_contrat': contract_type,
            'experience_demandee': experience,
            'etude_demandee': education,
            'salaire': salary,
            'date_publication': date_published,
            'secteur': sector,
            'description': description,
            'url': url,
            'source': 'Emploi.ma'
        }

    def scrape(self, max_pages=15):
        """Main method to run the Emploi.ma scraper."""
        links = self.get_job_links(max_pages)
        jobs = []
        print(f"[Emploi.ma] Starting detail page parsing for {len(jobs)} offers...")
        for i, link in enumerate(links):
            print(f"[Emploi.ma] Parsing job {i+1}/{len(links)}: {link}")
            job = self.parse_job_detail(link)
            if job:
                jobs.append(job)
        return pd.DataFrame(jobs)
