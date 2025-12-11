import React, { useState } from 'react';
import {
  searchPrescribers,
  getDrugPrescriberAnalytics,
  identifyTargetPrescribers,
  getPrescriberTreatmentPathways,
  searchConcepts,
  PrescriberMetrics,
  DrugPrescriberAnalytics,
  PrescriberTargetingResponse,
  TreatmentPathway,
  Concept,
} from '../services/api';
import './PrescriberAnalytics.css';

type TabType = 'search' | 'drug-analytics' | 'targeting' | 'pathways';

const PrescriberAnalytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('search');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search tab state
  const [searchSpecialty, setSearchSpecialty] = useState('');
  const [searchMinPatients, setSearchMinPatients] = useState<number>(10);
  const [searchResults, setSearchResults] = useState<PrescriberMetrics[]>([]);

  // Drug analytics tab state
  const [drugSearchQuery, setDrugSearchQuery] = useState('');
  const [drugConcepts, setDrugConcepts] = useState<Concept[]>([]);
  const [selectedDrugId, setSelectedDrugId] = useState<number | null>(null);
  const [drugAnalytics, setDrugAnalytics] = useState<DrugPrescriberAnalytics | null>(null);

  // Targeting tab state
  const [targetDrugIds, setTargetDrugIds] = useState<number[]>([]);
  const [competitorDrugIds, setCompetitorDrugIds] = useState<number[]>([]);
  const [targetingResults, setTargetingResults] = useState<PrescriberTargetingResponse | null>(null);

  // Pathways tab state
  const [pathwayProviderId, setPathwayProviderId] = useState<string>('');
  const [pathwayData, setPathwayData] = useState<TreatmentPathway | null>(null);

  // Search prescribers
  const handleSearchPrescribers = async () => {
    try {
      setLoading(true);
      setError(null);
      const results = await searchPrescribers({
        specialty: searchSpecialty || undefined,
        min_patients: searchMinPatients,
        limit: 50,
      });
      setSearchResults(results);
    } catch (err: any) {
      setError(err.message || 'Failed to search prescribers');
    } finally {
      setLoading(false);
    }
  };

  // Search for drugs
  const handleDrugSearch = async () => {
    if (!drugSearchQuery.trim()) return;
    try {
      setLoading(true);
      const concepts = await searchConcepts(drugSearchQuery, 'Drug', 20);
      setDrugConcepts(concepts);
    } catch (err: any) {
      setError(err.message || 'Failed to search drugs');
    } finally {
      setLoading(false);
    }
  };

  // Get drug prescriber analytics
  const handleGetDrugAnalytics = async () => {
    if (!selectedDrugId) return;
    try {
      setLoading(true);
      setError(null);
      const analytics = await getDrugPrescriberAnalytics(selectedDrugId, 50);
      setDrugAnalytics(analytics);
    } catch (err: any) {
      setError(err.message || 'Failed to get drug analytics');
    } finally {
      setLoading(false);
    }
  };

  // Identify target prescribers
  const handleTargeting = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await identifyTargetPrescribers({
        target_drug_concept_ids: targetDrugIds.length > 0 ? targetDrugIds : undefined,
        competitor_drug_concept_ids: competitorDrugIds.length > 0 ? competitorDrugIds : undefined,
        min_relevant_patients: 10,
        limit: 100,
      });
      setTargetingResults(response);
    } catch (err: any) {
      setError(err.message || 'Failed to identify target prescribers');
    } finally {
      setLoading(false);
    }
  };

  // Get treatment pathways
  const handleGetPathways = async () => {
    const providerId = parseInt(pathwayProviderId);
    if (isNaN(providerId)) {
      setError('Please enter a valid provider ID');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      const pathways = await getPrescriberTreatmentPathways(providerId);
      setPathwayData(pathways);
    } catch (err: any) {
      setError(err.message || 'Failed to get treatment pathways');
    } finally {
      setLoading(false);
    }
  };

  const renderSearchTab = () => (
    <div className="tab-content">
      <h3>Search Prescribers</h3>
      <p className="description">Find prescribers by specialty and patient volume</p>

      <div className="form-section">
        <div className="form-group">
          <label>Specialty (optional)</label>
          <input
            type="text"
            placeholder="e.g., Cardiology, Oncology"
            value={searchSpecialty}
            onChange={(e) => setSearchSpecialty(e.target.value)}
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label>Minimum Patients</label>
          <input
            type="number"
            value={searchMinPatients}
            onChange={(e) => setSearchMinPatients(parseInt(e.target.value) || 0)}
            className="form-input"
          />
        </div>

        <button onClick={handleSearchPrescribers} disabled={loading} className="btn btn-primary">
          {loading ? '🔍 Searching...' : '🔍 Search Prescribers'}
        </button>
      </div>

      {searchResults.length > 0 && (
        <div className="results-section">
          <h4>Found {searchResults.length} Prescribers</h4>
          <div className="table-container">
            <table className="prescriber-table">
              <thead>
                <tr>
                  <th>Provider ID</th>
                  <th>Name</th>
                  <th>Specialty</th>
                  <th>Patients</th>
                  <th>Prescriptions</th>
                  <th>Decile</th>
                  <th>Percentile</th>
                </tr>
              </thead>
              <tbody>
                {searchResults.map((prescriber) => (
                  <tr key={prescriber.provider_id}>
                    <td>{prescriber.provider_id}</td>
                    <td>{prescriber.provider_name || 'N/A'}</td>
                    <td>{prescriber.specialty || 'N/A'}</td>
                    <td>{prescriber.total_patients.toLocaleString()}</td>
                    <td>{prescriber.total_prescriptions.toLocaleString()}</td>
                    <td>
                      <span className={`decile-badge decile-${prescriber.decile}`}>
                        D{prescriber.decile}
                      </span>
                    </td>
                    <td>{prescriber.percentile_rank?.toFixed(1)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  const renderDrugAnalyticsTab = () => (
    <div className="tab-content">
      <h3>Drug Prescriber Analytics</h3>
      <p className="description">See top prescribers and market concentration for a specific drug</p>

      <div className="form-section">
        <div className="form-group">
          <label>Search for Drug</label>
          <div className="search-combo">
            <input
              type="text"
              placeholder="e.g., Metformin, Lisinopril"
              value={drugSearchQuery}
              onChange={(e) => setDrugSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleDrugSearch()}
              className="form-input"
            />
            <button onClick={handleDrugSearch} className="btn btn-secondary">
              Search
            </button>
          </div>
        </div>

        {drugConcepts.length > 0 && (
          <div className="concept-list">
            <label>Select Drug:</label>
            {drugConcepts.map((concept) => (
              <div
                key={concept.concept_id}
                className={`concept-item ${selectedDrugId === concept.concept_id ? 'selected' : ''}`}
                onClick={() => setSelectedDrugId(concept.concept_id)}
              >
                <strong>{concept.concept_name}</strong>
                <span className="concept-meta">
                  {concept.vocabulary_id} | {concept.concept_code}
                </span>
              </div>
            ))}
          </div>
        )}

        {selectedDrugId && (
          <button onClick={handleGetDrugAnalytics} disabled={loading} className="btn btn-primary">
            {loading ? '📊 Loading Analytics...' : '📊 Get Analytics'}
          </button>
        )}
      </div>

      {drugAnalytics && (
        <div className="results-section">
          <div className="analytics-summary">
            <h4>{drugAnalytics.drug_name}</h4>
            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{drugAnalytics.total_prescriptions.toLocaleString()}</div>
                <div className="stat-label">Total Prescriptions</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{drugAnalytics.total_unique_prescribers.toLocaleString()}</div>
                <div className="stat-label">Unique Prescribers</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{drugAnalytics.total_unique_patients.toLocaleString()}</div>
                <div className="stat-label">Unique Patients</div>
              </div>
              {drugAnalytics.top_10_percent_share && (
                <div className="stat-card highlight">
                  <div className="stat-value">{drugAnalytics.top_10_percent_share.toFixed(1)}%</div>
                  <div className="stat-label">Top 10% Prescriber Share</div>
                </div>
              )}
            </div>
          </div>

          <h4>Top Prescribers</h4>
          <div className="table-container">
            <table className="prescriber-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Name</th>
                  <th>Specialty</th>
                  <th>Patients</th>
                  <th>Prescriptions</th>
                  <th>Market Share</th>
                  <th>Decile</th>
                </tr>
              </thead>
              <tbody>
                {drugAnalytics.top_prescribers.map((prescriber, idx) => (
                  <tr key={prescriber.provider_id}>
                    <td>#{idx + 1}</td>
                    <td>{prescriber.provider_name || 'N/A'}</td>
                    <td>{prescriber.specialty || 'N/A'}</td>
                    <td>{prescriber.total_patients.toLocaleString()}</td>
                    <td>{prescriber.total_prescriptions.toLocaleString()}</td>
                    <td>{prescriber.market_share?.toFixed(2)}%</td>
                    <td>
                      <span className={`decile-badge decile-${prescriber.decile}`}>
                        D{prescriber.decile}
                      </span>
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

  const renderTargetingTab = () => (
    <div className="tab-content">
      <h3>Prescriber Targeting</h3>
      <p className="description">
        Identify high-value prescribers who prescribe competitors but not your drug
      </p>

      <div className="form-section">
        <div className="alert alert-info">
          <strong>💡 How it works:</strong> This finds prescribers with relevant patients who prescribe
          competitor drugs but have low/no adoption of your target drug. Higher scores = better targets.
        </div>

        <div className="form-group">
          <label>Target Drug IDs (comma-separated, optional)</label>
          <input
            type="text"
            placeholder="e.g., 1503297, 1545999"
            onChange={(e) => {
              const ids = e.target.value
                .split(',')
                .map((s) => parseInt(s.trim()))
                .filter((n) => !isNaN(n));
              setTargetDrugIds(ids);
            }}
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label>Competitor Drug IDs (comma-separated, required)</label>
          <input
            type="text"
            placeholder="e.g., 1503297, 1545999"
            onChange={(e) => {
              const ids = e.target.value
                .split(',')
                .map((s) => parseInt(s.trim()))
                .filter((n) => !isNaN(n));
              setCompetitorDrugIds(ids);
            }}
            className="form-input"
          />
        </div>

        <button
          onClick={handleTargeting}
          disabled={loading || competitorDrugIds.length === 0}
          className="btn btn-primary"
        >
          {loading ? '🎯 Analyzing...' : '🎯 Identify Targets'}
        </button>
      </div>

      {targetingResults && (
        <div className="results-section">
          <div className="targeting-summary">
            <h4>Targeting Summary</h4>
            <div className="stat-cards">
              <div className="stat-card">
                <div className="stat-value">{targetingResults.total_target_prescribers}</div>
                <div className="stat-label">Total Targets</div>
              </div>
              <div className="stat-card priority-high">
                <div className="stat-value">{targetingResults.high_priority_count}</div>
                <div className="stat-label">High Priority (Score &gt; 80)</div>
              </div>
              <div className="stat-card priority-medium">
                <div className="stat-value">{targetingResults.medium_priority_count}</div>
                <div className="stat-label">Medium Priority (50-80)</div>
              </div>
              <div className="stat-card highlight">
                <div className="stat-value">
                  {targetingResults.total_opportunity_prescriptions.toLocaleString()}
                </div>
                <div className="stat-label">Total Opportunity (Rx)</div>
              </div>
            </div>
          </div>

          <h4>Target Prescribers</h4>
          <div className="table-container">
            <table className="prescriber-table">
              <thead>
                <tr>
                  <th>Priority</th>
                  <th>Score</th>
                  <th>Name</th>
                  <th>Specialty</th>
                  <th>Relevant Patients</th>
                  <th>Competitor Rx</th>
                  <th>Your Drug Rx</th>
                  <th>Opportunity</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                {targetingResults.targets.map((target) => {
                  const priority =
                    target.reason_score > 80 ? 'high' : target.reason_score >= 50 ? 'medium' : 'low';
                  return (
                    <tr key={target.provider_id} className={`priority-${priority}`}>
                      <td>
                        <span className={`priority-badge priority-${priority}`}>
                          {priority.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <strong>{target.reason_score.toFixed(1)}</strong>
                      </td>
                      <td>{target.provider_name || 'N/A'}</td>
                      <td>{target.specialty || 'N/A'}</td>
                      <td>{target.relevant_patients}</td>
                      <td>{target.competitor_prescriptions}</td>
                      <td>{target.target_drug_prescriptions}</td>
                      <td>{target.estimated_opportunity || 0}</td>
                      <td>
                        {target.state || 'N/A'}
                        {target.zip_code && ` (${target.zip_code})`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );

  const renderPathwaysTab = () => (
    <div className="tab-content">
      <h3>Treatment Pathways</h3>
      <p className="description">See what drugs a prescriber uses first-line and switching patterns</p>

      <div className="form-section">
        <div className="form-group">
          <label>Provider ID</label>
          <input
            type="text"
            placeholder="Enter provider ID"
            value={pathwayProviderId}
            onChange={(e) => setPathwayProviderId(e.target.value)}
            className="form-input"
          />
        </div>

        <button onClick={handleGetPathways} disabled={loading} className="btn btn-primary">
          {loading ? '📈 Loading...' : '📈 Get Pathways'}
        </button>
      </div>

      {pathwayData && (
        <div className="results-section">
          <h4>
            Treatment Pathways for {pathwayData.provider_name || `Provider ${pathwayData.provider_id}`}
          </h4>

          {pathwayData.first_line_drugs.length > 0 && (
            <div className="pathway-section">
              <h5>First-Line Drug Preferences</h5>
              <div className="table-container">
                <table className="pathway-table">
                  <thead>
                    <tr>
                      <th>Drug</th>
                      <th>Patients Started</th>
                      <th>Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pathwayData.first_line_drugs.map((drug, idx) => (
                      <tr key={idx}>
                        <td>
                          <strong>{drug.drug_name}</strong>
                        </td>
                        <td>{drug.patient_count}</td>
                        <td>
                          <div className="percentage-bar">
                            <div
                              className="percentage-fill"
                              style={{ width: `${drug.percentage}%` }}
                            ></div>
                            <span className="percentage-text">{drug.percentage.toFixed(1)}%</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {pathwayData.switch_patterns.length > 0 && (
            <div className="pathway-section">
              <h5>Drug Switching Patterns</h5>
              <div className="table-container">
                <table className="pathway-table">
                  <thead>
                    <tr>
                      <th>From Drug</th>
                      <th>→</th>
                      <th>To Drug</th>
                      <th>Switch Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {pathwayData.switch_patterns.map((pattern, idx) => (
                      <tr key={idx}>
                        <td>{pattern.from_drug}</td>
                        <td className="arrow">→</td>
                        <td>{pattern.to_drug}</td>
                        <td>
                          <strong>{pattern.switch_count}</strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  return (
    <div className="prescriber-analytics">
      <div className="analytics-header">
        <h2>👨‍⚕️ Prescriber Analytics</h2>
        <p>Commercial intelligence for targeting and market insights</p>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          🔍 Search
        </button>
        <button
          className={`tab ${activeTab === 'drug-analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('drug-analytics')}
        >
          📊 Drug Analytics
        </button>
        <button
          className={`tab ${activeTab === 'targeting' ? 'active' : ''}`}
          onClick={() => setActiveTab('targeting')}
        >
          🎯 Targeting
        </button>
        <button
          className={`tab ${activeTab === 'pathways' ? 'active' : ''}`}
          onClick={() => setActiveTab('pathways')}
        >
          📈 Pathways
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}

      {activeTab === 'search' && renderSearchTab()}
      {activeTab === 'drug-analytics' && renderDrugAnalyticsTab()}
      {activeTab === 'targeting' && renderTargetingTab()}
      {activeTab === 'pathways' && renderPathwaysTab()}
    </div>
  );
};

export default PrescriberAnalytics;

