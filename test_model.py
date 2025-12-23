import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Test with available model
model = genai.GenerativeModel('models/gemini-2.0-flash')
response = model.generate_content("Say hello if you're working")
print(f"✅ Model response: {response.text}")