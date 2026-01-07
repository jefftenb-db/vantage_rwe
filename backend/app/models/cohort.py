from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class CriteriaType(str, Enum):
    """Types of criteria for cohort building."""
    CONDITION = "condition"
    DRUG = "drug"
    PROCEDURE = "procedure"
    VISIT = "visit"
    OBSERVATION = "observation"
    AGE = "age"
    GENDER = "gender"


class OperatorType(str, Enum):
    """Comparison operators for criteria."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"


class CriteriaDefinition(BaseModel):
    """A single criteria definition for cohort inclusion/exclusion."""
    
    id: str = Field(description="Unique identifier for this criteria")
    criteria_type: CriteriaType
    operator: Optional[OperatorType] = Field(default=OperatorType.EQUALS)
    
    # For concept-based criteria (condition, drug, procedure, observation)
    concept_ids: Optional[List[int]] = Field(default=None, description="OMOP concept IDs")
    concept_names: Optional[List[str]] = Field(default=None, description="Concept names for display")
    
    # For value-based criteria (age, dates, numeric observations)
    value: Optional[Any] = Field(default=None, description="Value for comparison")
    value_min: Optional[float] = Field(default=None, description="Minimum value for range")
    value_max: Optional[float] = Field(default=None, description="Maximum value for range")
    
    # Date constraints (accept both string and datetime)
    start_date: Optional[str] = Field(default=None, description="Earliest date for occurrence")
    end_date: Optional[str] = Field(default=None, description="Latest date for occurrence")
    
    # Occurrence constraints
    min_occurrences: int = Field(default=1, description="Minimum number of occurrences required")
    
    # Logic
    is_exclusion: bool = Field(default=False, description="If True, exclude patients meeting this criteria")


class CohortDefinition(BaseModel):
    """Complete definition of a patient cohort."""
    
    id: Optional[str] = None
    name: str = Field(description="Name of the cohort")
    description: Optional[str] = Field(default="", description="Description of the cohort")
    
    # Criteria lists
    inclusion_criteria: List[CriteriaDefinition] = Field(default_factory=list)
    exclusion_criteria: List[CriteriaDefinition] = Field(default_factory=list)
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None


class CohortResult(BaseModel):
    """Results from executing a cohort definition."""
    
    cohort_definition: CohortDefinition
    patient_count: int
    execution_time_seconds: float
    
    # Demographics summary
    demographics: Optional[Dict[str, Any]] = None
    
    # Sample patient IDs
    sample_patient_ids: Optional[List[int]] = None
    
    # SQL query used to generate the cohort
    sql_query: Optional[str] = None


class ConceptSearchRequest(BaseModel):
    """Request to search for OMOP concepts."""
    
    query: str = Field(description="Search term")
    domain_id: Optional[str] = Field(default=None, description="Filter by domain (Condition, Drug, etc.)")
    vocabulary_id: Optional[str] = Field(default=None, description="Filter by vocabulary (SNOMED, RxNorm, etc.)")
    limit: int = Field(default=20, ge=1, le=100)


class Concept(BaseModel):
    """OMOP concept representation."""
    
    concept_id: int
    concept_name: str
    domain_id: str
    vocabulary_id: str
    concept_class_id: str
    standard_concept: Optional[str] = None
    concept_code: str


class NaturalLanguageQuery(BaseModel):
    """Natural language query for GenAI."""
    
    query: str = Field(description="Natural language query about patient cohorts")
    context: Optional[str] = Field(default=None, description="Additional context for the query")


class NaturalLanguageResponse(BaseModel):
    """Response from GenAI natural language query."""
    
    query: str
    sql_generated: str
    cohort_definition: Optional[CohortDefinition] = None
    result_count: int
    explanation: str
    query_results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Actual query result rows")


class SaveCohortRequest(BaseModel):
    """Request to save a cohort definition to the database."""
    
    cohort_definition_name: str = Field(description="Name of the cohort definition")
    cohort_definition_description: str = Field(description="Description of the cohort definition")
    cohort_definition_syntax: str = Field(description="SQL query used to generate the cohort")


class SaveCohortResponse(BaseModel):
    """Response from saving a cohort definition."""
    
    cohort_definition_id: int = Field(description="Auto-generated ID of the saved cohort definition")
    cohort_definition_name: str
    cohort_definition_description: str
    cohort_initiation_date: str = Field(description="Date the cohort was saved (YYYY-MM-DD)")

