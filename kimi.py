import os
import json
from openai import OpenAI


OPENROUTER_API_KEY = ""
BASE_URL = "https://openrouter.ai/api/v1"
# You can use the free model or other Kimi models available on OpenRouter
# KIMI_MODEL = "moonshotai/kimi-k2"
KIMI_MODEL = "moonshotai/kimi-k2:free"



# The list of target keywords remains the same.
target = [
    # Technology usage
    "use", "using", "used", "adopted", "deployed", "implemented",
    "powered by", "enabled by", "built with", "runs on", "based on",
    "leveraged", "utilized", "developed with", "hosted on", "migrated to",

    # Partnerships and integrations
    "partner", "partnership", "strategic partner", "collaborated with",
    "integrated with", "alliance", "reseller", "technology partner",
    "solution partner", "OEM", "channel partner", "vendor",

    # Hiring indicators
    "hiring", "job posting", "career opportunity", "recruiting",
    "skills required", "experience with", "desired skills", "looking for",
    "join our team", "open roles", "vacancy", "apply", "certified in",

    # Spending and investment
    "investment", "budget", "procurement", "IT spend", "contract with",
    "financial commitment", "spending", "cost", "deal", "payment to", "funding"
]


def explain(chunk_text: str, keyword_tech: str, company_name: str, usage_indicators: list = None) -> dict:
    """
    Analyzes text to determine technology usage using the Kimi model via an OpenAI-compatible client.
    """
    if usage_indicators is None:
        usage_indicators = target

    indicators_str = ", ".join([f"'{ind}'" for ind in usage_indicators])

    # The prompt is the same, but we add a stronger instruction for JSON output.
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
    """

    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found. Please set it in your .env file.")
        return {"uses_tech": False, "explanation": "API key is not configured."}

    try:
        # --- Step 2: Initialize the OpenAI client pointing to OpenRouter ---
        client = OpenAI(
            base_url=BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
        print(f"--> Using Kimi model: {KIMI_MODEL} via OpenRouter")

        # --- Step 3: Call the Chat Completions API with the Kimi model ---
        response = client.chat.completions.create(
            model=KIMI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            # Instruct the model to return a JSON object for easier parsing
            response_format={"type": "json_object"},
            timeout=300
        )

        # --- Step 4: Parse the response from the OpenAI-compatible client ---
        # The JSON string is in the 'content' of the first choice's message
        json_string = response.choices[0].message.content
        parsed_response = json.loads(json_string)

        return {
            "uses_tech": parsed_response.get("uses_tech", False),
            "explanation": parsed_response.get("explanation", "No explanation from LLM.")
        }
    except Exception as e:
        print(f"Error calling Kimi API or parsing response for keyword '{keyword_tech}': {e}")
        return {"uses_tech": False, "explanation": f"API or parsing error: {e}"}

# --- Add this code to the end of your kimi.py file ---

if __name__ == "__main__":
    print("--- Running Test Cases for Kimi Explain Function ---")

    # --- Test Case 1: Clear Indication of Usage ---
    print("\n[Test Case 1: Positive Match]")
    company_1 = "Innovate Tech"
    keyword_1 = "AWS"
    text_1 = f"At {company_1}, our entire cloud infrastructure is built on AWS for scalability. We are hiring engineers with deep experience in AWS services."

    print(f"Company: {company_1}, Keyword: {keyword_1}")
    result_1 = explain(text_1, keyword_1, company_1)
    print("Kimi's Analysis:")
    # Use json.dumps for pretty-printing the result
    print(json.dumps(result_1, indent=2))
    print("-" * 20)


    # --- Test Case 2: No Clear Indication of Usage (Third-Party Mention) ---
    print("\n[Test Case 2: Negative Match]")
    company_2 = "Legacy Solutions Inc."
    keyword_2 = "Azure"
    text_2 = f"Our blog at {company_2} often discusses industry trends. A recent article featured a case study on how another company, Global Dynamics, successfully migrated to Microsoft Azure."

    print(f"Company: {company_2}, Keyword: {keyword_2}")
    result_2 = explain(text_2, keyword_2, company_2)
    print("Kimi's Analysis:")
    print(json.dumps(result_2, indent=2))
    print("-" * 20)


    # --- Test Case 3: Partnership Mention (Should be False based on prompt) ---
    print("\n[Test Case 3: Partnership Match]")
    company_3 = "Cloud Consultants"
    keyword_3 = "Google Cloud"
    text_3 = f"{company_3} is a certified Google Cloud Partner, helping businesses leverage the power of GCP."

    print(f"Company: {company_3}, Keyword: {keyword_3}")
    result_3 = explain(text_3, keyword_3, company_3)
    print("Kimi's Analysis:")
    print(json.dumps(result_3, indent=2))
    print("-" * 20)


