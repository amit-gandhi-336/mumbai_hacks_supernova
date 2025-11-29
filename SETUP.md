# Project Clarion - AI-Powered Fact-Checking Platform

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
GEMINI_API_KEY="your_new_gemini_api_key"
NEWSDATA_API_KEY="pub_b102c7ffe98b45e79ecefeebdd61c702"
GOOGLE_FACT_CHECK_KEY="your_google_fact_check_key"
```

⚠️ **Important**: Get a new Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip3 install fastapi uvicorn python-multipart requests gnews google-genai
```

3. Run the FastAPI server:
```bash
uvicorn app:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## 📱 Features

### 1. Trending News Dashboard
- **Auto-loads** top 5 trending news on page load
- **Real-time fact-checking** with verdict badges
- **Color-coded verdicts**:
  - ✅ Green: Verified
  - ❌ Red: False/Misleading
  - ⚠️ Yellow: Unchecked/Needs Review
- Source and timestamp information
- Links to original articles

### 2. Journalist Fact-Checking Tool
- **Research submission**: Enter any claim for comprehensive analysis
- **Multi-source verification**:
  - Google Fact Check API (if available)
  - NewsData.io article search
  - AI-powered analysis using Gemini
- **Supporting evidence**: Lists relevant articles with sources
- **History tracking**: View recent fact-checks
- **Detailed analysis**: AI-generated verdict with explanation

## 🔧 API Endpoints

### GET `/api/trending`
Fetches top 5 trending news with fact-check verdicts

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "News headline",
      "source": "Source name",
      "verdict": "VERIFIED",
      "summary": "Fact-check summary",
      "fact_check_source": "PolitiFact"
    }
  ]
}
```

### POST `/api/fact-check`
Fact-checks a claim using multiple sources

**Request:**
```json
{
  "claim": "Your claim text here"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "claim": "Your claim",
    "verdict": "ANALYZED",
    "analysis": "AI analysis text",
    "supporting_articles": [...],
    "google_fact_check": {...}
  }
}
```

## 🎨 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Gemini AI**: Advanced LLM for fact-checking analysis
- **NewsData.io**: News aggregation API
- **Google Fact Check API**: Official fact-check database
- **GNews**: Trending news scraper

### Frontend
- **React 19**: Modern UI library
- **Vite**: Fast build tool
- **Vanilla CSS**: Custom styling (no frameworks)
- **Fetch API**: HTTP requests

## 💼 Business Model

**Target Audience**: Professional Journalists

**Value Proposition**:
- Fast fact-checking for research verification
- Multi-source corroboration
- AI-powered analysis
- Historical tracking of fact-checks
- Professional-grade reliability

## 🐛 Troubleshooting

### Backend Issues

**CORS Error**: Make sure FastAPI is running on port 8000

**API Key Error**: Ensure environment variables are set correctly

**403 Error**: Your API key may be invalid or expired - generate a new one

### Frontend Issues

**Connection Error**: Verify backend is running on `http://localhost:8000`

**Build Error**: Try deleting `node_modules` and running `npm install` again

## 📝 Project Structure

```
mumbai_hacks_supernova/
├── backend/
│   ├── app.py              # FastAPI backend with all endpoints
│   ├── main.py             # Original agentic implementation
│   └── test.py             # API testing script
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── TrendingNews.jsx
    │   │   ├── TrendingNews.css
    │   │   ├── JournalistChat.jsx
    │   │   └── JournalistChat.css
    │   ├── App.jsx
    │   ├── App.css
    │   └── main.jsx
    └── package.json
```

## 🔐 Security Notes

- Never commit API keys to version control
- Use `.env` files for sensitive data
- Rotate API keys regularly
- Monitor API usage and quotas

## 📄 License

MIT License - Feel free to use for hackathons and projects!
