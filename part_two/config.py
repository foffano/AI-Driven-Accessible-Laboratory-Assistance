import os
import json

CONFIG_FILE = 'config.json'
openrouter_api_key = os.environ.get('OPENROUTER_API_KEY') # Get from environment variable
model_name = 'google/gemini-1.5-flash-latest'
system_prompt = "You are a helpful and friendly lab assistant. Describe what you see in the image. If you detect any safety hazards, include a brief educational alert. Limit your response to a maximum of 30 words."

def load_config():
    global openrouter_api_key, model_name, system_prompt
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Only update if the environment variable was not set
                if openrouter_api_key is None:
                    openrouter_api_key = config.get('openrouter_api_key', None)
                model_name = config.get('model_name', model_name)
                system_prompt = config.get('system_prompt', system_prompt)
    except Exception as e:
        print(f"Error loading config: {e}")

def save_config():
    try:
        with open(CONFIG_FILE, 'w') as f:
            config = {
                # Do not save API key to config.json
                'model_name': model_name,
                'system_prompt': system_prompt
            }
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# Load initial configuration
load_config()
