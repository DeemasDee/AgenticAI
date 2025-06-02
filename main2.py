from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import httpx # For making asynchronous HTTP requests

app = FastAPI()

# Mount static files (e.g., CSS, JS for the frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates to serve HTML files
templates = Jinja2Templates(directory="templates")

# Simple in-memory storage for chat history.
# This will be reset every time the FastAPI application restarts.
memory = []

class Message(BaseModel):
    """
    Pydantic model for incoming chat messages, ensuring the user_input is a string.
    """
    user_input: str

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """
    Handles the root URL ("/") and serves the main HTML page (index.html).
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(msg: Message):
    """
    Handles incoming chat messages, interacts with the Gemini API,
    and stores the conversation history in memory.
    """
    # Append the user's message to the in-memory chat history
    memory.append({"role": "user", "parts": [{"text": msg.user_input}]})

    # Construct the payload for the Gemini API request
    # The 'contents' field holds the conversation history
    payload = {
        "contents": memory
    }

    # The API key for Gemini. Leave this as an empty string;
    # the Canvas environment will provide it at runtime.
    api_key = "AIzaSyAG-XdQHYNw6Zs4SYU2tZ_sO5VCXbhDez8"
    # The URL for the Gemini 2.0 Flash model
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    try:
        # Use httpx for making asynchronous HTTP requests
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                headers={'Content-Type': 'application/json'},
                json=payload
            )
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        result = response.json()

        # Extract the generated text from the Gemini API response
        if result.get('candidates') and len(result['candidates']) > 0 and \
           result['candidates'][0].get('content') and \
           result['candidates'][0]['content'].get('parts') and \
           len(result['candidates'][0]['content']['parts']) > 0:
            reply = result['candidates'][0]['content']['parts'][0]['text']
        else:
            reply = "Maaf, saya tidak dapat menghasilkan respons saat ini."
            print(f"Unexpected Gemini API response structure: {result}")

        # Append the assistant's reply to the chat history
        memory.append({"role": "assistant", "parts": [{"text": reply}]})

        # Return the assistant's reply to the frontend
        return {"reply": reply}

    except httpx.RequestError as e:
        print(f"Error making request to Gemini API: {e}")
        return {"reply": "Maaf, terjadi kesalahan saat menghubungi layanan AI."}
    except httpx.HTTPStatusError as e:
        print(f"HTTP error from Gemini API: {e.response.status_code} - {e.response.text}")
        return {"reply": "Maaf, layanan AI mengembalikan kesalahan."}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"reply": "Maaf, terjadi kesalahan internal."}

