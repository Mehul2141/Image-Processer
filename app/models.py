from pydantic import BaseModel
from typing import List, Optional

class ProductInput(BaseModel):
    serial_number: int
    product_name: str
    input_image_urls: List[str]

class RequestResponse(BaseModel):
    request_id: str

class StatusResponse(BaseModel):
    total_requests: int
    total_completed_requests: int
    total_pending_requests: int
    results: List
    
