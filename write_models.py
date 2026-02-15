import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

try:
    with open('models_list.txt', 'w') as f:
        models = list(genai.list_models())
        f.write(f"Total models found: {len(models)}\n")
        for m in models:
            f.write(f"MODEL_ID: {m.name}\n")
    print("Models written to models_list.txt")
except Exception as e:
    print(f"ERROR: {e}")
