from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

app = FastAPI()

# Enable CORS (ubah allow_origins jika frontend berada di domain tertentu)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain frontend untuk keamanan
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory chat history
memory = []

# API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Message(BaseModel):
    user_input: str

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(msg: Message):
    memory.append({"role": "user", "parts": [{"text": msg.user_input}]})

    payload = {
        "contents": memory
    }

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                headers={'Content-Type': 'application/json'},
                json=payload
            )
            response.raise_for_status()

        result = response.json()

        # Safely extract Gemini response
        candidates = result.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts:
                reply = parts[0].get("text", "Maaf, tidak ada respons.")
            else:
                reply = "Maaf, tidak dapat mengambil balasan dari AI."
        else:
            reply = "Maaf, AI tidak memberikan balasan."

        memory.append({"role": "assistant", "parts": [{"text": reply}]})
        return {"reply": reply}

    except httpx.RequestError as e:
        print(f"Request error: {e}")
        return {"reply": "Maaf, terjadi kesalahan saat menghubungi layanan AI."}
    except httpx.HTTPStatusError as e:
        print(f"HTTP status error: {e.response.status_code} - {e.response.text}")
        return {"reply": "Maaf, layanan AI mengembalikan kesalahan."}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"reply": "Maaf, terjadi kesalahan internal."}
