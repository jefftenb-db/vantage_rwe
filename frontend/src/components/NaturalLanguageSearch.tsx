import React, { useState, useEffect, useRef } from 'react';
import { naturalLanguageQuery, getQueryStatus, NaturalLanguageResponse, ConversationMessage, saveCohortDefinition } from '../services/api';
import CohortResults from './CohortResults';
import './NaturalLanguageSearch.css';

const NaturalLanguageSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversationHistory, setConversationHistory] = useState<ConversationMessage[]>([]);
  const [currentResponse, setCurrentResponse] = useState<NaturalLanguageResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [savedCohortId, setSavedCohortId] = useState<number | null>(null);
  const [showSqlMap, setShowSqlMap] = useState<{ [key: string]: boolean }>({});
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const statusPollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (conversationHistory.length > 0) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversationHistory]);

  // Cleanup status polling on unmount
  useEffect(() => {
    return () => {
      if (statusPollIntervalRef.current) {
        clearInterval(statusPollIntervalRef.current);
      }
    };
  }, []);

  const pollStatus = async (convId: string, msgId: string) => {
    try {
      const statusData = await getQueryStatus(convId, msgId);
      if (statusData.status && statusData.status !== 'UNKNOWN') {
        setProcessingStatus(getStatusMessage(statusData.status));
      }
    } catch (err) {
      // Silently fail - status polling is best effort
      console.error('Status poll error:', err);
    }
  };

  const getStatusMessage = (status: string): string => {
    const statusMessages: { [key: string]: string } = {
      'SUBMITTED': '📤 Submitted to Genie...',
      'EXECUTING_QUERY': '⚙️ Generating SQL query...',
      'QUERYING_HISTORY': '🔍 Analyzing conversation context...',
      'COMPLETED': '✅ Completed!',
      'FAILED': '❌ Processing failed',
      'CANCELLED': '🚫 Cancelled',
      'QUERY_RESULT_EXPIRED': '⏰ Results expired',
      'EXECUTING': '⚙️ Executing query...',
      'FETCHING_METADATA': '📊 Fetching metadata...',
      'COMPILING': '🔨 Compiling response...',
    };
    return statusMessages[status] || `🔄 ${status}...`;
  };

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
      setProcessingStatus('🤖 Genie is analyzing your question and generating a response...');
      
      const result = await naturalLanguageQuery(query, conversationId || undefined);
      
      // Update conversation state
      if (result.conversation_id) {
        setConversationId(result.conversation_id);
      }
      
      // Update conversation history
      if (result.conversation_history) {
        setConversationHistory(result.conversation_history);
      }
      
      setCurrentResponse(result);
      setQuery(''); // Clear input for next message
      setProcessingStatus('');
    } catch (err: any) {
      setError(err.message || 'Failed to process query');
      setProcessingStatus('');
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = () => {
    // Reset all conversation state
    setConversationId(null);
    setConversationHistory([]);
    setCurrentResponse(null);
    setQuery('');
    setError(null);
    setShowSqlMap({});
    setProcessingStatus('');
    if (statusPollIntervalRef.current) {
      clearInterval(statusPollIntervalRef.current);
      statusPollIntervalRef.current = null;
    }
  };

  const toggleSql = (messageId: string) => {
    setShowSqlMap(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }));
  };

  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  const handleSuggestedQuestionClick = async (question: string) => {
    // Directly submit the suggested question
    try {
      setLoading(true);
      setError(null);
      setProcessingStatus('🤖 Genie is analyzing your question and generating a response...');
      
      const result = await naturalLanguageQuery(question, conversationId || undefined);
      
      // Update conversation state
      if (result.conversation_id) {
        setConversationId(result.conversation_id);
      }
      
      // Update conversation history
      if (result.conversation_history) {
        setConversationHistory(result.conversation_history);
      }
      
      setCurrentResponse(result);
      setProcessingStatus('');
    } catch (err: any) {
      setError(err.message || 'Failed to process query');
      setProcessingStatus('');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCohort = async () => {
    if (!currentResponse) return;
    
    setIsSaving(true);
    setSaveSuccess(false);
    setSaveError(null);
    
    try {
      // Use cohort_definition if available, otherwise use the query as the name
      const cohortName = currentResponse.cohort_definition?.name || `GenAI Query: ${currentResponse.query.substring(0, 50)}${currentResponse.query.length > 50 ? '...' : ''}`;
      const cohortDescription = currentResponse.cohort_definition?.description || currentResponse.explanation;
      
      // Call the real API to save the cohort definition
      const saveResponse = await saveCohortDefinition(
        cohortName,
        cohortDescription,
        currentResponse.sql_generated
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
    if (!currentResponse) return;
    
    try {
      let csvContent = '';
      
      // Add query information header
      csvContent += 'GenAI Query Results\n';
      csvContent += `Query,${escapeCSVField(currentResponse.query)}\n`;
      csvContent += `Result Count,${currentResponse.result_count}\n`;
      csvContent += '\n';
      
      // Export query results if available
      if (currentResponse.query_results && currentResponse.query_results.length > 0) {
        // Get column headers
        const headers = Object.keys(currentResponse.query_results[0]);
        csvContent += headers.map(escapeCSVField).join(',') + '\n';
        
        // Add data rows
        currentResponse.query_results.forEach((row) => {
          const values = headers.map(header => escapeCSVField(row[header]));
          csvContent += values.join(',') + '\n';
        });
      } else {
        csvContent += 'No detailed results available\n';
        csvContent += `Total Count: ${currentResponse.result_count}\n`;
      }
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
      const queryPrefix = currentResponse.query.substring(0, 30).replace(/[^a-z0-9]/gi, '_');
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
        {conversationId && (
          <div className="conversation-status">
            <span className="status-badge">💬 Conversation Active</span>
            <button 
              className="btn btn-small btn-secondary" 
              onClick={handleNewConversation}
            >
              🔄 New Conversation
            </button>
          </div>
        )}
      </div>

      {/* Conversation History */}
      {conversationHistory.length > 0 && (
        <div className="conversation-history">
          <h3 className="history-title">📜 Conversation History</h3>
          <div className="messages">
            {conversationHistory.map((message, index) => (
              <div key={message.message_id} className={`message message-${message.role}`}>
                <div className="message-header">
                  <span className="message-role">
                    {message.role === 'user' ? '👤 You' : '🤖 GenAI'}
                  </span>
                  <span className="message-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="message-content">
                  {message.content}
                </div>
                {message.role === 'assistant' && (
                  <div className="message-meta">
                    {message.result_count !== undefined && (
                      <span className="result-badge">
                        📊 {message.result_count.toLocaleString()} results
                      </span>
                    )}
                    {message.sql_generated && (
                      <div className="sql-toggle-section">
                        <button 
                          className="btn-sql-toggle"
                          onClick={() => toggleSql(message.message_id)}
                        >
                          {showSqlMap[message.message_id] ? '🔽 Hide SQL' : '▶️ Show SQL'}
                        </button>
                        {showSqlMap[message.message_id] && (
                          <div className="sql-box">
                            <pre>{message.sql_generated}</pre>
                          </div>
                        )}
                      </div>
                    )}
                    {message.suggested_questions && message.suggested_questions.length > 0 && (
                      <div className="suggested-questions">
                        <p className="suggested-questions-label">💡 Suggested follow-ups:</p>
                        <div className="suggested-questions-list">
                          {message.suggested_questions.map((question, idx) => (
                            <button
                              key={idx}
                              className="btn-suggested-question"
                              onClick={() => handleSuggestedQuestionClick(question)}
                              disabled={loading}
                            >
                              {question}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="nl-form">
        <div className="query-input-container">
          <textarea
            className="query-input"
            placeholder={
              conversationId 
                ? "Ask a follow-up question..." 
                : "e.g., Show me patients with diabetes who were prescribed insulin..."
            }
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
          {loading ? '🔄 Processing...' : conversationId ? '💬 Continue Conversation' : '🚀 Ask GenAI'}
        </button>
      </form>

      {loading && (
        <div className="status-indicator">
          <div className="status-spinner"></div>
          <span>{processingStatus || 'Processing your query with Genie...'}</span>
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {!conversationId && (
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
      )}

      {currentResponse && (
        <div className="nl-response">
          {currentResponse.query_results && currentResponse.query_results.length > 0 && (
            <div className="response-section">
              <h3>📊 Query Results</h3>
              <div className="results-table-container">
                <table className="results-table">
                  <thead>
                    <tr>
                      {Object.keys(currentResponse.query_results[0]).map((key) => (
                        <th key={key}>{key}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentResponse.query_results.map((row, idx) => (
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

          {currentResponse.cohort_definition && currentResponse.result_count > 0 && (
            <div className="response-section">
              <h3>📊 Cohort Definition</h3>
              <div className="cohort-def-box">
                <h4>{currentResponse.cohort_definition.name}</h4>
                
                {currentResponse.cohort_definition.inclusion_criteria.length > 0 && (
                  <div className="criteria-list">
                    <h5>Inclusion Criteria:</h5>
                    <ul>
                      {currentResponse.cohort_definition.inclusion_criteria.map((criteria, index) => (
                        <li key={index}>
                          <strong>{criteria.criteria_type}:</strong>{' '}
                          {criteria.concept_names?.join(', ') || 'N/A'}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {currentResponse.cohort_definition.exclusion_criteria.length > 0 && (
                  <div className="criteria-list">
                    <h5>Exclusion Criteria:</h5>
                    <ul>
                      {currentResponse.cohort_definition.exclusion_criteria.map((criteria, index) => (
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

          {currentResponse.result_count > 0 && (
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

