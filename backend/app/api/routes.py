from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from app.models.cohort import (
    ConceptSearchRequest, Concept, CohortDefinition, CohortResult,
    NaturalLanguageQuery, NaturalLanguageResponse
)
from app.models.prescriber import (
    PrescriberProfile, PrescriberMetrics, DrugPrescriberAnalytics,
    PrescriberSearchRequest, PrescriberTargetingRequest, PrescriberTargetingResponse,
    TreatmentPathwayByPrescriber
)
from app.services.omop_service import omop_service
from app.services.cohort_builder import cohort_builder
from app.services.genai_service import genai_service
from app.services.prescriber_service import prescriber_service

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


# ============================================================================
# PRESCRIBER ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/prescribers/{provider_id}", response_model=PrescriberProfile)
async def get_prescriber_profile(provider_id: int):
    """
    Get detailed profile for a specific prescriber.
    
    Returns prescriber information, specialties, and aggregate metrics.
    """
    try:
        profile = prescriber_service.get_prescriber_profile(provider_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Prescriber not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prescriber profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prescribers/search", response_model=List[PrescriberMetrics])
async def search_prescribers(request: PrescriberSearchRequest):
    """
    Search for prescribers with filtering.
    
    Supports filtering by specialty, drug prescribed, and minimum patient count.
    Returns prescribers ranked by volume with percentile/decile rankings.
    """
    try:
        prescribers = prescriber_service.search_prescribers(request)
        return prescribers
    except Exception as e:
        logger.error(f"Error searching prescribers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prescribers/drug/{drug_concept_id}/analytics", response_model=DrugPrescriberAnalytics)
async def get_drug_prescriber_analytics(
    drug_concept_id: int,
    limit: int = Query(50, ge=1, le=500, description="Max number of top prescribers to return")
):
    """
    Get comprehensive prescriber analytics for a specific drug.
    
    Returns:
    - Top prescribers by volume
    - Market concentration metrics
    - Prescriber distribution (top 10%, top 20%)
    
    Perfect for understanding who the key opinion leaders are for a drug.
    """
    try:
        analytics = prescriber_service.get_drug_prescriber_analytics(
            drug_concept_id=drug_concept_id,
            limit=limit
        )
        return analytics
    except Exception as e:
        logger.error(f"Error getting drug prescriber analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prescribers/targeting", response_model=PrescriberTargetingResponse)
async def identify_target_prescribers(request: PrescriberTargetingRequest):
    """
    Identify target prescribers for commercial outreach.
    
    Finds prescribers who:
    - Treat patients with target conditions
    - Prescribe competitor drugs
    - Have low/no adoption of your target drug
    
    Returns prioritized list with opportunity scores.
    This is the "money endpoint" for sales force targeting.
    """
    try:
        response = prescriber_service.identify_target_prescribers(request)
        return response
    except Exception as e:
        logger.error(f"Error identifying target prescribers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prescribers/{provider_id}/treatment-pathways", response_model=TreatmentPathwayByPrescriber)
async def get_prescriber_treatment_pathways(
    provider_id: int,
    condition_concept_id: Optional[int] = Query(None, description="Filter by condition")
):
    """
    Get treatment pathways for a specific prescriber.
    
    Shows:
    - What drugs they prescribe first-line
    - Common drug switching patterns
    - Treatment sequences
    
    Useful for understanding prescriber behavior and preferences.
    """
    try:
        pathways = prescriber_service.get_prescriber_treatment_pathways(
            provider_id=provider_id,
            condition_concept_id=condition_concept_id
        )
        return pathways
    except Exception as e:
        logger.error(f"Error getting prescriber treatment pathways: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prescribers/compare", response_model=List[PrescriberMetrics])
async def compare_prescribers(
    provider_ids: List[int],
    drug_concept_id: Optional[int] = Query(None, description="Filter by specific drug")
):
    """
    Compare multiple prescribers side-by-side.
    
    Useful for benchmarking and territory analysis.
    """
    try:
        if len(provider_ids) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 prescribers for comparison")
        
        comparison = prescriber_service.compare_prescribers(
            provider_ids=provider_ids,
            drug_concept_id=drug_concept_id
        )
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing prescribers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

