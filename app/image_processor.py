import os
from PIL import Image
import requests
from io import BytesIO

def ensure_directory_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_image(image_url: str, output_filename: str):
    output_directory = './static/uploads'
    ensure_directory_exists(output_directory)
    output_path = os.path.join(output_directory, output_filename)
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img.save(output_path, "JPEG", quality=50)

    return output_path
