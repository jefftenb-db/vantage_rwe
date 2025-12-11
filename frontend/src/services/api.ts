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

// Prescriber Analytics Types
export interface PrescriberMetrics {
  provider_id: number;
  provider_name?: string;
  specialty?: string;
  total_patients: number;
  new_patients?: number;
  total_prescriptions: number;
  percentile_rank?: number;
  decile?: number;
  market_share?: number;
}

export interface DrugPrescriberAnalytics {
  drug_concept_id: number;
  drug_name: string;
  top_prescribers: PrescriberMetrics[];
  total_prescriptions: number;
  total_unique_prescribers: number;
  total_unique_patients: number;
  top_10_percent_share?: number;
  top_20_percent_share?: number;
  herfindahl_index?: number;
}

export interface TargetPrescriber {
  provider_id: number;
  provider_name?: string;
  specialty?: string;
  reason_score: number;
  relevant_patients: number;
  competitor_prescriptions: number;
  target_drug_prescriptions: number;
  estimated_opportunity?: number;
  state?: string;
  zip_code?: string;
}

export interface PrescriberTargetingResponse {
  targets: TargetPrescriber[];
  total_opportunity_prescriptions: number;
  total_target_prescribers: number;
  high_priority_count: number;
  medium_priority_count: number;
  low_priority_count: number;
}

export interface TreatmentPathway {
  provider_id: number;
  provider_name?: string;
  first_line_drugs: Array<{
    drug_concept_id: number;
    drug_name: string;
    patient_count: number;
    percentage: number;
  }>;
  switch_patterns: Array<{
    from_drug_id: number;
    from_drug: string;
    to_drug_id: number;
    to_drug: string;
    switch_count: number;
  }>;
  pathways: any[];
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

// Prescriber Analytics API functions
export const searchPrescribers = async (params: {
  specialty?: string;
  min_patients?: number;
  drug_concept_id?: number;
  limit?: number;
}): Promise<PrescriberMetrics[]> => {
  const response = await api.post('/prescribers/search', params);
  return response.data;
};

export const getDrugPrescriberAnalytics = async (
  drugConceptId: number,
  limit: number = 50
): Promise<DrugPrescriberAnalytics> => {
  const response = await api.get(`/prescribers/drug/${drugConceptId}/analytics`, {
    params: { limit },
  });
  return response.data;
};

export const identifyTargetPrescribers = async (params: {
  target_drug_concept_ids?: number[];
  competitor_drug_concept_ids?: number[];
  condition_concept_ids?: number[];
  min_relevant_patients?: number;
  specialty?: string;
  state?: string;
  zip_code?: string;
  limit?: number;
}): Promise<PrescriberTargetingResponse> => {
  const response = await api.post('/prescribers/targeting', params);
  return response.data;
};

export const getPrescriberTreatmentPathways = async (
  providerId: number,
  conditionConceptId?: number
): Promise<TreatmentPathway> => {
  const response = await api.get(`/prescribers/${providerId}/treatment-pathways`, {
    params: conditionConceptId ? { condition_concept_id: conditionConceptId } : {},
  });
  return response.data;
};

export const comparePrescribers = async (
  providerIds: number[],
  drugConceptId?: number
): Promise<PrescriberMetrics[]> => {
  const response = await api.post('/prescribers/compare', providerIds, {
    params: drugConceptId ? { drug_concept_id: drugConceptId } : {},
  });
  return response.data;
};

export default api;

