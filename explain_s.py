import google.generativeai as genai
import json
# import random
from itertools import cycle
# Gemini API KEYs ----------------------------------------------
API_KEYS = ["AIzaSyCn7YEam6Vw5ToVQTJ6mRZogMwM3GwZAHU",
            "AIzaSyB8xmrgn87XTBr1_rxim0huAubOBDBvtD4",
            "AIzaSyB3sYWowbpnFO5fnC0TnJE-hxxlcMmvwIs",
            "AIzaSyCgXDFPLkH9geHJb13WrbbstKd5G3iYZc0"
            ]

# -----------------------------------------------------------

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

key_cycler = cycle(API_KEYS)

def explain(chunk_text: str, keyword_tech: str, company_name: str, usage_indicators: list = None) -> dict:
    if usage_indicators is None:
        usage_indicators = target
    # this will kep my code to work with older and new main function together.
    indicators_str = ", ".join([f"'{ind}'" for ind in usage_indicators])
    # print(indicators_str)

    #1
    # working prompt
    ''' # Old working prompt
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

    Provide your answer in a JSON format with two keys:
    1.  "uses_tech": a boolean (true/false) indicating if '{keyword_tech}' is used or involved by the company based on the text and the above guidance.
    2.  "explanation": a brief reason for your answer, quoting relevant parts of the text if possible.
    """
    '''

    #4
    prompt = f"""
    You are an objective and meticulous technology analyst. Your primary task is to make a balanced and evidence-based judgment to determine if **{company_name}** is actively and demonstrably using, supporting, developing, or deploying the technology or concept of **'{keyword_tech}'**, based *only* on the provided text.

    Your goal is to weigh the positive evidence against the strict exclusion rules to make a final, justifiable determination.

    ---
    ### **1. Positive Indicators (What constitutes a 'Yes')**

    The answer should be **true** if you find clear, direct evidence of the company's operational use. Strong evidence includes:

    * **Direct Company Statements:** The text explicitly states usage in the first person (e.g., "Our platform is built on...", "We have deployed...", "We partner with...").
    * **Technical Content & Case Studies:** A technical blog post, success story, or case study from a named internal team (e.g., "our engineering team," "the WebClaims division") that details the implementation or operational use of the technology **is considered strong evidence**.
    * **Job Postings:** A job description from the company for an internal, operational role that requires hands-on skills in the technology.
    * **General Indicators:** The text contains strong contextual keywords related to implementation, such as: {indicators_str}.

    ---
    ### **2. Exclusion Rules (What forces a 'No')**

    The answer must be **false** if the primary evidence falls into any of these categories, even if the keyword is present:

    * **CRITICAL - Context Mismatch:** The keyword is used but refers to the wrong concept.
        * **Acronyms:** An acronym like 'AWS' is used but the text defines it as something else (e.g., "Alliance for Water Stewardship") or the context is non-technical.
        * **Common Words:** A word like 'Glue' refers to a physical substance (e.g., 'chemical glue') and not the specific technology service.
    * **CRITICAL - Educational or Certification Use:** The company's main interaction with the technology is offering training, courses, university programs, or certifications *on* it. This is not operational use.
    * **No Direct Action by Company:**
        * **Third-Parties:** The text describes a customer, partner, or other organization using the technology.
        * **Individual Skills:** The text only refers to an individual employee's personal resume, skills, or certifications.
        * **Speculation:** The text uses conditional or future-looking language (e.g., "might use," "could explore," "plans to adopt").

    ---
    ### **Analysis Task**

    **Company:** `{company_name}`
    **Technology:** `{keyword_tech}`

    **Text to Analyze:** `{chunk_text}`
    
    ---

    Provide your answer in a JSON format with two keys: "uses_tech" and "explanation".
    
    1.  `uses_tech`: A boolean (true/false) value based on a balanced application of the rules above.
    2.  `explanation`: A single-line, JSON-safe string that justifies the answer. It must quote the key evidence and explicitly name the primary rule that was applied. Example for a false answer: `"The text mentions 'AWS Education Research Grant' which fails the 'CRITICAL - Educational or Certification Use' rule because it describes academic activity, not operational use."` Example for a true answer: `"The text states 'our entire platform is built on AWS' which meets the 'Direct Company Statements' positive indicator."`

    """

    #5 - Claude
    '''
    # claude
    prompt = f"""
    You are analyzing text to determine if **{company_name}** actively uses the technology **'{keyword_tech}'** for its business operations.

    **CONTEXT VALIDATION (Critical First Step):**
    1. **Acronym/Common Word Check:** If '{keyword_tech}' is an acronym (AWS, S3, etc.) or common word (Shield, Glue, etc.), verify the context is clearly technology-related. Look for supporting technical terms, cloud infrastructure mentions, or explicit definitions.

    2. **Company Attribution:** Ensure the content is genuinely about {company_name} and not primarily about other organizations.

    **POSITIVE INDICATORS (Answer: true):**
    - Direct operational use: "We use {keyword_tech}", "Our platform runs on {keyword_tech}", "We have deployed {keyword_tech}"
    - Job postings by the company requiring {keyword_tech} skills for internal roles
    - Case studies describing the company's implementation of {keyword_tech}
    - Partnership announcements where the company adopts {keyword_tech}
    - Technical documentation or blogs by the company describing their use of {keyword_tech}
    - Company-specific configurations, implementations, or integrations with {keyword_tech}

    **NEGATIVE INDICATORS (Answer: false):**
    - **Wrong Context:** Acronym/word used in non-technology context (e.g., AWS as "Alliance for Water Stewardship")
    - **Pure Training/Certification:** Content solely about offering courses or certifications (unless it mentions using the tech for course delivery infrastructure)
    - **Generic Mentions:** Casual references without indicating company use ("Technologies like {keyword_tech}...")
    - **Third-party Focus:** Content primarily about other companies' usage with no indication of {company_name}'s adoption
    - **Requirements/Terms:** Mentioning tech as participant requirements or in legal terms without operational use

    **EDGE CASES (Evaluate Carefully):**
    - **Training + Infrastructure:** If a company offers training BUT also mentions using the tech for their training platform infrastructure → **true**
    - **Partnership Content:** If hosted by {company_name} but describes their own adoption as part of partnership → **true**
    - **Academic Institutions:** Faculty research or curriculum mentioning tech use in actual research projects (not just teaching) → **true**

    **DECISION FRAMEWORK:**
    1. Is the technology mentioned in the correct context (not misidentified)?
    2. Is there evidence of {company_name}'s direct operational involvement?
    3. Is this more than just educational/training offerings or generic mentions?

    If yes to all three → **true**
    If no to any → **false**

    ---

    **Text to Analyze:**
    {chunk_text}

    ---

    **Required Output Format:**
    ```json
    {{
      "uses_tech": boolean,
      "explanation": "Brief explanation citing specific text evidence and which rule applied",
      "confidence": "high/medium/low based on clarity of evidence"
    }}
    """
    '''

    try:

        # Key Rotation logic
        # current_key = random.choice(API_KEYS)
        # current_key = ""
        current_key = next(key_cycler)
        print(f"--> Using API Key ending in: ...{current_key[-4:]}")
        # Call Gemini API
        genai.configure(api_key=current_key)

        # model = genai.GenerativeModel('gemini-1.5-flash')
        model = genai.GenerativeModel('gemini-2.0-flash-lite-001')

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
# chunk = "This is just an sample test case"
# keyword = "case"
# company = "test"
# x = explain(chunk,keyword,company)
# print(x)
# """