import os
import pygame
from gtts import gTTS
from queue import Queue
import threading

audio_folder = "audio_responses"
if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

audio_playing = threading.Event()
text_queue = Queue()

def generate_audio(text, filename):
    tts = gTTS(text, lang='en')
    tts.save(filename)
    print(f"Audio saved to {filename}")

def play_audio():
    global audio_playing
    while True:
        text, audio_path = text_queue.get()
        if text is None:
            break
        audio_playing.set()
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            print(f"Playing audio: {audio_path}")
        except Exception as e:
            print(f"Error in play_audio: {e}")
        finally:
            audio_playing.clear()