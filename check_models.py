import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Set GOOGLE_API_KEY in .env file")
    exit()

genai.configure(api_key=api_key)

print("🔍 Checking available Gemini models...\n")

try:
    models = genai.list_models()
    
    print("✅ Available models for generateContent:")
    print("-" * 50)
    
    gemini_models = []
    for model in models:
        if "gemini" in model.name.lower():
            if 'generateContent' in model.supported_generation_methods:
                gemini_models.append(model.name)
                print(f"• {model.name}")
                print(f"  Methods: {model.supported_generation_methods}")
                print()
    
    if gemini_models:
        print(f"\n🎯 Recommended: Try using '{gemini_models[0]}'")
    else:
        print("❌ No Gemini models found with generateContent support")
        
except Exception as e:
    print(f"❌ Error: {e}")