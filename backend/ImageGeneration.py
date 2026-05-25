import asyncio
from random import randint
import requests
from dotenv import load_dotenv, get_key
import os
import subprocess
from time import sleep
import re

# Load environment variables
load_dotenv()

# Define Hugging Face API endpoint and headers
API_URL = "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HUGGINGFACE_API_KEY')}"}

# Folder where images will be saved
folder_path = "data/Images"

def sanitize_filename(prompt):
    # Remove parentheses and other illegal filename characters
    return re.sub(r'[\\/*?:"<>|()]', '', prompt).replace(" ", "_")

# Query function to send request to Hugging Face
async def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print(f"API Error {response.status_code}: {response.text}")
        return b''  # Return empty bytes if failed

# Open and show the generated images
def open_image(prompt):
    clean_prompt = sanitize_filename(prompt)
    Files = [f"{clean_prompt}_{i}.jpg" for i in range(1, 5)]
    
    is_termux = "TERMUX_VERSION" in os.environ

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        if not os.path.exists(image_path):
            continue
            
        try:
            print(f"Image saved at: {image_path}")
            if is_termux:
                # Try termux-open
                subprocess.run(["termux-open", image_path], capture_output=True)
            else:
                # Use default system opener for other OS
                subprocess.run(["xdg-open", image_path], capture_output=True) # Linux
                subprocess.run(["open", image_path], capture_output=True) # MacOS
                subprocess.run(["start", image_path], shell=True, capture_output=True) # Windows
            sleep(1)
        except Exception as e:
            print(f"Could not open image {image_path}: {e}")

# Asynchronous image generation function
async def generate_images(prompt: str):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder created: {os.path.abspath(folder_path)}")
    tasks = []
    clean_prompt = sanitize_filename(prompt)

    # Create 4 asynchronous generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks to complete
    image_bytes_list = await asyncio.gather(*tasks)

    # Save images
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # Only save if not empty
            filename = f"{clean_prompt}_{i + 1}.jpg"
            save_path = os.path.join(folder_path, filename)
            with open(save_path, "wb") as f:
                f.write(image_bytes)

# Wrapper for image generation and display
def GenerateImage(prompt: str):
    asyncio.run(generate_images(prompt))
    open_image(prompt)

# Main polling loop
if __name__ == "__main__":
    while True:
        try:
            with open(os.path.join("data", "Files", "ImageGeneration.data"), "r") as file:
                Data: str = file.read().strip()

            Prompt, Status = Data.split(",")

            if Status.strip().lower() == "true":
                print("Generating Images .....")
                GenerateImage(Prompt.strip())

                with open(os.path.join("data", "Files", "ImageGeneration.data"), "w") as file:
                    file.write("False,False")
                break
            else:
                sleep(1)

        except Exception as e:
            print(f"Error: {e}")
            sleep(1)