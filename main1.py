from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import openai
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

memory = []  # Simple in-memory storage (reset on restart)

class Message(BaseModel):
    user_input: str

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(msg: Message):
    memory.append({"role": "user", "content": msg.user_input})

    prompt = [
        {"role": "system", "content": "Kamu adalah asisten pintar untuk mencatat dan mengatur tugas harian."},
        *memory
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt,
        temperature=0.7
    )

    reply = response['choices'][0]['message']['content']
    memory.append({"role": "assistant", "content": reply})

    return {"reply": reply}