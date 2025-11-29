import { useState, useEffect } from 'react';
import './TrendingNews.css';

const API_URL = 'http://localhost:8000';

function TrendingNews() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTrendingNews();
  }, []);

  const fetchTrendingNews = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_URL}/api/trending`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch trending news');
      }
      
      const data = await response.json();
      setNews(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getVerdictClass = (verdict) => {
    const v = verdict.toUpperCase();
    if (v.includes('VERIFIED') || v.includes('TRUE')) return 'verified';
    if (v.includes('FALSE') || v.includes('MISLEADING')) return 'false';
    if (v.includes('UNCHECKED') || v.includes('NEEDS')) return 'unchecked';
    return 'unchecked';
  };

  const getVerdictIcon = (verdict) => {
    const v = verdict.toUpperCase();
    if (v.includes('VERIFIED') || v.includes('TRUE')) return '✅';
    if (v.includes('FALSE') || v.includes('MISLEADING')) return '❌';
    if (v.includes('UNCHECKED') || v.includes('NEEDS')) return '⚠️';
    return '🔍';
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading trending news...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <h3>Error Loading News</h3>
        <p>{error}</p>
        <button onClick={fetchTrendingNews} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="trending-news">
      <div className="section-header">
        <h2>📰 Top 5 Trending News</h2>
        <p>Real-time fact-checking of trending stories</p>
        <button onClick={fetchTrendingNews} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="news-grid">
        {news.map((item) => (
          <div key={item.id} className="news-card">
            <div className="news-header">
              <span className="news-number">#{item.id}</span>
              <span className={`verdict-badge ${getVerdictClass(item.verdict)}`}>
                {getVerdictIcon(item.verdict)} {item.verdict}
              </span>
            </div>

            <h3 className="news-title">{item.title}</h3>

            <div className="news-meta">
              <span className="news-source">📰 {item.source}</span>
              {item.published_date && (
                <span className="news-date">🕒 {item.published_date}</span>
              )}
            </div>

            <div className="fact-check-info">
              <p className="fact-check-summary">
                <strong>Fact-Check:</strong> {item.summary}
              </p>
              {item.fact_check_source !== 'N/A' && (
                <p className="fact-check-source">
                  Source: {item.fact_check_source}
                </p>
              )}
            </div>

            {item.url && (
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="read-more"
              >
                Read Full Article →
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default TrendingNews;
