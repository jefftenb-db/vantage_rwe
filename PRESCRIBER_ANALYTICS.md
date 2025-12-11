# Prescriber Analytics Feature

## Overview

The Prescriber Analytics module provides commercial intelligence capabilities for pharmaceutical companies to analyze healthcare provider (HCP) prescribing patterns, identify targeting opportunities, and understand treatment pathways.

## 🎯 Key Capabilities

### 1. **Prescriber Search**
Find and rank prescribers based on:
- Specialty (e.g., Cardiology, Oncology)
- Patient volume
- Prescription volume
- Percentile and decile rankings

**Use Case**: "Show me all cardiologists with at least 50 patients"

### 2. **Drug Prescriber Analytics**
Comprehensive analytics for any drug including:
- Top prescribers by volume
- Market share distribution
- Concentration metrics (top 10%, top 20% share)
- Total unique prescribers and patients

**Use Case**: "Who are the top 50 prescribers of Metformin?"

### 3. **Prescriber Targeting** 🚀
**The "money feature"** - Identifies high-value targets:
- Prescribers treating relevant patient populations
- Currently prescribing competitor drugs
- Low/no adoption of your target drug
- Prioritized by opportunity score
- Segmented into High/Medium/Low priority

**Use Case**: "Find cardiologists prescribing competitor statins but not ours"

### 4. **Treatment Pathways**
Understand prescriber behavior:
- First-line drug preferences
- Drug switching patterns (Drug A → Drug B)
- Treatment sequences

**Use Case**: "What does Dr. Smith prescribe first for diabetes? When does she switch drugs?"

## 📊 Backend API Endpoints

### GET `/prescribers/{provider_id}`
Get detailed prescriber profile

### POST `/prescribers/search`
Search prescribers with filters
```json
{
  "specialty": "Cardiology",
  "min_patients": 10,
  "drug_concept_id": 1503297,
  "limit": 50
}
```

### GET `/prescribers/drug/{drug_concept_id}/analytics`
Get drug prescriber analytics with market concentration

### POST `/prescribers/targeting`
Identify target prescribers for outreach
```json
{
  "target_drug_concept_ids": [1503297],
  "competitor_drug_concept_ids": [1545999, 1594973],
  "condition_concept_ids": [201826],
  "min_relevant_patients": 10,
  "specialty": "Endocrinology",
  "limit": 100
}
```

### GET `/prescribers/{provider_id}/treatment-pathways`
Get treatment pathways for specific prescriber

### POST `/prescribers/compare`
Compare multiple prescribers side-by-side

## 🖥️ Frontend UI

Access via the **"👨‍⚕️ Prescriber Analytics"** tab in the main application.

### Four Interactive Tabs:

1. **🔍 Search** - Find prescribers by criteria
2. **📊 Drug Analytics** - Market share and top prescribers
3. **🎯 Targeting** - Identify outreach opportunities
4. **📈 Pathways** - Treatment sequences

## 💼 Commercial Use Cases

### For Sales Teams:
- **Territory Planning**: Who are the high-volume prescribers in my territory?
- **Target Lists**: Which doctors should I prioritize for visits?
- **Opportunity Sizing**: How many potential Rx could I gain?

### For Marketing:
- **Key Opinion Leaders**: Who are the top prescribers to engage?
- **Market Share**: How concentrated is prescribing?
- **Competitive Intelligence**: Where are we losing to competitors?

### For Medical Affairs:
- **Prescribing Patterns**: How do HCPs choose therapies?
- **Treatment Algorithms**: What do prescribers use first-line?
- **Switch Behavior**: Why and when do prescribers change drugs?

## 🗄️ OMOP Tables Used

- **PROVIDER** - Prescriber profiles and specialties
- **DRUG_EXPOSURE** - Prescription records
- **CONDITION_OCCURRENCE** - Patient diagnoses (for targeting)
- **VISIT_OCCURRENCE** - Healthcare visits
- **CARE_SITE** - Practice locations
- **LOCATION** - Geographic data

## 📈 Example Queries

### Find Top Oncologists
```
Tab: Search
Specialty: Oncology
Min Patients: 25
→ Returns ranked list with volume metrics
```

### Analyze Lipitor Prescribing
```
Tab: Drug Analytics
Search: Lipitor
Select: Lipitor (concept_id)
→ Shows top prescribers, market concentration
```

### Target Diabetes Prescribers
```
Tab: Targeting
Target Drug IDs: 1503297 (Metformin)
Competitor Drug IDs: 1545999 (Insulin)
→ Returns prioritized targets with opportunity scores
```

### Dr. Smith's Treatment Preferences
```
Tab: Pathways
Provider ID: 12345
→ Shows first-line drugs and switch patterns
```

## 🔧 Technical Details

### Backend Service (`prescriber_service.py`)
- Efficient SQL queries with CTEs
- Window functions for ranking (PERCENT_RANK, NTILE)
- Market concentration calculations
- Geographic filtering support

### Data Models (`prescriber.py`)
- **PrescriberMetrics** - Volume and ranking
- **DrugPrescriberAnalytics** - Comprehensive drug analytics
- **TargetPrescriber** - Targeting with scoring
- **TreatmentPathway** - Sequential patterns

### Frontend Component (`PrescriberAnalytics.tsx`)
- Tab-based navigation
- Real-time search and filtering
- Interactive data tables
- Visual priority indicators

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

3. **Navigate to Prescriber Analytics tab**

4. **Start with Search tab** to explore prescribers in your dataset

## 🔄 Rollback Instructions

If you need to revert to the previous version:

```bash
# Switch back to main branch
git checkout main

# The feature is isolated in the feature/prescriber-analytics branch
# Your original code remains intact on main
```

To re-enable the feature later:
```bash
git checkout feature/prescriber-analytics
```

To merge the feature permanently:
```bash
git checkout main
git merge feature/prescriber-analytics
```

## 📝 Future Enhancements

Potential additions:
- **Geographic heatmaps** - Visualize prescriber concentration
- **Trend analysis** - Prescribing over time
- **Peer comparison** - Benchmark against specialty averages
- **Export to Excel** - Download target lists
- **Save targeting profiles** - Reuse common searches
- **Email alerts** - Notify on prescriber changes

## 🐛 Troubleshooting

### No results returned
- Check that your OMOP database has the PROVIDER table populated
- Verify provider_id is linked in DRUG_EXPOSURE records
- Some synthetic datasets may have limited provider data

### Slow queries
- Add indexes on: `provider_id`, `drug_concept_id`, `condition_concept_id`
- Consider date filters to limit data scanned
- Use Databricks query optimization (OPTIMIZE, Z-ORDER)

### Missing specialties
- OMOP PROVIDER table may use different specialty coding
- Check `specialty_source_value` vs `specialty_concept_id`
- Map to your organization's specialty taxonomy

## 📚 Additional Resources

- [OMOP PROVIDER Table Documentation](https://ohdsi.github.io/CommonDataModel/cdm54.html#PROVIDER)
- [Prescriber NPI Lookup](https://npiregistry.cms.hhs.gov/)
- [Project SETUP_GUIDE.md](./SETUP_GUIDE.md)

## 🤝 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review OMOP data quality in your database
3. Consult the API docs at `http://localhost:8000/docs`

---

**Built for pharmaceutical commercial teams to drive data-informed decisions** 🎯

