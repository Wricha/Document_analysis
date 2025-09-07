from uuid import uuid4
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.upload import extract_text_from_doc
from app.models import ExtractResponse
from app.db import documents_collection
from app.models import InvoiceData
from fastapi.encoders import jsonable_encoder
app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload", response_model=ExtractResponse)
async def upload_document(file: UploadFile = File(...)):

    try:
        result = extract_text_from_doc(file)
        documents_collection.insert_one({
        "doc_id" : result["doc_id"],   
        "filename" : file.filename,
        "data" : result["data"],
        "created_at" : datetime.utcnow(),
        
    })  

        return result

    except Exception as e:
        print("Error occurred while uploading document:", e)
        return {"error": "Failed to upload document"}

@app.get("/invoices")
def get_invoices():
    try:
        invoices = list(documents_collection.find().limit(100))

        structured_invoices = []
        for inv in invoices:
            if inv.get("data"):
                structured_invoices.append(inv["data"])

        print("Structured invoices from DB:", structured_invoices) #print invoices fetched from db

        return structured_invoices

    except Exception as e:
        print("Error fetching invoices:", e)
        return []