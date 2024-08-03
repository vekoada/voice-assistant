# voice-assistant

## Overview
This project is a multimodal AI voice assistant that can process voice commands, analyze images, extract text from the clipboard, and provide responses using various AI models. It integrates services from Groq, Google, OpenAI, and Whisper.

## Features
- **Voice Command Recognition**: Listens for a wake word and processes the subsequent command.
- **Image Analysis**: Analyzes images from screenshots or webcam captures to provide contextual information.
- **Clipboard Text Extraction**: Extracts text from the clipboard for use in responses.
- **Text-to-Speech**: Converts text responses into speech.
- **Speech-to-Text**: Transcribes spoken prompts into text.

## Requirements
- Python 3.7 or higher
- Required Python libraries (listed in `requirements.txt`)
- API keys for Groq, Google Generative AI, and OpenAI
- A working webcam
- A microphone

## Setup
1. **Clone the Repository**:
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **API Keys**:
    - Obtain API keys for Groq, Google Generative AI, and OpenAI.
    - Create a file named `API Keys.json` in the root directory and add your API keys:
      ```json
      {
          "Groq": "your-groq-api-key",
          "Google": "your-google-api-key",
          "OpenAI": "your-openai-api-key"
      }
      ```

## Usage
1. **Run the Assistant**:
    ```sh
    python assistant.py
    ```
    The assistant will start listening for the wake word (`"Worko"` by default) followed by your prompt.

2. **Voice Commands**:
    - **Take Screenshot**: Captures the screen and analyzes the image.
    - **Capture Webcam**: Captures an image from the webcam and analyzes it.
    - **Extract Clipboard**: Extracts text from the clipboard and includes it in the context.
    - **None**: Continues without additional context.

## Functions and Modules
- **use_vision(prompt, photo_path)**: Analyzes the image and generates a detailed text description.
- **ask_llama(prompt, image_context)**: Sends the prompt and context to the Groq model and returns the response.
- **call_function(prompt)**: Determines the appropriate function to call based on the prompt.
- **screenshot()**: Takes a screenshot and saves it.
- **capture_webcam()**: Captures an image from the webcam and saves it.
- **get_clipboard()**: Extracts text from the clipboard.
- **speak(text)**: Converts text to speech.
- **wav_to_text(audio_path)**: Transcribes audio to text using the Whisper model.
- **extract_prompt(transcribed_text, wake_word)**: Extracts the prompt from the transcribed text.
- **start_listening()**: Starts listening for the wake word and processes the command.

## Customization
- **Wake Word**: Change the `wake_word` variable to customize the wake word.
- **AI Models and Configurations**: Modify the configurations for the AI models as needed.
