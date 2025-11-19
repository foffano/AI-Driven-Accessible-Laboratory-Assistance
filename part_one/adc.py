import os
import base64
import requests
import csv
import time
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATIONS ---

# Replace with your OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") 

# Name of the folder containing the images
DATASET_FOLDER = "dataset"

# The prompt that will be sent together with each image
PROMPT_TEXT = "You are a helpful and friendly lab assistant. Describe what you see in the image. If you detect any safety hazards, include a brief educational alert. Limit your response to a maximum of 30 words."

# Internal list of models to test
# You may add or remove models depending on availability in OpenRouter
MODEL_LIST = [
    "google/gemini-2.5-flash",
]

# OpenRouter API URL
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- HELPER FUNCTIONS ---

def encode_image(image_path):
    """Reads an image file and converts it to a Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_image_files(folder):
    """Returns a list of image files in the folder."""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    return [f for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]

def analyze_image(model, base64_image, prompt):
    """Sends the request to the API."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Optional headers recommended by OpenRouter
        "HTTP-Referer": "http://localhost:8000", 
        "X-Title": "Dataset Analysis Script",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raises error if status is not 200 OK
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error while processing model {model}: {e}")
        return f"ERROR: {str(e)}"

# --- MAIN BLOCK ---

def main():
    # Check if the folder exists
    if not os.path.exists(DATASET_FOLDER):
        print(f"Error: Folder '{DATASET_FOLDER}' not found.")
        return

    images = get_image_files(DATASET_FOLDER)
    
    if not images:
        print(f"No images found in folder '{DATASET_FOLDER}'.")
        return

    print(f"Found {len(images)} images. Starting analysis using {len(MODEL_LIST)} models...")

    # Loop through models
    for model in MODEL_LIST:
        # Create a safe filename (replace / with _)
        safe_model_name = model.replace("/", "_")
        csv_filename = f"results_{safe_model_name}.csv"
        
        print(f"\n--- Starting model: {model} ---")
        print(f"Saving to: {csv_filename}")

        # Open CSV file for writing
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # CSV header
            writer.writerow(["image_id", "prompt", "model", "response"])

            # Loop through images
            for img_name in images:
                img_path = os.path.join(DATASET_FOLDER, img_name)
                
                print(f"Processing {img_name} with {model}...")
                
                # 1. Encode image
                base64_img = encode_image(img_path)
                
                # 2. Send request
                res_text = analyze_image(model, base64_img, PROMPT_TEXT)
                
                # 3. Save row in CSV
                writer.writerow([img_name, PROMPT_TEXT, model, res_text])
                
                # Small delay to avoid aggressive rate limiting
                time.sleep(1) 

    print("\nProcess completed! Check the generated .csv files.")

if __name__ == "__main__":
    main()
