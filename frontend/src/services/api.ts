import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Concept {
  concept_id: number;
  concept_name: string;
  domain_id: string;
  vocabulary_id: string;
  concept_class_id: string;
  standard_concept?: string;
  concept_code: string;
}

export interface CriteriaDefinition {
  id: string;
  criteria_type: 'condition' | 'drug' | 'procedure' | 'visit' | 'observation' | 'age' | 'gender';
  operator?: string;
  concept_ids?: number[];
  concept_names?: string[];
  value?: any;
  value_min?: number;
  value_max?: number;
  start_date?: string;
  end_date?: string;
  min_occurrences?: number;
  is_exclusion?: boolean;
}

export interface CohortDefinition {
  id?: string;
  name: string;
  description?: string;
  inclusion_criteria: CriteriaDefinition[];
  exclusion_criteria: CriteriaDefinition[];
  created_at?: string;
  updated_at?: string;
  created_by?: string;
}

export interface CohortResult {
  cohort_definition: CohortDefinition;
  patient_count: number;
  execution_time_seconds: number;
  demographics?: any;
  sample_patient_ids?: number[];
}

export interface NaturalLanguageResponse {
  query: string;
  sql_generated: string;
  cohort_definition?: CohortDefinition;
  result_count: number;
  explanation: string;
  query_results?: Array<Record<string, any>>;
}

// API functions
export const searchConcepts = async (
  query: string,
  domain_id?: string,
  limit: number = 20
): Promise<Concept[]> => {
  const response = await api.post('/concepts/search', {
    query,
    domain_id,
    limit,
  });
  return response.data;
};

export const getConcept = async (conceptId: number): Promise<Concept> => {
  const response = await api.get(`/concepts/${conceptId}`);
  return response.data;
};

export const buildCohort = async (cohortDefinition: CohortDefinition): Promise<CohortResult> => {
  const response = await api.post('/cohorts/build', cohortDefinition);
  return response.data;
};

export const previewCohortCount = async (cohortDefinition: CohortDefinition): Promise<number> => {
  const response = await api.post('/cohorts/preview-count', cohortDefinition);
  return response.data.count;
};

export const naturalLanguageQuery = async (query: string): Promise<NaturalLanguageResponse> => {
  const response = await api.post('/genai/query', { query });
  return response.data;
};

export const getDatabaseSummary = async (): Promise<any> => {
  const response = await api.get('/stats/summary');
  return response.data;
};

export default api;

