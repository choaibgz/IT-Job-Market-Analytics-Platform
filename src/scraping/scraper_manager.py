"""
Scraper Manager - orchestrates all scrapers, handles caching and merging.
Sources: Rekrute (IT category s=3) + MarocAnnonces (Informatique domain)
"""
import os
import json
import hashlib
import time
import pandas as pd
from datetime import datetime

from src.scraping.rekrute_scraper import RekruteScraper
from src.scraping.marocannonces_scraper import MarocAnnoncesScraper

RAW_DATA_DIR = os.path.join("data", "raw")
CACHE_DIR = os.path.join("data", "cache")
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(source_name):
    key = hashlib.md5(source_name.encode()).hexdigest()[:8]
    return os.path.join(CACHE_DIR, f"{source_name.lower()}_{key}.json")


def _load_cache(source_name):
    path = _cache_path(source_name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[Cache] Loaded {len(data)} records for '{source_name}'.")
        return pd.DataFrame(data)
    return None


def _save_cache(source_name, df):
    path = _cache_path(source_name)
    df.to_json(path, orient='records', force_ascii=False, indent=2)
    print(f"[Cache] Saved {len(df)} records for '{source_name}' -> {path}")
    return df


def run_scraper(name, scraper_instance, max_pages, use_cache=True):
    """Run a single scraper with optional file-based caching."""
    if use_cache:
        cached = _load_cache(name)
        if cached is not None and not cached.empty:
            return cached

    print(f"\n{'='*60}")
    print(f"  Running scraper: {name}")
    print(f"{'='*60}")
    try:
        df = scraper_instance.scrape(max_pages=max_pages)
        if df is not None and not df.empty:
            _save_cache(name, df)
            return df
        else:
            print(f"[Warning] {name} returned 0 records.")
            return pd.DataFrame()
    except Exception as e:
        print(f"[Error] {name} scraper failed: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def main(use_cache=True, max_pages_rekrute=8, max_pages_ma=8):
    """Main orchestrator: run all scrapers and merge results."""
    all_dfs = []

    # 1. Rekrute (IT sector, s=3)
    rekrute_df = run_scraper(
        'Rekrute', RekruteScraper(),
        max_pages=max_pages_rekrute, use_cache=use_cache
    )
    if not rekrute_df.empty:
        all_dfs.append(rekrute_df)
        print(f"\n[Manager] Rekrute: {len(rekrute_df)} jobs collected.")

    time.sleep(3)

    # 2. MarocAnnonces (Informatique / Multimedia / Internet domain)
    ma_df = run_scraper(
        'MarocAnnonces', MarocAnnoncesScraper(),
        max_pages=max_pages_ma, use_cache=use_cache
    )
    if not ma_df.empty:
        all_dfs.append(ma_df)
        print(f"[Manager] MarocAnnonces: {len(ma_df)} jobs collected.")

    if not all_dfs:
        print("\n[ERROR] All scrapers returned 0 records. Check connectivity.")
        return pd.DataFrame()

    # Merge
    combined = pd.concat(all_dfs, ignore_index=True)
    print(f"\n[Manager] Total raw records before dedup: {len(combined)}")

    # Deduplicate: by URL first, then by (title + company)
    combined.drop_duplicates(subset=['url'], inplace=True)
    combined.drop_duplicates(
        subset=['titre_poste', 'entreprise'], keep='first', inplace=True
    )
    combined.reset_index(drop=True, inplace=True)
    print(f"[Manager] Records after deduplication: {len(combined)}")

    # Save timestamped + latest
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(RAW_DATA_DIR, f"jobs_raw_{ts}.csv")
    latest_path = os.path.join(RAW_DATA_DIR, "jobs_raw_latest.csv")
    combined.to_csv(output_path, index=False, encoding='utf-8-sig')
    combined.to_csv(latest_path, index=False, encoding='utf-8-sig')

    print(f"\n[Manager] Saved {len(combined)} jobs -> {output_path}")
    print(f"[Manager] Latest snapshot -> {latest_path}")

    print("\n--- Source breakdown ---")
    print(combined['source'].value_counts().to_string())
    print("\n--- Columns ---")
    print(list(combined.columns))

    return combined


if __name__ == '__main__':
    main(use_cache=True)
