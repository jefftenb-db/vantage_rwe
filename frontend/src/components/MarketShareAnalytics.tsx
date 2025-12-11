import React, { useState } from 'react';
import {
  getMarketShareAnalysis,
  getTrendAnalysis,
  getCompetitivePositioning,
  getNewToBrandAnalysis,
  searchConcepts,
  MarketShareResponse,
  TrendAnalysisResponse,
  CompetitivePositioning,
  NewToBrandAnalysis,
  Concept,
} from '../services/api';
import './MarketShareAnalytics.css';

type TabType = 'overview' | 'trends' | 'competitive' | 'nbx';

const MarketShareAnalytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Overview tab state
  const [overviewDrugIds, setOverviewDrugIds] = useState<string>('');
  const [overviewStartDate, setOverviewStartDate] = useState('');
  const [overviewEndDate, setOverviewEndDate] = useState('');
  const [overviewResults, setOverviewResults] = useState<MarketShareResponse | null>(null);

  // Trends tab state
  const [trendsDrugSearch, setTrendsDrugSearch] = useState('');
  const [trendsDrugConcepts, setTrendsDrugConcepts] = useState<Concept[]>([]);
  const [trendsSelectedDrugId, setTrendsSelectedDrugId] = useState<number | null>(null);
  const [trendsGranularity, setTrendsGranularity] = useState<string>('month');
  const [trendsResults, setTrendsResults] = useState<TrendAnalysisResponse | null>(null);

  // Competitive tab state
  const [compYourDrugId, setCompYourDrugId] = useState<string>('');
  const [compCompetitorIds, setCompCompetitorIds] = useState<string>('');
  const [compResults, setCompResults] = useState<CompetitivePositioning | null>(null);

  // NBx tab state
  const [nbxDrugId, setNbxDrugId] = useState<string>('');
  const [nbxStartDate, setNbxStartDate] = useState('');
  const [nbxEndDate, setNbxEndDate] = useState('');
  const [nbxResults, setNbxResults] = useState<NewToBrandAnalysis | null>(null);

  // Overview analysis
  const handleOverviewAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      const drugIds = overviewDrugIds
        .split(',')
        .map((s) => parseInt(s.trim()))
        .filter((n) => !isNaN(n));

      if (drugIds.length === 0) {
        setError('Please enter at least one drug concept ID');
        return;
      }

      const results = await getMarketShareAnalysis({
        drug_concept_ids: drugIds,
        start_date: overviewStartDate || undefined,
        end_date: overviewEndDate || undefined,
        top_n: 20,
      });

      setOverviewResults(results);
    } catch (err: any) {
      setError(err.message || 'Failed to get market share analysis');
    } finally {
      setLoading(false);
    }
  };

  // Search for drugs (trends tab)
  const handleTrendsDrugSearch = async () => {
    if (!trendsDrugSearch.trim()) return;
    try {
      setLoading(true);
      const concepts = await searchConcepts(trendsDrugSearch, 'Drug', 20);
      setTrendsDrugConcepts(concepts);
    } catch (err: any) {
      setError(err.message || 'Failed to search drugs');
    } finally {
      setLoading(false);
    }
  };

  // Get trends analysis
  const handleTrendsAnalysis = async () => {
    if (!trendsSelectedDrugId) return;
    try {
      setLoading(true);
      setError(null);
      const results = await getTrendAnalysis(
        trendsSelectedDrugId,
        undefined,
        undefined,
        trendsGranularity
      );
      setTrendsResults(results);
    } catch (err: any) {
      setError(err.message || 'Failed to get trend analysis');
    } finally {
      setLoading(false);
    }
  };

  // Competitive analysis
  const handleCompetitiveAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      const yourDrugId = parseInt(compYourDrugId);
      const competitorIds = compCompetitorIds
        .split(',')
        .map((s) => parseInt(s.trim()))
        .filter((n) => !isNaN(n));

      if (isNaN(yourDrugId)) {
        setError('Please enter your drug ID');
        return;
      }

      if (competitorIds.length === 0) {
        setError('Please enter at least one competitor drug ID');
        return;
      }

      const results = await getCompetitivePositioning(yourDrugId, competitorIds);
      setCompResults(results);
    } catch (err: any) {
      setError(err.message || 'Failed to get competitive positioning');
    } finally {
      setLoading(false);
    }
  };

  // NBx analysis
  const handleNBxAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);

      const drugId = parseInt(nbxDrugId);

      if (isNaN(drugId)) {
        setError('Please enter a valid drug ID');
        return;
      }

      if (!nbxStartDate || !nbxEndDate) {
        setError('Please enter both start and end dates');
        return;
      }

      const results = await getNewToBrandAnalysis(drugId, nbxStartDate, nbxEndDate, 365);
      setNbxResults(results);
    } catch (err: any) {
      setError(err.message || 'Failed to get NBx analysis');
    } finally {
      setLoading(false);
    }
  };

  const renderOverviewTab = () => (
    <div className="tab-content">
      <h3>Market Share Overview</h3>
      <p className="description">
        Analyze market share distribution across drugs in a therapeutic area
      </p>

      <div className="form-section">
        <div className="form-group">
          <label>Drug Concept IDs (comma-separated)</label>
          <input
            type="text"
            placeholder="e.g., 1503297, 1545999, 1594973"
            value={overviewDrugIds}
            onChange={(e) => setOverviewDrugIds(e.target.value)}
            className="form-input"
          />
          <small className="help-text">Enter drug IDs to define your market</small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Start Date (optional)</label>
            <input
              type="date"
              value={overviewStartDate}
              onChange={(e) => setOverviewStartDate(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>End Date (optional)</label>
            <input
              type="date"
              value={overviewEndDate}
              onChange={(e) => setOverviewEndDate(e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        <button onClick={handleOverviewAnalysis} disabled={loading} className="btn btn-primary">
          {loading ? '📊 Analyzing...' : '📊 Analyze Market Share'}
        </button>
      </div>

      {overviewResults && (
        <div className="results-section">
          <div className="market-summary">
            <h4>{overviewResults.market_definition}</h4>
            <p className="period">{overviewResults.time_period}</p>

            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">
                  {overviewResults.total_market_prescriptions.toLocaleString()}
                </div>
                <div className="stat-label">Total Prescriptions</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {overviewResults.total_market_patients.toLocaleString()}
                </div>
                <div className="stat-label">Total Patients</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{overviewResults.total_drugs_in_market}</div>
                <div className="stat-label">Drugs in Market</div>
              </div>
              <div className="stat-card highlight">
                <div className="stat-value">{overviewResults.top_3_concentration.toFixed(1)}%</div>
                <div className="stat-label">Top 3 Concentration</div>
              </div>
              <div className="stat-card highlight">
                <div className="stat-value">{overviewResults.herfindahl_index?.toFixed(0)}</div>
                <div className="stat-label">HHI (Concentration)</div>
              </div>
            </div>
          </div>

          <h4>Market Share by Drug</h4>
          <div className="table-container">
            <table className="market-share-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Drug</th>
                  <th>Prescriptions</th>
                  <th>Patients</th>
                  <th>Market Share (Rx)</th>
                  <th>Market Share (Patients)</th>
                  <th>Visual</th>
                </tr>
              </thead>
              <tbody>
                {overviewResults.drug_shares.map((drug) => (
                  <tr key={drug.drug_concept_id} className={drug.rank <= 3 ? 'top-3' : ''}>
                    <td>
                      <span className={`rank-badge rank-${drug.rank}`}>#{drug.rank}</span>
                    </td>
                    <td>
                      <strong>{drug.drug_name}</strong>
                    </td>
                    <td>{drug.total_prescriptions.toLocaleString()}</td>
                    <td>{drug.total_patients.toLocaleString()}</td>
                    <td>
                      <strong>{drug.market_share_by_prescriptions.toFixed(2)}%</strong>
                    </td>
                    <td>{drug.market_share_by_patients.toFixed(2)}%</td>
                    <td>
                      <div className="market-share-bar">
                        <div
                          className="market-share-fill"
                          style={{ width: `${drug.market_share_by_prescriptions}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  const renderTrendsTab = () => (
    <div className="tab-content">
      <h3>Market Share Trends</h3>
      <p className="description">Track how market share changes over time</p>

      <div className="form-section">
        <div className="form-group">
          <label>Search for Drug</label>
          <div className="search-combo">
            <input
              type="text"
              placeholder="e.g., Metformin, Lisinopril"
              value={trendsDrugSearch}
              onChange={(e) => setTrendsDrugSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleTrendsDrugSearch()}
              className="form-input"
            />
            <button onClick={handleTrendsDrugSearch} className="btn btn-secondary">
              Search
            </button>
          </div>
        </div>

        {trendsDrugConcepts.length > 0 && (
          <div className="concept-list">
            <label>Select Drug:</label>
            {trendsDrugConcepts.map((concept) => (
              <div
                key={concept.concept_id}
                className={`concept-item ${
                  trendsSelectedDrugId === concept.concept_id ? 'selected' : ''
                }`}
                onClick={() => setTrendsSelectedDrugId(concept.concept_id)}
              >
                <strong>{concept.concept_name}</strong>
                <span className="concept-meta">
                  {concept.vocabulary_id} | {concept.concept_code}
                </span>
              </div>
            ))}
          </div>
        )}

        {trendsSelectedDrugId && (
          <>
            <div className="form-group">
              <label>Time Granularity</label>
              <select
                value={trendsGranularity}
                onChange={(e) => setTrendsGranularity(e.target.value)}
                className="form-input"
              >
                <option value="month">Monthly</option>
                <option value="quarter">Quarterly</option>
                <option value="year">Yearly</option>
              </select>
            </div>

            <button onClick={handleTrendsAnalysis} disabled={loading} className="btn btn-primary">
              {loading ? '📈 Loading...' : '📈 Get Trends'}
            </button>
          </>
        )}
      </div>

      {trendsResults && (
        <div className="results-section">
          <div className="trends-summary">
            <h4>
              {trendsResults.drug_name} - Trend: {trendsResults.trend_direction.toUpperCase()}
            </h4>

            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{trendsResults.overall_change_pct.toFixed(1)}%</div>
                <div className="stat-label">Overall Change</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {trendsResults.overall_share_change > 0 ? '+' : ''}
                  {trendsResults.overall_share_change.toFixed(2)}
                </div>
                <div className="stat-label">Share Point Change</div>
              </div>
              {trendsResults.peak_market_share && (
                <div className="stat-card highlight">
                  <div className="stat-value">{trendsResults.peak_market_share.toFixed(2)}%</div>
                  <div className="stat-label">Peak Share ({trendsResults.peak_period})</div>
                </div>
              )}
            </div>
          </div>

          <h4>Trend Data</h4>
          <div className="table-container">
            <table className="market-share-table">
              <thead>
                <tr>
                  <th>Period</th>
                  <th>Prescriptions</th>
                  <th>Patients</th>
                  <th>Market Share</th>
                  <th>Rx Change %</th>
                  <th>Share Change (pts)</th>
                </tr>
              </thead>
              <tbody>
                {trendsResults.trends.map((trend, idx) => (
                  <tr key={idx}>
                    <td>
                      <strong>{trend.time_period}</strong>
                    </td>
                    <td>{trend.prescriptions.toLocaleString()}</td>
                    <td>{trend.patients.toLocaleString()}</td>
                    <td>
                      <strong>{trend.market_share.toFixed(2)}%</strong>
                    </td>
                    <td>
                      {trend.prescriptions_change_pct !== null && trend.prescriptions_change_pct !== undefined ? (
                        <span className={trend.prescriptions_change_pct >= 0 ? 'positive' : 'negative'}>
                          {trend.prescriptions_change_pct > 0 ? '+' : ''}
                          {trend.prescriptions_change_pct.toFixed(1)}%
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      {trend.market_share_change_points !== null && trend.market_share_change_points !== undefined ? (
                        <span className={trend.market_share_change_points >= 0 ? 'positive' : 'negative'}>
                          {trend.market_share_change_points > 0 ? '+' : ''}
                          {trend.market_share_change_points.toFixed(2)}
                        </span>
                      ) : (
                        '-'
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  const renderCompetitiveTab = () => (
    <div className="tab-content">
      <h3>Competitive Positioning</h3>
      <p className="description">Compare your drug's position vs. competitors</p>

      <div className="form-section">
        <div className="alert alert-info">
          <strong>💡 How to use:</strong> Enter your drug ID and competitor drug IDs to see
          relative market positioning and share gaps.
        </div>

        <div className="form-group">
          <label>Your Drug Concept ID</label>
          <input
            type="text"
            placeholder="e.g., 1503297"
            value={compYourDrugId}
            onChange={(e) => setCompYourDrugId(e.target.value)}
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label>Competitor Drug IDs (comma-separated)</label>
          <input
            type="text"
            placeholder="e.g., 1545999, 1594973, 1559684"
            value={compCompetitorIds}
            onChange={(e) => setCompCompetitorIds(e.target.value)}
            className="form-input"
          />
        </div>

        <button onClick={handleCompetitiveAnalysis} disabled={loading} className="btn btn-primary">
          {loading ? '🎯 Analyzing...' : '🎯 Analyze Competition'}
        </button>
      </div>

      {compResults && (
        <div className="results-section">
          <div className="competitive-summary">
            <h4>Your Position: {compResults.your_drug_name}</h4>

            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">#{compResults.your_rank}</div>
                <div className="stat-label">Your Rank</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{compResults.your_market_share.toFixed(2)}%</div>
                <div className="stat-label">Your Market Share</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{compResults.your_prescriptions.toLocaleString()}</div>
                <div className="stat-label">Your Prescriptions</div>
              </div>
              <div className={`stat-card ${compResults.share_gap_to_leader > 0 ? 'alert-warning' : 'highlight'}`}>
                <div className="stat-value">{compResults.share_gap_to_leader.toFixed(2)} pts</div>
                <div className="stat-label">Gap to Leader</div>
              </div>
            </div>
          </div>

          <h4>Competitive Landscape</h4>
          <div className="table-container">
            <table className="market-share-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Drug</th>
                  <th>Prescriptions</th>
                  <th>Patients</th>
                  <th>Market Share</th>
                  <th>Visual</th>
                </tr>
              </thead>
              <tbody>
                {/* Your drug */}
                <tr className="your-drug">
                  <td>
                    <span className={`rank-badge rank-${compResults.your_rank}`}>
                      #{compResults.your_rank}
                    </span>
                  </td>
                  <td>
                    <strong>{compResults.your_drug_name}</strong> <span className="you-badge">YOU</span>
                  </td>
                  <td>{compResults.your_prescriptions.toLocaleString()}</td>
                  <td>{compResults.your_patients.toLocaleString()}</td>
                  <td>
                    <strong>{compResults.your_market_share.toFixed(2)}%</strong>
                  </td>
                  <td>
                    <div className="market-share-bar">
                      <div
                        className="market-share-fill your-fill"
                        style={{ width: `${compResults.your_market_share}%` }}
                      ></div>
                    </div>
                  </td>
                </tr>
                {/* Competitors */}
                {compResults.competitors.map((competitor) => (
                  <tr key={competitor.drug_concept_id}>
                    <td>
                      <span className={`rank-badge rank-${competitor.rank}`}>
                        #{competitor.rank}
                      </span>
                    </td>
                    <td>{competitor.drug_name}</td>
                    <td>{competitor.total_prescriptions.toLocaleString()}</td>
                    <td>{competitor.total_patients.toLocaleString()}</td>
                    <td>
                      <strong>{competitor.market_share_by_prescriptions.toFixed(2)}%</strong>
                    </td>
                    <td>
                      <div className="market-share-bar">
                        <div
                          className="market-share-fill"
                          style={{ width: `${competitor.market_share_by_prescriptions}%` }}
                        ></div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  const renderNBxTab = () => (
    <div className="tab-content">
      <h3>New-to-Brand (NBx) Analysis</h3>
      <p className="description">Analyze where new patients are coming from</p>

      <div className="form-section">
        <div className="form-group">
          <label>Drug Concept ID</label>
          <input
            type="text"
            placeholder="e.g., 1503297"
            value={nbxDrugId}
            onChange={(e) => setNbxDrugId(e.target.value)}
            className="form-input"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Start Date</label>
            <input
              type="date"
              value={nbxStartDate}
              onChange={(e) => setNbxStartDate(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>End Date</label>
            <input
              type="date"
              value={nbxEndDate}
              onChange={(e) => setNbxEndDate(e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        <button onClick={handleNBxAnalysis} disabled={loading} className="btn btn-primary">
          {loading ? '🔄 Analyzing...' : '🔄 Analyze NBx'}
        </button>
      </div>

      {nbxResults && (
        <div className="results-section">
          <div className="nbx-summary">
            <h4>{nbxResults.drug_name}</h4>
            <p className="period">{nbxResults.time_period}</p>

            <div className="stat-cards">
              <div className="stat-card highlight">
                <div className="stat-value">{nbxResults.new_patients.toLocaleString()}</div>
                <div className="stat-label">New Patients (NBx)</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{nbxResults.total_patients.toLocaleString()}</div>
                <div className="stat-label">Total Patients</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{nbxResults.nbx_rate.toFixed(1)}%</div>
                <div className="stat-label">NBx Rate</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{nbxResults.treatment_naive.toLocaleString()}</div>
                <div className="stat-label">Treatment Naive</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{nbxResults.switched_from_competitor.toLocaleString()}</div>
                <div className="stat-label">Switched from Competitor</div>
              </div>
            </div>
          </div>

          {nbxResults.switch_sources.length > 0 && (
            <>
              <h4>Source of Switchers</h4>
              <div className="table-container">
                <table className="market-share-table">
                  <thead>
                    <tr>
                      <th>Competitor Drug</th>
                      <th>Patients Switched</th>
                      <th>% of Total Switchers</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nbxResults.switch_sources.map((source, idx) => (
                      <tr key={idx}>
                        <td>
                          <strong>{source.drug_name}</strong>
                        </td>
                        <td>{source.patient_count.toLocaleString()}</td>
                        <td>
                          {((source.patient_count / nbxResults.switched_from_competitor) * 100).toFixed(1)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className="market-share-analytics">
      <div className="analytics-header">
        <h2>📈 Market Share Analytics</h2>
        <p>Competitive intelligence and market dynamics analysis</p>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={`tab ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          📈 Trends
        </button>
        <button
          className={`tab ${activeTab === 'competitive' ? 'active' : ''}`}
          onClick={() => setActiveTab('competitive')}
        >
          🎯 Competitive
        </button>
        <button
          className={`tab ${activeTab === 'nbx' ? 'active' : ''}`}
          onClick={() => setActiveTab('nbx')}
        >
          🔄 NBx
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'trends' && renderTrendsTab()}
      {activeTab === 'competitive' && renderCompetitiveTab()}
      {activeTab === 'nbx' && renderNBxTab()}
    </div>
  );
};

export default MarketShareAnalytics;

