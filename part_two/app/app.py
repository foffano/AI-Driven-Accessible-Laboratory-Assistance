import os
import cv2
import threading
import base64
import time
import requests
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from queue import Queue
import requests
import json
from PIL import Image
import numpy as np
import errno
from gtts import gTTS
import csv
import pygame
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.json')

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        "api_key": os.getenv('OPENROUTER_API_KEY', ''),
        "model": "google/gemini-2.0-flash-exp:free",
        "prompt": "You are a helpful and friendly lab assistant. Describe what you see in the image. If you detect any safety hazards, include a brief educational alert. Limit your response to a maximum of 30 words."
    }

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# Load initial settings
current_settings = load_settings()

YOUR_SITE_URL = 'http://localhost:5001'
YOUR_SITE_NAME = 'Laboratory Assistant'

# Folders to save frames, audios, and CSV file
frame_folder = "frames"
audio_folder = "audio_responses"
csv_file = "results.csv"

# Ensure folders exist
if not os.path.exists(frame_folder):
    os.makedirs(frame_folder)
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Queue to store text responses
text_queue = Queue()

# Flag to indicate when audio playback is in progress
audio_playing = threading.Event()

# Global variables
running = True
latest_encoded_image = None
script = []

def generate_audio(text, filename):
    tts = gTTS(text, lang='pt-br')
    tts.save(filename)
    print(f"Audio saved to {filename}")

def play_audio():
    global audio_playing
    while True:
        text = text_queue.get()
        if text is None:
            break
        audio_playing.set()
        try:
            audio_files = [f for f in os.listdir(audio_folder) if f.endswith('.mp3')]
            if audio_files:
                latest_audio_file = max(audio_files, key=lambda x: os.path.getctime(os.path.join(audio_folder, x)))
                audio_path = os.path.abspath(os.path.join(audio_folder, latest_audio_file))
                pygame.mixer.init()
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
                print(f"Playing audio: {audio_path}")
            else:
                print("No audio files found.")
        except Exception as e:
            print(f"Error in play_audio: {e}")
        finally:
            audio_playing.clear()

def generate_new_line(encoded_image, prompt_text):
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encoded_image}"
                    }
                }
            ]
        }
    ]

def analyze_image(encoded_image, script):
    global current_settings
    try:
        # Refresh settings in case they were changed
        current_settings = load_settings()
        
        api_key = current_settings.get('api_key') or os.getenv('OPENROUTER_API_KEY')
        model = current_settings.get('model', "google/gemini-2.0-flash-exp:free")
        prompt = current_settings.get('prompt', "You are a helpful and friendly lab assistant...")

        messages = script + generate_new_line(encoded_image, prompt)
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            data=json.dumps({
                "model": model,
                "messages": messages
            })
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return ""

def capture_images():
    global running
    global latest_encoded_image
    cap = cv2.VideoCapture(0)

    while running:
        try:
            ret, frame = cap.read()
            if ret:
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                max_size = 250
                ratio = max_size / max(pil_img.size)
                new_size = tuple([int(x * ratio) for x in pil_img.size])
                resized_img = pil_img.resize(new_size, Image.LANCZOS)
                frame_resized = cv2.cvtColor(np.array(resized_img), cv2.COLOR_RGB2BGR)

                # Encode image to base64 string
                _, buffer = cv2.imencode('.jpg', frame_resized)
                encoded_image = base64.b64encode(buffer.tobytes()).decode('utf-8')
                
                latest_encoded_image = encoded_image
                socketio.emit('stream', {'image': encoded_image})
                
            else:
                print("Failed to capture image")

            time.sleep(0.05) # Faster refresh rate for smoother video
        except Exception as e:
            print(f"Error in capture_images: {e}")
    cap.release()

def save_results_to_csv(results, csv_path):
    try:
        with open(csv_path, mode='a', newline='', encoding='utf-8') as file: # Changed to append mode 'a'
            writer = csv.writer(file)
            if os.stat(csv_path).st_size == 0:
                writer.writerow(['Image Name', 'Response', 'Audio Filename'])
            for result in results:
                writer.writerow(result)
        print(f"Results saved to {csv_path}")
    except Exception as e:
        print(f"Error in save_results_to_csv: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stop')
def stop():
    global running
    running = False
    return jsonify({"status": "stopped"})

@app.route('/resume')
def resume():
    global running
    global capture_thread
    running = True
    if not capture_thread.is_alive():
        capture_thread = threading.Thread(target=capture_images)
        capture_thread.start()
    return jsonify({"status": "resumed"})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global current_settings
    if request.method == 'POST':
        new_settings = request.json
        save_settings(new_settings)
        current_settings = new_settings
        return jsonify({"status": "success", "message": "Settings saved"})
    else:
        return jsonify(load_settings())

@app.route('/analyze', methods=['POST'])
def analyze():
    global latest_encoded_image
    global script
    
    if not latest_encoded_image:
        return jsonify({"status": "failed", "message": "No image available"}), 400

    try:
        image_id = int(time.time())
        image_name = f"frame_{image_id}.jpg"
        image_path = os.path.join(frame_folder, image_name)
        
        # Decode and save the image for record
        with open(image_path, "wb") as fh:
            fh.write(base64.b64decode(latest_encoded_image))
        print(f"📸 Saving photo: {image_path}")

        response_text = analyze_image(latest_encoded_image, script)
        print(f"Response: {response_text}")

        with text_queue.mutex:
            text_queue.queue.clear()

        text_queue.put(response_text)
        socketio.emit('text', {'message': response_text})
        script.append(
            {
                "role": "assistant",
                "content": response_text
            }
        )

        audio_filename = f"audio_{image_id}.mp3"
        audio_path = os.path.join(audio_folder, audio_filename)
        generate_audio(response_text, audio_path)
        
        results = [(image_name, response_text, audio_filename)]
        save_results_to_csv(results, csv_file)

        return jsonify({"status": "success", "message": response_text})
    except Exception as e:
        print(f"Error during analysis: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

import webbrowser

if __name__ == '__main__':
    global capture_thread
    global audio_thread
    running = True
    capture_thread = threading.Thread(target=capture_images)
    capture_thread.start()
    audio_thread = threading.Thread(target=play_audio)
    audio_thread.start()
    webbrowser.open('http://localhost:5001')
    socketio.run(app, host='0.0.0.0', port=5001)
    capture_thread.join()
    text_queue.put(None)
    audio_thread.join()
