import React, { useState } from 'react';
import { CohortResult } from '../services/api';
import './CohortResults.css';

interface Props {
  result: CohortResult;
}

const CohortResults: React.FC<Props> = ({ result }) => {
  const { patient_count, execution_time_seconds, demographics, sample_patient_ids } = result;
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [savedCohortId, setSavedCohortId] = useState<number | null>(null);

  const handleSaveCohort = () => {
    setIsSaving(true);
    setSaveSuccess(false);
    
    // Generate random cohort_definition_id between 1 and 100000
    const cohortId = Math.floor(Math.random() * 100000) + 1;
    
    // Simulate saving the cohort definition
    setTimeout(() => {
      setIsSaving(false);
      setSaveSuccess(true);
      setSavedCohortId(cohortId);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
        setSavedCohortId(null);
      }, 3000);
    }, 1000);
  };

  const handleExportPatients = () => {
    setExportSuccess(true);
    
    // Simulate export
    setTimeout(() => {
      setExportSuccess(false);
    }, 3000);
  };

  return (
    <div className="cohort-results">
      <h3 className="results-header">📊 Cohort Results</h3>

      <div className="results-summary">
        <div className="summary-card highlight">
          <div className="summary-icon">👥</div>
          <div className="summary-content">
            <div className="summary-value">{patient_count.toLocaleString()}</div>
            <div className="summary-label">Patients in Cohort</div>
          </div>
        </div>

        <div className="summary-card">
          <div className="summary-icon">⏱️</div>
          <div className="summary-content">
            <div className="summary-value">{execution_time_seconds.toFixed(2)}s</div>
            <div className="summary-label">Execution Time</div>
          </div>
        </div>
      </div>

      {demographics && demographics.gender_distribution && (
        <div className="demographics-section">
          <h4>Demographics Summary</h4>
          
          <div className="demographics-grid">
            <div className="demo-card">
              <h5>Gender Distribution</h5>
              <div className="distribution-list">
                {demographics.gender_distribution.map((item: any, index: number) => (
                  <div key={index} className="distribution-item">
                    <span className="distribution-label">{item.gender}</span>
                    <span className="distribution-value">{item.count.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            </div>

            {demographics.age_stats && (
              <div className="demo-card">
                <h5>Age Statistics</h5>
                <div className="distribution-list">
                  <div className="distribution-item">
                    <span className="distribution-label">Mean Age</span>
                    <span className="distribution-value">
                      {typeof demographics.age_stats.mean === 'number' 
                        ? demographics.age_stats.mean.toFixed(1) 
                        : '0.0'} years
                    </span>
                  </div>
                  <div className="distribution-item">
                    <span className="distribution-label">Min Age</span>
                    <span className="distribution-value">{demographics.age_stats.min || 0} years</span>
                  </div>
                  <div className="distribution-item">
                    <span className="distribution-label">Max Age</span>
                    <span className="distribution-value">{demographics.age_stats.max || 0} years</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {sample_patient_ids && sample_patient_ids.length > 0 && (
        <div className="sample-patients">
          <h4>Sample Patient IDs</h4>
          <div className="patient-ids">
            {sample_patient_ids.map((id) => (
              <span key={id} className="patient-id-badge">{id}</span>
            ))}
          </div>
        </div>
      )}

      <div className="export-section">
        <button 
          className="btn btn-primary" 
          onClick={handleExportPatients}
          disabled={exportSuccess}
        >
          {exportSuccess ? '✅ Exported!' : '📥 Export Patient List'}
        </button>
        <button 
          className={`btn btn-secondary ${isSaving ? 'btn-saving' : ''} ${saveSuccess ? 'btn-success' : ''}`}
          onClick={handleSaveCohort}
          disabled={isSaving || saveSuccess}
        >
          {isSaving ? '💾 Saving...' : saveSuccess ? '✅ Saved!' : '💾 Save Cohort Definition'}
        </button>
      </div>

      {saveSuccess && savedCohortId && (
        <div className="success-message">
          ✅ Saved cohort with cohort_definition_id {savedCohortId}
        </div>
      )}

      {exportSuccess && (
        <div className="success-message">
          ✅ Patient list has been exported successfully!
        </div>
      )}
    </div>
  );
};

export default CohortResults;

