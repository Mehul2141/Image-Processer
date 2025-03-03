from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from app.database import requests_collection, products_collection
from app.models import ProductInput, RequestResponse, StatusResponse
from app.image_processor import process_image
from app.utils import generate_unique_id
from app.webhook import trigger_webhook
import csv
from io import StringIO
import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/upload", response_model=RequestResponse)
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    contents = await file.read()
    file_contents = contents.decode("utf-8")
    csv_file = StringIO(file_contents)
    reader = csv.DictReader(csv_file)

    request_id = generate_unique_id()

    for row in reader:
        if not row["Product Name"] or not row["Input Image Urls"]:
            raise HTTPException(status_code=400, detail="Invalid CSV format.")
        
        product = ProductInput(
            serial_number=row["S. No."],
            product_name=row["Product Name"],
            input_image_urls=row["Input Image Urls"].split(",")
        )
        
        product_dict = product.dict()
        product_dict["request_id"] = request_id
        products_collection.insert_one(product_dict)
        
        request_dict = {}
        request_dict["serial_number"] = product_dict["serial_number"]
        request_dict["product_name"] = product_dict["product_name"]
        request_dict["request_id"] = request_id
        request_dict["status"] = "pending"
        request_dict["submitted_at"] = datetime.datetime.now()
        requests_collection.insert_one(request_dict)
    
    background_tasks.add_task(process_images, request_id)
    return {"request_id": request_id}

@app.get("/status", response_model=StatusResponse)
async def check_status(request_id: str):
    products = list(products_collection.find({"request_id": request_id}))
    
    total_requests = len(products)
    if not products:
        raise HTTPException(status_code=404, detail="Request ID not found")
    
    total_completed_requests = 0
    final_response = {}
    final_response["results"] = []
    for product in products:
        request = requests_collection.find_one({"product_name": product["product_name"]})
        result = {}
        result["serial_number"] = product["serial_number"]
        result["product_name"] = product["product_name"]
        result["input_image_urls"] = product["input_image_urls"]
        result["process_details"] = {"status": request["status"], "submitted_at": request["submitted_at"], "completed_at": "", "output_image_urls": []}
        if request["status"] == "completed":
            result["process_details"]["completed_at"] = request["completed_at"]
            result["process_details"]["output_image_urls"] = product["output_image_urls"]
            total_completed_requests += 1 
        final_response["results"].append(result) 
    
    final_response["total_requests"] = total_requests
    final_response["total_completed_requests"] = total_completed_requests
    final_response["total_pending_requests"] = total_requests - total_completed_requests 
    
    return final_response  

@app.post("/trigger-webhook/{request_id}")
async def trigger_webhook_endpoint(request_id: str, webhook_url: str):
    requests = requests_collection.find({"request_id": request_id})
    for request in requests:
        if request["status"] != "completed":
            raise HTTPException(status_code=400, detail="Request is not completed yet") 
    trigger_webhook(request_id, webhook_url)
    return {"message": "Webhook triggered successfully"}
        
    
async def process_images(request_id: str):
    products = list(products_collection.find({"request_id": request_id}))
    
    for product in products:
        product_proccessed_images = []
        for idx, image_url in enumerate(product['input_image_urls']):
            output_filename = f"{product['product_name']}_{idx}.jpg"
            process_image(image_url, output_filename) 
            output_url = f"http://localhost:8000/static/uploads/{output_filename}"
            product_proccessed_images.append(output_url)
        
        products_collection.update_one(
            {"_id": product["_id"]},
            {"$set": {"output_image_urls": product_proccessed_images}}
        )
        requests_collection.update_one(
            {"product_name": product['product_name']},
            {"$set": {"status": "completed", "completed_at": datetime.datetime.now()}}
        )
    
