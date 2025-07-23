import re
import requests
from bs4 import BeautifulSoup
# normal is the main function

def fetch_html(url):
    return requests.get(url).text


def clean_html(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    # text = soup.get_text()
    return re.sub(r"\s+", " ", text).strip()

def context_around_keyword(text, keyword, context_words=500):
    words = re.findall(r'\b\w+\b', text)
    pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)

    matches = []
    for match in pattern.finditer(text):
        idx = match.start()
        word_idx = len(re.findall(r'\b\w+\b', text[:idx]))
        start = max(0, word_idx - context_words)
        end = min(len(words), word_idx + context_words)
        context = " ".join(words[start:end])
        matches.append({
            "keyword": keyword,
            "context": context
        })
    return matches,

def normal(url,keyword):
    html = fetch_html(url)
    text = clean_html(html)
    chunk = context_around_keyword(text,keyword)
    return chunk







"""
# url = "https://www.bcg.com/publications/2022/developers-influence-in-enterprise-tech-sales"
url = "https://www.shinkin.co.jp/info/houjincl_k/kankyo_02.html"
y = fetch_html(url)
x = clean_html(y)
print(x)
key = "VMware"
print(normal(url,key))
# """