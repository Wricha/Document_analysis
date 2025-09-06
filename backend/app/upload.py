# app/extractor.py
import re
import uuid
import base64
import os
from fastapi import UploadFile
from together import Together
from dotenv import load_dotenv
import json
from uuid import uuid4
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Together client
client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"


def extract_text_from_doc(file: UploadFile) -> dict:
    """
    Uploads document image, sends it to Together API (Qwen2-VL),
    returns structured JSON with invoice details.
    """
    doc_id = str(uuid.uuid4())

    # Read and base64 encode the file
    file_bytes = file.file.read()
    base64_str = base64.b64encode(file_bytes).decode("utf-8")
    try:
    # Send the image to Qwen2-VL model
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Extract fields and return ONLY valid JSON (no markdown, no explanation). Schema:

                        {
                        "invoiceNumber": "...",
                        "date": "...",
                        "dueDate": "...",
                        "vendor": {
                            "name": "...",
                            "address": "...",
                            "city": "...",
                            "phone": "...",
                            "email": "..."
                        },
                        "billTo": {
                            "name": "...",
                            "address": "...",
                            "city": "..."
                        },
                        "items": [
                            {
                            "description": "...",
                            "quantity": 0,
                            "unitPrice": 0.0,
                            "total": 0.0
                            }
                        ],
                        "subtotal": 0.0,
                        "tax": 0.0,
                        "total": 0.0,
                        "paymentTerms": "..."
                        }
                        """
                        },
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_str}"}}
                    ],
                    
                    
                }
            ]
        )
        raw_output = completion.choices[0].message.content.strip()
        clean_output = re.sub(r"^```(json)?|```$", "", raw_output, flags=re.MULTILINE).strip()

        try:
            structured_json = json.loads(clean_output)
            print("Structured JSON:", structured_json)
        except json.JSONDecodeError:
            print("Model did not return valid JSON, got:", clean_output)
            structured_json = {"error": "Invalid JSON from model", "raw": clean_output}

    # Return doc_id + structured data
        return {"doc_id": doc_id, "data": structured_json}

    except Exception as e:
        print("Error occurred while extracting text:", e)
        return {"doc_id": doc_id, "data": None, "error": str(e)}

    
    
