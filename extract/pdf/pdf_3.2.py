import requests
import fitz  # PyMuPDF
import re
from io import BytesIO
from dateutil.parser import parse
from datetime import datetime
from datefinder import find_dates
import warnings

warnings.filterwarnings("ignore", category=UnknownTimezoneWarning)

# --- Ignore the known, harmless timezone warning from dateutil ---

# --- Configuration ---
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
REQUEST_TIMEOUT = 45

# ==============================================================================
#  1. CONTENT EXTRACTION FUNCTION (This part is working well)
# ==============================================================================

def pdf_content(doc: fitz.Document, keyword: str, max_total=4) -> str:
    """
    Extracts relevant text snippets containing the keyword from an opened PDF document.
    """
    def clean_text(txt: str) -> str:
        txt = re.sub(r"[\n\r\t]+", " ", txt)
        txt = re.sub(r"[•·►▪●◆★☑✔➤➔➣➥→⇒➢➧⬤]", ".", txt)
        txt = re.sub(r"[^\w\s.,:;()\-\[\]'\"/]", "", txt)
        return re.sub(r"\s{2,}", " ", txt).strip()

    contexts = []
    keyword_lower = keyword.lower()
    for page in doc:
        if len(contexts) >= max_total:
            break
        text = page.get_text("text")
        if keyword_lower in text.lower():
            try:
                idx = text.lower().index(keyword_lower)
                start = max(0, idx - 400)
                end = min(len(text), idx + len(keyword) + 400)
                snippet = text[start:end]
                contexts.append(clean_text(snippet))
            except ValueError:
                continue
    return " ... ".join(contexts)

# ==============================================================================
#  2. DATE EXTRACTION FUNCTIONS (WITH THE CORRECTED URL LOGIC)
# ==============================================================================

def _find_date_in_url(url: str) -> str | None:
    """
    DATE STEP 1: Finds a date in the URL using a reliable hybrid approach.
    1. A precise regex for common /YYYY/MM/ or /YYYY-MM-DD/ patterns.
    2. A fallback to the more general datefinder library.
    """
    # 1. Precise Regex Search (Extremely reliable for this pattern)
    # This looks for a 4-digit year (2000-2029) followed by a 2-digit month (01-12)
    match = re.search(r'/(20[0-2]\d)[/-]([01]\d)/', url)
    if match:
        year, month = int(match.group(1)), int(match.group(2))
        if 2000 <= year <= datetime.now().year + 1 and 1 <= month <= 12:
            return f"{month:02d}/{year}"

    # 2. Fallback to datefinder for other, less common formats
    try:
        found_dates = list(find_dates(url, strict=True))
        if found_dates:
            for dt in found_dates:
                if 2000 <= dt.year <= datetime.now().year + 1:
                    return dt.strftime("%m/%Y")
    except Exception:
        pass # Ignore datefinder errors
    return None

def _find_date_in_pages(doc: fitz.Document) -> str | None:
    """DATE STEP 2: Searches the text of the first two pages of the document."""
    text_to_search = ""
    for i in range(min(2, len(doc))):
        text_to_search += doc[i].get_text("text") + "\n"

    if text_to_search:
        try:
            found_dates = list(find_dates(text_to_search, strict=True))
            if found_dates:
                for dt in found_dates:
                    if 2000 <= dt.year <= datetime.now().year + 1:
                        return dt.strftime("%m/%Y")
        except Exception:
            pass
    return None

def _find_date_in_metadata(doc: fitz.Document) -> str | None:
    """DATE STEP 3: Falls back to checking the PDF's internal metadata."""
    def _parse_date(date_string: str) -> str | None:
        if not date_string: return None
        try:
            dt = parse(date_string, fuzzy=True)
            if 2000 < dt.year <= datetime.now().year + 1:
                return dt.strftime("%m/%Y")
            return None
        except (ValueError, TypeError):
            return None

    if mod_date_str := doc.metadata.get("modDate"):
        return _parse_date(mod_date_str)
    return None

# ==============================================================================
#  3. MAIN ORCHESTRATOR FUNCTION (Manages the pipeline)
# ==============================================================================

def pdf(url: str, keyword: str) -> tuple[str, str]:
    """
    Orchestrates the entire PDF processing pipeline: content and date extraction.
    """
    final_date = _find_date_in_url(url)
    context = ""

    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers={'User-Agent': USER_AGENT})
        response.raise_for_status()

        with fitz.open(stream=BytesIO(response.content), filetype="pdf") as doc:
            context = pdf_content(doc, keyword)
            if not final_date:
                final_date = _find_date_in_pages(doc) or _find_date_in_metadata(doc)

        return context, final_date or "Not found"

    except (requests.RequestException, fitz.fitz.FitzError, ValueError) as e:
        print(f"  [PDF Processing Error] Could not process {url}. Reason: {e}")
        return context, final_date or "Not found"

# --- Testing block to demonstrate the new, correct structure ---
if __name__ == "__main__":
    test_keyword = "VMware"
    test_urls = [
        "https://adorwelding.com/wp-content/uploads/2021/08/AGMNewspaperAdvt.pdf",
        "https://dxc.com/content/dam/dxc/projects/dxc-com/us/pdfs/about-us/partner-ecosystem/DG_8351a-22%20DXC%20VMware%20Partner%20Fact%20Sheet%20Final.pdf",
        "https://renew.com/resources/investor-corner/RMG-II-ReNew-Power-Transaction-Announcement-Presentation-Feb-2021-.pdf",
        "https://rajuandprasad.com/lo-admin/drive/November-NL-24-.pdf",
        "https://simedarbyproperty.com/sites/default/files/2021-09/00%20Compilation%20of%20report%20&%20guidelines%20of%20constructed%20wetlands%20in%20CoE%20(2)_.pdf"
    ]

    for test_url in test_urls:
        content_str, date_str = pdf(test_url, test_keyword)
        print("-" * 20)
        print(f"URL: {test_url}")
        print(f"Content Found: '{content_str}'")
        print(f"Date Found: '{date_str}'")
