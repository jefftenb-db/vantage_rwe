import React, { useState } from 'react';
import { CohortResult, saveCohortDefinition } from '../services/api';
import './CohortResults.css';

interface Props {
  result: CohortResult;
}

const CohortResults: React.FC<Props> = ({ result }) => {
  const { cohort_definition, patient_count, execution_time_seconds, demographics, sample_patient_ids, sql_query } = result;
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [savedCohortId, setSavedCohortId] = useState<number | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const handleSaveCohort = async () => {
    setIsSaving(true);
    setSaveSuccess(false);
    setSaveError(null);
    
    try {
      // Call the real API to save the cohort definition
      const response = await saveCohortDefinition(
        cohort_definition.name,
        cohort_definition.description || '',
        sql_query || ''
      );
      
      setIsSaving(false);
      setSaveSuccess(true);
      setSavedCohortId(response.cohort_definition_id);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
        setSavedCohortId(null);
      }, 3000);
    } catch (error) {
      setIsSaving(false);
      setSaveError(error instanceof Error ? error.message : 'Failed to save cohort definition');
      console.error('Error saving cohort:', error);
    }
  };

  const downloadCSV = (csvContent: string, filename: string) => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportPatients = () => {
    try {
      // Create CSV content
      let csvContent = '';
      
      // Add cohort header information
      csvContent += 'Cohort Export\n';
      csvContent += `Cohort Name,${cohort_definition.name}\n`;
      csvContent += `Description,${cohort_definition.description || 'N/A'}\n`;
      csvContent += `Total Patients,${patient_count}\n`;
      csvContent += `Execution Time,${execution_time_seconds.toFixed(2)}s\n`;
      csvContent += '\n';
      
      // Add demographics if available
      if (demographics && demographics.gender_distribution) {
        csvContent += 'Gender Distribution\n';
        csvContent += 'Gender,Count\n';
        demographics.gender_distribution.forEach((item: any) => {
          csvContent += `${item.gender},${item.count}\n`;
        });
        csvContent += '\n';
      }
      
      if (demographics && demographics.age_stats) {
        csvContent += 'Age Statistics\n';
        csvContent += 'Metric,Value\n';
        csvContent += `Mean Age,${demographics.age_stats.mean?.toFixed(1) || 0}\n`;
        csvContent += `Min Age,${demographics.age_stats.min || 0}\n`;
        csvContent += `Max Age,${demographics.age_stats.max || 0}\n`;
        csvContent += '\n';
      }
      
      // Add sample patient IDs
      if (sample_patient_ids && sample_patient_ids.length > 0) {
        csvContent += 'Sample Patient IDs\n';
        csvContent += 'Patient ID\n';
        sample_patient_ids.forEach((id) => {
          csvContent += `${id}\n`;
        });
      }
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const filename = `cohort_${cohort_definition.name.replace(/[^a-z0-9]/gi, '_')}_${timestamp}.csv`;
      
      // Trigger download
      downloadCSV(csvContent, filename);
      
      // Show success message
      setExportSuccess(true);
      setTimeout(() => {
        setExportSuccess(false);
      }, 3000);
    } catch (error) {
      console.error('Error exporting CSV:', error);
      alert('Failed to export CSV file');
    }
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

      {saveError && (
        <div className="error-message">
          ❌ Error: {saveError}
        </div>
      )}
    </div>
  );
};

export default CohortResults;

