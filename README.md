# AI-Driven Accessible Laboratory Assistance

This repository contains the code and resources for the paper "AI-Driven Accessible Laboratory Assistance". The project is divided into two main parts: a controlled evaluation of Multimodal LLMs and a real-world integrated assistive system.

---

## 🚀 Quick Start for Users

If you want to use the **Laboratory Assistant** application without worrying about code or installation, follow these simple steps:

### 1. Download the Application
Download the latest version of the executable from the link below:

👉 **[[DOWNLOAD LINK](https://github.com/foffano/AI-Driven-Accessible-Laboratory-Assistance/tree/main/part_two/app/dist)]**

### 2. Get an API Key
The application uses **OpenRouter** to access powerful AI models. You will need an API Key to use it.
1.  Go to [OpenRouter.ai](https://openrouter.ai/).
2.  Create an account and generate an API Key.

### 3. Run the App
1.  Double-click the downloaded `.exe` file.
2.  The application will open in your web browser.
3.  Go to **Settings** and enter your OpenRouter API Key.
4.  You are ready to go!

---

## 🛠️ For Developers & Researchers

This section is for those who want to explore the source code, run the evaluation scripts, or build the application from scratch.

> [!IMPORTANT]
> **API Keys Security:** For security reasons, API keys should never be hardcoded or committed directly into the repository. Please use environment variables to store and access your API keys.

### Part I: Evaluation of the Multimodal LLM

This section focuses on evaluating the performance of Multimodal Large Language Models (LLMs) using a controlled dataset of laboratory images.

- **Main Script:** `part_one/adc.py`
- **Dataset:** `part_one/dataset/`

### Part II: Real-World Evaluation of the Integrated Assistive System

This section contains the source code for the real-time laboratory assistant application. The system integrates computer vision, LLMs, and text-to-speech to assist visually impaired users in a laboratory setting.

#### Prerequisites

- **Python 3.13** (Recommended for PyInstaller compatibility)
- **Webcam**

#### Installation

1.  **Navigate to the application directory:**
    ```bash
    cd part_two/app
    ```

2.  **Create a virtual environment:**
    ```powershell
    # Windows
    py -3.13 -m venv venv
    ```

3.  **Activate the virtual environment:**
    ```powershell
    # Windows
    .\venv\Scripts\activate
    ```

4.  **Install dependencies:**
    ```bash
    pip install -r ../../requirements.txt
    # Or manually:
    pip install flask flask-socketio opencv-python requests pillow numpy gTTS pygame python-dotenv pyinstaller
    ```

#### Running the Application (Source Code)

To run the application in development mode:

```bash
python app.py
```

The application will start a local server (usually at `http://localhost:5001`) and open your default web browser.

#### Generating the Executable (.exe)

To create a standalone Windows executable for the Laboratory Assistant, follow these steps. This process ensures that all dependencies, including static files and templates, are correctly bundled.

**1. Prepare the Environment**

Ensure you are using **Python 3.13** to avoid known compatibility issues with PyInstaller and Python 3.10+.

```powershell
# Remove old environment if exists
Remove-Item -Recurse -Force venv

# Create new environment with Python 3.13
py -3.13 -m venv venv
```

**2. Install Dependencies**

Install the required packages within your virtual environment:

```powershell
.\venv\Scripts\pip install flask flask-socketio opencv-python requests pillow numpy gTTS pygame python-dotenv pyinstaller
```

**3. Build the Executable**

Run the following PyInstaller command from the `part_two/app` directory. This command bundles the application into a single file, includes necessary data folders, and handles hidden imports.

```powershell
.\venv\Scripts\pyinstaller --noconfirm --onefile --console --name "LaboratoryAssistant" --add-data "templates;templates" --add-data "static;static" --hidden-import "engineio.async_drivers.threading" app.py
```

**4. Locate the Executable**

After the build completes, your executable will be located in:

```
part_two/app/dist/LaboratoryAssistant.exe
```

---
*This project is derived from [DIY-Astra](https://github.com/Doriandarko/DIY-Astra).*
