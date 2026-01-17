import React, { useEffect, useState } from 'react';
import { getDatabaseSummary } from '../services/api';
import './DatabaseStats.css';

interface Stats {
  total_patients: number;
  unique_conditions: number;
  unique_drugs: number;
  unique_procedures: number;
  total_visits: number;
}

const DatabaseStats: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getDatabaseSummary();
      setStats(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load database statistics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="stats-container">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stats-container">
        <div className="alert alert-error">{error}</div>
      </div>
    );
  }

  if (!stats) return null;

  const statItems = [
    { label: 'Patients', value: stats.total_patients?.toLocaleString() || '0', icon: '👥' },
    { label: 'Conditions', value: stats.unique_conditions?.toLocaleString() || '0', icon: '🏥' },
    { label: 'Drugs', value: stats.unique_drugs?.toLocaleString() || '0', icon: '💊' },
    { label: 'Procedures', value: stats.unique_procedures?.toLocaleString() || '0', icon: '⚕️' },
    { label: 'Visits', value: stats.total_visits?.toLocaleString() || '0', icon: '📋' },
  ];

  return (
    <div className="stats-container">
      <div className="stats-grid">
        {statItems.map((item, index) => (
          <div key={index} className="stat-card">
            <div className="stat-icon">{item.icon}</div>
            <div className="stat-content">
              <div className="stat-value">{item.value}</div>
              <div className="stat-label">{item.label}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DatabaseStats;

