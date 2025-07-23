import requests
import fitz  # PyMuPDF
import re
from io import BytesIO
from dateutil.parser import parse
from datetime import datetime

from transformers.utils.chat_template_utils import returns_re

# --- Configuration ---
USER_AGENT = 'Chrome/108.0.0.0'
REQUEST_TIMEOUT = 45


# --- Helper Functions ---
def clean_text(txt: str) -> str:
    """Cleans up a text snippet for better processing by the language model."""
    txt = re.sub(r"[\n\r\t]+", " ", txt)  # Consolidate whitespace
    txt = re.sub(r"[•·►▪●◆★☑✔➤➔➣➥→⇒➢➧⬤]", ".", txt)  # Normalize list symbols
    # Keep a broader set of characters that might be relevant
    txt = re.sub(r"[^\w\s.,:;()\-\[\]'\"/]", "", txt)
    return re.sub(r"\s{2,}", " ", txt).strip()


def _parse_pdf_date(date_string: str) -> str or None:
    """Safely parses a date string and returns it in MM/YYYY format."""
    if not date_string:
        return None
    try:
        # The fuzzy parser can find dates inside strings like 'Published on: Jan 2023'
        dt = parse(date_string, fuzzy=True)
        # Sanity check to avoid invalid years
        if 2000 < dt.year <= datetime.now().year + 0:
            return dt.strftime("%m/%Y")
        return None
    except (ValueError, TypeError):
        return None

# date in url
def _find_date_in_url(url: str) -> str or None:
    """Finds a plausible date within the URL string and returns it in MM/YYYY format."""
    try:
        found_dates = list(find_dates(url))
        if found_dates:
            # Check against a reasonable year range to avoid false positives
            first_date = found_dates[0]
            if 2000 < first_date.year <= datetime.now().year + 1:
                return first_date.strftime("%m/%Y")
    except Exception:
        # datefinder can sometimes fail on complex strings
        return None
    return None



# --- Main Public Functions ---

def pdf_content(doc: fitz.Document, keyword: str, max_total=4) -> str:
    """Extracts text snippets containing the keyword from a PDF document."""
    contexts = []
    keyword_lower = keyword.lower()

    for page in doc:
        if len(contexts) >= max_total:
            break
        text = page.get_text("text")
        if keyword_lower in text.lower():
            # Create a simple, clean context around the keyword
            try:
                idx = text.lower().index(keyword_lower)
                start = max(0, idx - 400)
                end = min(len(text), idx + len(keyword) + 400)
                snippet = text[start:end]
                contexts.append(clean_text(snippet))
            except ValueError:
                continue

    return " ... ".join(contexts)  # Return a single string for the LLM


def date_pdf(doc: fitz.Document) -> str:
    """
    Finds the best date for a PDF using a prioritized strategy:
    1. Metadata (fast and reliable)
    2. Text on the first page (often contains publication dates)
    3. Text on the last page (can contain dates)
    """
    # 1. Try metadata first
    if mod_date_str := doc.metadata.get("modDate"):
        if parsed_date := _parse_pdf_date(mod_date_str):
            return parsed_date

    # 2. Search the first page's text
    if len(doc) > 0:
        first_page_text = doc[0].get_text("text")
        if parsed_date := _parse_pdf_date(first_page_text[:1500]):  # Search start of page
            return parsed_date

    # 3. Search the last page's text
    if len(doc) > 1:
        last_page_text = doc[-1].get_text("text")
        if parsed_date := _parse_pdf_date(last_page_text):
            return parsed_date

    return "Not found"


def pdf(url: str, keyword: str) -> tuple[str, str]:
    """
    Orchestrates the entire PDF processing.
    Downloads the PDF once and passes the document object to helper functions.
    This is much more efficient than downloading it multiple times.
    """
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': USER_AGENT})
        response.raise_for_status()

        # Open the PDF document from the downloaded content in memory
        doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")

        # Pass the opened document to the content and date extractors
        context = pdf_content(doc, keyword)
        date = date_pdf(doc)

        doc.close()  # Important to free up resources

        return context, date

    except (requests.RequestException, fitz.fitz.FitzError, ValueError) as e:
        # Log the error for debugging but don't stop the script.
        print(f"  [PDF Processing Error] Could not process {url}. Reason: {e}")
        # Return default values so the main script can proceed.
        return "", "Not found"



keyword = "VMware"
list = [
    "https://adorwelding.com/wp-content/uploads/2021/08/AGMNewspaperAdvt.pdf",
    "https://adslot.com/wp-content/uploads/2013/12/CountingTheCostOfSales.pdf"
    ]


for i in list:
    url_1 = i
    content, date = pdf(url_1, keyword)
    # pdf_date = date_pdf(url_1)
    print()
    print("\n",content,"\n Date of the article : ",date)