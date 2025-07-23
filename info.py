# Most probably we will get this details in our .csv file.
# Keep this just for an exception.
# info is the main function

from urllib.parse import urlparse
import pandas as pd

'''
def info(url):
    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # Get the home link (scheme + netloc)
    home_link = f"{parsed.scheme}://{parsed.netloc}"

    # Extract company name from domain (netloc)
    domain = parsed.netloc.lower().replace("www.", "")
    parts = domain.split(".")

    # Try to guess company name from domain
    company_name = parts[0].title()

    return company_name
'''

def info(url, company_name_from_csv=None):

    if pd.notna(company_name_from_csv) and isinstance(company_name_from_csv, str) and company_name_from_csv.strip():
        return company_name_from_csv.strip()

    # --- Fallback: Derive the name from the URL if no valid name was provided ---
    if not isinstance(url, str) or not url.strip():
        return "Unknown Company"  # Handle cases where URL is also invalid

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        parts = domain.split(".")

        # A slightly better heuristic to guess the company name from the domain
        if len(parts) > 2 and len(parts[1]) <= 3:  # Handles TLDs like .co.uk, .com.au
            company_name = parts[0].title()
        else:
            company_name = parts[0].title()

        return company_name
    except Exception:
        # Gracefully handle any URL parsing errors
        return "Unknown Company"
