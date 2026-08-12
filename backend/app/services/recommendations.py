import os
import json
import requests
import sys
from urllib.parse import urlparse

# Ensure stdout and stderr use UTF-8 to prevent encoding crashes on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def classify_content(translated_text: str) -> dict:
    """
    Classify the translated text using Gemini to determine content category and key topics.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY is not set in backend/.env. Skipping classification.")
        return {"content_category": "other", "key_topics": []}

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    prompt = (
        f"Analyze this text: '{translated_text}'. Determine:\n"
        "1. content_category: exactly one of ['current_affairs', 'academic_study', 'casual', 'other']\n"
        "2. key_topics: a list of 2-4 specific searchable entities/topics mentioned. "
        "IMPORTANT: Always return the key_topics in English (for search engine indexing), "
        "even if the input text is in another language (e.g., convert 'प्रधानमंत्री' to 'Prime Minister'). "
        "Keep them short and search-friendly, not full sentences.\n"
        "Return strictly as JSON: {\"content_category\": \"...\", \"key_topics\": [...]}"
    )

    payload = {
        "contents": [
            {
                "parts": [
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
                    "content_category": {
                        "type": "STRING",
                        "enum": ["current_affairs", "academic_study", "casual", "other"]
                    },
                    "key_topics": {
                        "type": "ARRAY",
                        "items": { "type": "STRING" }
                    }
                },
                "required": ["content_category", "key_topics"]
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Warning: Gemini classification failed with status {response.status_code}: {response.text}")
            return {"content_category": "other", "key_topics": []}

        resp_json = response.json()
        text_content = resp_json['candidates'][0]['content']['parts'][0]['text']
        return json.loads(text_content)
    except Exception as e:
        print(f"Warning: Gemini classification exception: {e}")
        return {"content_category": "other", "key_topics": []}

def fetch_recommendations(category: str, topics: list[str]) -> list[dict]:
    """
    Fetch news articles or study resources based on content category and topics.
    """
    if not topics or not isinstance(topics, list):
        return []

    recommendations = []

    if category == "current_affairs":
        gnews_key = os.getenv("GNEWS_API_KEY")
        if not gnews_key:
            print("Warning: GNEWS_API_KEY is not set. Skipping news search.")
            return []

        # Join top 2 topics as the search query
        query = " ".join(topics[:2]) if len(topics) > 1 else topics[0]
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": query,
            "token": gnews_key,
            "lang": "en",
            "max": 3
        }

        try:
            try:
                print(f"Fetching news articles from GNews for query: '{query}'...")
            except Exception:
                print("Fetching news articles from GNews for query...")
            r = requests.get(url, params=params, timeout=10)
            
            articles = []
            if r.status_code == 200:
                articles = r.json().get("articles", [])
            else:
                print(f"Warning: GNews API failed with status {r.status_code}: {r.text}")
                
            # Fallback 1: if no articles found with combined query, try with just the second topic (usually more specific)
            if not articles and len(topics) > 1:
                fallback_query = topics[1]
                try:
                    print(f"No results for combined query. Retrying with fallback query: '{fallback_query}'...")
                except Exception:
                    print("No results for combined query. Retrying with fallback query...")
                params["q"] = fallback_query
                r = requests.get(url, params=params, timeout=10)
                if r.status_code == 200:
                    articles = r.json().get("articles", [])
                else:
                    print(f"Warning: GNews API fallback 1 failed with status {r.status_code}: {r.text}")
                    
            # Fallback 2: if still no articles, try with just the first topic
            if not articles and len(topics) > 0:
                fallback_query = topics[0]
                try:
                    print(f"Still no results. Retrying with fallback query: '{fallback_query}'...")
                except Exception:
                    print("Still no results. Retrying with fallback query...")
                params["q"] = fallback_query
                r = requests.get(url, params=params, timeout=10)
                if r.status_code == 200:
                    articles = r.json().get("articles", [])
                else:
                    print(f"Warning: GNews API fallback 2 failed with status {r.status_code}: {r.text}")

            for article in articles:
                recommendations.append({
                    "title": article.get("title", ""),
                    "link": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "GNews"),
                    "image": article.get("image", None)
                })
        except Exception as e:
            print(f"Warning: GNews request failed: {e}")

    elif category == "academic_study":
        serpapi_key = os.getenv("SERPAPI_KEY")
        if not serpapi_key:
            print("Warning: SERPAPI_KEY is not set. Skipping academic search.")
            return []

        # Use the first key_topic as the query
        query = topics[0]
        url = "https://serpapi.com/search.json"
        params = {
            "q": f"{query} study resources",
            "api_key": serpapi_key
        }

        try:
            try:
                print(f"Fetching study resources from SerpAPI for query: '{query}'...")
            except Exception:
                print("Fetching study resources from SerpAPI for query...")
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for result in data.get("organic_results", [])[:3]:
                    # Extract site source
                    source = result.get("source")
                    if not source:
                        link = result.get("link", "")
                        domain = urlparse(link).netloc
                        source = domain.replace("www.", "") if domain else "SerpAPI"
                        
                    recommendations.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "source": source,
                        "image": result.get("thumbnail", None)
                    })
            else:
                print(f"Warning: SerpAPI failed with status {r.status_code}: {r.text}")
        except Exception as e:
            print(f"Warning: SerpAPI request failed: {e}")

    return recommendations
