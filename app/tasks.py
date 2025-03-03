from celery import Celery
from app.image_processor import process_image
from app.database import requests_collection, products_collection
from app.utils import generate_unique_id
import datetime
from app.config import settings


def process_images(request_id: str):
    products = list(products_collection.find({"request_id": request_id}))
    processed_images = []
    for product in products:
        for idx, image_url in enumerate(product['input_image_urls']):
            output_filename = f"{product['product_name']}_{idx}.jpg"
            process_image(image_url, output_filename)
            output_url = f"{settings.IMAGE_UPLOAD_PATH}/{output_filename}"
            processed_images.append(output_url)
        products_collection.update_one(
            {"_id": product["_id"]},
            {"$set": {"output_image_urls": processed_images}}
        )
    requests_collection.update_one(
        {"request_id": request_id},
        {"$set": {"status": "completed", "completed_at": datetime.datetime.now()}}
    )
