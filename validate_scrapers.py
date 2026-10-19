"""Quick validation: test parsing of 1 detail page per scraper."""
import sys
sys.path.insert(0, '.')

from src.scraping.rekrute_scraper import RekruteScraper
from src.scraping.marocannonces_scraper import MarocAnnoncesScraper

print("=" * 60)
print("VALIDATION v2")
print("=" * 60)

# --- REKRUTE ---
print("\n--- REKRUTE ---")
r = RekruteScraper()
links = r.get_job_links(max_pages=1)
print(f"Links: {len(links)}")
if links:
    job = r.parse_job_detail(links[0])
    if job:
        for k, v in job.items():
            if k != 'description':
                print(f"  {k}: {repr(v)}")
        print(f"  description length: {len(job['description'])} chars")
        print(f"  description snippet: {job['description'][:200]}")
    else:
        print("  FAILED to parse detail!")

# --- MAROCANNONCES ---
print("\n--- MAROCANNONCES ---")
ma = MarocAnnoncesScraper()
ma_links = ma.get_job_links(max_pages=1)
print(f"Links: {len(ma_links)}")
if ma_links:
    job_ma = ma.parse_job_detail(ma_links[0])
    if job_ma:
        for k, v in job_ma.items():
            if k != 'description':
                print(f"  {k}: {repr(v)}")
        print(f"  description length: {len(job_ma['description'])} chars")
    else:
        print("  FAILED to parse detail!")

print("\n[OK] Validation complete.")
