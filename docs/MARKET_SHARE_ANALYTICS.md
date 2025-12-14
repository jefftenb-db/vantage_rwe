# Market Share Analytics Feature - Vantage RWE

**Commercial Intelligence from Real-World Evidence**

## Overview

The Market Share Analytics module in Vantage RWE provides comprehensive competitive intelligence and market dynamics analysis for pharmaceutical commercial teams. Track market position, analyze trends, understand competitive landscape, and identify growth opportunities.

## 🎯 Key Capabilities

### 1. **Market Share Overview** 
Comprehensive market analysis including:
- Market share by drug (prescriptions & patients)
- Market concentration metrics (HHI, top 3/5 share)
- Rank ordering by volume
- Visual share distribution

**Use Case**: "What's the market share distribution for diabetes drugs?"

### 2. **Trend Analysis** 📈
Historical market share tracking:
- Time-series analysis (monthly/quarterly/yearly)
- Growth rates and share point changes
- Peak period identification
- Trend direction (growing/declining/stable)

**Use Case**: "How has our market share changed over the past year?"

### 3. **Competitive Positioning** 🎯
Head-to-head competitive analysis:
- Your position vs. competitors
- Share gap to market leader
- Relative ranking
- Visual competitive landscape

**Use Case**: "Where do we stand vs. our top 3 competitors?"

### 4. **New-to-Brand (NBx) Analysis** 🔄
Patient acquisition insights:
- New patient counts (NBx)
- NBx rate calculation
- Treatment-naive vs. switchers
- Source of switchers (which competitor drugs)

**Use Case**: "Are we gaining patients from competitors or treating new patients?"

## 📊 Backend API Endpoints

### POST `/market-share/analysis`
Get comprehensive market share analysis
```json
{
  "drug_concept_ids": [1503297, 1545999, 1594973],
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "top_n": 10
}
```

**Returns**: Market shares, concentration metrics, drug rankings

### GET `/market-share/trends/{drug_concept_id}`
Get time-series trend analysis
- Parameters: `start_date`, `end_date`, `granularity` (month/quarter/year)
- Returns: Historical market share with period-over-period changes

### GET `/market-share/competitive/{your_drug_id}`
Analyze competitive position
- Parameters: `competitor_ids` (comma-separated), date range
- Returns: Your position, competitors' shares, gap to leader

### POST `/market-share/geographic`
Geographic market share breakdown
- Parameters: `drug_concept_ids`, `geography_type` (state/zip/region)
- Returns: Market share by geographic region

### GET `/market-share/new-to-brand/{drug_concept_id}`
NBx analysis with switch tracking
- Parameters: `start_date`, `end_date`, `lookback_days`
- Returns: New patients, source analysis, switch patterns

## 🖥️ Frontend UI

Access via the **"📈 Market Share"** tab in the main application.

### Four Interactive Tabs:

1. **📊 Overview** - Market distribution and concentration
2. **📈 Trends** - Historical share changes
3. **🎯 Competitive** - Your position vs. competitors
4. **🔄 NBx** - New patient acquisition

## 💼 Commercial Use Cases

### For Brand Teams:
- **Performance Tracking**: Are we gaining or losing share?
- **Competitive Intelligence**: How do we compare to competitors?
- **Forecasting**: What's our trajectory?

### For Sales Leadership:
- **Territory Analysis**: Where are we strong/weak?
- **Goal Setting**: What share can we realistically achieve?
- **Resource Allocation**: Focus on high-opportunity markets

### For Marketing:
- **Campaign Effectiveness**: Did our campaign move share?
- **Market Dynamics**: Is the market growing or consolidating?
- **Positioning**: Are we a leader, challenger, or niche player?

### For Finance:
- **Revenue Forecasting**: Market size × our share = revenue
- **Budget Impact**: What if we gain/lose 1% share?
- **ROI Analysis**: Investment vs. share gains

## 📈 Key Metrics Explained

### Herfindahl-Hirschman Index (HHI)
- **Scale**: 0-10,000
- **Interpretation**:
  - < 1,500: Competitive market
  - 1,500-2,500: Moderately concentrated
  - > 2,500: Highly concentrated
- **Example**: HHI of 3,200 means the market is dominated by a few large players

### Top 3/Top 5 Concentration
- **Definition**: % of total market held by top 3 or 5 drugs
- **Interpretation**:
  - < 50%: Fragmented market
  - 50-75%: Moderate concentration
  - > 75%: Highly concentrated
- **Example**: Top 3 concentration of 68% means three drugs control 2/3 of market

### NBx Rate
- **Definition**: New patients / Total patients × 100
- **Interpretation**:
  - High NBx rate: Strong patient acquisition
  - Low NBx rate: Mature product, focus on retention
- **Example**: NBx rate of 15% means 15% of patients are new this period

### Share Gap to Leader
- **Definition**: Leader's share - Your share (in percentage points)
- **Interpretation**:
  - 0: You're the leader!
  - < 5 pts: Close second, realistic to challenge
  - > 20 pts: Significant gap, long-term strategy needed

## 🗄️ OMOP Tables Used

- **DRUG_EXPOSURE** - Prescription records
- **PERSON** - Patient demographics
- **LOCATION** - Geographic data
- **CONCEPT** - Drug names and classifications

