from typing import List, Set, Dict, Any
import time
import logging
from datetime import date
from app.db.databricks import db
from app.config import settings
from app.models.cohort import (
    CohortDefinition, CohortResult, CriteriaDefinition, 
    CriteriaType, OperatorType, SaveCohortRequest, SaveCohortResponse
)
from app.services.omop_service import omop_service

logger = logging.getLogger(__name__)


class CohortBuilder:
    """Service for building and executing patient cohorts."""
    
    def __init__(self):
        self.schema = settings.omop_full_schema
    
    def build_cohort(self, cohort_definition: CohortDefinition) -> CohortResult:
        """
        Execute a cohort definition and return results.
        
        This method:
        1. Starts with all patients
        2. Applies inclusion criteria (intersection)
        3. Applies exclusion criteria (subtraction)
        4. Returns count and demographics
        """
        start_time = time.time()
        
        logger.info(f"Building cohort: {cohort_definition.name}")
        
        # Build SQL query for cohort
        sql = self._build_cohort_sql(cohort_definition)
        
        logger.info(f"Generated SQL:\n{sql}")
        
        # Execute query to get patient IDs
        results = db.execute_query(sql)
        person_ids = [row['person_id'] for row in results]
        
        # Get demographics
        demographics = None
        if person_ids:
            demographics = omop_service.get_demographics_summary(person_ids[:1000])  # Limit for performance
        
        # Get sample patient IDs
        sample_patient_ids = person_ids[:10] if person_ids else []
        
        execution_time = time.time() - start_time
        
        return CohortResult(
            cohort_definition=cohort_definition,
            patient_count=len(person_ids),
            execution_time_seconds=execution_time,
            demographics=demographics,
            sample_patient_ids=sample_patient_ids,
            sql_query=sql
        )
    
    def _build_cohort_sql(self, cohort_definition: CohortDefinition) -> str:
        """Build SQL query for cohort definition."""
        
        # Start with all persons
        base_query = f"""
        WITH base_population AS (
            SELECT DISTINCT person_id
            FROM {self.schema}.person
        )
        """
        
        cte_parts = []
        cte_counter = 0
        
        # Build CTEs for each inclusion criteria
        for criteria in cohort_definition.inclusion_criteria:
            cte_counter += 1
            cte_name = f"inclusion_{cte_counter}"
            cte_sql = self._build_criteria_sql(criteria)
            cte_parts.append(f"{cte_name} AS (\n{cte_sql}\n)")
        
        # Build CTEs for each exclusion criteria
        for criteria in cohort_definition.exclusion_criteria:
            cte_counter += 1
            cte_name = f"exclusion_{cte_counter}"
            cte_sql = self._build_criteria_sql(criteria)
            cte_parts.append(f"{cte_name} AS (\n{cte_sql}\n)")
        
        # Combine all CTEs
        if cte_parts:
            base_query += ",\n" + ",\n".join(cte_parts)
        
        # Build final SELECT with intersections and exclusions
        final_query = "\nSELECT person_id FROM base_population\n"
        
        # Add INTERSECT for each inclusion criteria
        inclusion_count = len(cohort_definition.inclusion_criteria)
        for i in range(1, inclusion_count + 1):
            final_query += f"INTERSECT\nSELECT person_id FROM inclusion_{i}\n"
        
        # Add EXCEPT for each exclusion criteria
        exclusion_count = len(cohort_definition.exclusion_criteria)
        for i in range(1, exclusion_count + 1):
            final_query += f"EXCEPT\nSELECT person_id FROM exclusion_{inclusion_count + i}\n"
        
        return base_query + final_query
    
    def _build_criteria_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for a single criteria."""
        
        if criteria.criteria_type == CriteriaType.CONDITION:
            return self._build_condition_sql(criteria)
        elif criteria.criteria_type == CriteriaType.DRUG:
            return self._build_drug_sql(criteria)
        elif criteria.criteria_type == CriteriaType.PROCEDURE:
            return self._build_procedure_sql(criteria)
        elif criteria.criteria_type == CriteriaType.VISIT:
            return self._build_visit_sql(criteria)
        elif criteria.criteria_type == CriteriaType.OBSERVATION:
            return self._build_observation_sql(criteria)
        elif criteria.criteria_type == CriteriaType.AGE:
            return self._build_age_sql(criteria)
        elif criteria.criteria_type == CriteriaType.GENDER:
            return self._build_gender_sql(criteria)
        else:
            raise ValueError(f"Unknown criteria type: {criteria.criteria_type}")
    
    def _build_condition_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for condition occurrence criteria."""
        
        concept_ids_str = ",".join(map(str, criteria.concept_ids or []))
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.condition_occurrence
            WHERE condition_concept_id IN (
                SELECT descendant_concept_id 
                FROM {self.schema}.concept_ancestor 
                WHERE ancestor_concept_id IN ({concept_ids_str})
            )
        """
        
        if criteria.start_date:
            sql += f" AND condition_start_date >= '{criteria.start_date}'"
        
        if criteria.end_date:
            sql += f" AND condition_start_date <= '{criteria.end_date}'"
        
        if criteria.min_occurrences > 1:
            sql = f"""
                SELECT person_id
                FROM ({sql}) t
                GROUP BY person_id
                HAVING COUNT(*) >= {criteria.min_occurrences}
            """
        
        return sql
    
    def _build_drug_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for drug exposure criteria."""
        
        concept_ids_str = ",".join(map(str, criteria.concept_ids or []))
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.drug_exposure
            WHERE drug_concept_id IN (
                SELECT descendant_concept_id 
                FROM {self.schema}.concept_ancestor 
                WHERE ancestor_concept_id IN ({concept_ids_str})
            )
        """
        
        if criteria.start_date:
            sql += f" AND drug_exposure_start_date >= '{criteria.start_date}'"
        
        if criteria.end_date:
            sql += f" AND drug_exposure_start_date <= '{criteria.end_date}'"
        
        if criteria.min_occurrences > 1:
            sql = f"""
                SELECT person_id
                FROM ({sql}) t
                GROUP BY person_id
                HAVING COUNT(*) >= {criteria.min_occurrences}
            """
        
        return sql
    
    def _build_procedure_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for procedure occurrence criteria."""
        
        concept_ids_str = ",".join(map(str, criteria.concept_ids or []))
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.procedure_occurrence
            WHERE procedure_concept_id IN (
                SELECT descendant_concept_id 
                FROM {self.schema}.concept_ancestor 
                WHERE ancestor_concept_id IN ({concept_ids_str})
            )
        """
        
        if criteria.start_date:
            sql += f" AND procedure_date >= '{criteria.start_date}'"
        
        if criteria.end_date:
            sql += f" AND procedure_date <= '{criteria.end_date}'"
        
        if criteria.min_occurrences > 1:
            sql = f"""
                SELECT person_id
                FROM ({sql}) t
                GROUP BY person_id
                HAVING COUNT(*) >= {criteria.min_occurrences}
            """
        
        return sql
    
    def _build_visit_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for visit occurrence criteria."""
        
        concept_ids_str = ",".join(map(str, criteria.concept_ids or []))
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.visit_occurrence
            WHERE visit_concept_id IN (
                SELECT descendant_concept_id 
                FROM {self.schema}.concept_ancestor 
                WHERE ancestor_concept_id IN ({concept_ids_str})
            )
        """
        
        if criteria.start_date:
            sql += f" AND visit_start_date >= '{criteria.start_date}'"
        
        if criteria.end_date:
            sql += f" AND visit_start_date <= '{criteria.end_date}'"
        
        if criteria.min_occurrences > 1:
            sql = f"""
                SELECT person_id
                FROM ({sql}) t
                GROUP BY person_id
                HAVING COUNT(*) >= {criteria.min_occurrences}
            """
        
        return sql
    
    def _build_observation_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for observation criteria."""
        
        concept_ids_str = ",".join(map(str, criteria.concept_ids or []))
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.observation
            WHERE observation_concept_id IN (
                SELECT descendant_concept_id 
                FROM {self.schema}.concept_ancestor 
                WHERE ancestor_concept_id IN ({concept_ids_str})
            )
        """
        
        if criteria.start_date:
            sql += f" AND observation_date >= '{criteria.start_date}'"
        
        if criteria.end_date:
            sql += f" AND observation_date <= '{criteria.end_date}'"
        
        # Add value constraints for numeric observations
        if criteria.value_min is not None:
            sql += f" AND value_as_number >= {criteria.value_min}"
        
        if criteria.value_max is not None:
            sql += f" AND value_as_number <= {criteria.value_max}"
        
        if criteria.min_occurrences > 1:
            sql = f"""
                SELECT person_id
                FROM ({sql}) t
                GROUP BY person_id
                HAVING COUNT(*) >= {criteria.min_occurrences}
            """
        
        return sql
    
    def _build_age_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for age criteria."""
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.person
            WHERE FLOOR(DATEDIFF(CURRENT_DATE(), 
                CONCAT(year_of_birth, '-', 
                    LPAD(COALESCE(month_of_birth, 1), 2, '0'), '-',
                    LPAD(COALESCE(day_of_birth, 1), 2, '0')
                )
            ) / 365.25)
        """
        
        if criteria.operator == OperatorType.EQUALS:
            sql += f" = {criteria.value}"
        elif criteria.operator == OperatorType.GREATER_THAN:
            sql += f" > {criteria.value}"
        elif criteria.operator == OperatorType.LESS_THAN:
            sql += f" < {criteria.value}"
        elif criteria.operator == OperatorType.BETWEEN:
            sql += f" BETWEEN {criteria.value_min} AND {criteria.value_max}"
        
        return sql
    
    def _build_gender_sql(self, criteria: CriteriaDefinition) -> str:
        """Build SQL for gender criteria."""
        
        concept_ids_str = ",".join(map(str, criteria.concept_ids or []))
        
        sql = f"""
            SELECT person_id
            FROM {self.schema}.person
            WHERE gender_concept_id IN ({concept_ids_str})
        """
        
        return sql
    
    def save_cohort_definition(self, request: SaveCohortRequest) -> SaveCohortResponse:
        """
        Save a cohort definition to the cohort_definition table.
        
        This method:
        1. Gets the next cohort_definition_id by incrementing the max value
        2. Inserts a new row into cohort_definition table
        3. Returns the saved cohort information
        """
        logger.info(f"Saving cohort definition: {request.cohort_definition_name}")
        
        # Get the next cohort_definition_id
        max_id_query = f"SELECT COALESCE(MAX(cohort_definition_id), 0) FROM {self.schema}.cohort_definition"
        max_id = db.execute_scalar(max_id_query)
        next_id = max_id + 1
        
        # Get current date in YYYY-MM-DD format
        current_date = date.today().strftime('%Y-%m-%d')
        
        # Build INSERT statement
        insert_sql = f"""
        INSERT INTO {self.schema}.cohort_definition (
            cohort_definition_id,
            cohort_definition_name,
            cohort_definition_description,
            definition_type_concept_id,
            cohort_definition_syntax,
            subject_concept_id,
            cohort_initiation_date
        ) VALUES (
            {next_id},
            '{request.cohort_definition_name.replace("'", "''")}',
            '{request.cohort_definition_description.replace("'", "''")}',
            {next_id},
            '{request.cohort_definition_syntax.replace("'", "''")}',
            {next_id},
            '{current_date}'
        )
        """
        
        # Execute the INSERT
        db.execute_query(insert_sql)
        
        logger.info(f"Successfully saved cohort definition with ID: {next_id}")
        
        return SaveCohortResponse(
            cohort_definition_id=next_id,
            cohort_definition_name=request.cohort_definition_name,
            cohort_definition_description=request.cohort_definition_description,
            cohort_initiation_date=current_date
        )


cohort_builder = CohortBuilder()

