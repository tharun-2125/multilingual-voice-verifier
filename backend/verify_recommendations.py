import os
import sys
# Ensure stdout/stderr use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.recommendations import classify_content, fetch_recommendations

def run_test(name: str, sentence: str):
    print(f"\n==========================================")
    print(f"TEST: {name}")
    print(f"Input Text: '{sentence}'")
    print(f"==========================================")
    
    # 1. Classify content
    print("Classifying content using Gemini...")
    classification = classify_content(sentence)
    category = classification.get("content_category", "other")
    topics = classification.get("key_topics", [])
    
    print(f"Classified Category: {category}")
    print(f"Key Topics:          {topics}")
    
    # 2. Fetch recommendations
    print("Fetching recommendations...")
    recommendations = fetch_recommendations(category, topics)
    
    print(f"\nResults ({len(recommendations)}):")
    for idx, rec in enumerate(recommendations, 1):
        print(f"  {idx}. [{rec['source']}] {rec['title']}")
        print(f"     Link:  {rec['link']}")
        print(f"     Image: {rec.get('image')}")
    print("==========================================\n")

def main():
    load_dotenv()
    
    # Verify API keys are present
    gemini_key = os.getenv("GEMINI_API_KEY")
    gnews_key = os.getenv("GNEWS_API_KEY")
    serpapi_key = os.getenv("SERPAPI_KEY")
    
    print("API Key Status:")
    print(f"  GEMINI_API_KEY: {'Set' if gemini_key else 'Missing'}")
    print(f"  GNEWS_API_KEY:  {'Set' if gnews_key else 'Missing'}")
    print(f"  SERPAPI_KEY:   {'Set' if serpapi_key else 'Missing'}")
    
    if not gemini_key:
        print("\nError: GEMINI_API_KEY is required to run classification.")
        return
        
    if not gnews_key or not serpapi_key:
        print("\nWarning: GNEWS_API_KEY or SERPAPI_KEY is missing. Real links will not be fetched.")
        print("Please add these keys to backend/.env if you want to see live recommendations.")
    
    # Example 1: News/Sports Event
    news_text = "The Prime Minister announced a new economic policy today regarding renewable energy subsidies."
    run_test("Current Affairs (GNews)", news_text)

    # Example 1b: News/Sports Event (Hindi Translation - User's Case)
    news_text_hindi = "प्रधानमंत्री ने आज नवीकरणीय ऊर्जा सब्सिडी को लेकर एक नई आर्थिक नीति की घोषणा की।"
    run_test("Current Affairs Hindi (GNews)", news_text_hindi)
    
    # Example 2: Study/Exam Topic
    study_text = "I need some learning resources to study quantum physics and understand thermodynamics equations for my exam."
    run_test("Academic Study (SerpAPI)", study_text)

if __name__ == "__main__":
    main()
