import os
import json
import requests
from gnews import GNews
from google import genai
from google.genai import types

# --- CONFIGURATION & CLIENT INITIALIZATION ---
# 1. Retrieve keys from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY") 
GOOGLE_FACT_CHECK_KEY = os.getenv("GOOGLE_FACT_CHECK_KEY") 

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable not found. "
        "Please ensure it is set using the '$env:GEMINI_API_KEY=\"...\"' command."
    )

# 2. Initialize the Gemini Client explicitly passing the key (Fixes ValueError)
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash" 

# --- 1. TOOL DEFINITIONS (APIs as Python Functions) ---

def get_trending_topics(country: str) -> str:
    """
    Fetches the current top 5 trending news headlines for a specified country (e.g., 'US', 'IN').
    This function is used to identify emerging misinformation claims that need verification.

    Args:
        country: The two-letter country code for the trend search.

    Returns:
        A JSON string listing the top trending topics (headline and source).
    """
    try:
        # Using GNews for simplicity and stability in a hackathon
        google_news = GNews(country=country, max_results=5)
        news_list = google_news.get_top_news()
        
        trending_claims = [{
            "id": i + 1, 
            "claim_text": item.get('title'), 
            "source": item.get('publisher', {}).get('title')
        } for i, item in enumerate(news_list)]
        
        return json.dumps(trending_claims)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch trends using GNews: {e}"})

def get_fact_check_verdict(claim_text: str) -> str:
    """
    Queries the Google Fact Check Tools API to find pre-existing credibility ratings and fact-check articles.
    This is the highest-confidence source for an immediate verdict.

    Args:
        claim_text: The specific factual claim or short headline to verify.

    Returns:
        A JSON string containing the most relevant fact-check verdict and source, or a message indicating no verdict was found.
    """
    # --- GOOGLE FACT CHECK API INTEGRATION ---
    
    # You would typically use the requests library here.
    # url = f"https://content-factchecktools.googleapis.com/v1alpha1/claims:search?query={claim_text}&key={GOOGLE_FACT_CHECK_KEY}"
    
    # Mocking for immediate demonstration:
    if "new bank rule" in claim_text.lower():
        return json.dumps({"verdict": "FALSE", "source": "PolitiFact", "summary": "The rule affects only large trusts, not private accounts."})
    elif "tax cut passed" in claim_text.lower():
        return json.dumps({"verdict": "VERIFIED", "source": "FactCheck.org", "summary": "Bill signed into law on Friday."})
    else:
        return json.dumps({"verdict": "UNCHECKED", "reason": "No previous fact-check found in the database."})

def search_weighted_news(query: str) -> str:
    """
    Searches a diverse database of trusted news sources (NewsData.io) for corroborating 
    or refuting evidence related to a claim. Used when no official fact-check is found.
    Returns weighted sentiment/source data to help the LLM synthesize a score.

    Args:
        query: The topic or claim to search for.

    Returns:
        A JSON string listing high-authority articles with their headlines and sentiment.
    """
    # --- NEWSDATA.IO API INTEGRATION ---

    # Example API structure for NewsData.io (using a simplified mock)
    # url = f"https://newsdata.io/api/1/latest?apikey={NEWSDATA_API_KEY}&q={query}&language=en&country=us"
    
    # Mocking a response for demonstration:
    if "earthquake aid" in query.lower():
        articles = [
            {"source": "Reuters", "headline": "Aid is confirmed slow, but convoys moving.", "sentiment": "Neutral"},
            {"source": "AP", "headline": "Government confirms delays due to weather.", "sentiment": "Negative"},
            {"source": "Local Blog", "headline": "Govt is hoarding all the aid, nothing is coming!", "sentiment": "Extremely Negative"},
        ]
    else:
        articles = []
        
    return json.dumps({"corroboration_articles": articles})


# Map tool names to their function objects
AVAILABLE_TOOLS = {
    "get_trending_topics": get_trending_topics,
    "get_fact_check_verdict": get_fact_check_verdict,
    "search_weighted_news": search_weighted_news,
}

# --- 2. THE AGENTIC EXECUTION LOOP ---

def run_project_clarion_agent(initial_prompt: str):
    """
    Manages the Gemini agent's reasoning and tool execution loop.
    """
    print("--- Project Clarion Agent Initiated ---")
    
    # 1. Define the System Prompt and Tools for the LLM
    system_prompt = (
        "You are Project Clarion, a highly objective and fast misinformation detection agent. "
        "Your PRIMARY GOAL is to check emerging claims and output a final, concise verdict and justification. "
        "Your STRATEGY is: "
        "1. Identify trends using `get_trending_topics`. "
        "2. Select the most suspicious claim. "
        "3. Check for an existing official verdict using `get_fact_check_verdict`. "
        "4. If UNCHECKED, use `search_weighted_news` for corroboration. "
        "5. Conclude with a clear verdict (Verified, False, or Needs Review) and justification based *only* on the tool outputs."
    )
    
    tools = list(AVAILABLE_TOOLS.values()) 
    
    # Corrected creation of initial user message (Fixes TypeError)
    messages = [
        types.Content(
            role="user", 
            parts=[types.Part.from_text(text=initial_prompt)]
        )
    ]

    # 2. Start the Execution Loop
    for _ in range(7): # Limit steps to avoid infinite loop
        
        # Call the Gemini API with the available tools
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
            config=types.GenerateContentConfig(tools=tools, system_instruction=system_prompt),
        )

        if response.function_calls:
            
            # 3. Handle Tool Calls
            tool_calls = response.function_calls
            function_responses = []

            for call in tool_calls:
                tool_name = call.name
                tool_args = dict(call.args)
                
                if tool_name in AVAILABLE_TOOLS:
                    print(f"\n[AGENT ACTION] Calling Tool: {tool_name} with args: {tool_args}")
                    
                    # Execute the actual Python function
                    tool_function = AVAILABLE_TOOLS[tool_name]
                    tool_output_str = tool_function(**tool_args)
                    
                    # Package the result to send back to the LLM
                    function_responses.append(
                        types.Part.from_function_response(
                            name=tool_name, 
                            response={"result": tool_output_str}
                        )
                    )
                else:
                    print(f"[ERROR] LLM requested unknown tool: {tool_name}")

            # Append the assistant's request and the tool's output to the history
            messages.append(response.candidates[0].content)
            messages.append(types.Content(role="tool", parts=function_responses))
            
        elif response.text:
            # 4. Final Response (Verdict)
            print("\n--- AGENT FINAL VERDICT ---")
            print(response.text)
            break
            
        else:
            print("[STATUS] No response text or tool call detected. Agent finished early.")
            break
            
if __name__ == "__main__":
    # The initial prompt that starts the agent's work
    run_project_clarion_agent("Begin the misinformation monitoring process by identifying current top trends in the US.")