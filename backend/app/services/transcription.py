import os
import json
import base64
import requests
from deep_translator import GoogleTranslator

_whisper_model = None

def get_whisper_model():
    """
    Lazy loads and caches the WhisperModel to avoid blocking application startup.
    """
    global _whisper_model
    if _whisper_model is None:
        from faster_whisper import WhisperModel
        MODEL_SIZE = "medium"
        print(f"Loading faster-whisper model (lazy-loaded): {MODEL_SIZE}...")
        _whisper_model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        print("Model loaded.")
    return _whisper_model

def transcribe_whisper(file_path: str, target_language: str, source_language: str = "auto") -> dict:
    """
    Transcribe the given audio file using faster-whisper, and translate the result using GoogleTranslator.
    """
    model = get_whisper_model()
    whisper_lang = None if source_language == "auto" else source_language
    
    # 1. Transcribe
    segments, info = model.transcribe(file_path, beam_size=5, language=whisper_lang)
    detected_language = info.language
    
    # Debug logging for top 3 candidate languages
    if hasattr(info, 'all_language_probs') and info.all_language_probs:
        sorted_probs = sorted(info.all_language_probs, key=lambda x: x[1], reverse=True)
        print("\n--- WHISPER LANGUAGE DETECTION SCORES ---")
        for lang, prob in sorted_probs[:3]:
            print(f"{lang}: {prob:.4f}")
        print("-----------------------------------------\n")
    else:
        print(f"\nDetected Language: {detected_language} (Prob: {info.language_probability})\n")

    original_meaning = ""
    for segment in segments:
        original_meaning += segment.text + " "
    original_meaning = original_meaning.strip()

    translated_meaning = original_meaning

    # 2. Translate if target language is different from detected/source
    if target_language != detected_language:
        if target_language == "en":
            # Whisper natively translates to English
            t_segments, _ = model.transcribe(file_path, beam_size=5, task="translate", language=whisper_lang)
            translated_meaning = ""
            for segment in t_segments:
                translated_meaning += segment.text + " "
            translated_meaning = translated_meaning.strip()
        else:
            # Use deep-translator for other languages (ta, hi)
            try:
                translator = GoogleTranslator(source='auto', target=target_language)
                translated_meaning = translator.translate(original_meaning)
            except Exception as e:
                translated_meaning = f"[Translation failed: {str(e)}] {original_meaning}"

    return {
        "original_meaning": original_meaning,
        "translated_meaning": translated_meaning,
        "detected_language": detected_language,
        "target_language": target_language
    }

def transcribe_gemini(file_path: str, target_language: str) -> dict:
    """
    Transcribe and translate using Gemini native audio understanding via REST API.
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set in backend/.env file. Please check setup instructions.")

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
        "1. A natural transcript of what was said, in its original language (keep it code-mixed if spoken that way, but natural).\n"
        f"2. translated_full: A complete, natural, meaning-based translation into {target_lang_name} — "
        "cover every key point and nuance spoken, sentence by sentence if needed.\n"
        f"3. translated_main: A single concise line (20–30 words max) summarising the core gist/message in {target_lang_name}. "
        "Do NOT copy translated_full; write a tight summary instead.\n"
        "4. detected_language: The primary language spoken.\n"
        "Do not do literal phonetic transcription — understand context and intent, "
        "especially for casual code-mixed speech."
    )

    # 3. Call REST API using Gemini 3.5 Flash
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
                    "original_meaning":  { "type": "STRING" },
                    "translated_full":   { "type": "STRING" },
                    "translated_main":   { "type": "STRING" },
                    "detected_language": { "type": "STRING" }
                },
                "required": ["original_meaning", "translated_full", "translated_main", "detected_language"]
            }
        }
    }

    print(f"Calling Gemini REST API (gemini-3.5-flash) via header authentication...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini API returned error {response.status_code}: {response.text}")

    resp_json = response.json()
    try:
        text_content = resp_json['candidates'][0]['content']['parts'][0]['text']
        data = json.loads(text_content)
        translated_full = data.get("translated_full", "")
        translated_main = data.get("translated_main", "")
        return {
            "original_meaning":  data.get("original_meaning", ""),
            # Keep legacy field pointing to the full translation so Whisper path stays unaffected
            "translated_meaning": translated_full,
            "translated_full":   translated_full,
            "translated_main":   translated_main,
            "detected_language": data.get("detected_language", "auto"),
            "target_language":   target_language
        }
    except (KeyError, IndexError, ValueError) as e:
        raise Exception(f"Failed to parse response: {e}. Raw response: {response.text}")


def extract_claim_gemini(translated_text: str) -> str:
    """
    Extract the single core factual claim from the translated text using Gemini 3.5 Flash REST API.
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set in backend/.env file.")

    prompt = (
        "Extract the single core factual claim from this text, ignoring greetings, "
        "opinions, and forwarding instructions like 'share this' or 'forward to everyone'. "
        "If there is no checkable factual claim, respond exactly: 'no_claim_found'."
        f"\n\n{translated_text}"
    )

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
                        "text": prompt
                    }
                ]
            }
        ]
    }

    print(f"Calling Gemini REST API for claim extraction...")
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Gemini API returned error {response.status_code}: {response.text}")

    resp_json = response.json()
    try:
        extracted = resp_json['candidates'][0]['content']['parts'][0]['text']
        # Clean quotes and whitespace
        clean_extracted = extracted.strip().strip("'\"`").strip()
        if "no_claim_found" in clean_extracted.lower():
            return "no_claim_found"
        return clean_extracted
    except (KeyError, IndexError, ValueError) as e:
        raise Exception(f"Failed to parse claim extraction response: {e}. Raw response: {response.text}")

