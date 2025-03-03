from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGODB_URI)
db = client[settings.DB_NAME]

requests_collection = db["requests"]
products_collection = db["products"]
