import google.generativeai as genai
import json
import random
import random

# -----------------------------------------------------------

API_KEYS = [ "AIzaSyB6EmZVg0V0-0OQCuCajKk-lZsSxR3xFz8",
             "AIzaSyCd8WMXsVmhZDuB4EgpRb85HgIpeVKcKJ0",
             "AIzaSyBIKfbK6EhSqx4FxZkWDHOXmzSZBwSV5hY",
             "AIzaSyAnoBK9VLxOKfFqAFJpUT9Wpqyq4VZSjsw",
             "AIzaSyAiPbkL94Q4u6RawKPopg94-zhtEEBlopA",
             ]

target = [
    "use", "using", "used", "adopted", "deployed", "running on",
    "built with", "powered by", "partner", "integration", "migrated to"
]


def explain(chunk_text: str, keyword_tech: str, company_name: str, usage_indicators: list = None) -> dict:

    if usage_indicators is None:
        usage_indicators = target
    # this will kep my code to work with older and new main function together.
    indicators_str = ", ".join([f"'{ind}'" for ind in usage_indicators])

    prompt = f"""
    Analyze the following text about {company_name} (company name might not be well structured) to determine if it indicates that {company_name} uses, supports, develops, deploys, partners with, or is actively involved with the technology or concept of '{keyword_tech}'.
    Note: If the technology is mentioned in Job description by that company means they use that technology.
    Note: The company name might not always be explicitly mentioned, could be misspelled, have irregular spacing, or be mixed with unrelated tokens or unknown words. Focus on contextual clues to assess technology usage.
    **Important Guidance:** Indications of usage often include words or phrases like: {indicators_str}.
    However, also consider semantic equivalents and contextual implications beyond just these specific words.
    

    ---
    Text about {company_name}:
    {chunk_text}
    ---

    Provide your answer in a JSON format with two keys:
    1.  "uses_tech": a boolean (true/false) indicating if '{keyword_tech}' is used or involved by the company based on the text and the above guidance.
    2.  "explanation": a brief reason for your answer, quoting relevant parts of the text if possible.
    """

    try:

        # Key Rotation logic
        current_key = random.choice(API_KEYS)
        # current_key = ""
        print(f"--> Using API Key ending in: ...{current_key[-4:]}")
        # Call Gemini API
        genai.configure(api_key=current_key)

        model = genai.GenerativeModel('gemini-1.5-flash')

        # response = model.generate_content(prompt)
        response = model.generate_content(
            prompt,
            request_options={"timeout": 300}
        )
        # Clean and parse JSON response
        cleaned_text = response.text.strip().replace("```json\n", "").replace("\n```", "")
        parsed_response = json.loads(cleaned_text)
        return {
            "uses_tech": parsed_response.get("uses_tech", False),
            "explanation": parsed_response.get("explanation", "No explanation from LLM.")
        }
    except Exception as e:
        print(f"Error calling Gemini API or parsing response for keyword '{keyword_tech}': {e}")
        return {"uses_tech": False, "explanation": f"API or parsing error: {e}"}

# Test -------------------
# """
chunk = "This is just an sample test case"
keyword = "case"
company = "test"
x = explain(chunk,keyword,company)
print(x)
# """
#
