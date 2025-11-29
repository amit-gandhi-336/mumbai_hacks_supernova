import { useState } from 'react';
import './JournalistChat.css';

const API_URL = 'http://localhost:8000';

function JournalistChat() {
  const [claim, setClaim] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!claim.trim()) {
      setError('Please enter a claim to fact-check');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_URL}/api/fact-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ claim: claim.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const errorMessage = errorData?.detail || `Server error: ${response.status}`;
        
        if (response.status === 500 && errorMessage.includes('rate limit')) {
          throw new Error('⚠️ Rate limit reached. Please wait a moment and try again.');
        } else if (response.status === 500 && errorMessage.includes('API key')) {
          throw new Error('⚠️ API configuration issue. Please check your API keys.');
        } else {
          throw new Error(errorMessage);
        }
      }

      const data = await response.json();
      setResult(data.data);
      
      // Add to history
      setHistory(prev => [{
        claim: claim.trim(),
        result: data.data,
        timestamp: new Date().toLocaleString()
      }, ...prev]);
      
      setClaim('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => {
    setHistory([]);
    setResult(null);
  };

  return (
    <div className="journalist-chat">
      <div className="section-header">
        <h2>💼 Journalist Fact-Checking Tool</h2>
        <p>Enter any claim or news statement for comprehensive fact-checking</p>
        <div className="rate-limit-notice">
          ⏱️ <strong>Tip:</strong> If you see rate limit errors, wait 60 seconds between requests or refresh the page
        </div>
      </div>

      <div className="chat-container">
        <div className="input-section">
          <form onSubmit={handleSubmit} className="fact-check-form">
            <div className="input-group">
              <label htmlFor="claim-input">Enter Claim to Fact-Check:</label>
              <textarea
                id="claim-input"
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="E.g., 'New study shows coffee reduces heart disease risk by 50%'"
                rows="4"
                disabled={loading}
                className="claim-input"
              />
            </div>

            <button 
              type="submit" 
              className="submit-btn"
              disabled={loading || !claim.trim()}
            >
              {loading ? '🔍 Analyzing...' : '🔍 Fact-Check'}
            </button>
          </form>

          {error && (
            <div className="error">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        {result && (
          <div className="result-section">
            <div className="result-card">
              <div className="result-header">
                <h3>📊 Fact-Check Analysis</h3>
                <span className="verdict-badge analysis">
                  {result.verdict}
                </span>
              </div>

              <div className="claim-display">
                <strong>Claim Analyzed:</strong>
                <p>{result.claim}</p>
              </div>

              {result.google_fact_check && result.google_fact_check.verdict !== 'UNCHECKED' && (
                <div className="google-verdict">
                  <h4>🔍 Official Fact-Check</h4>
                  <div className="verdict-info">
                    <span className={`verdict-badge ${result.google_fact_check.verdict.toLowerCase()}`}>
                      {result.google_fact_check.verdict}
                    </span>
                    <p><strong>Source:</strong> {result.google_fact_check.source}</p>
                    <p>{result.google_fact_check.summary}</p>
                  </div>
                </div>
              )}

              <div className="ai-analysis">
                <h4>🤖 AI Analysis</h4>
                <div className="analysis-content">
                  {result.analysis}
                </div>
              </div>

              {result.supporting_articles && result.supporting_articles.length > 0 && (
                <div className="supporting-articles">
                  <h4>📰 Supporting Articles ({result.articles_count})</h4>
                  <div className="articles-list">
                    {result.supporting_articles.map((article, idx) => (
                      <div key={idx} className="article-item">
                        <h5>{article.title}</h5>
                        <p className="article-source">
                          <strong>{article.source}</strong> • {article.pubDate}
                        </p>
                        {article.description && (
                          <p className="article-desc">{article.description}</p>
                        )}
                        {article.url && (
                          <a 
                            href={article.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="article-link"
                          >
                            Read Article →
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {history.length > 0 && (
          <div className="history-section">
            <div className="history-header">
              <h3>📜 Recent Fact-Checks</h3>
              <button onClick={clearHistory} className="clear-btn">
                Clear History
              </button>
            </div>
            <div className="history-list">
              {history.map((item, idx) => (
                <div key={idx} className="history-item">
                  <div className="history-meta">
                    <span className="history-time">{item.timestamp}</span>
                    <span className={`verdict-badge small ${item.result.verdict.toLowerCase()}`}>
                      {item.result.verdict}
                    </span>
                  </div>
                  <p className="history-claim">{item.claim}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default JournalistChat;
