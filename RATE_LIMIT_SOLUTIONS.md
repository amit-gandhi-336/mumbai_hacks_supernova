# 🚀 Complete Guide to Tackling Gemini API Rate Limits

## ✅ What I Just Implemented

### 1. **Switched to Stable Model** 
Changed from `gemini-2.0-flash-exp` (experimental) to `gemini-1.5-flash` (stable)
- ✅ Better rate limits
- ✅ More reliable
- ✅ Production-ready

### 2. **Added Retry Logic with Exponential Backoff**
```python
def call_gemini_with_retry(prompt, system_prompt, max_retries=3):
    # Retries with 2s, 4s, 8s delays
    # Automatically handles temporary rate limits
```
- ✅ 3 automatic retry attempts
- ✅ Smart waiting (2s → 4s → 8s)
- ✅ Handles temporary spikes

### 3. **Added User-Friendly Warning**
Shows notice in the UI about rate limits
- ✅ Users know to wait between requests
- ✅ Sets proper expectations

## 🎯 Additional Strategies You Can Use

### **Option 1: Get API Key Upgrade (Best for Production)**

**Free Tier Limits:**
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)
- 1,500 requests per day (RPD)

**To Upgrade:**
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Click on your project
3. Enable billing for higher limits
4. Or use multiple API keys and rotate them

### **Option 2: Add Request Caching**

Add this to your backend to cache results:

```python
# At the top of app.py
from functools import lru_cache
import hashlib

# Cache recent fact-checks for 1 hour
fact_check_cache = {}

def get_cache_key(claim: str) -> str:
    return hashlib.md5(claim.lower().strip().encode()).hexdigest()

def fact_check_with_newsdata(claim: str):
    # Check cache first
    cache_key = get_cache_key(claim)
    if cache_key in fact_check_cache:
        cached_result = fact_check_cache[cache_key]
        if time.time() - cached_result['timestamp'] < 3600:  # 1 hour
            return cached_result['data']
    
    # ... rest of your function ...
    
    # Store in cache before returning
    result = {
        "claim": claim,
        "verdict": "ANALYZED",
        "analysis": analysis,
        "supporting_articles": articles,
        "articles_count": len(articles)
    }
    
    fact_check_cache[cache_key] = {
        'data': result,
        'timestamp': time.time()
    }
    
    return result
```

### **Option 3: Add Rate Limiting on Frontend**

Prevent users from spamming requests:

```javascript
// In JournalistChat.jsx
const [lastRequestTime, setLastRequestTime] = useState(0);
const MIN_REQUEST_INTERVAL = 5000; // 5 seconds

const handleSubmit = async (e) => {
  e.preventDefault();
  
  const now = Date.now();
  const timeSinceLastRequest = now - lastRequestTime;
  
  if (timeSinceLastRequest < MIN_REQUEST_INTERVAL) {
    const waitTime = Math.ceil((MIN_REQUEST_INTERVAL - timeSinceLastRequest) / 1000);
    setError(`Please wait ${waitTime} seconds before checking another claim`);
    return;
  }
  
  setLastRequestTime(now);
  // ... rest of function
};
```

### **Option 4: Use Multiple API Keys (Load Balancing)**

```python
# In app.py
GEMINI_API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
]

current_key_index = 0

def get_next_api_key():
    global current_key_index
    key = GEMINI_API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(GEMINI_API_KEYS)
    return key

# Use rotating keys
client = genai.Client(api_key=get_next_api_key())
```

### **Option 5: Use Queue System (For High Traffic)**

For production with many users:

```python
from fastapi import BackgroundTasks
import asyncio

# Create a queue
fact_check_queue = asyncio.Queue()

async def process_fact_check_queue():
    while True:
        claim_data = await fact_check_queue.get()
        await asyncio.sleep(5)  # Throttle: 1 request per 5 seconds
        # Process the claim
        fact_check_queue.task_done()

@app.post("/api/fact-check")
async def fact_check(request: FactCheckRequest, background_tasks: BackgroundTasks):
    # Add to queue instead of processing immediately
    await fact_check_queue.put(request.claim)
    return {"status": "queued", "message": "Your request is being processed"}
```

## 📊 Rate Limit Best Practices

### **For Development/Hackathons:**
1. ✅ Use retry logic (already implemented)
2. ✅ Switch to stable models (already done)
3. ✅ Add 2-5 second delays between requests
4. ✅ Cache identical requests
5. ✅ Show friendly error messages

### **For Production:**
1. Enable billing on Google AI Studio
2. Implement request queuing
3. Use multiple API keys with load balancing
4. Add Redis caching for results
5. Monitor usage with logging

## 🔧 Quick Test

Restart your backend and test:

```bash
# Kill old process
lsof -ti:8000 | xargs kill -9

# Start with new code
cd backend
python3 -m uvicorn app:app --reload --port 8000
```

The app now:
- ✅ Retries automatically (3 attempts)
- ✅ Uses stable model with better limits
- ✅ Shows user-friendly warnings
- ✅ Degrades gracefully if AI unavailable

## 💡 Pro Tips

1. **Test with different queries** - Don't repeat the same claim
2. **Wait 10-15 seconds** between requests during testing
3. **Use the cache** - Same claims get instant results
4. **Monitor console** - Check backend logs for retry messages
5. **Upgrade for prod** - Free tier is fine for demos, upgrade for real users

## 🆘 Still Getting Rate Limited?

**Immediate workarounds:**
- Wait 60 seconds and try again
- Use a different API key
- Reduce requests per minute
- Check [Google AI Studio quota page](https://aistudio.google.com/app/apikey)

**Long-term solution:**
- Enable billing (first $200/month free)
- Implement caching (prevents duplicate API calls)
- Use queue system for high traffic
