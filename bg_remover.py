# Created At: 2024-10-22
# Author: Sanath Narasimhan
# Reference: https://www.remove.bg/api#sample-code

import os
from PIL import Image
import requests
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def initialize_api_key():
    return os.getenv('REMOVE_BG_API_KEY')

def remove_background(image_path, api_key):
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open(image_path, 'rb')},
        data={'size': 'auto'},
        headers={'X-Api-Key': api_key},
    )
    if response.status_code == requests.codes.ok:
        """
        with open('no-bg.png', 'wb') as out:
            out.write(response.content)
        """
        return response.content #'no-bg.png'
    else:
        print("Error:", response.status_code, response.text)
        return None


# Function to show images in a directory and process them
def process_images_in_directory(directory, api_key):
    # List all files in the directory
    for filename in os.listdir(directory):
        # Check if the file is an image (you can extend the supported extensions)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(directory, filename)
            
            # Open and display the image
            image = Image.open(image_path)
            print(f"Displaying: {filename}")
            image.show()
            
            # Pass the image to remove_background function
            result_image_path = remove_background(image_path, api_key)
            
            # If the background removal was successful, display the new image
            if result_image_path:
                print(f"Displaying image with background removed: {result_image_path}")
                result_image = Image.open(result_image_path)
                result_image.show()
                return result_image

# Example usage:
api_key = initialize_api_key()
"""
directory = 'samples'  # Replace with your image directory
process_images_in_directory(directory, api_key)

"""

def remove_background_from_image(image: Image, api_key):
    # Convert the image to bytes for the API call
    img_byte_arr = io.BytesIO()  # Create an in-memory bytes buffer
    image.save(img_byte_arr, format="PNG")  # Save the image in the buffer in the specified format
    img_byte_arr.seek(0)  # Reset the pointer to the start of the buffer
    image_bytes = img_byte_arr.getvalue()  # Get the bytes

    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': image_bytes},
        data={'size': 'auto'},
        headers={'X-Api-Key': api_key},
    )
    if response.status_code == requests.codes.ok:
        """
        with open('no-bg.png', 'wb') as out:
            out.write(response.content)
        """
        return response.content 
    else:
        print("Error:", response.status_code, response.text)
        return None