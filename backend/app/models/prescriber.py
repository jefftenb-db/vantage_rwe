from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class PrescriberProfile(BaseModel):
    """Prescriber/HCP profile information."""
    
    provider_id: int = Field(description="OMOP provider_id")
    provider_name: Optional[str] = Field(default=None, description="Provider name")
    specialty_concept_id: Optional[int] = Field(default=None, description="Specialty concept ID")
    specialty_source_value: Optional[str] = Field(default=None, description="Specialty description")
    npi: Optional[str] = Field(default=None, description="National Provider Identifier")
    dea: Optional[str] = Field(default=None, description="DEA number")
    
    # Aggregated metrics
    total_patients: int = Field(default=0, description="Total unique patients seen")
    total_prescriptions: int = Field(default=0, description="Total prescriptions written")
    total_visits: int = Field(default=0, description="Total visits")


class PrescriberMetrics(BaseModel):
    """Prescriber performance metrics."""
    
    provider_id: int
    provider_name: Optional[str] = None
    specialty: Optional[str] = None
    
    # Volume metrics
    total_patients: int = Field(default=0)
    new_patients: int = Field(default=0, description="Patients with first prescription in date range")
    total_prescriptions: int = Field(default=0)
    
    # Ranking
    percentile_rank: Optional[float] = Field(default=None, description="Percentile rank among peers (0-100)")
    decile: Optional[int] = Field(default=None, description="Decile (1-10, where 10 is highest volume)")
    
    # Share metrics
    market_share: Optional[float] = Field(default=None, description="% of total prescriptions in category")


class DrugPrescriberAnalytics(BaseModel):
    """Analytics for a specific drug or drug class."""
    
    drug_concept_id: int
    drug_name: str
    
    # Top prescribers
    top_prescribers: List[PrescriberMetrics]
    
    # Summary stats
    total_prescriptions: int
    total_unique_prescribers: int
    total_unique_patients: int
    
    # Concentration metrics
    top_10_percent_share: Optional[float] = Field(default=None, description="% of Rx from top 10% of prescribers")
    top_20_percent_share: Optional[float] = Field(default=None, description="% of Rx from top 20% of prescribers")
    herfindahl_index: Optional[float] = Field(default=None, description="Market concentration index")


class PrescriberSearchRequest(BaseModel):
    """Request to search for prescribers."""
    
    specialty: Optional[str] = Field(default=None, description="Filter by specialty")
    min_patients: Optional[int] = Field(default=None, description="Minimum patient count")
    drug_concept_id: Optional[int] = Field(default=None, description="Filter by specific drug prescribed")
    limit: int = Field(default=50, ge=1, le=500)


class PrescriberComparison(BaseModel):
    """Compare multiple prescribers."""
    
    provider_ids: List[int]
    metrics: List[PrescriberMetrics]
    
    # Comparative insights
    avg_patients_per_prescriber: float
    avg_prescriptions_per_prescriber: float


class TreatmentPathwayByPrescriber(BaseModel):
    """Treatment pathways for a specific prescriber."""
    
    provider_id: int
    provider_name: Optional[str] = None
    
    # Sequential patterns
    pathways: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of common treatment sequences (drug1 -> drug2 -> drug3)"
    )
    
    # First-line preferences
    first_line_drugs: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Most commonly prescribed first drugs with counts"
    )
    
    # Switch patterns
    switch_patterns: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Common drug switches (from X to Y)"
    )


class PrescriberTargetingRequest(BaseModel):
    """Request to identify target prescribers."""
    
    # Target drug/class
    target_drug_concept_ids: Optional[List[int]] = Field(default=None)
    
    # Competitor drugs
    competitor_drug_concept_ids: Optional[List[int]] = Field(default=None)
    
    # Patient criteria (who would be good candidates)
    condition_concept_ids: Optional[List[int]] = Field(default=None)
    
    # Prescriber filters
    min_relevant_patients: int = Field(default=10, description="Min patients with target condition")
    specialty: Optional[str] = None
    
    # Geographic
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
    limit: int = Field(default=100, ge=1, le=500)


class TargetPrescriber(BaseModel):
    """Prescriber identified as a target for outreach."""
    
    provider_id: int
    provider_name: Optional[str] = None
    specialty: Optional[str] = None
    
    # Why they're a target
    reason_score: float = Field(description="Targeting score (higher = better target)")
    
    # Key metrics
    relevant_patients: int = Field(description="Patients with target condition")
    competitor_prescriptions: int = Field(description="Competitor drug prescriptions")
    target_drug_prescriptions: int = Field(default=0, description="Our drug prescriptions")
    
    # Opportunity
    estimated_opportunity: Optional[int] = Field(
        default=None, 
        description="Estimated additional prescriptions if prescriber adopts"
    )
    
    # Location
    state: Optional[str] = None
    zip_code: Optional[str] = None


class PrescriberTargetingResponse(BaseModel):
    """Response with targeted prescriber list."""
    
    targets: List[TargetPrescriber]
    
    # Summary
    total_opportunity_prescriptions: int
    total_target_prescribers: int
    
    # Segmentation
    high_priority_count: int = Field(description="Count of prescribers with score > 80")
    medium_priority_count: int = Field(description="Count of prescribers with score 50-80")
    low_priority_count: int = Field(description="Count of prescribers with score < 50")

