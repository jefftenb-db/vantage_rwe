from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from app.models.cohort import (
    ConceptSearchRequest, Concept, CohortDefinition, CohortResult,
    NaturalLanguageQuery, NaturalLanguageResponse, SaveCohortRequest, SaveCohortResponse
)
from app.models.prescriber import (
    PrescriberProfile, PrescriberMetrics, DrugPrescriberAnalytics,
    PrescriberSearchRequest, PrescriberTargetingRequest, PrescriberTargetingResponse,
    TreatmentPathwayByPrescriber
)
from app.models.market_share import (
    MarketShareRequest, MarketShareResponse, TrendAnalysisResponse,
    GeographicMarketShare, CompetitivePositioning, NewToBrandAnalysis
)
from app.services.omop_service import omop_service
from app.services.cohort_builder import cohort_builder
from app.services.genai_service import genai_service
from app.services.prescriber_service import prescriber_service
from app.services.market_share_service import market_share_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Vantage RWE", "tagline": "Commercial Intelligence from Real-World Evidence"}


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


@router.post("/cohorts/save", response_model=SaveCohortResponse)
async def save_cohort_definition(request: SaveCohortRequest):
    """
    Save a cohort definition to the cohort_definition table.
    
    Stores the cohort name, description, and SQL query used to generate it.
    Returns the auto-generated cohort_definition_id.
    """
    try:
        response = cohort_builder.save_cohort_definition(request)
        return response
    except Exception as e:
        logger.error(f"Error saving cohort definition: {e}")
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


# ============================================================================
# MARKET SHARE ANALYTICS ENDPOINTS
# ============================================================================

@router.post("/market-share/analysis", response_model=MarketShareResponse)
async def get_market_share_analysis(request: MarketShareRequest):
    """
    Get comprehensive market share analysis.
    
    Returns market share for drugs in a therapeutic area/condition,
    including concentration metrics (HHI, top 3/5 share).
    
    Perfect for understanding competitive landscape and market dynamics.
    """
    try:
        response = market_share_service.get_market_share_analysis(request)
        return response
    except Exception as e:
        logger.error(f"Error getting market share analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-share/trends/{drug_concept_id}", response_model=TrendAnalysisResponse)
async def get_trend_analysis(
    drug_concept_id: int,
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    granularity: str = Query('month', description="'month', 'quarter', or 'year'")
):
    """
    Get market share trends over time for a drug.
    
    Shows how market share has changed period-over-period,
    identifies peaks, and calculates growth rates.
    
    Essential for tracking product performance and forecasting.
    """
    try:
        response = market_share_service.get_trend_analysis(
            drug_concept_id=drug_concept_id,
            start_date=start_date,
            end_date=end_date,
            granularity=granularity
        )
        return response
    except Exception as e:
        logger.error(f"Error getting trend analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market-share/geographic", response_model=List[GeographicMarketShare])
async def get_geographic_market_share(
    drug_concept_ids: List[int],
    geography_type: str = Query('state', description="'state', 'zip', or 'region'")
):
    """
    Get market share by geographic region.
    
    Shows where your drug is strong vs. weak geographically.
    Useful for territory planning and regional marketing strategies.
    """
    try:
        if len(drug_concept_ids) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 drugs for geographic analysis")
        
        response = market_share_service.get_geographic_market_share(
            drug_concept_ids=drug_concept_ids,
            geography_type=geography_type
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting geographic market share: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-share/competitive/{your_drug_id}", response_model=CompetitivePositioning)
async def get_competitive_positioning(
    your_drug_id: int,
    competitor_ids: str = Query(..., description="Comma-separated competitor drug IDs"),
    start_date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="YYYY-MM-DD")
):
    """
    Analyze competitive position of your drug vs. competitors.
    
    Returns:
    - Your rank and share vs. competitors
    - Gap to market leader
    - Relative positioning
    
    The "war room" view for brand teams.
    """
    try:
        competitor_drug_ids = [int(id.strip()) for id in competitor_ids.split(',')]
        
        response = market_share_service.get_competitive_positioning(
            your_drug_concept_id=your_drug_id,
            competitor_drug_concept_ids=competitor_drug_ids,
            start_date=start_date,
            end_date=end_date
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid competitor IDs: {e}")
    except Exception as e:
        logger.error(f"Error getting competitive positioning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-share/new-to-brand/{drug_concept_id}", response_model=NewToBrandAnalysis)
async def get_new_to_brand_analysis(
    drug_concept_id: int,
    start_date: str = Query(..., description="Analysis period start (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Analysis period end (YYYY-MM-DD)"),
    lookback_days: int = Query(365, description="Days to look back for prior therapy")
):
    """
    Analyze new-to-brand (NBx) patients.
    
    Identifies:
    - How many patients are new to your drug
    - Are they treatment-naive or switching from competitors?
    - Which competitor drugs are they switching from?
    
    Critical for understanding growth sources and competitive dynamics.
    """
    try:
        response = market_share_service.get_new_to_brand_analysis(
            drug_concept_id=drug_concept_id,
            start_date=start_date,
            end_date=end_date,
            lookback_days=lookback_days
        )
        return response
    except Exception as e:
        logger.error(f"Error getting new-to-brand analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

