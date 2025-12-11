from fastapi import APIRouter, HTTPException
from typing import List
import logging
from app.models.cohort import (
    ConceptSearchRequest, Concept, CohortDefinition, CohortResult,
    NaturalLanguageQuery, NaturalLanguageResponse
)
from app.services.omop_service import omop_service
from app.services.cohort_builder import cohort_builder
from app.services.genai_service import genai_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "OMOP Cohort Builder"}


@router.post("/concepts/search", response_model=List[Concept])
async def search_concepts(request: ConceptSearchRequest):
    """
    Search for OMOP concepts by name.
    
    Supports filtering by domain (Condition, Drug, Procedure, etc.)
    and vocabulary (SNOMED, RxNorm, etc.).
    """
    try:
        concepts = omop_service.search_concepts(
            query=request.query,
            domain_id=request.domain_id,
            vocabulary_id=request.vocabulary_id,
            limit=request.limit
        )
        return concepts
    except Exception as e:
        logger.error(f"Error searching concepts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concepts/{concept_id}", response_model=Concept)
async def get_concept(concept_id: int):
    """Get a specific OMOP concept by ID."""
    try:
        concept = omop_service.get_concept_by_id(concept_id)
        if not concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        return concept
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting concept: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cohorts/build", response_model=CohortResult)
async def build_cohort(cohort_definition: CohortDefinition):
    """
    Build and execute a cohort definition.
    
    Returns patient count, demographics, and sample patient IDs.
    """
    try:
        result = cohort_builder.build_cohort(cohort_definition)
        return result
    except Exception as e:
        logger.error(f"Error building cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cohorts/preview-count")
async def preview_cohort_count(cohort_definition: CohortDefinition):
    """
    Get a quick count preview for a cohort without full demographics.
    
    Faster than full build for interactive editing.
    """
    try:
        # Just get the count without demographics
        sql = cohort_builder._build_cohort_sql(cohort_definition)
        results = cohort_builder.db.execute_query(f"SELECT COUNT(*) as cnt FROM ({sql}) t")
        count = results[0]['cnt'] if results else 0
        
        return {"count": count}
    except Exception as e:
        logger.error(f"Error previewing cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/genai/query", response_model=NaturalLanguageResponse)
async def natural_language_query(nl_query: NaturalLanguageQuery):
    """
    Process a natural language query and convert to cohort definition.
    
    Uses Databricks GenAI features to understand the query and
    automatically generate cohort criteria.
    """
    try:
        response = genai_service.process_natural_language_query(nl_query)
        return response
    except Exception as e:
        logger.error(f"Error processing natural language query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_database_summary():
    """
    Get summary statistics about the OMOP database.
    
    Returns counts of patients, conditions, drugs, etc.
    """
    try:
        from app.db.databricks import db
        from app.config import settings
        
        schema = settings.omop_full_schema
        
        stats = {}
        
        # Count patients
        person_count = db.execute_scalar(f"SELECT COUNT(*) FROM {schema}.person")
        stats['total_patients'] = person_count
        
        # Count conditions
        condition_count = db.execute_scalar(f"SELECT COUNT(DISTINCT condition_concept_id) FROM {schema}.condition_occurrence")
        stats['unique_conditions'] = condition_count
        
        # Count drugs
        drug_count = db.execute_scalar(f"SELECT COUNT(DISTINCT drug_concept_id) FROM {schema}.drug_exposure")
        stats['unique_drugs'] = drug_count
        
        # Count procedures
        procedure_count = db.execute_scalar(f"SELECT COUNT(DISTINCT procedure_concept_id) FROM {schema}.procedure_occurrence")
        stats['unique_procedures'] = procedure_count
        
        # Count visits
        visit_count = db.execute_scalar(f"SELECT COUNT(*) FROM {schema}.visit_occurrence")
        stats['total_visits'] = visit_count
        
        return stats
    except Exception as e:
        logger.error(f"Error getting database summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

