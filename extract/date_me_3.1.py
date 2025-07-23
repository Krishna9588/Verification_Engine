# C:/Users/propl/PycharmProjects/rook_dont/extract/date_me_3.py

import requests
import json
import re
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datefinder import find_dates
from datetime import datetime, date
from typing import Optional, Tuple

# --- Configuration Constants ---
# A more realistic User-Agent helps prevent getting blocked by websites.
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
REQUEST_TIMEOUT = 30  # Increased timeout for slower sites.
MAX_FUTURE_YEAR_OFFSET = 1 # Allow for dates in the next year.


# --- Private Helper Functions (Largely the same, but with robust checks) ---

def _parse_and_get_date(date_string: str) -> Optional[date]:
    """Safely parses a string and returns only the date part."""
    if not date_string:
        return None
    try:
        dt_object = parse(date_string, fuzzy=True)
        # Sanity check the year to avoid parsing version numbers or irrelevant numbers
        if 2000 < dt_object.year <= datetime.now().year + MAX_FUTURE_YEAR_OFFSET:
            return dt_object.date()
        return None
    except (ValueError, TypeError, OverflowError):
        return None

def _find_date_in_url(url: str) -> Optional[date]:
    """Step 1: Find a plausible date within the URL string."""
    # Use find_dates which is more powerful than a simple regex
    found_dates = list(find_dates(url))
    if found_dates:
        return _parse_and_get_date(found_dates[0].isoformat())
    return None

def _find_date_in_metadata(soup: BeautifulSoup) -> Tuple[Optional[date], Optional[str]]:
    """Step 2: Search structured metadata (JSON-LD, meta tags). This is highly reliable."""
    # JSON-LD
    json_ld_keys = ['datePublished', 'dateModified', 'publishedDate', 'dateCreated', 'uploadDate']
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            for key in json_ld_keys:
                if dt := _parse_and_get_date(data.get(key)):
                    return dt, f"json-ld:{key}"
        except (json.JSONDecodeError, TypeError):
            continue

    # Meta Tags
    meta_selectors = {
        "meta[property='article:modified_time']": "meta_tag",
        "meta[property='article:published_time']": "meta_tag",
        "meta[name='date']": "meta_tag",
        "meta[name='pubdate']": "meta_tag",
    }
    for selector, method in meta_selectors.items():
        if tag := soup.select_one(selector):
            if dt := _parse_and_get_date(tag.get('content')):
                return dt, method
    return None, None

def _find_date_in_visible_text(soup: BeautifulSoup) -> Optional[date]:
    """Step 3: Searches for dates in specific, high-probability HTML tags."""
    # Prioritize specific tags that are semantically for dates
    date_selectors = ['time[datetime]', '[class*="date"]', '[class*="publish"]', '[class*="timestamp"]']
    for selector in date_selectors:
        for tag in soup.select(selector):
            # Prioritize the 'datetime' attribute if it exists
            tag_text = tag.get('datetime', '') or tag.get_text()
            if dt := _parse_and_get_date(tag_text):
                return dt
    return None

def _find_date_in_copyright(text: str) -> Optional[date]:
    """Step 4 (Last Resort): Infer date from a copyright notice."""
    match = re.search(r'(?:©|&copy;|copyright)\s+(\d{4})', text, re.I)
    if match:
        year_str = match.group(1)
        if dt := _parse_and_get_date(year_str):
            return dt
    return None

# --- Main Public Function ---

def find_best_date_on_page(url: str) -> Tuple[Optional[str], str]:
    """Finds the best possible date on a webpage using a prioritized strategy."""
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
    except requests.RequestException as e:
        # Re-raise the specific exception to be handled by the main script
        raise e

    # Execute search strategy in order of reliability
    if dt := _find_date_in_url(url):
        return dt.strftime("%m/%Y"), "url_path"

    if (dt_meta := _find_date_in_metadata(soup))[0]:
        return dt_meta[0].strftime("%m/%Y"), dt_meta[1]

    if dt := _find_date_in_visible_text(soup):
        return dt.strftime("%m/%Y"), "body_text_targeted"

    # Search the whole body text as a broader fallback
    text_to_search = soup.get_text(separator=' ', strip=True)
    if dt := _parse_and_get_date(text_to_search[:2000]): # Limit to first 2000 chars for performance
        return dt.strftime("%m/%Y"), "body_text_general"

    if dt := _find_date_in_copyright(text_to_search):
        return dt.strftime("%m/%Y"), "copyright_inference"

    return None, "not_found"


def date_me(url):
    """
    Main entry point for date extraction.
    This wrapper now directly calls the main logic and lets exceptions propagate
    up to the main script's error handler for consistent logging.
    """
    found_date, _ = find_best_date_on_page(url)
    return found_date