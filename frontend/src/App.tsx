import React, { useState } from 'react';
import './App.css';
import CohortBuilder from './components/CohortBuilder';
import NaturalLanguageSearch from './components/NaturalLanguageSearch';
import DatabaseStats from './components/DatabaseStats';
import PrescriberAnalytics from './components/PrescriberAnalytics';
import MarketShareAnalytics from './components/MarketShareAnalytics';

function App() {
  const [activeTab, setActiveTab] = useState<'home' | 'builder' | 'genai' | 'prescribers' | 'market-share'>('home');

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="home-content">
            <h2>Welcome to Vantage RWE</h2>
            <p className="home-subtitle">Commercial Intelligence from Real-World Evidence</p>
            
            <div className="features-grid">
              <div className="feature-card" onClick={() => setActiveTab('builder')}>
                <div className="feature-icon">📊</div>
                <h3>Cohort Builder</h3>
                <p>Build and analyze patient cohorts using clinical criteria. Filter by conditions, drugs, procedures, demographics, and more.</p>
                <button className="feature-btn">Get Started →</button>
              </div>

              <div className="feature-card" onClick={() => setActiveTab('genai')}>
                <div className="feature-icon">🤖</div>
                <h3>GenAI Query</h3>
                <p>Ask questions in natural language and get instant insights from your healthcare data powered by AI.</p>
                <button className="feature-btn">Try It Now →</button>
              </div>

              <div className="feature-card" onClick={() => setActiveTab('prescribers')}>
                <div className="feature-icon">👨‍⚕️</div>
                <h3>Prescriber Analytics</h3>
                <p>Analyze prescriber behavior, identify key opinion leaders, and understand prescription patterns across specialties.</p>
                <button className="feature-btn">Explore →</button>
              </div>

              <div className="feature-card" onClick={() => setActiveTab('market-share')}>
                <div className="feature-icon">📈</div>
                <h3>Market Share</h3>
                <p>Track drug market share over time, compare therapeutic classes, and identify trends in prescription volume.</p>
                <button className="feature-btn">View Analytics →</button>
              </div>
            </div>

            <div className="quick-start">
              <h3>Quick Start Guide</h3>
              <ul>
                <li><strong>Cohort Builder:</strong> Start by selecting criteria to build your patient population</li>
                <li><strong>GenAI Query:</strong> Ask questions like "Show me diabetes patients on insulin"</li>
                <li><strong>Prescriber Analytics:</strong> Discover top prescribers and their prescription patterns</li>
                <li><strong>Market Share:</strong> Analyze market dynamics and competitive positioning</li>
              </ul>
            </div>
          </div>
        );
      case 'builder':
        return <CohortBuilder />;
      case 'genai':
        return <NaturalLanguageSearch />;
      case 'prescribers':
        return <PrescriberAnalytics />;
      case 'market-share':
        return <MarketShareAnalytics />;
      default:
        return null;
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-title">
          <h1>📊 Vantage RWE</h1>
          <p className="subtitle">Commercial Intelligence from Real-World Evidence</p>
        </div>
        <DatabaseStats />
      </header>

      <div className="app-layout">
        <nav className="sidebar">
          <button
            className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            <span className="nav-icon">🏠</span>
            <span className="nav-label">Home</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'builder' ? 'active' : ''}`}
            onClick={() => setActiveTab('builder')}
          >
            <span className="nav-icon">📊</span>
            <span className="nav-label">Cohort Builder</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'genai' ? 'active' : ''}`}
            onClick={() => setActiveTab('genai')}
          >
            <span className="nav-icon">🤖</span>
            <span className="nav-label">GenAI Query</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'prescribers' ? 'active' : ''}`}
            onClick={() => setActiveTab('prescribers')}
          >
            <span className="nav-icon">👨‍⚕️</span>
            <span className="nav-label">Prescriber Analytics</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'market-share' ? 'active' : ''}`}
            onClick={() => setActiveTab('market-share')}
          >
            <span className="nav-icon">📈</span>
            <span className="nav-label">Market Share</span>
          </button>
        </nav>

        <main className="main-content">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;

