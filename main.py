import os
from fastapi import FastAPI
from google.generativeai import GenerativeModel
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))


app = FastAPI(title="Gemini Test API")

# Gemini設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found")

genai.configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel("gemini-2.5-pro")  # まず安定版で

@app.get("/")
async def root():
    return {"message": "Gemini Test API"}

@app.get("/test")
async def test_gemini():
    try:
        response = model.generate_content("Hello, how are you?")
        return {
            "success": True,
            "response": response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/analyze")
async def analyze_company(company_name: str):
    try:
        prompt = f"{company_name}について100文字程度で説明してください。"
        response = model.generate_content(prompt)
        return {
            "success": True,
            "company": company_name,
            "analysis": response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
