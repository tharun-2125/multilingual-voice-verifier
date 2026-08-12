import os
import sys
import requests

def test_api():
    url = "http://localhost:8000/api/upload-audio"
    
    # Test Case 1: News audio with Claim Extraction ON
    print("\n--- Test Case 1: News audio ('news_petrol.wav') with Claim Extraction ON ---")
    wav_path = r"C:\Users\acer\OneDrive\news_petrol.wav"
    if not os.path.exists(wav_path):
        print(f"Error: {wav_path} does not exist.")
        return
        
    with open(wav_path, "rb") as f:
        files = {"file": ("news_petrol.wav", f, "audio/wav")}
        data = {
            "language": "en",
            "source_language": "auto",
            "pipeline": "gemini",
            "suggest_links": "false",
            "extract_claim": "true"
        }
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        res = response.json()
        print("Success!")
        print("Original Meaning:", res.get("original_meaning"))
        print("Translated Meaning:", res.get("translated_meaning"))
        print("Extracted Claim:", res.get("extracted_claim"))
        if res.get("extracted_claim") and res.get("extracted_claim") != "no_claim_found":
            print("PASS: Claim successfully extracted.")
        else:
            print("FAIL: Expected a claim to be extracted.")
    else:
        print(f"FAIL: API returned status code {response.status_code}: {response.text}")

    # Test Case 2: Casual audio with Claim Extraction ON
    print("\n--- Test Case 2: Casual audio ('test.ogg') with Claim Extraction ON ---")
    ogg_path = r"C:\Users\acer\OneDrive\test.ogg"
    if not os.path.exists(ogg_path):
        print(f"Error: {ogg_path} does not exist.")
        return
        
    with open(ogg_path, "rb") as f:
        files = {"file": ("test.ogg", f, "audio/ogg")}
        data = {
            "language": "en",
            "source_language": "auto",
            "pipeline": "gemini",
            "suggest_links": "false",
            "extract_claim": "true"
        }
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        res = response.json()
        print("Success!")
        print("Original Meaning:", res.get("original_meaning"))
        print("Translated Meaning:", res.get("translated_meaning"))
        print("Extracted Claim:", res.get("extracted_claim"))
        if res.get("extracted_claim") == "no_claim_found":
            print("PASS: Correctly reported no_claim_found.")
        else:
            print("FAIL: Expected no_claim_found.")
    else:
        print(f"FAIL: API returned status code {response.status_code}: {response.text}")

    # Test Case 3: News audio with Claim Extraction OFF
    print("\n--- Test Case 3: News audio ('news_petrol.wav') with Claim Extraction OFF ---")
    with open(wav_path, "rb") as f:
        files = {"file": ("news_petrol.wav", f, "audio/wav")}
        data = {
            "language": "en",
            "source_language": "auto",
            "pipeline": "gemini",
            "suggest_links": "false",
            "extract_claim": "false"
        }
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        res = response.json()
        print("Success!")
        print("Original Meaning:", res.get("original_meaning"))
        print("Translated Meaning:", res.get("translated_meaning"))
        print("Extracted Claim:", res.get("extracted_claim"))
        if res.get("extracted_claim") is None:
            print("PASS: Claim extraction was skipped (returned None).")
        else:
            print("FAIL: Expected extracted_claim to be None.")
    else:
        print(f"FAIL: API returned status code {response.status_code}: {response.text}")

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    test_api()
