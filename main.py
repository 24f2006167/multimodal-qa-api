import os
import base64
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# 1. Initialize FastAPI app
app = FastAPI()

# 2. Enable CORS (Required so the external assignment grader can access your API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# 3. Define the expected incoming JSON structure
class RequestBody(BaseModel):
    image_base64: str
    question: str

# 4. Initialize the Gemini Client
# It automatically looks for an environment variable named GEMINI_API_KEY
client = genai.Client()

@app.post("/answer-image")
async def answer_image(body: RequestBody):
    try:
        # Step A: Clean up the Base64 string if it contains metadata prefixes
        base64_data = body.image_base64
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
            
        # Step B: Convert the Base64 text string into raw binary image bytes
        image_bytes = base64.b64decode(base64_data)
        
        # Step C: Format the image bytes specifically for the Google GenAI SDK
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png",  # Defaulting to PNG
        )
        
        # Step D: Structure a strict system instruction prompt for the model
        system_prompt = (
            "You are an expert data extraction assistant. "
            "Analyze the provided image and answer the user's question accurately. "
            "CRITICAL RULE: If the answer is a number, amount, or value, return ONLY the raw numeric digits "
            "(e.g., '4089.35'). Do NOT include currency symbols like $, ₹, €, commas, or text units."
        )
        
        # Step E: Send the image and question to Gemini 2.5 Flash
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image_part, body.question],
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.0, # Zero temperature ensures deterministic, factual extraction
            )
        )
        
        # Step F: Extract and clean the textual answer
        final_answer = response.text.strip()
        
        # Return the required JSON response structure
        return {"answer": final_answer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