## 📈 Example Queries

### Analyze Diabetes Market
```
Tab: Overview
Drug Concept IDs: 1503297, 1545999, 1594973 (Metformin, Insulin, Glipizide)
→ Shows market share, rankings, concentration metrics
```

### Track Lipitor Trends
```
Tab: Trends
Search: Lipitor
Select drug
Granularity: Monthly
→ Shows how Lipitor's share changed month-by-month
```

### Compare Your Drug to Competitors
```
Tab: Competitive
Your Drug ID: 1503297
Competitor IDs: 1545999, 1594973, 1559684
→ Shows your position, gap to leader, visual comparison
```

### Analyze New Patients
```
Tab: NBx
Drug ID: 1503297
Period: 2023-Q4
→ Shows new patient counts, treatment-naive vs. switchers
```

## 🔧 Technical Details

### Backend Service (`market_share_service.py`)
- Complex SQL with window functions (PERCENT_RANK, ROW_NUMBER)
- Market concentration calculations (HHI)
- Time-series analysis with LAG/LEAD
- Treatment sequence tracking

### Data Models (`market_share.py`)
- **DrugMarketShare** - Share by drug
- **MarketShareTrend** - Time-series data
- **CompetitivePositioning** - Competitive analysis
- **NewToBrandAnalysis** - Patient acquisition
- **MarketShareResponse** - Comprehensive results

### Frontend Component (`MarketShareAnalytics.tsx`)
- Tab-based navigation
- Interactive drug selection
- Real-time date filtering
- Visual share bars and rankings

## 🚀 Getting Started

1. **Start Backend**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Navigate to Market Share tab**

4. **Try Overview tab first** - Enter some drug concept IDs to see market distribution

## 🔄 Rollback Instructions

This feature is on a separate branch for easy rollback:

```bash
# To rollback to version WITHOUT market share
git checkout feature/prescriber-analytics  # or main

# To return to market share feature
git checkout feature/market-share-analysis
```

**Branch hierarchy**:
- `main` - Original code
- `feature/prescriber-analytics` - Prescriber analytics only
- `feature/market-share-analysis` - Prescriber + Market Share

## 📝 Commercial Best Practices

### Setting Market Boundaries
- **Narrow definition**: Only your drug + direct competitors
  - Pros: Precise competitive analysis
  - Cons: Misses broader market dynamics
  
- **Broad definition**: Entire therapeutic area
  - Pros: Full market context
  - Cons: Includes non-competitive products

**Recommendation**: Define multiple markets (narrow, medium, broad)

### Time Periods to Analyze
- **Monthly**: For fast-moving markets, recent launches
- **Quarterly**: Standard for most brand reporting
- **Yearly**: Strategic planning, long-term trends

### NBx Analysis Tips
- **Lookback period**: 12 months (365 days) is standard
- **Shorter lookback** (90 days): Recent competitive activity
- **Longer lookback** (24 months): Chronic conditions

### Competitive Set Selection
Include:
1. **Direct competitors**: Same mechanism of action
2. **Indirect competitors**: Different drugs, same indication
3. **Aspirational competitors**: Where you want to be

## 📊 Reporting Templates

### Monthly Business Review
- Overall market size (total Rx)
- Your market share (current vs. prior month)
- Share change (points and %)
- Rank vs. competitors
- NBx rate

### Quarterly Board Report
- Market share trend (quarterly for past 4-8 quarters)
- Competitive positioning
- Market concentration
- Growth drivers (NBx vs. retention)

### Annual Strategic Planning
- 3-year market share trends
- Peak share achieved
- Competitive landscape evolution
- Growth opportunities by segment

## 🐛 Troubleshooting

### No results or low data volumes
- Check date ranges match your data
- Verify drug_concept_ids are in your database
- Some synthetic datasets have limited historical data

### Market share doesn't sum to 100%
- This is correct if you're analyzing a subset of the market
- `top_n` parameter limits returned drugs
- Use broader drug list to see full market

### NBx analysis shows 0 new patients
- Check date range is appropriate
- Ensure drug has prescriptions in the period
- Verify lookback period captures prior therapy

### Trends show flat line
- May indicate insufficient data variation
- Try different time granularity (month vs. quarter)
- Expand date range to see longer-term patterns

## 📚 Additional Resources

- [Herfindahl-Hirschman Index (FTC)](https://www.ftc.gov/enforcement/merger-review/herfindahl-hirschman-index)
- [OMOP DRUG_EXPOSURE Table](https://ohdsi.github.io/CommonDataModel/cdm54.html#DRUG_EXPOSURE)
- [Market Share Analysis Best Practices](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights)

## 🔮 Future Enhancements

Potential additions:
- **Share of voice trending** - Track over time
- **Patient flow diagrams** - Sankey charts for switches
- **Predictive analytics** - Forecast future share
- **Segment analysis** - Share by payer, age group, etc.
- **Export to PowerBI** - Integration with BI tools
- **Automated alerts** - Notify on share changes
- **Cohort-based share** - Share within specific patient populations

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review API docs at `http://localhost:8000/docs`
3. Verify data quality in your OMOP database

---

**Built for pharmaceutical commercial teams to drive data-informed market strategy** 📈

