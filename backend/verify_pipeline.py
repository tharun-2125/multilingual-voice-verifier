import os
import sys
import base64
import requests
import json
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

def transcribe_gemini_rest(file_path: str, target_language: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set in backend/.env")

    # 1. Read file and encode to base64
    with open(file_path, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        ".ogg": "audio/ogg",
        ".mp3": "audio/mp3",
        ".wav": "audio/wav",
        ".m4a": "audio/m4a"
    }
    mime_type = mime_types.get(ext, "audio/ogg")

    # 2. Formulate target language name
    lang_names = {
        "en": "English",
        "ta": "Tamil",
        "hi": "Hindi"
    }
    target_lang_name = lang_names.get(target_language, target_language)

    prompt = (
        "Listen to this audio. It may contain Tamil, Hindi, English, or a mix. "
        "Understand the actual MEANING of what's being said (not literal word-for-word), "
        "then provide:\n"
        "1. A natural transcript of what was said, in its original language (keep it code-mixed if spoken that way, but natural)\n"
        f"2. A natural, meaning-based translation into {target_lang_name}.\n"
        "Do not do literal phonetic transcription — understand context and intent, "
        "especially for casual code-mixed speech."
    )

    # 3. Call REST API
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": audio_data
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "original_meaning": { "type": "STRING" },
                    "translated_meaning": { "type": "STRING" },
                    "detected_language": { "type": "STRING" }
                },
                "required": ["original_meaning", "translated_meaning", "detected_language"]
            }
        }
    }

    print(f"Calling Gemini REST API via x-goog-api-key header...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini API returned error {response.status_code}: {response.text}")

    resp_json = response.json()
    try:
        text_content = resp_json['candidates'][0]['content']['parts'][0]['text']
        data = json.loads(text_content)
        return {
            "original_meaning": data.get("original_meaning", ""),
            "translated_meaning": data.get("translated_meaning", ""),
            "detected_language": data.get("detected_language", "auto"),
            "target_language": target_language
        }
    except (KeyError, IndexError, ValueError) as e:
        raise Exception(f"Failed to parse response: {e}. Raw response: {response.text}")

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    test_file = r"C:\Users\acer\OneDrive\test.ogg"
    if not os.path.exists(test_file):
        print(f"Error: Test file not found at {test_file}")
        return

    print("Checking for GEMINI_API_KEY...")
    if not os.getenv("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set in backend/.env")
        return
    else:
        print(f"API Key found: {os.getenv('GEMINI_API_KEY')[:10]}...")

    print(f"Running Gemini REST transcription & translation for {test_file} (target_language: Hindi)...")
    try:
        result = transcribe_gemini_rest(test_file, target_language="hi")
        print("\n--- RESULTS ---")
        print(f"Detected Language: {result['detected_language']}")
        print(f"Target Language:   {result['target_language']}")
        print(f"Original Meaning:  {result['original_meaning']}")
        print(f"Translated Meaning: {result['translated_meaning']}")
        print("---------------\n")
        print("Success! Gemini Audio understanding ran successfully via REST API.")
    except Exception as e:
        print(f"Failed to process: {e}")

if __name__ == "__main__":
    main()
