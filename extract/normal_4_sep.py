import re
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# --- Define a constant path for the single log file ---
LOG_FILE_PATH = "normal_results_log.json"


def _save_result_to_json(url: str, keyword: str, contexts: list):
    """
    Appends the extracted contexts to a single JSON log file.
    """
    # Ensure the directory for the log file exists, if it's in a subdirectory
    output_dir = os.path.dirname(LOG_FILE_PATH)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Prepare the new data entry to be added to the log
    new_entry = {
        "url": url,
        "keyword": keyword,
        "retrieval_timestamp_utc": datetime.utcnow().isoformat(),
        "results": contexts
    }

    all_data = []
    try:
        # Try to read the existing log file first
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
            # Ensure the loaded data is a list, start fresh if it's not
            if not isinstance(all_data, list):
                all_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty/invalid, we'll start with an empty list
        pass

    # Append the new result to the list
    all_data.append(new_entry)

    # Write the entire updated list back to the file
    try:
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        # print(f"  [INFO] Appended result to {LOG_FILE_PATH}")
    except Exception as e:
        print(f"  [WARNING] Could not save result to JSON log file: {e}")


def fetch_html(url: str) -> str:
    """
    Fetches HTML content from a URL with a timeout and error handling.
    This will now let the main script catch network errors.
    """
    # Using a realistic user-agent and a timeout is good practice
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return response.text


def clean_html(html: str) -> str:
    """Removes unwanted tags and extra whitespace from HTML."""
    soup = BeautifulSoup(html, "lxml")
    # Added <header> to the list of common non-content tags to remove
    for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def context_around_keyword(text: str, keyword: str, context_words: int = 250, max_matches: int = 5) -> list:
    """
    Finds up to `max_matches` occurrences of a keyword and returns the surrounding context.
    """
    words = re.findall(r'\b\w+\b', text)
    pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)

    matches = []
    for match in pattern.finditer(text):
        # --- LIMIT ADDED HERE ---
        # If we have already found the maximum number of matches, stop searching.
        if len(matches) >= max_matches:
            break

        idx = match.start()
        word_idx = len(re.findall(r'\b\w+\b', text[:idx]))
        start = max(0, word_idx - context_words)
        end = min(len(words), word_idx + context_words)
        context = " ".join(words[start:end])
        matches.append({
            "keyword": keyword,
            "context": context
        })

    # --- BUG FIX ---
    # Now returns the list of matches directly, not as a tuple `(matches,)`.
    # This makes it work correctly with `if not contexts:` in your main script.
    return matches


def normal(url: str, keyword: str) -> list:
    """
    Main function to fetch, clean, and extract keyword contexts from a URL.
    Returns a list of context dictionaries.
    """
    # Let exceptions from fetch_html be caught by the main script
    html = fetch_html(url)
    text = clean_html(html)
    contexts = context_around_keyword(text, keyword)

    # --- NEW: Automatically save the result to a JSON file ---
    _save_result_to_json(url, keyword, contexts)

    return contexts