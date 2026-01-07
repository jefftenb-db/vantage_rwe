import React, { useState } from 'react';
import { naturalLanguageQuery, NaturalLanguageResponse, saveCohortDefinition } from '../services/api';
import CohortResults from './CohortResults';
import './NaturalLanguageSearch.css';

const NaturalLanguageSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<NaturalLanguageResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [savedCohortId, setSavedCohortId] = useState<number | null>(null);

  const exampleQueries = [
    "Show me patients with Type 2 Diabetes who were prescribed Metformin",
    "Find patients with hypertension who had a stroke",
    "Patients with COPD who have been to the emergency room",
    "Type 1 Diabetes patients on insulin therapy",
    "Patients with heart disease who had bypass surgery"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await naturalLanguageQuery(query);
      setResponse(result);
    } catch (err: any) {
      setError(err.message || 'Failed to process query');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  const handleSaveCohort = async () => {
    if (!response) return;
    
    setIsSaving(true);
    setSaveSuccess(false);
    setSaveError(null);
    
    try {
      // Use cohort_definition if available, otherwise use the query as the name
      const cohortName = response.cohort_definition?.name || `GenAI Query: ${query.substring(0, 50)}${query.length > 50 ? '...' : ''}`;
      const cohortDescription = response.cohort_definition?.description || response.explanation;
      
      // Call the real API to save the cohort definition
      const saveResponse = await saveCohortDefinition(
        cohortName,
        cohortDescription,
        response.sql_generated
      );
      
      setIsSaving(false);
      setSaveSuccess(true);
      setSavedCohortId(saveResponse.cohort_definition_id);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setSaveSuccess(false);
        setSavedCohortId(null);
      }, 3000);
    } catch (err) {
      setIsSaving(false);
      setSaveError(err instanceof Error ? err.message : 'Failed to save cohort definition');
      console.error('Error saving cohort:', err);
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

  const escapeCSVField = (field: any): string => {
    if (field === null || field === undefined) return '';
    const stringField = String(field);
    // Escape quotes and wrap in quotes if contains comma, quote, or newline
    if (stringField.includes(',') || stringField.includes('"') || stringField.includes('\n')) {
      return `"${stringField.replace(/"/g, '""')}"`;
    }
    return stringField;
  };

  const handleExportResults = () => {
    if (!response) return;
    
    try {
      let csvContent = '';
      
      // Add query information header
      csvContent += 'GenAI Query Results\n';
      csvContent += `Query,${escapeCSVField(query)}\n`;
      csvContent += `Result Count,${response.result_count}\n`;
      csvContent += '\n';
      
      // Export query results if available
      if (response.query_results && response.query_results.length > 0) {
        // Get column headers
        const headers = Object.keys(response.query_results[0]);
        csvContent += headers.map(escapeCSVField).join(',') + '\n';
        
        // Add data rows
        response.query_results.forEach((row) => {
          const values = headers.map(header => escapeCSVField(row[header]));
          csvContent += values.join(',') + '\n';
        });
      } else {
        csvContent += 'No detailed results available\n';
        csvContent += `Total Count: ${response.result_count}\n`;
      }
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const queryPrefix = query.substring(0, 30).replace(/[^a-z0-9]/gi, '_');
      const filename = `genai_query_${queryPrefix}_${timestamp}.csv`;
      
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
    <div className="natural-language-search">
      <div className="nl-header">
        <h2>🤖 GenAI Cohort Query</h2>
        <p className="description">
          Ask questions about patient cohorts in natural language
        </p>
      </div>

      <form onSubmit={handleSubmit} className="nl-form">
        <div className="query-input-container">
          <textarea
            className="query-input"
            placeholder="e.g., Show me patients with diabetes who were prescribed insulin..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
          />
        </div>

        <button
          type="submit"
          className="btn btn-primary btn-large"
          disabled={loading || !query.trim()}
        >
          {loading ? '🔄 Processing...' : '🚀 Ask GenAI'}
        </button>
      </form>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="example-queries">
        <h4>Example Queries:</h4>
        <div className="example-list">
          {exampleQueries.map((example, index) => (
            <div
              key={index}
              className="example-item"
              onClick={() => handleExampleClick(example)}
            >
              💡 {example}
            </div>
          ))}
        </div>
      </div>

      {response && (
        <div className="nl-response">
          <div className="response-section">
            <h3>📝 Explanation</h3>
            <div className="explanation-box">
              {response.explanation.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>

          <div className="response-section">
            <h3>🔍 Generated SQL</h3>
            <div className="sql-box">
              <pre>{response.sql_generated}</pre>
            </div>
          </div>

          <div className="response-section">
            <div className="result-count">
              <span className="count-label">Results Found:</span>
              <span className="count-value">{response.result_count.toLocaleString()}</span>
            </div>
          </div>

          {response.query_results && response.query_results.length > 0 && (
            <div className="response-section">
              <h3>📊 Query Results</h3>
              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      {Object.keys(response.query_results[0]).map((key) => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {response.query_results.map((row, idx) => (
                      <tr key={idx}>
                        {Object.values(row).map((value, vidx) => (
                          <td key={vidx}>
                            {value !== null && value !== undefined ? String(value) : 'N/A'}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {response.cohort_definition && response.result_count > 0 && (
            <div className="response-section">
              <h3>📊 Cohort Definition</h3>
              <div className="cohort-def-box">
                <h4>{response.cohort_definition.name}</h4>
                
                {response.cohort_definition.inclusion_criteria.length > 0 && (
                  <div className="criteria-list">
                    <h5>Inclusion Criteria:</h5>
                    <ul>
                      {response.cohort_definition.inclusion_criteria.map((criteria, index) => (
                        <li key={index}>
                          <strong>{criteria.criteria_type}:</strong>{' '}
                          {criteria.concept_names?.join(', ') || 'N/A'}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {response.cohort_definition.exclusion_criteria.length > 0 && (
                  <div className="criteria-list">
                    <h5>Exclusion Criteria:</h5>
                    <ul>
                      {response.cohort_definition.exclusion_criteria.map((criteria, index) => (
                        <li key={index}>
                          <strong>{criteria.criteria_type}:</strong>{' '}
                          {criteria.concept_names?.join(', ') || 'N/A'}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {response.result_count > 0 && (
            <div className="response-section">
              <div className="export-section">
                <button 
                  className="btn btn-primary" 
                  onClick={handleExportResults}
                  disabled={exportSuccess}
                >
                  {exportSuccess ? '✅ Exported!' : '📥 Export Results'}
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
                  ✅ Query results have been exported successfully!
                </div>
              )}

              {saveError && (
                <div className="error-message">
                  ❌ Error: {saveError}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NaturalLanguageSearch;

