from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from app.models.market_share import (
    DrugMarketShare, TherapeuticAreaMarketShare, MarketShareTrend,
    GeographicMarketShare, SegmentMarketShare, CompetitivePositioning,
    MarketShareRequest, MarketShareResponse, TrendAnalysisResponse,
    NewToBrandAnalysis, ShareOfVoiceAnalysis
)
from app.db.databricks import db
from app.config import settings

logger = logging.getLogger(__name__)


class MarketShareService:
    """
    Service for market share analytics.
    
    Provides comprehensive market analysis including:
    - Market share by drug
    - Trend analysis over time
    - Geographic distribution
    - Competitive positioning
    - New-to-brand analysis
    """
    
    def __init__(self):
        self.schema = settings.omop_full_schema
    
    def get_market_share_analysis(self, request: MarketShareRequest) -> MarketShareResponse:
        """
        Get comprehensive market share analysis for a therapeutic area or condition.
        """
        
        # Build market definition
        market_filter = self._build_market_filter(request)
        date_filter = self._build_date_filter(request)
        
        market_definition = self._describe_market(request)
        time_period = f"{request.start_date or 'Beginning'} to {request.end_date or 'Present'}"
        
        # Get drug shares in the market
        sql = f"""
        WITH market_drugs AS (
            SELECT 
                de.drug_concept_id,
                c.concept_name as drug_name,
                COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
                COUNT(DISTINCT de.person_id) as total_patients
            FROM {self.schema}.drug_exposure de
            INNER JOIN {self.schema}.concept c ON de.drug_concept_id = c.concept_id
            {market_filter}
            {date_filter}
            GROUP BY de.drug_concept_id, c.concept_name
            HAVING COUNT(DISTINCT de.drug_exposure_id) >= {request.min_prescriptions or 10}
        ),
        market_totals AS (
            SELECT 
                SUM(total_prescriptions) as total_rx,
                SUM(total_patients) as total_patients
            FROM market_drugs
        )
        SELECT 
            md.drug_concept_id,
            md.drug_name,
            md.total_prescriptions,
            md.total_patients,
            ROUND(md.total_prescriptions * 100.0 / mt.total_rx, 2) as market_share_by_prescriptions,
            ROUND(md.total_patients * 100.0 / mt.total_patients, 2) as market_share_by_patients,
            ROW_NUMBER() OVER (ORDER BY md.total_prescriptions DESC) as rank
        FROM market_drugs md
        CROSS JOIN market_totals mt
        ORDER BY md.total_prescriptions DESC
        LIMIT {request.top_n or 10}
        """
        
        try:
            results = db.execute_query(sql)
            
            drug_shares = [DrugMarketShare(**row) for row in results]
            
            total_market_rx = sum(d.total_prescriptions for d in drug_shares)
            total_market_patients = sum(d.total_patients for d in drug_shares)
            
            # Calculate concentration metrics
            top_3_concentration = sum(d.market_share_by_prescriptions for d in drug_shares[:3])
            top_5_concentration = sum(d.market_share_by_prescriptions for d in drug_shares[:5])
            
            # Herfindahl-Hirschman Index (HHI)
            hhi = sum((d.market_share_by_prescriptions ** 2) for d in drug_shares)
            
            avg_prescriptions = total_market_rx / len(drug_shares) if drug_shares else 0
            
            return MarketShareResponse(
                market_definition=market_definition,
                time_period=time_period,
                total_market_prescriptions=total_market_rx,
                total_market_patients=total_market_patients,
                drug_shares=drug_shares,
                top_3_concentration=round(top_3_concentration, 2),
                top_5_concentration=round(top_5_concentration, 2),
                herfindahl_index=round(hhi, 2),
                total_drugs_in_market=len(drug_shares),
                avg_prescriptions_per_drug=round(avg_prescriptions, 2)
            )
        except Exception as e:
            logger.error(f"Error getting market share analysis: {e}")
            raise
    
    def get_trend_analysis(
        self, 
        drug_concept_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        granularity: str = 'month'
    ) -> TrendAnalysisResponse:
        """
        Get market share trends over time for a specific drug.
        """
        
        # Determine date grouping based on granularity
        if granularity == 'month':
            date_group = "DATE_FORMAT(de.drug_exposure_start_date, 'yyyy-MM')"
        elif granularity == 'quarter':
            date_group = "CONCAT(YEAR(de.drug_exposure_start_date), '-Q', QUARTER(de.drug_exposure_start_date))"
        else:  # year
            date_group = "YEAR(de.drug_exposure_start_date)"
        
        date_filter = ""
        if start_date:
            date_filter += f" AND de.drug_exposure_start_date >= '{start_date}'"
        if end_date:
            date_filter += f" AND de.drug_exposure_start_date <= '{end_date}'"
        
        sql = f"""
        WITH drug_trends AS (
            SELECT 
                {date_group} as time_period,
                COUNT(DISTINCT de.drug_exposure_id) as prescriptions,
                COUNT(DISTINCT de.person_id) as patients
            FROM {self.schema}.drug_exposure de
            WHERE de.drug_concept_id = {drug_concept_id}
            {date_filter}
            GROUP BY {date_group}
        ),
        market_trends AS (
            SELECT 
                {date_group} as time_period,
                COUNT(DISTINCT de.drug_exposure_id) as total_market_rx
            FROM {self.schema}.drug_exposure de
            {date_filter}
            GROUP BY {date_group}
        ),
        combined_trends AS (
            SELECT 
                dt.time_period,
                dt.prescriptions,
                dt.patients,
                ROUND(dt.prescriptions * 100.0 / mt.total_market_rx, 2) as market_share,
                LAG(dt.prescriptions) OVER (ORDER BY dt.time_period) as prev_prescriptions,
                LAG(ROUND(dt.prescriptions * 100.0 / mt.total_market_rx, 2)) OVER (ORDER BY dt.time_period) as prev_share
            FROM drug_trends dt
            INNER JOIN market_trends mt ON dt.time_period = mt.time_period
            ORDER BY dt.time_period
        )
        SELECT 
            time_period,
            prescriptions,
            patients,
            market_share,
            CASE 
                WHEN prev_prescriptions IS NOT NULL 
                THEN ROUND((prescriptions - prev_prescriptions) * 100.0 / prev_prescriptions, 2)
                ELSE NULL 
            END as prescriptions_change_pct,
            CASE 
                WHEN prev_share IS NOT NULL 
                THEN ROUND(market_share - prev_share, 2)
                ELSE NULL 
            END as market_share_change_points
        FROM combined_trends
        ORDER BY time_period
        """
        
        try:
            results = db.execute_query(sql)
            
            # Get drug name
            drug_name_sql = f"SELECT concept_name FROM {self.schema}.concept WHERE concept_id = {drug_concept_id}"
            drug_name_result = db.execute_query(drug_name_sql)
            drug_name = drug_name_result[0]['concept_name'] if drug_name_result else f"Drug {drug_concept_id}"
            
            trends = [
                MarketShareTrend(
                    drug_concept_id=drug_concept_id,
                    drug_name=drug_name,
                    **row
                ) for row in results
            ]
            
            # Calculate overall metrics
            if len(trends) >= 2:
                first_share = trends[0].market_share
                last_share = trends[-1].market_share
                overall_change_pct = round((last_share - first_share) * 100.0 / first_share, 2) if first_share > 0 else 0
                overall_share_change = round(last_share - first_share, 2)
                
                # Determine trend direction
                if overall_share_change > 1:
                    trend_direction = "growing"
                elif overall_share_change < -1:
                    trend_direction = "declining"
                else:
                    trend_direction = "stable"
                
                # Find peak
                peak_trend = max(trends, key=lambda t: t.market_share)
                peak_period = peak_trend.time_period
                peak_market_share = peak_trend.market_share
            else:
                overall_change_pct = 0
                overall_share_change = 0
                trend_direction = "insufficient_data"
                peak_period = None
                peak_market_share = None
            
            return TrendAnalysisResponse(
                drug_concept_id=drug_concept_id,
                drug_name=drug_name,
                trends=trends,
                overall_change_pct=overall_change_pct,
                overall_share_change=overall_share_change,
                trend_direction=trend_direction,
                peak_period=peak_period,
                peak_market_share=peak_market_share
            )
        except Exception as e:
            logger.error(f"Error getting trend analysis: {e}")
            raise
    
    def get_geographic_market_share(
        self,
        drug_concept_ids: List[int],
        geography_type: str = 'state'
    ) -> List[GeographicMarketShare]:
        """
        Get market share by geographic region.
        """
        
        drug_ids_str = ",".join(str(id) for id in drug_concept_ids)
        
        # Determine geography field
        if geography_type == 'state':
            geo_field = "loc.state"
        elif geography_type == 'zip':
            geo_field = "loc.zip"
        else:
            geo_field = "loc.state"  # default
        
        sql = f"""
        WITH drug_by_region AS (
            SELECT 
                {geo_field} as region,
                de.drug_concept_id,
                c.concept_name as drug_name,
                COUNT(DISTINCT de.drug_exposure_id) as prescriptions,
                COUNT(DISTINCT de.person_id) as patients
            FROM {self.schema}.drug_exposure de
            INNER JOIN {self.schema}.concept c ON de.drug_concept_id = c.concept_id
            INNER JOIN {self.schema}.person p ON de.person_id = p.person_id
            LEFT JOIN {self.schema}.location loc ON p.location_id = loc.location_id
            WHERE de.drug_concept_id IN ({drug_ids_str})
            AND {geo_field} IS NOT NULL
            GROUP BY {geo_field}, de.drug_concept_id, c.concept_name
        ),
        region_totals AS (
            SELECT 
                region,
                SUM(prescriptions) as total_rx
            FROM drug_by_region
            GROUP BY region
        )
        SELECT 
            dbr.region,
            '{geography_type}' as region_type,
            dbr.drug_concept_id,
            dbr.drug_name,
            dbr.prescriptions,
            dbr.patients,
            ROUND(dbr.prescriptions * 100.0 / rt.total_rx, 2) as market_share,
            ROW_NUMBER() OVER (PARTITION BY dbr.region ORDER BY dbr.prescriptions DESC) as rank_in_region
        FROM drug_by_region dbr
        INNER JOIN region_totals rt ON dbr.region = rt.region
        ORDER BY dbr.region, dbr.prescriptions DESC
        """
        
        try:
            results = db.execute_query(sql)
            return [GeographicMarketShare(**row) for row in results]
        except Exception as e:
            logger.error(f"Error getting geographic market share: {e}")
            raise
    
    def get_competitive_positioning(
        self,
        your_drug_concept_id: int,
        competitor_drug_concept_ids: List[int],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> CompetitivePositioning:
        """
        Analyze competitive position of your drug vs competitors.
        """
        
        all_drug_ids = [your_drug_concept_id] + competitor_drug_concept_ids
        drug_ids_str = ",".join(str(id) for id in all_drug_ids)
        
        date_filter = ""
        if start_date:
            date_filter += f" AND de.drug_exposure_start_date >= '{start_date}'"
        if end_date:
            date_filter += f" AND de.drug_exposure_start_date <= '{end_date}'"
        
        sql = f"""
        WITH drug_volumes AS (
            SELECT 
                de.drug_concept_id,
                c.concept_name as drug_name,
                COUNT(DISTINCT de.drug_exposure_id) as total_prescriptions,
                COUNT(DISTINCT de.person_id) as total_patients
            FROM {self.schema}.drug_exposure de
            INNER JOIN {self.schema}.concept c ON de.drug_concept_id = c.concept_id
            WHERE de.drug_concept_id IN ({drug_ids_str})
            {date_filter}
            GROUP BY de.drug_concept_id, c.concept_name
        ),
        market_totals AS (
            SELECT 
                SUM(total_prescriptions) as total_rx,
                SUM(total_patients) as total_patients
            FROM drug_volumes
        )
        SELECT 
            dv.drug_concept_id,
            dv.drug_name,
            dv.total_prescriptions,
            dv.total_patients,
            ROUND(dv.total_prescriptions * 100.0 / mt.total_rx, 2) as market_share_by_prescriptions,
            ROUND(dv.total_patients * 100.0 / mt.total_patients, 2) as market_share_by_patients,
            ROW_NUMBER() OVER (ORDER BY dv.total_prescriptions DESC) as rank
        FROM drug_volumes dv
        CROSS JOIN market_totals mt
        ORDER BY dv.total_prescriptions DESC
        """
        
        try:
            results = db.execute_query(sql)
            
            your_drug = None
            competitors = []
            
            for row in results:
                drug_share = DrugMarketShare(**row)
                if row['drug_concept_id'] == your_drug_concept_id:
                    your_drug = drug_share
                else:
                    competitors.append(drug_share)
            
            if not your_drug:
                raise ValueError(f"Your drug (ID: {your_drug_concept_id}) not found in results")
            
            # Calculate competitive metrics
            leader = results[0]  # Top drug by Rx
            share_gap_to_leader = float(leader['market_share_by_prescriptions']) - your_drug.market_share_by_prescriptions
            
            top_3_total = sum(float(r['market_share_by_prescriptions']) for r in results[:3])
            share_of_top_3 = round(your_drug.market_share_by_prescriptions / top_3_total * 100, 2) if top_3_total > 0 else 0
            
            return CompetitivePositioning(
                your_drug_concept_id=your_drug.drug_concept_id,
                your_drug_name=your_drug.drug_name,
                your_prescriptions=your_drug.total_prescriptions,
                your_patients=your_drug.total_patients,
                your_market_share=your_drug.market_share_by_prescriptions,
                your_rank=your_drug.rank,
                competitors=competitors,
                share_gap_to_leader=round(share_gap_to_leader, 2),
                share_of_top_3=share_of_top_3 if your_drug.rank <= 3 else None
            )
        except Exception as e:
            logger.error(f"Error getting competitive positioning: {e}")
            raise
    
    def get_new_to_brand_analysis(
        self,
        drug_concept_id: int,
        start_date: str,
        end_date: str,
        lookback_days: int = 365
    ) -> NewToBrandAnalysis:
        """
        Analyze new-to-brand (NBx) patients.
        
        Identifies patients who started the drug in the time period
        and determines if they were treatment-naive or switched from competitors.
        """
        
        # Calculate lookback date
        from datetime import datetime, timedelta
        lookback_date = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
        
        sql = f"""
        WITH current_patients AS (
            -- Patients on drug in analysis period
            SELECT DISTINCT person_id
            FROM {self.schema}.drug_exposure
            WHERE drug_concept_id = {drug_concept_id}
            AND drug_exposure_start_date BETWEEN '{start_date}' AND '{end_date}'
        ),
        first_exposure AS (
            -- Find first exposure to drug for each patient
            SELECT 
                de.person_id,
                MIN(de.drug_exposure_start_date) as first_date
            FROM {self.schema}.drug_exposure de
            WHERE de.drug_concept_id = {drug_concept_id}
            GROUP BY de.person_id
        ),
        new_patients AS (
            -- New patients = first exposure in analysis period
            SELECT fe.person_id
            FROM first_exposure fe
            WHERE fe.first_date BETWEEN '{start_date}' AND '{end_date}'
        ),
        prior_exposures AS (
            -- Check for any drug exposure before start date
            SELECT DISTINCT 
                de.person_id,
                de.drug_concept_id
            FROM {self.schema}.drug_exposure de
            INNER JOIN new_patients np ON de.person_id = np.person_id
            WHERE de.drug_exposure_start_date < '{start_date}'
            AND de.drug_exposure_start_date >= '{lookback_date}'
            AND de.drug_concept_id != {drug_concept_id}
        )
        SELECT 
            (SELECT COUNT(*) FROM new_patients) as new_patients,
            (SELECT COUNT(*) FROM current_patients) as total_patients,
            (SELECT COUNT(DISTINCT person_id) FROM new_patients np 
             WHERE NOT EXISTS (SELECT 1 FROM prior_exposures pe WHERE pe.person_id = np.person_id)) as treatment_naive,
            (SELECT COUNT(DISTINCT person_id) FROM new_patients np 
             WHERE EXISTS (SELECT 1 FROM prior_exposures pe WHERE pe.person_id = np.person_id)) as switched_from_competitor
        """
        
        # Get switch sources
        switch_sources_sql = f"""
        WITH new_patients AS (
            SELECT 
                de.person_id,
                MIN(de.drug_exposure_start_date) as first_date
            FROM {self.schema}.drug_exposure de
            WHERE de.drug_concept_id = {drug_concept_id}
            GROUP BY de.person_id
            HAVING MIN(de.drug_exposure_start_date) BETWEEN '{start_date}' AND '{end_date}'
        ),
        prior_drugs AS (
            SELECT 
                de.person_id,
                de.drug_concept_id,
                c.concept_name as drug_name,
                MAX(de.drug_exposure_start_date) as last_exposure_date
            FROM {self.schema}.drug_exposure de
            INNER JOIN {self.schema}.concept c ON de.drug_concept_id = c.concept_id
            INNER JOIN new_patients np ON de.person_id = np.person_id
            WHERE de.drug_exposure_start_date < '{start_date}'
            AND de.drug_exposure_start_date >= '{lookback_date}'
            AND de.drug_concept_id != {drug_concept_id}
            GROUP BY de.person_id, de.drug_concept_id, c.concept_name
        )
        SELECT 
            drug_concept_id,
            drug_name,
            COUNT(DISTINCT person_id) as patient_count
        FROM prior_drugs
        GROUP BY drug_concept_id, drug_name
        ORDER BY patient_count DESC
        LIMIT 10
        """
        
        try:
            results = db.execute_query(sql)
            switch_sources_results = db.execute_query(switch_sources_sql)
            
            # Get drug name
            drug_name_sql = f"SELECT concept_name FROM {self.schema}.concept WHERE concept_id = {drug_concept_id}"
            drug_name_result = db.execute_query(drug_name_sql)
            drug_name = drug_name_result[0]['concept_name'] if drug_name_result else f"Drug {drug_concept_id}"
            
            data = results[0] if results else {}
            new_patients = data.get('new_patients', 0)
            total_patients = data.get('total_patients', 0)
            nbx_rate = round(new_patients / total_patients * 100, 2) if total_patients > 0 else 0
            
            switch_sources = [dict(row) for row in switch_sources_results]
            
            return NewToBrandAnalysis(
                drug_concept_id=drug_concept_id,
                drug_name=drug_name,
                time_period=f"{start_date} to {end_date}",
                new_patients=new_patients,
                total_patients=total_patients,
                nbx_rate=nbx_rate,
                treatment_naive=data.get('treatment_naive', 0),
                switched_from_competitor=data.get('switched_from_competitor', 0),
                switch_sources=switch_sources
            )
        except Exception as e:
            logger.error(f"Error getting new-to-brand analysis: {e}")
            raise
    
    def _build_market_filter(self, request: MarketShareRequest) -> str:
        """Build WHERE clause to define the market."""
        conditions = []
        
        if request.drug_concept_ids:
            drug_ids_str = ",".join(str(id) for id in request.drug_concept_ids)
            conditions.append(f"de.drug_concept_id IN ({drug_ids_str})")
        
        if request.condition_concept_ids:
            condition_ids_str = ",".join(str(id) for id in request.condition_concept_ids)
            conditions.append(f"""
                de.person_id IN (
                    SELECT person_id 
                    FROM {self.schema}.condition_occurrence 
                    WHERE condition_concept_id IN ({condition_ids_str})
                )
            """)
        
        if conditions:
            return "WHERE " + " AND ".join(conditions)
        return ""
    
    def _build_date_filter(self, request: MarketShareRequest) -> str:
        """Build date filter clause."""
        conditions = []
        
        if request.start_date:
            conditions.append(f"de.drug_exposure_start_date >= '{request.start_date}'")
        
        if request.end_date:
            conditions.append(f"de.drug_exposure_start_date <= '{request.end_date}'")
        
        if conditions:
            return "AND " + " AND ".join(conditions)
        return ""
    
    def _describe_market(self, request: MarketShareRequest) -> str:
        """Generate human-readable market definition."""
        parts = []
        
        if request.therapeutic_area:
            parts.append(f"{request.therapeutic_area} market")
        elif request.condition_concept_ids:
            parts.append(f"Condition-defined market (IDs: {', '.join(str(id) for id in request.condition_concept_ids)})")
        elif request.drug_concept_ids:
            parts.append(f"Specified drugs (IDs: {', '.join(str(id) for id in request.drug_concept_ids)})")
        else:
            parts.append("Total drug market")
        
        return " - ".join(parts) if parts else "Market analysis"


# Global instance
market_share_service = MarketShareService()

