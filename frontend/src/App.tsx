import React, { useState } from 'react';
import './App.css';
import CohortBuilder from './components/CohortBuilder';
import NaturalLanguageSearch from './components/NaturalLanguageSearch';
import DatabaseStats from './components/DatabaseStats';
import PrescriberAnalytics from './components/PrescriberAnalytics';
import MarketShareAnalytics from './components/MarketShareAnalytics';

function App() {
  const [activeTab, setActiveTab] = useState<'builder' | 'genai' | 'prescribers' | 'market-share'>('builder');

  return (
    <div className="App">
      <header className="app-header">
        <h1>🏥 Cohort Builder</h1>
        <p className="subtitle">Interactive Patient Cohort Creation from Healthcare Data</p>
      </header>

      <div className="container">
        <DatabaseStats />
        
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'builder' ? 'active' : ''}`}
            onClick={() => setActiveTab('builder')}
          >
            📊 Cohort Builder
          </button>
          <button
            className={`tab ${activeTab === 'genai' ? 'active' : ''}`}
            onClick={() => setActiveTab('genai')}
          >
            🤖 GenAI Query
          </button>
          <button
            className={`tab ${activeTab === 'prescribers' ? 'active' : ''}`}
            onClick={() => setActiveTab('prescribers')}
          >
            👨‍⚕️ Prescriber Analytics
          </button>
          <button
            className={`tab ${activeTab === 'market-share' ? 'active' : ''}`}
            onClick={() => setActiveTab('market-share')}
          >
            📈 Market Share
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'builder' && <CohortBuilder />}
          {activeTab === 'genai' && <NaturalLanguageSearch />}
          {activeTab === 'prescribers' && <PrescriberAnalytics />}
          {activeTab === 'market-share' && <MarketShareAnalytics />}
        </div>
      </div>
    </div>
  );
}

export default App;

