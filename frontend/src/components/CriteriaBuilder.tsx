import React, { useState, useEffect } from 'react';
import { CriteriaDefinition, Concept, searchConcepts } from '../services/api';
import './CriteriaBuilder.css';

interface Props {
  criteria: CriteriaDefinition;
  onUpdate: (criteria: CriteriaDefinition) => void;
  onRemove: () => void;
}

const CriteriaBuilder: React.FC<Props> = ({ criteria, onUpdate, onRemove }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<Concept[]>([]);
  const [searching, setSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);

  useEffect(() => {
    const delaySearch = setTimeout(() => {
      if (searchTerm.length >= 3) {
        performSearch();
      } else {
        setSearchResults([]);
      }
    }, 500);

    return () => clearTimeout(delaySearch);
  }, [searchTerm, criteria.criteria_type]);

  const performSearch = async () => {
    setSearching(true);
    try {
      const domainMap: { [key: string]: string } = {
        condition: 'Condition',
        drug: 'Drug',
        procedure: 'Procedure',
        visit: 'Visit',
        observation: 'Observation',
      };
      
      const domain = domainMap[criteria.criteria_type];
      const results = await searchConcepts(searchTerm, domain);
      setSearchResults(results);
      setShowResults(true);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleAddConcept = (concept: Concept) => {
    const conceptIds = [...(criteria.concept_ids || []), concept.concept_id];
    const conceptNames = [...(criteria.concept_names || []), concept.concept_name];
    
    onUpdate({
      ...criteria,
      concept_ids: conceptIds,
      concept_names: conceptNames,
    });
    
    setSearchTerm('');
    setSearchResults([]);
    setShowResults(false);
  };

  const handleRemoveConcept = (index: number) => {
    const conceptIds = [...(criteria.concept_ids || [])];
    const conceptNames = [...(criteria.concept_names || [])];
    
    conceptIds.splice(index, 1);
    conceptNames.splice(index, 1);
    
    onUpdate({
      ...criteria,
      concept_ids: conceptIds,
      concept_names: conceptNames,
    });
  };

  const handleTypeChange = (type: string) => {
    onUpdate({
      ...criteria,
      criteria_type: type as any,
      concept_ids: [],
      concept_names: [],
    });
  };

  const criteriaTypeLabels: { [key: string]: string } = {
    condition: '🏥 Condition',
    drug: '💊 Drug',
    procedure: '⚕️ Procedure',
    visit: '📋 Visit',
    observation: '🔬 Observation',
  };

  return (
    <div className="criteria-builder">
      <div className="criteria-controls">
        <select
          className="form-select criteria-type-select"
          value={criteria.criteria_type}
          onChange={(e) => handleTypeChange(e.target.value)}
        >
          {Object.entries(criteriaTypeLabels).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
        
        <button className="btn-icon btn-danger" onClick={onRemove} title="Remove criteria">
          🗑️
        </button>
      </div>

      <div className="concept-search">
        <input
          type="text"
          className="form-input"
          placeholder={`Search for ${criteria.criteria_type}s...`}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onFocus={() => setShowResults(true)}
        />
        
        {searching && <div className="search-loading">Searching...</div>}
        
        {showResults && searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((concept) => (
              <div
                key={concept.concept_id}
                className="search-result-item"
                onClick={() => handleAddConcept(concept)}
              >
                <div className="concept-name">{concept.concept_name}</div>
                <div className="concept-details">
                  {concept.vocabulary_id} · {concept.concept_code}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="selected-concepts">
        {criteria.concept_names && criteria.concept_names.length > 0 ? (
          criteria.concept_names.map((name, index) => (
            <div key={index} className="concept-tag">
              <span>{name}</span>
              <button
                className="remove-concept"
                onClick={() => handleRemoveConcept(index)}
              >
                ×
              </button>
            </div>
          ))
        ) : (
          <div className="no-concepts">No concepts selected. Search to add.</div>
        )}
      </div>

      <div className="criteria-options">
        <div className="option-group">
          <label className="option-label">Min Occurrences:</label>
          <input
            type="number"
            className="form-input number-input"
            min="1"
            value={criteria.min_occurrences || 1}
            onChange={(e) => onUpdate({ ...criteria, min_occurrences: parseInt(e.target.value) || 1 })}
          />
        </div>
        
        <div className="option-group">
          <label className="option-label">Start Date:</label>
          <input
            type="date"
            className="form-input date-input"
            value={criteria.start_date || ''}
            onChange={(e) => onUpdate({ ...criteria, start_date: e.target.value as any })}
          />
        </div>
        
        <div className="option-group">
          <label className="option-label">End Date:</label>
          <input
            type="date"
            className="form-input date-input"
            value={criteria.end_date || ''}
            onChange={(e) => onUpdate({ ...criteria, end_date: e.target.value as any })}
          />
        </div>
      </div>
    </div>
  );
};

export default CriteriaBuilder;

