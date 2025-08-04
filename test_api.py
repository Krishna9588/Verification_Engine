import os
import google.generativeai as genai

# ✅ Fix: Set API Key Correctly
API_KEY = "" # working
os.environ["GEMINI_API_KEY"] = API_KEY
# ✅ Fix: Pass API Key Correctly
genai.configure(api_key=API_KEY)

# ✅ Fix: Ensure Model is Set Correctly
model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Fix: Ensure API Call is Valid
response = model.generate_content("Test response from Gemini AI")

# ✅ Print Output
print(response.text)

# from dotenv import load_dotenv
# import os
#
# load_dotenv()  # Load environment variables from .env file
#
# api_key = os.getenv("GEMINI_API_KEY")
# print("API key set successfully!" if api_key else "API key NOT found!")
# print(f"API_key from .env {api_key}")

