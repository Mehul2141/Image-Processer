from app.database import requests_collection, products_collection
import requests
from requests.exceptions import HTTPError

def trigger_webhook(request_id: str, webhook_url: str):
    products = list(products_collection.find({"request_id": request_id}))
    
    if not products:
        raise HTTPError(status_code=404, detail="Request ID not found")
    
    results = []
    for product in products:
        result = {}
        result["serial_number"] = product["serial_number"]
        result["product_name"] = product["product_name"]
        result["input_image_urls"] = product["input_image_urls"]
        result["output_image_urls"] = product["output_image_urls"]
        results.append(result)
      
    data = {
        "request_id": request_id,
        "results": results
    }
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print(f"Webhook sent successfully for {request_id}")
        else:
            print(f"Failed to send webhook for {request_id}")
    except Exception as e:
        print(f"Error sending webhook: {e}")
