from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date


class DrugMarketShare(BaseModel):
    """Market share for a specific drug."""
    
    drug_concept_id: int
    drug_name: str
    total_prescriptions: int
    total_patients: int
    market_share_by_prescriptions: float = Field(description="% of total prescriptions in market")
    market_share_by_patients: float = Field(description="% of total patients in market")
    rank: int = Field(description="Rank by prescription volume")


class TherapeuticAreaMarketShare(BaseModel):
    """Market share within a therapeutic area or drug class."""
    
    therapeutic_area: str = Field(description="e.g., 'Diabetes', 'Cardiovascular'")
    drugs: List[DrugMarketShare]
    total_market_prescriptions: int
    total_market_patients: int
    top_3_concentration: float = Field(description="% of market held by top 3 drugs")
    herfindahl_index: Optional[float] = Field(default=None, description="Market concentration index (0-10000)")


class MarketShareTrend(BaseModel):
    """Market share over time for a drug."""
    
    drug_concept_id: int
    drug_name: str
    time_period: str = Field(description="e.g., '2023-Q1', '2023-01'")
    prescriptions: int
    patients: int
    market_share: float
    new_to_brand: Optional[int] = Field(default=None, description="New patients (NBx)")
    
    # Growth metrics
    prescriptions_change_pct: Optional[float] = Field(default=None, description="% change vs previous period")
    market_share_change_points: Optional[float] = Field(default=None, description="Market share point change")


class GeographicMarketShare(BaseModel):
    """Market share by geographic region."""
    
    region: str = Field(description="State, ZIP, or custom region")
    region_type: str = Field(description="'state', 'zip', 'territory'")
    drug_concept_id: int
    drug_name: str
    prescriptions: int
    patients: int
    market_share: float
    rank_in_region: int


class SegmentMarketShare(BaseModel):
    """Market share by segment (specialty, payer, etc.)."""
    
    segment_type: str = Field(description="'specialty', 'payer', 'age_group', etc.")
    segment_value: str = Field(description="e.g., 'Cardiology', 'Medicare'")
    drug_concept_id: int
    drug_name: str
    prescriptions: int
    patients: int
    market_share: float


class CompetitivePositioning(BaseModel):
    """Competitive position of your drug vs competitors."""
    
    your_drug_concept_id: int
    your_drug_name: str
    your_prescriptions: int
    your_patients: int
    your_market_share: float
    your_rank: int
    
    competitors: List[DrugMarketShare]
    
    # Competitive metrics
    share_gap_to_leader: float = Field(description="Points behind #1")
    share_of_top_3: Optional[float] = Field(default=None, description="Your share of top 3 total")
    
    # Patient flow
    patients_gained_from_competitors: Optional[int] = Field(default=None)
    patients_lost_to_competitors: Optional[int] = Field(default=None)


class MarketShareRequest(BaseModel):
    """Request parameters for market share analysis."""
    
    # Define the market
    condition_concept_ids: Optional[List[int]] = Field(default=None, description="Define market by condition")
    drug_concept_ids: Optional[List[int]] = Field(default=None, description="Specific drugs to analyze")
    therapeutic_area: Optional[str] = Field(default=None, description="Therapeutic classification")
    
    # Time range
    start_date: Optional[str] = Field(default=None)
    end_date: Optional[str] = Field(default=None)
    
    # Segmentation
    segment_by: Optional[str] = Field(default=None, description="'geography', 'specialty', 'payer', 'time'")
    geography_type: Optional[str] = Field(default='state', description="'state', 'zip', 'region'")
    time_granularity: Optional[str] = Field(default='month', description="'month', 'quarter', 'year'")
    
    # Filters
    min_prescriptions: Optional[int] = Field(default=10, description="Minimum Rx to include drug")
    top_n: Optional[int] = Field(default=10, description="Return top N drugs")


class MarketShareResponse(BaseModel):
    """Comprehensive market share response."""
    
    market_definition: str = Field(description="Description of the market analyzed")
    time_period: str = Field(description="Date range of analysis")
    
    # Overall market
    total_market_prescriptions: int
    total_market_patients: int
    
    # Drug shares
    drug_shares: List[DrugMarketShare]
    
    # Market concentration
    top_3_concentration: float
    top_5_concentration: float
    herfindahl_index: Optional[float] = None
    
    # Summary stats
    total_drugs_in_market: int
    avg_prescriptions_per_drug: float


class TrendAnalysisResponse(BaseModel):
    """Time-series trend analysis."""
    
    drug_concept_id: int
    drug_name: str
    trends: List[MarketShareTrend]
    
    # Overall trajectory
    overall_change_pct: float = Field(description="Total % change from first to last period")
    overall_share_change: float = Field(description="Market share point change")
    trend_direction: str = Field(description="'growing', 'declining', 'stable'")
    
    # Peak/trough
    peak_period: Optional[str] = None
    peak_market_share: Optional[float] = None


class NewToBrandAnalysis(BaseModel):
    """New-to-brand (NBx) analysis."""
    
    drug_concept_id: int
    drug_name: str
    time_period: str
    
    # NBx metrics
    new_patients: int = Field(description="Patients with first Rx in period")
    total_patients: int = Field(description="All patients in period")
    nbx_rate: float = Field(description="NBx / Total patients")
    
    # Source of NBx patients
    treatment_naive: int = Field(description="Never on any drug in class")
    switched_from_competitor: int = Field(description="Previously on competitor")
    
    # Competitor switches
    switch_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Which competitor drugs patients switched from"
    )


class ShareOfVoiceAnalysis(BaseModel):
    """Share of voice within therapeutic area."""
    
    therapeutic_area: str
    
    # By volume
    share_by_prescriptions: Dict[str, float] = Field(description="Drug name -> % share")
    share_by_patients: Dict[str, float] = Field(description="Drug name -> % share")
    
    # By breadth
    share_by_prescribers: Dict[str, float] = Field(description="Drug name -> % of prescribers")
    
    # Market dynamics
    market_leader: str
    challenger_brands: List[str] = Field(description="Drugs with 10-25% share")
    niche_players: List[str] = Field(description="Drugs with <10% share")

