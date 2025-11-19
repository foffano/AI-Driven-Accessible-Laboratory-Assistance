import os
import cv2
import base64
import time
import requests
from flask_socketio import emit
import config

frame_folder = "../frames"
if not os.path.exists(frame_folder):
    os.makedirs(frame_folder)

# OpenRouter API endpoint
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

latest_encoded_image = None
script = []



def generate_new_line(encoded_image):
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": config.system_prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }
        ]
    }

def analyze_image(encoded_image):
    global script
    try:
        messages = script + [generate_new_line(encoded_image)]

        headers = {
            "Authorization": f"Bearer {config.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5001", # Replace with your actual site URL
            "X-Title": "Gemini CLI App", # Replace with your actual site name
        }

        payload = {
            "model": config.model_name,
            "messages": messages
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for HTTP errors
        
        response_data = response.json()
        if response_data and response_data.get("choices"):
            response_text = response_data["choices"][0]["message"]["content"]
            script.append({
                "role": "assistant",
                "content": response_text
            })
            return response_text
        return ""
    except requests.exceptions.RequestException as e:
        print(f"Error in analyze_image (HTTP request): {e}")
        if e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return ""
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return ""

def capture_images(socketio):
    global latest_encoded_image
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        try:
            ret, frame = cap.read()
            if ret:
                # Calculate new dimensions to maintain aspect ratio
                h, w, _ = frame.shape
                max_size = 250
                if max(h, w) > max_size:
                    scale = max_size / float(max(h, w))
                    new_w, new_h = int(w * scale), int(h * scale)
                    frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

                # Encode the frame directly without saving to disk
                _, buffer = cv2.imencode('.jpg', frame)
                encoded_image = base64.b64encode(buffer).decode("utf-8")
                
                if not encoded_image:
                    print("Failed to encode image. Retrying in 1 second...")
                    time.sleep(1)
                    continue

                latest_encoded_image = encoded_image
                print("Emitting frame to stream...")
                socketio.emit('stream', {'image': encoded_image})
                
            else:
                print("Failed to capture image")

            # A small sleep to prevent high CPU usage
            time.sleep(0.05)
        except Exception as e:
            print(f"Error in capture_images: {e}")
    cap.release()