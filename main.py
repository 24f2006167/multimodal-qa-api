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
    img_b64 = payload.image_base64
    if "," in img_b64 and img_b64.strip().startswith("data:"):
        img_b64 = img_b64.split(",", 1)[1]

    # Multimodal model ko image + question bhejo
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # ye vision support karta hai
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Look at this image carefully and answer this question: "
                            f"{payload.question}\n\n"
                            f"IMPORTANT: Reply with ONLY the answer itself. "
                            f"If it's a number, give just the number (no currency "
                            f"symbols, no units, no extra words)."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        },
                    },
                ],
            }
        ],
    )

    answer_text = response.choices[0].message.content.strip()

    return {"answer": answer_text}


@app.get("/")
def health_check():
    return {"status": "ok"}