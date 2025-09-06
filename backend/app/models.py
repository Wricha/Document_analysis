from pydantic import BaseModel
from typing import List, Optional

class Vendor(BaseModel):
    name: str
    address: str
    city: str
    phone: str
    email: str

class BillTo(BaseModel):
    name: str
    address: str
    city: str

class Item(BaseModel):
    description: str
    quantity: float
    unitPrice: float
    total: float

class InvoiceData(BaseModel):
    invoiceNumber: str
    date: str
    dueDate: Optional[str] = None
    vendor: Vendor
    billTo: BillTo
    items: List[Item]
    subtotal: float
    tax: float
    total: float
    paymentTerms: Optional[str] = None

class ExtractResponse(BaseModel):
    doc_id: str
    data: Optional[InvoiceData] = None
