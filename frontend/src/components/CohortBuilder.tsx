import React, { useState } from 'react';
import { CohortDefinition, CriteriaDefinition, CohortResult, buildCohort } from '../services/api';
import CriteriaBuilder from './CriteriaBuilder';
import CohortResults from './CohortResults';
import './CohortBuilder.css';

const CohortBuilder: React.FC = () => {
  const [cohortName, setCohortName] = useState('');
  const [cohortDescription, setCohortDescription] = useState('');
  const [inclusionCriteria, setInclusionCriteria] = useState<CriteriaDefinition[]>([]);
  const [exclusionCriteria, setExclusionCriteria] = useState<CriteriaDefinition[]>([]);
  const [result, setResult] = useState<CohortResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addInclusionCriteria = () => {
    const newCriteria: CriteriaDefinition = {
      id: `inc_${Date.now()}`,
      criteria_type: 'condition',
      min_occurrences: 1,
      is_exclusion: false,
    };
    setInclusionCriteria([...inclusionCriteria, newCriteria]);
  };

  const addExclusionCriteria = () => {
    const newCriteria: CriteriaDefinition = {
      id: `exc_${Date.now()}`,
      criteria_type: 'condition',
      min_occurrences: 1,
      is_exclusion: true,
    };
    setExclusionCriteria([...exclusionCriteria, newCriteria]);
  };

  const updateInclusionCriteria = (index: number, criteria: CriteriaDefinition) => {
    const updated = [...inclusionCriteria];
    updated[index] = criteria;
    setInclusionCriteria(updated);
  };

  const updateExclusionCriteria = (index: number, criteria: CriteriaDefinition) => {
    const updated = [...exclusionCriteria];
    updated[index] = criteria;
    setExclusionCriteria(updated);
  };

  const removeInclusionCriteria = (index: number) => {
    setInclusionCriteria(inclusionCriteria.filter((_, i) => i !== index));
  };

  const removeExclusionCriteria = (index: number) => {
    setExclusionCriteria(exclusionCriteria.filter((_, i) => i !== index));
  };

  const handleBuildCohort = async () => {
    if (!cohortName.trim()) {
      setError('Please enter a cohort name');
      return;
    }

    if (inclusionCriteria.length === 0) {
      setError('Please add at least one inclusion criteria');
      return;
    }

    const cohortDefinition: CohortDefinition = {
      name: cohortName,
      description: cohortDescription,
      inclusion_criteria: inclusionCriteria,
      exclusion_criteria: exclusionCriteria,
    };

    try {
      setLoading(true);
      setError(null);
      const cohortResult = await buildCohort(cohortDefinition);
      setResult(cohortResult);
    } catch (err: any) {
      setError(err.message || 'Failed to build cohort');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setCohortName('');
    setCohortDescription('');
    setInclusionCriteria([]);
    setExclusionCriteria([]);
    setResult(null);
    setError(null);
  };

  return (
    <div className="cohort-builder">
      <div className="builder-header">
        <h2>Build Patient Cohort</h2>
        <p className="description">
          Define your patient population by adding inclusion and exclusion criteria
        </p>
      </div>

      <div className="form-section">
        <div className="form-group">
          <label className="form-label">Cohort Name *</label>
          <input
            type="text"
            className="form-input"
            placeholder="e.g., Diabetes Type 2 Patients on Metformin"
            value={cohortName}
            onChange={(e) => setCohortName(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea
            className="form-textarea"
            placeholder="Describe your cohort..."
            value={cohortDescription}
            onChange={(e) => setCohortDescription(e.target.value)}
          />
        </div>
      </div>

      <div className="criteria-section">
        <div className="criteria-header">
          <h3>✅ Inclusion Criteria</h3>
          <button className="btn btn-secondary" onClick={addInclusionCriteria}>
            + Add Criteria
          </button>
        </div>
        
        {inclusionCriteria.length === 0 ? (
          <div className="empty-state">
            No inclusion criteria yet. Click "Add Criteria" to start building your cohort.
          </div>
        ) : (
          <div className="criteria-list">
            {inclusionCriteria.map((criteria, index) => (
              <CriteriaBuilder
                key={criteria.id}
                criteria={criteria}
                onUpdate={(updated) => updateInclusionCriteria(index, updated)}
                onRemove={() => removeInclusionCriteria(index)}
              />
            ))}
          </div>
        )}
      </div>

      <div className="criteria-section">
        <div className="criteria-header">
          <h3>❌ Exclusion Criteria</h3>
          <button className="btn btn-secondary" onClick={addExclusionCriteria}>
            + Add Criteria
          </button>
        </div>
        
        {exclusionCriteria.length === 0 ? (
          <div className="empty-state">
            No exclusion criteria. Add criteria to exclude specific patient populations.
          </div>
        ) : (
          <div className="criteria-list">
            {exclusionCriteria.map((criteria, index) => (
              <CriteriaBuilder
                key={criteria.id}
                criteria={criteria}
                onUpdate={(updated) => updateExclusionCriteria(index, updated)}
                onRemove={() => removeExclusionCriteria(index)}
              />
            ))}
          </div>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="action-buttons">
        <button
          className="btn btn-primary"
          onClick={handleBuildCohort}
          disabled={loading || inclusionCriteria.length === 0}
        >
          {loading ? '⏳ Building Cohort...' : '🚀 Build Cohort'}
        </button>
        <button className="btn btn-secondary" onClick={handleReset}>
          🔄 Reset
        </button>
      </div>

      {result && <CohortResults result={result} />}
    </div>
  );
};

export default CohortBuilder;

