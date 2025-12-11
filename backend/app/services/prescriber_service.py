from typing import List, Optional, Dict, Any
import logging
from app.models.prescriber import (
    PrescriberProfile, PrescriberMetrics, DrugPrescriberAnalytics,
    PrescriberSearchRequest, TargetPrescriber, PrescriberTargetingRequest,
    PrescriberTargetingResponse, TreatmentPathwayByPrescriber
)
from app.db.databricks import db
from app.config import settings

logger = logging.getLogger(__name__)


class PrescriberService:
    """
    Service for prescriber/HCP analytics.
    
    Provides insights into prescribing patterns, prescriber profiles,
    and targeting opportunities for pharmaceutical commercial teams.
    """
    
    def __init__(self):
        self.schema = settings.omop_full_schema
    
    def get_prescriber_profile(self, provider_id: int) -> Optional[PrescriberProfile]:
        """Get detailed profile for a specific prescriber."""
        
        sql = f"""
        SELECT 
            p.provider_id,
            p.provider_name,
            p.specialty_concept_id,
            p.specialty_source_value,
            p.npi,
            p.dea,
            COUNT(DISTINCT de.person_id) as total_patients,
            COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
            COUNT(DISTINCT vo.visit_occurrence_id) as total_visits
        FROM {self.schema}.provider p
        LEFT JOIN {self.schema}.drug_exposure de ON p.provider_id = de.provider_id
        LEFT JOIN {self.schema}.visit_occurrence vo ON p.provider_id = vo.provider_id
        WHERE p.provider_id = {provider_id}
        GROUP BY 
            p.provider_id, p.provider_name, p.specialty_concept_id,
            p.specialty_source_value, p.npi, p.dea
        """
        
        try:
            results = db.execute_query(sql)
            if results:
                return PrescriberProfile(**results[0])
            return None
        except Exception as e:
            logger.error(f"Error getting prescriber profile: {e}")
            raise
    
    def search_prescribers(self, request: PrescriberSearchRequest) -> List[PrescriberMetrics]:
        """Search for prescribers with filtering."""
        
        where_clauses = []
        
        if request.specialty:
            where_clauses.append(f"LOWER(p.specialty_source_value) LIKE '%{request.specialty.lower()}%'")
        
        if request.drug_concept_id:
            where_clauses.append(f"de.drug_concept_id = {request.drug_concept_id}")
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        sql = f"""
        SELECT 
            p.provider_id,
            p.provider_name,
            p.specialty_source_value as specialty,
            COUNT(DISTINCT de.person_id) as total_patients,
            COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
            PERCENT_RANK() OVER (ORDER BY COUNT(DISTINCT de.drug_exposure_id)) * 100 as percentile_rank,
            NTILE(10) OVER (ORDER BY COUNT(DISTINCT de.drug_exposure_id)) as decile
        FROM {self.schema}.provider p
        INNER JOIN {self.schema}.drug_exposure de ON p.provider_id = de.provider_id
        WHERE {where_sql}
        GROUP BY p.provider_id, p.provider_name, p.specialty_source_value
        {"HAVING COUNT(DISTINCT de.person_id) >= " + str(request.min_patients) if request.min_patients else ""}
        ORDER BY total_prescriptions DESC
        LIMIT {request.limit}
        """
        
        try:
            results = db.execute_query(sql)
            return [PrescriberMetrics(**row) for row in results]
        except Exception as e:
            logger.error(f"Error searching prescribers: {e}")
            raise
    
    def get_drug_prescriber_analytics(
        self, 
        drug_concept_id: int,
        limit: int = 50
    ) -> DrugPrescriberAnalytics:
        """
        Get comprehensive prescriber analytics for a specific drug.
        
        Includes top prescribers, concentration metrics, and market share.
        """
        
        # Get drug name
        drug_name_sql = f"""
        SELECT concept_name 
        FROM {self.schema}.concept 
        WHERE concept_id = {drug_concept_id}
        """
        drug_name_result = db.execute_query(drug_name_sql)
        drug_name = drug_name_result[0]['concept_name'] if drug_name_result else f"Drug {drug_concept_id}"
        
        # Get top prescribers
        top_prescribers_sql = f"""
        WITH prescriber_stats AS (
            SELECT 
                p.provider_id,
                p.provider_name,
                p.specialty_source_value as specialty,
                COUNT(DISTINCT de.person_id) as total_patients,
                COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
                PERCENT_RANK() OVER (ORDER BY COUNT(DISTINCT de.drug_exposure_id)) * 100 as percentile_rank,
                NTILE(10) OVER (ORDER BY COUNT(DISTINCT de.drug_exposure_id)) as decile
            FROM {self.schema}.provider p
            INNER JOIN {self.schema}.drug_exposure de ON p.provider_id = de.provider_id
            WHERE de.drug_concept_id = {drug_concept_id}
            GROUP BY p.provider_id, p.provider_name, p.specialty_source_value
        ),
        total_stats AS (
            SELECT 
                COUNT(DISTINCT drug_exposure_id) as total_rx,
                COUNT(DISTINCT provider_id) as total_providers,
                COUNT(DISTINCT person_id) as total_patients
            FROM {self.schema}.drug_exposure
            WHERE drug_concept_id = {drug_concept_id}
        )
        SELECT 
            ps.*,
            ROUND(ps.total_prescriptions * 100.0 / ts.total_rx, 2) as market_share
        FROM prescriber_stats ps
        CROSS JOIN total_stats ts
        ORDER BY ps.total_prescriptions DESC
        LIMIT {limit}
        """
        
        # Get summary statistics
        summary_sql = f"""
        WITH ranked_prescribers AS (
            SELECT 
                provider_id,
                COUNT(DISTINCT drug_exposure_id) as rx_count,
                NTILE(10) OVER (ORDER BY COUNT(DISTINCT drug_exposure_id)) as decile
            FROM {self.schema}.drug_exposure
            WHERE drug_concept_id = {drug_concept_id}
            GROUP BY provider_id
        )
        SELECT 
            COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
            COUNT(DISTINCT de.provider_id) as total_unique_prescribers,
            COUNT(DISTINCT de.person_id) as total_unique_patients,
            SUM(CASE WHEN rp.decile = 10 THEN rp.rx_count ELSE 0 END) * 100.0 / 
                NULLIF(SUM(rp.rx_count), 0) as top_10_percent_share,
            SUM(CASE WHEN rp.decile >= 9 THEN rp.rx_count ELSE 0 END) * 100.0 / 
                NULLIF(SUM(rp.rx_count), 0) as top_20_percent_share
        FROM {self.schema}.drug_exposure de
        LEFT JOIN ranked_prescribers rp ON de.provider_id = rp.provider_id
        WHERE de.drug_concept_id = {drug_concept_id}
        """
        
        try:
            top_prescribers_results = db.execute_query(top_prescribers_sql)
            summary_results = db.execute_query(summary_sql)
            
            top_prescribers = [PrescriberMetrics(**row) for row in top_prescribers_results]
            
            summary = summary_results[0] if summary_results else {}
            
            return DrugPrescriberAnalytics(
                drug_concept_id=drug_concept_id,
                drug_name=drug_name,
                top_prescribers=top_prescribers,
                total_prescriptions=summary.get('total_prescriptions', 0),
                total_unique_prescribers=summary.get('total_unique_prescribers', 0),
                total_unique_patients=summary.get('total_unique_patients', 0),
                top_10_percent_share=summary.get('top_10_percent_share'),
                top_20_percent_share=summary.get('top_20_percent_share')
            )
        except Exception as e:
            logger.error(f"Error getting drug prescriber analytics: {e}")
            raise
    
    def identify_target_prescribers(
        self, 
        request: PrescriberTargetingRequest
    ) -> PrescriberTargetingResponse:
        """
        Identify target prescribers for outreach.
        
        Finds prescribers who:
        - Treat patients with target conditions
        - Prescribe competitor drugs
        - Have limited or no adoption of target drug
        """
        
        # Build WHERE clauses
        where_clauses = ["1=1"]
        
        if request.specialty:
            where_clauses.append(f"LOWER(p.specialty_source_value) LIKE '%{request.specialty.lower()}%'")
        
        if request.state:
            where_clauses.append(f"UPPER(loc.state) = UPPER('{request.state}')")
        
        if request.zip_code:
            where_clauses.append(f"loc.zip = '{request.zip_code}'")
        
        where_sql = " AND ".join(where_clauses)
        
        # Build condition filter
        condition_filter = ""
        if request.condition_concept_ids:
            condition_ids_str = ",".join(str(id) for id in request.condition_concept_ids)
            condition_filter = f"AND co.condition_concept_id IN ({condition_ids_str})"
        
        # Build competitor filter
        competitor_filter = ""
        if request.competitor_drug_concept_ids:
            competitor_ids_str = ",".join(str(id) for id in request.competitor_drug_concept_ids)
            competitor_filter = f"WHERE drug_concept_id IN ({competitor_ids_str})"
        
        # Build target drug filter
        target_drug_filter = ""
        if request.target_drug_concept_ids:
            target_ids_str = ",".join(str(id) for id in request.target_drug_concept_ids)
            target_drug_filter = f"WHERE drug_concept_id IN ({target_ids_str})"
        
        sql = f"""
        WITH relevant_patients AS (
            -- Patients with target conditions
            SELECT DISTINCT 
                co.person_id,
                co.provider_id
            FROM {self.schema}.condition_occurrence co
            WHERE 1=1
            {condition_filter}
        ),
        competitor_rx AS (
            -- Competitor prescriptions by provider
            SELECT 
                de.provider_id,
                COUNT(DISTINCT de.drug_exposure_id) as competitor_prescriptions,
                COUNT(DISTINCT de.person_id) as competitor_patients
            FROM {self.schema}.drug_exposure de
            {competitor_filter}
            GROUP BY de.provider_id
        ),
        target_rx AS (
            -- Target drug prescriptions by provider
            SELECT 
                de.provider_id,
                COUNT(DISTINCT de.drug_exposure_id) as target_prescriptions
            FROM {self.schema}.drug_exposure de
            {target_drug_filter}
            GROUP BY de.provider_id
        ),
        provider_metrics AS (
            SELECT 
                p.provider_id,
                p.provider_name,
                p.specialty_source_value as specialty,
                COUNT(DISTINCT rp.person_id) as relevant_patients,
                COALESCE(cr.competitor_prescriptions, 0) as competitor_prescriptions,
                COALESCE(tr.target_prescriptions, 0) as target_drug_prescriptions,
                loc.state,
                loc.zip as zip_code
            FROM {self.schema}.provider p
            INNER JOIN relevant_patients rp ON p.provider_id = rp.provider_id
            LEFT JOIN competitor_rx cr ON p.provider_id = cr.provider_id
            LEFT JOIN target_rx tr ON p.provider_id = tr.provider_id
            LEFT JOIN {self.schema}.care_site cs ON p.care_site_id = cs.care_site_id
            LEFT JOIN {self.schema}.location loc ON cs.location_id = loc.location_id
            WHERE {where_sql}
            GROUP BY 
                p.provider_id, p.provider_name, p.specialty_source_value,
                cr.competitor_prescriptions, tr.target_prescriptions,
                loc.state, loc.zip
            HAVING COUNT(DISTINCT rp.person_id) >= {request.min_relevant_patients}
        )
        SELECT 
            provider_id,
            provider_name,
            specialty,
            relevant_patients,
            competitor_prescriptions,
            target_drug_prescriptions,
            state,
            zip_code,
            -- Scoring: Higher score = better target
            -- High relevant patients + high competitor Rx + low target Rx = best target
            ROUND(
                (relevant_patients * 0.4 + 
                 competitor_prescriptions * 0.4 + 
                 (100 - COALESCE(target_drug_prescriptions, 0)) * 0.2) * 
                (CASE WHEN target_drug_prescriptions = 0 THEN 1.2 ELSE 1.0 END), -- Boost for non-users
                2
            ) as reason_score,
            -- Estimated opportunity: relevant patients - current target Rx
            GREATEST(0, relevant_patients - COALESCE(target_drug_prescriptions, 0)) as estimated_opportunity
        FROM provider_metrics
        WHERE competitor_prescriptions > 0  -- Must be prescribing competitors
        ORDER BY reason_score DESC
        LIMIT {request.limit}
        """
        
        try:
            results = db.execute_query(sql)
            
            targets = [TargetPrescriber(**row) for row in results]
            
            # Calculate summary statistics
            total_opportunity = sum(t.estimated_opportunity or 0 for t in targets)
            high_priority = sum(1 for t in targets if t.reason_score > 80)
            medium_priority = sum(1 for t in targets if 50 <= t.reason_score <= 80)
            low_priority = sum(1 for t in targets if t.reason_score < 50)
            
            return PrescriberTargetingResponse(
                targets=targets,
                total_opportunity_prescriptions=total_opportunity,
                total_target_prescribers=len(targets),
                high_priority_count=high_priority,
                medium_priority_count=medium_priority,
                low_priority_count=low_priority
            )
        except Exception as e:
            logger.error(f"Error identifying target prescribers: {e}")
            raise
    
    def get_prescriber_treatment_pathways(
        self, 
        provider_id: int,
        condition_concept_id: Optional[int] = None
    ) -> TreatmentPathwayByPrescriber:
        """
        Get treatment pathways for a specific prescriber.
        
        Shows what drugs they prescribe first, and common sequences.
        """
        
        # Get provider info
        provider_sql = f"""
        SELECT provider_id, provider_name
        FROM {self.schema}.provider
        WHERE provider_id = {provider_id}
        """
        provider_result = db.execute_query(provider_sql)
        provider_name = provider_result[0]['provider_name'] if provider_result else None
        
        # Condition filter
        condition_filter = ""
        if condition_concept_id:
            condition_filter = f"""
            AND de.person_id IN (
                SELECT person_id 
                FROM {self.schema}.condition_occurrence 
                WHERE condition_concept_id = {condition_concept_id}
            )
            """
        
        # Get first-line drugs (first drug prescribed to patients)
        first_line_sql = f"""
        WITH first_drug_per_patient AS (
            SELECT 
                de.person_id,
                de.drug_concept_id,
                c.concept_name as drug_name,
                de.drug_exposure_start_date,
                ROW_NUMBER() OVER (
                    PARTITION BY de.person_id 
                    ORDER BY de.drug_exposure_start_date
                ) as rn
            FROM {self.schema}.drug_exposure de
            INNER JOIN {self.schema}.concept c ON de.drug_concept_id = c.concept_id
            WHERE de.provider_id = {provider_id}
            {condition_filter}
        )
        SELECT 
            drug_concept_id,
            drug_name,
            COUNT(*) as patient_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
        FROM first_drug_per_patient
        WHERE rn = 1
        GROUP BY drug_concept_id, drug_name
        ORDER BY patient_count DESC
        LIMIT 10
        """
        
        # Get switch patterns (drug A followed by drug B)
        switch_sql = f"""
        WITH drug_sequences AS (
            SELECT 
                de.person_id,
                de.drug_concept_id as from_drug_id,
                c1.concept_name as from_drug,
                LEAD(de.drug_concept_id) OVER (
                    PARTITION BY de.person_id 
                    ORDER BY de.drug_exposure_start_date
                ) as to_drug_id,
                LEAD(c1.concept_name) OVER (
                    PARTITION BY de.person_id 
                    ORDER BY de.drug_exposure_start_date
                ) as to_drug
            FROM {self.schema}.drug_exposure de
            INNER JOIN {self.schema}.concept c1 ON de.drug_concept_id = c1.concept_id
            WHERE de.provider_id = {provider_id}
            {condition_filter}
        )
        SELECT 
            from_drug_id,
            from_drug,
            to_drug_id,
            to_drug,
            COUNT(*) as switch_count
        FROM drug_sequences
        WHERE to_drug_id IS NOT NULL 
            AND from_drug_id != to_drug_id  -- Actual switch, not refill
        GROUP BY from_drug_id, from_drug, to_drug_id, to_drug
        ORDER BY switch_count DESC
        LIMIT 15
        """
        
        try:
            first_line_results = db.execute_query(first_line_sql)
            switch_results = db.execute_query(switch_sql)
            
            first_line_drugs = [dict(row) for row in first_line_results]
            switch_patterns = [dict(row) for row in switch_results]
            
            return TreatmentPathwayByPrescriber(
                provider_id=provider_id,
                provider_name=provider_name,
                first_line_drugs=first_line_drugs,
                switch_patterns=switch_patterns,
                pathways=[]  # Could add multi-step pathways if needed
            )
        except Exception as e:
            logger.error(f"Error getting prescriber treatment pathways: {e}")
            raise
    
    def compare_prescribers(
        self, 
        provider_ids: List[int],
        drug_concept_id: Optional[int] = None
    ) -> List[PrescriberMetrics]:
        """Compare metrics across multiple prescribers."""
        
        provider_ids_str = ",".join(str(id) for id in provider_ids)
        
        drug_filter = ""
        if drug_concept_id:
            drug_filter = f"AND de.drug_concept_id = {drug_concept_id}"
        
        sql = f"""
        SELECT 
            p.provider_id,
            p.provider_name,
            p.specialty_source_value as specialty,
            COUNT(DISTINCT de.person_id) as total_patients,
            COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
            PERCENT_RANK() OVER (ORDER BY COUNT(DISTINCT de.drug_exposure_id)) * 100 as percentile_rank,
            NTILE(10) OVER (ORDER BY COUNT(DISTINCT de.drug_exposure_id)) as decile
        FROM {self.schema}.provider p
        LEFT JOIN {self.schema}.drug_exposure de ON p.provider_id = de.provider_id
        WHERE p.provider_id IN ({provider_ids_str})
        {drug_filter}
        GROUP BY p.provider_id, p.provider_name, p.specialty_source_value
        ORDER BY total_prescriptions DESC
        """
        
        try:
            results = db.execute_query(sql)
            return [PrescriberMetrics(**row) for row in results]
        except Exception as e:
            logger.error(f"Error comparing prescribers: {e}")
            raise


# Global instance
prescriber_service = PrescriberService()

