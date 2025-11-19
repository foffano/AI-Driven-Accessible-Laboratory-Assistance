import os
import threading
import time
import webbrowser
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

import config
import vision
import audio
import utils

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Global variables
results = []
csv_file = "../results.csv"

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('get_settings')
def handle_get_settings():
    settings = {
        'api_key': config.openrouter_api_key,
        'model': config.model_name,
        'prompt': config.system_prompt
    }
    emit('current_settings', settings)

@app.route('/save_settings', methods=['POST'])
def handle_save_settings():
    data = request.json
    config.openrouter_api_key = data.get('api_key', config.openrouter_api_key)
    config.model_name = data.get('model', config.model_name)
    config.system_prompt = data.get('prompt', config.system_prompt)
    config.save_config()
    return jsonify({"status": "success", "message": "Settings saved."})

@socketio.on('analyze_frame')
def handle_analyze_frame():
    print("`analyze_frame` event received.")

    if not config.openrouter_api_key:
        print("API key is not set. Emitting error.")
        socketio.emit('text', {'message': "Please set your API key in the settings."})
        return

    if vision.latest_encoded_image:
        print("Analyzing current frame...")
        response_text = vision.analyze_image(vision.latest_encoded_image)
        print(f"Response from analyze_image: {response_text}")

        with audio.text_queue.mutex:
            audio.text_queue.queue.clear()

        
        print("Emitting text to client...")
        socketio.emit('text', {'message': response_text})
        
        image_id = int(time.time())
        audio_filename = f"audio_{image_id}.mp3"
        audio_path = os.path.join(audio.audio_folder, audio_filename)
        audio.generate_audio(response_text, audio_path)
        
        # Put the audio path in the queue for playback
        audio.text_queue.put((response_text, audio_path))

        # We need an image name for the CSV, let's use the timestamp
        image_name = f"frame_{image_id}.jpg"
        results.append((image_name, response_text, audio_filename))
        utils.save_results_to_csv(results, csv_file)
    else:
        print("No image has been captured yet.")

if __name__ == '__main__':
    # Start the background threads
    capture_thread = threading.Thread(target=vision.capture_images, args=(socketio,))
    capture_thread.daemon = True
    capture_thread.start()

    audio_thread = threading.Thread(target=audio.play_audio)
    audio_thread.daemon = True
    audio_thread.start()

    # Open the web browser
    webbrowser.open('http://localhost:5001')

    # Start the Flask-SocketIO server
    socketio.run(app, host='0.0.0.0', port=5001)

    # Clean up the audio queue
    audio.text_queue.put((None, None))
    audio_thread.join()