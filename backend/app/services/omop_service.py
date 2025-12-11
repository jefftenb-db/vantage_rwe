from typing import List, Dict, Any, Optional
import logging
from app.db.databricks import db
from app.config import settings
from app.models.cohort import (
    Concept, CriteriaDefinition, CriteriaType, OperatorType
)

logger = logging.getLogger(__name__)


class OMOPService:
    """Service for querying OMOP CDM data."""
    
    def __init__(self):
        self.schema = settings.omop_full_schema
    
    def search_concepts(
        self, 
        query: str, 
        domain_id: Optional[str] = None,
        vocabulary_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Concept]:
        """Search for OMOP concepts by name."""
        
        sql = f"""
        SELECT 
            concept_id,
            concept_name,
            domain_id,
            vocabulary_id,
            concept_class_id,
            standard_concept,
            concept_code
        FROM {self.schema}.concept
        WHERE LOWER(concept_name) LIKE LOWER('{query}%')
        """
        
        if domain_id:
            sql += f" AND domain_id = '{domain_id}'"
        
        if vocabulary_id:
            sql += f" AND vocabulary_id = '{vocabulary_id}'"
        
        sql += f" AND invalid_reason IS NULL"
        sql += f" ORDER BY concept_name LIMIT {limit}"
        
        results = db.execute_query(sql)
        return [Concept(**row) for row in results]
    
    def get_concept_by_id(self, concept_id: int) -> Optional[Concept]:
        """Get a specific concept by ID."""
        
        sql = f"""
        SELECT 
            concept_id,
            concept_name,
            domain_id,
            vocabulary_id,
            concept_class_id,
            standard_concept,
            concept_code
        FROM {self.schema}.concept
        WHERE concept_id = {concept_id}
        """
        
        results = db.execute_query(sql)
        return Concept(**results[0]) if results else None
    
    def get_patient_count_by_condition(self, concept_ids: List[int]) -> int:
        """Get count of patients with specified conditions."""
        
        concept_ids_str = ",".join(map(str, concept_ids))
        
        sql = f"""
        SELECT COUNT(DISTINCT person_id) as patient_count
        FROM {self.schema}.condition_occurrence
        WHERE condition_concept_id IN ({concept_ids_str})
        """
        
        result = db.execute_scalar(sql)
        return int(result) if result else 0
    
    def get_patient_count_by_drug(self, concept_ids: List[int]) -> int:
        """Get count of patients with specified drug exposures."""
        
        concept_ids_str = ",".join(map(str, concept_ids))
        
        sql = f"""
        SELECT COUNT(DISTINCT person_id) as patient_count
        FROM {self.schema}.drug_exposure
        WHERE drug_concept_id IN ({concept_ids_str})
        """
        
        result = db.execute_scalar(sql)
        return int(result) if result else 0
    
    def get_patient_count_by_procedure(self, concept_ids: List[int]) -> int:
        """Get count of patients with specified procedures."""
        
        concept_ids_str = ",".join(map(str, concept_ids))
        
        sql = f"""
        SELECT COUNT(DISTINCT person_id) as patient_count
        FROM {self.schema}.procedure_occurrence
        WHERE procedure_concept_id IN ({concept_ids_str})
        """
        
        result = db.execute_scalar(sql)
        return int(result) if result else 0
    
    def get_demographics_summary(self, person_ids: List[int]) -> Dict[str, Any]:
        """Get demographics summary for a list of patients."""
        
        if not person_ids:
            return {}
        
        person_ids_str = ",".join(map(str, person_ids))
        
        # Gender distribution
        gender_sql = f"""
        SELECT 
            c.concept_name as gender,
            COUNT(*) as count
        FROM {self.schema}.person p
        JOIN {self.schema}.concept c ON p.gender_concept_id = c.concept_id
        WHERE p.person_id IN ({person_ids_str})
        GROUP BY c.concept_name
        """
        
        # Age distribution
        age_sql = f"""
        SELECT 
            FLOOR(DATEDIFF(CURRENT_DATE(), 
                CONCAT(year_of_birth, '-', 
                    LPAD(COALESCE(month_of_birth, 1), 2, '0'), '-',
                    LPAD(COALESCE(day_of_birth, 1), 2, '0')
                )
            ) / 365.25) as age,
            COUNT(*) as count
        FROM {self.schema}.person
        WHERE person_id IN ({person_ids_str})
        GROUP BY age
        ORDER BY age
        """
        
        gender_dist = db.execute_query(gender_sql)
        age_dist = db.execute_query(age_sql)
        
        # Calculate age statistics
        ages = [row['age'] for row in age_dist if row['age'] is not None]
        
        return {
            "gender_distribution": gender_dist,
            "age_distribution": age_dist,
            "age_stats": {
                "mean": float(sum(ages) / len(ages)) if ages else 0.0,
                "min": int(min(ages)) if ages else 0,
                "max": int(max(ages)) if ages else 0
            }
        }


omop_service = OMOPService()

