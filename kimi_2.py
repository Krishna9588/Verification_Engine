# kimi_guarded.py
import os
import json
import time
import random
from typing import Dict
from openai import OpenAI, RateLimitError

# -------------------- CONFIG --------------------
API_KEY     = "sk-A8C8nKRVL2TC6p3qj0T10ne0Y5kUXnffdr8RAwTvbqzpd6R7"
BASE_URL   = "https://api.moonshot.ai/v1"   # clean, no HTML, no trailing space
# KIMI_MODEL = "kimi-1.5-flash"
KIMI_MODEL = "kimi-k2-0711-preview"
# Your project limits
MAX_RPM      = 6          # requests per minute
MAX_TPM      = 64_000     # tokens per minute
SAFE_DELAY   = 60 / MAX_RPM   # 10 s between calls
MAX_RETRIES  = 3

# Indicator list (unchanged)
target = [
    "use", "using", "used", "adopted", "deployed", "implemented",
    "powered by", "enabled by", "built with", "runs on", "based on",
    "leveraged", "utilized", "developed with", "hosted on", "migrated to",
    "partner", "partnership", "strategic partner", "collaborated with",
    "integrated with", "alliance", "reseller", "technology partner",
    "solution partner", "OEM", "channel partner", "vendor",
    "hiring", "job posting", "career opportunity", "recruiting",
    "skills required", "experience with", "desired skills", "looking for",
    "join our team", "open roles", "vacancy", "apply", "certified in",
    "investment", "budget", "procurement", "IT spend", "contract with",
    "financial commitment", "spending", "cost", "deal", "payment to", "funding"
]
# ------------------------------------------------

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def _safe_sleep(attempt: int):
    """Exponential back-off with jitter."""
    delay = SAFE_DELAY * (2 ** attempt) + random.uniform(0, 1)
    time.sleep(delay)

def explain(chunk_text: str,
            keyword_tech: str,
            company_name: str,
            usage_indicators: list = None) -> Dict:
    """
    Rate-limit-aware wrapper around Kimi K2.
    """
    if usage_indicators is None:
        usage_indicators = target

    indicators_str = ", ".join([f"'{i}'" for i in usage_indicators])

    prompt = f"""
    Analyze the following text about {company_name} (company name might not be well structured) to determine if it indicates that {company_name} uses, supports, develops, deploys, partners with, or is actively involved with the technology or concept of '{keyword_tech}'.
    Note: If the technology is mentioned in Job description by that company means they use that technology.
    Note: The company name might not always be explicitly mentioned, could be misspelled, have irregular spacing, or be mixed with unrelated tokens or unknown words. Focus on contextual clues to assess technology usage.
    **Important Guidance:**
    To help you assess company involvement accurately, compare the text against the following key phrases. These are indicators of meaningful involvement with "{keyword_tech}":
    Indications of usage often include words or phrases like: {indicators_str}.
    Do not assume involvement unless there is a clear match or a strong semantic equivalent to one of these phrases.
    However, also consider semantic equivalents and contextual implications beyond just these specific words as exceptions are possible and we can't include each indicator separately.

    If the text (chunk) discusses another company (e.g., mentions companies like Wipro, IBM, Infosys, etc.) using or developing the technology, and there is no clear evidence that the company "{company_name}" is directly involved in those activities, then the answer should be **false**.
    Even if "{company_name}" is the host of the content (such as a blog, case study, or article), do **not** assume it is using or endorsing the technology unless explicitly stated.
    Always cross-check if the **actions are attributed directly to {company_name}** and not a third-party company.

    ---
    Text about {company_name}:
    {chunk_text}
    ---

    Provide your answer ONLY in a valid JSON format with two keys:
    1.  "uses_tech": a boolean (true/false) indicating if '{keyword_tech}' is used or involved by the company based on the text and the above guidance.
    2.  "explanation": a brief reason for your answer, quoting relevant parts of the text if possible.
    
    Return **only** a valid JSON object:
    {{
      "uses_tech": <true|false>,
      "explanation": "<one-sentence reason>"
    }}
    """

    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=KIMI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,           # keep TPM usage low
                temperature=0.2,
                timeout=30
            )

            raw = resp.choices[0].message.content.strip()
            return json.loads(raw)

        except RateLimitError:
            if attempt == MAX_RETRIES:
                return {"uses_tech": False, "explanation": "Rate limit exceeded after retries."}
            _safe_sleep(attempt)

        except Exception as e:
            # Catch-all for JSON parse errors, network hiccups, etc.
            return {"uses_tech": False, "explanation": f"Error: {e}"}

# ------------------- SELF-TEST -------------------

chunk_text = "This is an sample chunck where we belive Google use GCP"
keyword_tech = "GCP"
company_name = "Google"
x = explain(chunk_text,keyword_tech,company_name)
print(x)