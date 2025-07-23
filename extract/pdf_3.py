import requests
import fitz #PyMuPDF
import re
from io import BytesIO
# pdf is the main function


def pdf_content(url: str, keyword: str, max_per_page=2, max_total=4) -> list:

    def clean_text(txt: str) -> str:
        txt = re.sub(r"[\n\r\t]", " ", txt)
        txt = re.sub(r"[•·►▪●◆★☑✔➤➔➣➥→⇒➢➧⬤]", ".", txt)
        txt = re.sub(r"[^a-zA-Z0-9.,:;()\-\s]", "", txt)
        txt = re.sub(r"([.,:;])\1+", r"\1", txt)
        return re.sub(r"\s{2,}", " ", txt).strip()

    results = []
    total_found = 0
    # ---------------------------------------
    # char = 200
    # ---------------------------------------
    try:
        response = requests.get(url, timeout=10)
        doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")

        for page_num, page in enumerate(doc):
            if total_found >= max_total:
                break

            text = page.get_text()
            text_lower = text.lower()
            keyword_lower = keyword.lower()
            # print(f"Text Content of pdf: {text_lower} and keyword locating in the file: {keyword_lower}")

            if keyword_lower in text_lower:
                start_idx = 0
                count_this_page = 0

                while total_found < max_total and count_this_page < max_per_page:
                    idx = text_lower.find(keyword_lower, start_idx)
                    if idx == -1:
                        break
                    start = max(0, idx - 200)
                    # start = max(0, idx - char)
                    end = min(len(text), idx + len(keyword) + 300)
                    # end = min(len(text), idx + len(keyword) + char)
                    snippet = text[start:end]
                    text = clean_text(snippet)
                    # results.append(f"keyword: {keyword}, context: {text}")
                    results.append({
                        "keyword": keyword,
                        "context": text
                    })
                    total_found += 1
                    count_this_page += 1
                    start_idx = idx + len(keyword)


        return results

    except Exception as e:
        return [{"error": str(e)}]


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



def pdf(url,keyword):
    chunk = pdf_content(url,keyword)
    date = date_pdf(url)
    return chunk, date




"""
# url = "https://www.biznetnetworks.com/custom-upload/press-release/biznet-press-release---cloud-computing-launch-28-oct-2010-1573980449.pdf"
# url = "https://www.hellermanntyton.com/binaries/content/assets/downloads/ht-data/brochures/bro-dcim-r10-2013-low.pdf"
# url = "https://dxc.com/content/dam/dxc/projects/dxc-com/us/pdfs/about-us/partner-ecosystem/DG_8351a-22%20DXC%20VMware%20Partner%20Fact%20Sheet%20Final.pdf"
url = "https://www.fusion5.com/media/fnsjc1y2/session-2-why-oci-for-ai-and-ml-oracle.pdf"
keyword = "VMware"

content = pdf(url, keyword)
pdf_date = date_pdf(url)
print("\n",content,"\n Date of the article : ",pdf_date)
"""

"""
main.py
from extract.pdf_3 import *

# url = "https://www.fgvholdings.com/wp-content/uploads/2023/03/FGV-Corporate-Brochure-1.pdf"
url = "https://www.biznetnetworks.com/custom-upload/press-release/biznet-press-release---cloud-computing-launch-28-oct-2010-1573980449.pdf"
keyword = "VMware"

content = pdf(url, keyword)
pdf_date = date(url)
print("\n",content,"\n Date of the article : ",pdf_date)
# for match in matches:
#     print()
    # print(f"\n📄 Page {match['page']}:\n{match['cleaned_snippet']}")
    # return [{"message": f"Keyword: '{keyword}' not found in PDF."}]

"""