import requests
import json
import re
from bs4 import BeautifulSoup
from dateutil.parser import parse
from datefinder import find_dates
from datetime import datetime, date
from typing import Optional, Tuple
# from pdf_3 import *
from extract.pdf_3 import *

# --- Configuration Constants ---
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
USER_AGENT = 'Chrome/91.0.4472.124'
REQUEST_TIMEOUT = 45
MAX_FUTURE_YEAR_OFFSET = 0


# --- Private Helper Functions for Each Step ---

def _parse_and_get_date(date_string: str) -> Optional[date]:
    """Safely parses a string and returns only the date part."""
    if not date_string:
        return None
    try:
        # fuzzy=True helps parse dates from surrounding text
        dt_object = parse(date_string, fuzzy=True)
        if 2000 < dt_object.year <= datetime.now().year + MAX_FUTURE_YEAR_OFFSET:
            return dt_object.date()
        return None
    except (ValueError, TypeError, OverflowError):
        return None


def _find_date_in_url(url: str) -> Optional[date]:
    """Step 1: Find a plausible date within the URL string."""
    found_dates = list(find_dates(url))
    if found_dates:
        first_date = found_dates[0]
        # Sanity check to avoid matching version numbers like /v2024/
        # This line helps use limit the date range
        if 2001 < first_date.year <= datetime.now().year + MAX_FUTURE_YEAR_OFFSET:
            return first_date.date()
    return None


def _find_date_in_metadata(soup: BeautifulSoup) -> Tuple[Optional[date], Optional[str]]:
    """Step 2: Search structured metadata (JSON-LD, meta tags). This is highly reliable."""
    # 2a: JSON-LD (often used by news sites and blogs)
    json_ld_keys = ['dateModified','datePublished', 'publishedDate', 'dateCreated', 'uploadDate']
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            for key in json_ld_keys:
                if dt := _parse_and_get_date(data.get(key)):
                    return dt, "json-ld"
        except (json.JSONDecodeError, TypeError):
            continue

    # 2b: Meta Tags
    # ------------------------------------------------------------------------
    # last modified this list

    meta_selectors = {
        "meta[name='dateModified']": "meta_tag",
        "meta[property='article:modified_time']": "meta_tag",
        "meta[name='datePublished']": "meta_tag",
        "meta[property='article:published_time']": "meta_tag",
        "meta[name='pubdate']": "meta_tag",
        "meta[name='date']": "meta_tag",
    }
    for selector, method in meta_selectors.items():
        if tag := soup.select_one(selector):
            if dt := _parse_and_get_date(tag.get('content')):
                return dt, method
    return None, None


def _find_date_in_visible_text(soup: BeautifulSoup, text: str) -> Optional[date]:
    """
    Step 3 (Improved): Searches for dates first in specific, high-probability HTML tags,
    and then falls back to a general search on the page's text.
    """
    # 3a: High-precision search in common date-related tags
    date_selectors = [
        'time[datetime]', '[class*="date"]', '[class*="publish"]',
        '[class*="timestamp"]', '[id*="date"]', '[id*="publish"]'
    ]
    for selector in date_selectors:
        for tag in soup.select(selector):
            tag_text = tag.get_text() or tag.get('datetime', '')
            found_dates = list(find_dates(tag_text))
            if found_dates:
                dt = found_dates[0]
                if 2001 < dt.year <= datetime.now().year + MAX_FUTURE_YEAR_OFFSET:
                    return dt.date()

    # 3b: Fallback to a broader search on the first 10,000 characters
    found_dates = list(find_dates(text[:10000]))
    if found_dates:
        dt = found_dates[0]
        if 2001 < dt.year <= datetime.now().year + MAX_FUTURE_YEAR_OFFSET:
            return dt.date()

    return None


def _find_date_in_copyright(text: str) -> Optional[date]:
    """Step 4 (Last Resort): Infer date from a copyright notice."""
    match = re.search(r'(?:©|&copy;|copyright)\s+(\d{4})', text, re.I)
    if match:
        year = int(match.group(1))
        now = datetime.now()
        # Only accept copyright years that are in the past or current year
        if 1990 < year <= now.year:
            # If it's a past year, assume end of that year
            return date(year, 12, 31) if year < now.year else now.date()
    return None


# --- Main Public Function ---

def find_best_date_on_page(url: str) -> Tuple[Optional[str], str]:
    """
    Finds the best possible date on a webpage using a prioritized 4-step strategy.
    """
    try:
        response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml') # Using lxml is generally faster
    except requests.RequestException:
        # Let the main script handle the error by re-raising it
        raise

    # --- Execute search strategy in order of reliability ---

    # Step 1: Check the URL itself (fast and often accurate)
    if dt := _find_date_in_url(url):
        return dt.strftime("%m/%Y"), "url_path"

    # Step 2: Check structured metadata (very reliable)
    if (dt_meta := _find_date_in_metadata(soup))[0]:
        return dt_meta[0].strftime("%m/%Y"), dt_meta[1]

    # Step 3: Perform the improved search on visible page text
    text_to_search = soup.get_text(separator=' ', strip=True)
    if dt := _find_date_in_visible_text(soup, text_to_search):
        return dt.strftime("%m/%Y"), "body_text_targeted"

    # Step 4: As a last resort, check for a copyright year
    if dt := _find_date_in_copyright(text_to_search):
        return dt.strftime("%m/%Y"), "copyright_inference"

    return None, "not_found"

def date_pdf (url: str):
    try:
        response = requests.get(url, timeout=10)
        doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")

        metadata = doc.metadata
        mod_date = metadata.get("modDate", "No modification date found")
        y = mod_date[2:6]
        m = mod_date[6:8]
        # d = f"{m}/{y}"
        # return d
        return f"{m}/{y}"
    except Exception as e:
        return "Not found"


def date_me(url):
    try:
        found_date, method = find_best_date_on_page(url)
        # print(f"\n--- Results for: {url} ---")
        # print(f"Date: {found_date}")
        # print(f"Method: {method}\n")
        return found_date
    except Exception as e:
        print(f"An unexpected error occurred: {e}")