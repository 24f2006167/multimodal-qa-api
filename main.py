import os
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Step A: CORS enable karo - taaki Cloudflare Worker se grader call kar sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # sabko allow karo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step B: aipipe.org client setup
client = OpenAI(
    api_key=os.environ.get("AIPIPE_TOKEN"),   # token yahan se aayega (env var)
    base_url="https://aipipe.org/openai/v1",
)

# Step C: Request ka shape define karo
class ImageQuestion(BaseModel):
    image_base64: str
    question: str


@app.post("/answer-image")
async def answer_image(payload: ImageQuestion):
    # image_base64 kabhi kabhi "data:image/png;base64,...." format mein aata hai
    # agar aisa hai to sirf base64 wala part rakho
    img_b64 = payload.image_base64.strip()
    if "," in img_b64 and img_b64.strip().startswith("data:"):
        img_b64 = img_b64.split(",", 1)[1]

    # Multimodal model ko image + question bhejo
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,   # deterministic answers - randomness nahi chahiye
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise data-extraction assistant. You will be shown an "
                    "image and a question about it. Respond with ONLY the raw answer - "
                    "no explanations, no full sentences, no labels like 'Answer:'. "
                    "If the answer is a number, give ONLY the digits and decimal point "
                    "exactly as shown in the image (e.g. 495.00 stays 495.00, do not "
                    "round or reformat). No currency symbols (₹ $ € £), no commas, no "
                    "units (kg, %, etc.), no extra words. "
                    "If the answer is a name, category, or label, give ONLY that text, "
                    "plain, with no extra punctuation or explanation."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": payload.question,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        },
                    },
                ],
            },
        ],
    )

    answer_text = response.choices[0].message.content.strip()

    # Safety cleanup - agar model phir bhi extra cheezein de de
    answer_text = answer_text.strip('"').strip("'")
    answer_text = answer_text.replace(",", "")
    for symbol in ["₹", "$", "€", "£"]:
        answer_text = answer_text.replace(symbol, "")

    # Agar model ne multi-line ya extra explanation de diya ho, pehli line hi rakho
    if "\n" in answer_text:
        answer_text = answer_text.split("\n")[0].strip()

    # Agar model ne "Answer: X" jaisa format diya ho
    if ":" in answer_text and len(answer_text.split(":")[0]) < 15:
        answer_text = answer_text.split(":", 1)[1].strip()

    answer_text = answer_text.strip()

    return {"answer": answer_text}


@app.get("/")
def health_check():
    return {"status": "ok"}