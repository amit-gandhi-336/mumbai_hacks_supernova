import os
import json
import requests
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gnews import GNews
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
GOOGLE_FACT_CHECK_KEY = os.getenv("GOOGLE_FACT_CHECK_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not found.")

# Initialize FastAPI app
app = FastAPI(title="Project Clarion API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.0-flash-exp"  # Using experimental model - it's available and works

# --- MODELS ---
class FactCheckRequest(BaseModel):
    claim: str

# --- HELPER FUNCTIONS ---

def call_gemini_with_retry(prompt: str, system_prompt: str, max_retries: int = 3):
    """Call Gemini API with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                config=types.GenerateContentConfig(system_instruction=system_prompt)
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            
            # If it's a rate limit error and not the last attempt, retry
            if ("429" in error_msg or "Too Many Requests" in error_msg) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 2s, 4s, 8s
                print(f"Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            
            # If it's the last attempt or a different error, raise it
            raise e
    
    raise Exception("Max retries exceeded")

def get_trending_topics_with_verdict(country: str = "US", max_results: int = 5):
    """Get trending news with fact-check verdicts"""
    try:
        google_news = GNews(country=country, max_results=max_results)
        news_list = google_news.get_top_news()
        
        results = []
        for i, item in enumerate(news_list):
            claim_text = item.get('title', '')
            
            # Get verdict for each claim
            verdict = get_fact_check_verdict_internal(claim_text)
            
            results.append({
                "id": i + 1,
                "title": claim_text,
                "source": item.get('publisher', {}).get('title', 'Unknown'),
                "url": item.get('url', ''),
                "published_date": item.get('published date', ''),
                "verdict": verdict.get('verdict', 'UNCHECKED'),
                "summary": verdict.get('summary', 'No fact-check available'),
                "fact_check_source": verdict.get('source', 'N/A')
            })
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trends: {str(e)}")

def get_fact_check_verdict_internal(claim_text: str):
    """Internal function to check fact-check verdict"""
    try:
        if GOOGLE_FACT_CHECK_KEY:
            url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {
                'query': claim_text,
                'languageCode': 'en',
                'key': GOOGLE_FACT_CHECK_KEY,
                'pageSize': 1
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'claims' in data and len(data['claims']) > 0:
                    claim = data['claims'][0]
                    review = claim.get('claimReview', [{}])[0]
                    return {
                        "verdict": review.get('textualRating', 'UNCHECKED'),
                        "source": review.get('publisher', {}).get('name', 'Unknown'),
                        "summary": claim.get('text', 'No summary available')
                    }
        
        # Default response if no fact-check found
        return {
            "verdict": "UNCHECKED",
            "source": "N/A",
            "summary": "No previous fact-check found"
        }
    except Exception as e:
        return {
            "verdict": "ERROR",
            "source": "N/A",
            "summary": f"Error checking: {str(e)}"
        }

def fact_check_with_newsdata(claim: str):
    """Fact-check using NewsData.io and Gemini AI"""
    try:
        # Search NewsData.io for related articles
        articles = []
        if NEWSDATA_API_KEY:
            url = "https://newsdata.io/api/1/latest"
            params = {
                'apikey': NEWSDATA_API_KEY,
                'q': claim,
                'language': 'en',
                'size': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'results' in data:
                    for article in data['results'][:5]:
                        articles.append({
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'source': article.get('source_name', ''),
                            'url': article.get('link', ''),
                            'pubDate': article.get('pubDate', '')
                        })
        
        # Use Gemini to analyze the claim with the articles
        try:
            system_prompt = """You are a professional fact-checker. Analyze the given claim and supporting articles.
            Provide a verdict (VERIFIED, FALSE, MISLEADING, or NEEDS_REVIEW) and a detailed explanation.
            Base your analysis only on the provided articles. Be objective and cite sources."""
            
            articles_text = "\n\n".join([
                f"Article {i+1}:\nTitle: {a['title']}\nSource: {a['source']}\nDescription: {a['description']}"
                for i, a in enumerate(articles)
            ]) if articles else "No articles found."
            
            prompt = f"""Claim to fact-check: "{claim}"

Supporting Articles:
{articles_text}

Provide your fact-check verdict and explanation."""

            # Use the retry function instead of direct call
            analysis = call_gemini_with_retry(prompt, system_prompt, max_retries=3)
            
        except Exception as gemini_error:
            # Handle Gemini API errors (rate limits, etc.)
            error_msg = str(gemini_error)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                analysis = "⚠️ AI Analysis temporarily unavailable due to rate limits. Please try again in a few moments.\n\nBased on the articles found, please review the sources manually for now."
            elif "403" in error_msg or "PERMISSION_DENIED" in error_msg:
                analysis = "⚠️ AI Analysis unavailable - API key issue. Please check your Gemini API key.\n\nBased on the articles found, please review the sources manually."
            else:
                analysis = f"⚠️ AI Analysis unavailable: {error_msg}\n\nBased on the articles found, please review the sources manually."
        
        return {
            "claim": claim,
            "verdict": "ANALYZED",
            "analysis": analysis,
            "supporting_articles": articles,
            "articles_count": len(articles)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact-check failed: {str(e)}")

# --- API ENDPOINTS ---
@app.get("/")
def read_root():
    return {"message": "Project Clarion API is running", "status": "healthy"}

@app.get("/api/trending")
def get_trending():
    """Get top 5 trending news with fact-check verdicts"""
    try:
        results = get_trending_topics_with_verdict(country="US")
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fact-check")
def fact_check(request: FactCheckRequest):
    """Fact-check a claim for journalists"""
    try:
        # First check Google Fact Check API
        google_verdict = get_fact_check_verdict_internal(request.claim)
        
        # If no existing fact-check, use NewsData + Gemini
        if google_verdict['verdict'] in ['UNCHECKED', 'ERROR']:
            result = fact_check_with_newsdata(request.claim)
            return {
                "status": "success",
                "data": {
                    **result,
                    "google_fact_check": google_verdict
                }
            }
        else:
            # Use existing fact-check but also get additional context
            result = fact_check_with_newsdata(request.claim)
            return {
                "status": "success",
                "data": {
                    **result,
                    "google_fact_check": google_verdict,
                    "primary_verdict": google_verdict
                }
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
