import os
import cv2
import threading
import base64
import time
import requests
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from queue import Queue
import google.generativeai as genai
from PIL import Image
import numpy as np
import errno
from gtts import gTTS
import csv
import pygame

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Set the API key for Google AI
GOOGLE_API_KEY = 'YOUR_API_KEY'

# Configure the Google AI client
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

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
capture_interval = 2  # Default interval in seconds

def encode_image(image_path):
    while True:
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
        except IOError as e:
            if e.errno == errno.EACCES:
                print("Permission denied, retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Error {e.errno}: {e.strerror}")
                return None

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

def generate_new_line(encoded_image):
    return [
        {
            "role": "user",
            "content": {
                "parts": [
                    {
                        "text": "Por favor, descreva o que você vê em no máximo 30 palavras. Você é um assistente útil e amigável de laboratório. Se você visualizar situações perigosas, alerte de forma educativa!"
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": encoded_image
                        }
                    }
                ]
            }
        }
    ]

def analyze_image(encoded_image, script):
    try:
        messages = script + generate_new_line(encoded_image)
        content_messages = [
            {
                "role": message["role"],
                "parts": [
                    {"text": part["text"]} if "text" in part else {"inline_data": part["inline_data"]}
                    for part in message["content"]["parts"]
                ]
            }
            for message in messages
        ]
        response = model.generate_content(content_messages)
        return response.text
    except Exception as e:
        print(f"Error in analyze_image: {e}")
        return ""

def capture_images():
    global capture_interval
    global script
    script = []
    cap = cv2.VideoCapture(0)
    results = []

    while running:
        try:
            ret, frame = cap.read()
            if ret:
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                max_size = 250
                ratio = max_size / max(pil_img.size)
                new_size = tuple([int(x * ratio) for x in pil_img.size])
                resized_img = pil_img.resize(new_size, Image.LANCZOS)
                frame = cv2.cvtColor(np.array(resized_img), cv2.COLOR_RGB2BGR)

                image_id = int(time.time())
                image_name = f"frame_{image_id}.jpg"
                image_path = os.path.join(frame_folder, image_name)
                cv2.imwrite(image_path, frame)
                print(f"📸 Saving photo: {image_path}")

                encoded_image = encode_image(image_path)
                print(f"Encoded image: {encoded_image[:30]}...")

                if not encoded_image:
                    print("Failed to encode image. Retrying in 5 seconds...")
                    time.sleep(5)
                    continue

                socketio.emit('stream', {'image': encoded_image})
                
                response_text = analyze_image(encoded_image, script)
                print(f"Response: {response_text}")

                with text_queue.mutex:
                    text_queue.queue.clear()

                text_queue.put(response_text)
                socketio.emit('text', {'message': response_text})
                script.append(
                    {
                        "role": "model",
                        "content": {
                            "parts": [
                                {
                                    "text": response_text
                                }
                            ]
                        }
                    }
                )

                audio_filename = f"audio_{image_id}.mp3"
                audio_path = os.path.join(audio_folder, audio_filename)
                generate_audio(response_text, audio_path)
                results.append((image_name, response_text, audio_filename))

                save_results_to_csv(results, csv_file)

            else:
                print("Failed to capture image")

            time.sleep(capture_interval)
        except Exception as e:
            print(f"Error in capture_images: {e}")
    cap.release()

def save_results_to_csv(results, csv_path):
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
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

@app.route('/set_interval', methods=['POST'])
def set_interval():
    global capture_interval
    interval = request.json.get('interval')
    if interval:
        capture_interval = interval
        return jsonify({"status": "interval updated", "interval": capture_interval})
    return jsonify({"status": "failed", "message": "Invalid interval"}), 400

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
