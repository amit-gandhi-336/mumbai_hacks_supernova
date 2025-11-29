import { useState } from 'react';
import TrendingNews from './components/TrendingNews';
import JournalistChat from './components/JournalistChat';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('trending');

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">🔍 Project Clarion</h1>
          <p className="tagline">AI-Powered Fact-Checking Platform</p>
        </div>
      </header>

      <nav className="nav-tabs">
        <button
          className={`tab ${activeTab === 'trending' ? 'active' : ''}`}
          onClick={() => setActiveTab('trending')}
        >
          📰 Trending News
        </button>
        <button
          className={`tab ${activeTab === 'journalist' ? 'active' : ''}`}
          onClick={() => setActiveTab('journalist')}
        >
          💼 Journalist Tools
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'trending' ? <TrendingNews /> : <JournalistChat />}
      </main>

      <footer className="footer">
        <p>© 2025 Project Clarion | Fighting Misinformation with AI</p>
      </footer>
    </div>
  );
}

export default App;
