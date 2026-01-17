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
  sql_query?: string;
}

export interface NaturalLanguageResponse {
  query: string;
  sql_generated: string;
  cohort_definition?: CohortDefinition;
  result_count: number;
  explanation: string;
  query_results?: Array<Record<string, any>>;
  conversation_id?: string;
  message_id?: string;
  conversation_history?: ConversationMessage[];
  suggested_questions?: string[];
}

export interface ConversationMessage {
  message_id: string;
  role: 'user' | 'assistant';
  content: string;
  sql_generated?: string;
  result_count?: number;
  query_results?: Array<Record<string, any>>;
  suggested_questions?: string[];
  timestamp: string;
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

export const saveCohortDefinition = async (
  cohortDefinitionName: string,
  cohortDefinitionDescription: string,
  cohortDefinitionSyntax: string
): Promise<{ cohort_definition_id: number; cohort_definition_name: string; cohort_definition_description: string; cohort_initiation_date: string }> => {
  const response = await api.post('/cohorts/save', {
    cohort_definition_name: cohortDefinitionName,
    cohort_definition_description: cohortDefinitionDescription,
    cohort_definition_syntax: cohortDefinitionSyntax,
  });
  return response.data;
};

export const naturalLanguageQuery = async (
  query: string,
  conversationId?: string
): Promise<NaturalLanguageResponse> => {
  const response = await api.post('/genai/query', { 
    query,
    conversation_id: conversationId 
  });
  return response.data;
};

export const getQueryStatus = async (
  conversationId: string,
  messageId: string
): Promise<{ status: string }> => {
  const response = await api.get(`/genai/status/${conversationId}/${messageId}`);
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

// Market Share Analytics Types
export interface DrugMarketShare {
  drug_concept_id: number;
  drug_name: string;
  total_prescriptions: number;
  total_patients: number;
  market_share_by_prescriptions: number;
  market_share_by_patients: number;
  rank: number;
}

export interface MarketShareResponse {
  market_definition: string;
  time_period: string;
  total_market_prescriptions: number;
  total_market_patients: number;
  drug_shares: DrugMarketShare[];
  top_3_concentration: number;
  top_5_concentration: number;
  herfindahl_index?: number;
  total_drugs_in_market: number;
  avg_prescriptions_per_drug: number;
}

export interface MarketShareTrend {
  time_period: string;
  prescriptions: number;
  patients: number;
  market_share: number;
  prescriptions_change_pct?: number;
  market_share_change_points?: number;
}

export interface TrendAnalysisResponse {
  drug_concept_id: number;
  drug_name: string;
  trends: MarketShareTrend[];
  overall_change_pct: number;
  overall_share_change: number;
  trend_direction: string;
  peak_period?: string;
  peak_market_share?: number;
}

export interface CompetitivePositioning {
  your_drug_concept_id: number;
  your_drug_name: string;
  your_prescriptions: number;
  your_patients: number;
  your_market_share: number;
  your_rank: number;
  competitors: DrugMarketShare[];
  share_gap_to_leader: number;
  share_of_top_3?: number;
}

export interface NewToBrandAnalysis {
  drug_concept_id: number;
  drug_name: string;
  time_period: string;
  new_patients: number;
  total_patients: number;
  nbx_rate: number;
  treatment_naive: number;
  switched_from_competitor: number;
  switch_sources: Array<{
    drug_concept_id: number;
    drug_name: string;
    patient_count: number;
  }>;
}

// Market Share Analytics API functions
export const getMarketShareAnalysis = async (params: {
  condition_concept_ids?: number[];
  drug_concept_ids?: number[];
  therapeutic_area?: string;
  start_date?: string;
  end_date?: string;
  min_prescriptions?: number;
  top_n?: number;
}): Promise<MarketShareResponse> => {
  const response = await api.post('/market-share/analysis', params);
  return response.data;
};

export const getTrendAnalysis = async (
  drugConceptId: number,
  startDate?: string,
  endDate?: string,
  granularity: string = 'month'
): Promise<TrendAnalysisResponse> => {
  const response = await api.get(`/market-share/trends/${drugConceptId}`, {
    params: {
      start_date: startDate,
      end_date: endDate,
      granularity,
    },
  });
  return response.data;
};

export const getCompetitivePositioning = async (
  yourDrugId: number,
  competitorIds: number[],
  startDate?: string,
  endDate?: string
): Promise<CompetitivePositioning> => {
  const response = await api.get(`/market-share/competitive/${yourDrugId}`, {
    params: {
      competitor_ids: competitorIds.join(','),
      start_date: startDate,
      end_date: endDate,
    },
  });
  return response.data;
};

export const getNewToBrandAnalysis = async (
  drugConceptId: number,
  startDate: string,
  endDate: string,
  lookbackDays: number = 365
): Promise<NewToBrandAnalysis> => {
  const response = await api.get(`/market-share/new-to-brand/${drugConceptId}`, {
    params: {
      start_date: startDate,
      end_date: endDate,
      lookback_days: lookbackDays,
    },
  });
  return response.data;
};

export default api;

