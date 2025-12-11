# Example Cohort Definitions

This document provides example cohort definitions you can use as templates or for testing Vantage RWE.

## Basic Cohorts

### 1. Diabetes Patients

**Description**: All patients with Type 2 Diabetes diagnosis

**Inclusion Criteria**:
- Condition: Type 2 Diabetes Mellitus
  - Concept IDs: 201826, 443238
  - Min Occurrences: 1

**Expected Result**: ~5-10% of total patients (varies by dataset)

---

### 2. Patients on Metformin

**Description**: Patients who have been prescribed Metformin

**Inclusion Criteria**:
- Drug: Metformin
  - Concept IDs: 1503297
  - Min Occurrences: 1

---

### 3. Emergency Room Visits

**Description**: Patients who have visited the emergency room

**Inclusion Criteria**:
- Visit: Emergency Room Visit
  - Concept IDs: 9203
  - Min Occurrences: 1

---

## Intermediate Cohorts

### 4. Diabetes on Metformin

**Description**: Type 2 Diabetes patients treated with Metformin

**Inclusion Criteria**:
1. Condition: Type 2 Diabetes Mellitus
   - Concept IDs: 201826, 443238
   - Min Occurrences: 1

2. Drug: Metformin
   - Concept IDs: 1503297
   - Min Occurrences: 1

**Expected Result**: ~60-70% of diabetes patients

---

### 5. Hypertension without Diabetes

**Description**: Patients with hypertension who don't have diabetes

**Inclusion Criteria**:
- Condition: Essential Hypertension
  - Concept IDs: 320128
  - Min Occurrences: 1

**Exclusion Criteria**:
- Condition: Diabetes Mellitus
  - Concept IDs: 201826, 443238, 201254
  - Min Occurrences: 1

---

### 6. Recent Hospital Admissions

**Description**: Patients admitted to hospital in the last year

**Inclusion Criteria**:
- Visit: Inpatient Visit
  - Concept IDs: 9201
  - Start Date: 2023-01-01 (adjust to current year - 1)
  - End Date: 2023-12-31 (adjust to current year)

---

## Advanced Cohorts

### 7. Diabetes with Complications

**Description**: Type 2 Diabetes patients with cardiovascular complications

**Inclusion Criteria**:
1. Condition: Type 2 Diabetes Mellitus
   - Concept IDs: 201826, 443238

2. Condition: One of:
   - Myocardial Infarction (4329847)
   - Heart Failure (316139)
   - Stroke (443454)
   - Min Occurrences: 1

---

### 8. COPD Treatment Escalation

**Description**: COPD patients who progressed from single to dual therapy

**Inclusion Criteria**:
1. Condition: COPD
   - Concept IDs: 255573

2. Drug: Short-acting Beta Agonist
   - Concept IDs: 1154343 (Albuterol)
   - Min Occurrences: 2

3. Drug: Long-acting Muscarinic Antagonist
   - Concept IDs: 1236607 (Tiotropium)
   - Start Date: At least 90 days after first SABA

---

### 9. Newly Diagnosed Diabetes (Incident Cases)

**Description**: Patients newly diagnosed with diabetes in 2023

**Inclusion Criteria**:
1. Condition: Type 2 Diabetes Mellitus
   - Concept IDs: 201826, 443238
   - Start Date: 2023-01-01
   - End Date: 2023-12-31
   - Min Occurrences: 1

**Exclusion Criteria**:
1. Condition: Type 2 Diabetes Mellitus
   - Concept IDs: 201826, 443238
   - End Date: 2022-12-31
   - (Had diabetes before 2023)

---

### 10. High-Risk Cardiac Patients

**Description**: Patients with multiple cardiac risk factors

**Inclusion Criteria**:
1. Condition: Hypertension
   - Concept IDs: 320128

2. Condition: Hyperlipidemia
   - Concept IDs: 432867

3. Age: Greater than 65 years

4. Condition: Current or former smoker
   - (Use observation table for smoking status)

**Exclusion Criteria**:
1. Procedure: Coronary Artery Bypass Graft
   - Concept IDs: 4336464
   - (Already had bypass)

---

## Clinical Trial Simulation Cohorts

### 11. Heart Failure Trial Eligibility

**Description**: Simulating eligibility criteria for a heart failure clinical trial

**Inclusion Criteria**:
1. Condition: Heart Failure
   - Concept IDs: 316139
   - Min Occurrences: 2 (confirmed diagnosis)

2. Age: Between 18 and 80 years

3. Visit: At least 1 outpatient visit in last 6 months

**Exclusion Criteria**:
1. Condition: Severe Kidney Disease
   - Concept IDs: 46271022

2. Condition: Active Cancer
   - Domain: Condition
   - Search: "malignant neoplasm"

3. Procedure: Cardiac Transplant
   - Concept IDs: 4214956

---

### 12. Diabetes Prevention Study

**Description**: Pre-diabetic patients for prevention trial

**Inclusion Criteria**:
1. Observation: HbA1c between 5.7% and 6.4%
   - Concept IDs: 4184637 (HbA1c)
   - Value Min: 5.7
   - Value Max: 6.4

2. Observation: BMI > 25
   - Concept IDs: 3038553 (BMI)
   - Value Min: 25

3. Age: 40-70 years

**Exclusion Criteria**:
1. Condition: Diabetes (any type)
   - Concept IDs: 201826, 443238, 201254

2. Drug: Any diabetes medication
   - Domain: Drug
   - Search: "insulin" OR "metformin"

---

## GenAI Query Examples

These natural language queries work with the GenAI feature:

### Simple Queries
```
"Show me patients with diabetes"
"Find patients prescribed metformin"
"Patients who had bypass surgery"
"Type 2 diabetes patients"
```

### Complex Queries
```
"Show me patients with Type 2 Diabetes who were prescribed Metformin and had at least one ER visit"

"Find hypertension patients on ACE inhibitors who don't have heart failure"

"Patients with COPD who have been prescribed antibiotics and steroids in the last year"

"Diabetes patients over 65 who had a stroke"
```

### Clinical Questions
```
"What's the prevalence of diabetes in patients with hypertension?"

"Show me patients on dual antiplatelet therapy"

"Find patients with asthma exacerbations requiring hospitalization"

"Patients with depression and anxiety comorbidity"
```

---

## Testing Your Cohorts

### Validation Checklist

✅ **Concept IDs are valid**
- Search for concepts in the UI first
- Verify IDs match your vocabulary version

✅ **Date ranges are appropriate**
- Use dates that exist in your dataset
- Consider data refresh frequency

✅ **Occurrence counts make sense**
- Min occurrences = 1 for any diagnosis
- Min occurrences > 1 for confirmed/chronic conditions

✅ **Exclusion criteria are logical**
- Don't exclude conditions required in inclusion
- Consider temporal relationships

### Common Patterns

**Pattern 1: Primary Condition + Treatment**
```
Inclusion: [Condition] + [Drug for that condition]
Result: Treated patients
```

**Pattern 2: Condition Without Complication**
```
Inclusion: [Primary Condition]
Exclusion: [Complication]
Result: Uncomplicated cases
```

**Pattern 3: Multi-Morbidity**
```
Inclusion: [Condition 1] + [Condition 2] + [Condition 3]
Result: Patients with multiple conditions
```

**Pattern 4: Incident Cases**
```
Inclusion: [Condition with recent date range]
Exclusion: [Same condition with earlier date range]
Result: Newly diagnosed patients
```

---

## Tips for Creating Cohorts

1. **Start Simple**: Begin with one condition, then add criteria

2. **Use Standard Concepts**: Prefer standard concepts (standard_concept = 'S')

3. **Consider Hierarchies**: OMOP concepts have parent-child relationships

4. **Test Incrementally**: Build cohort, check count, add criteria, repeat

5. **Document Your Logic**: Use clear cohort names and descriptions

6. **Validate Results**: Sample patient IDs and verify they meet criteria

7. **Consider Temporal Logic**: When did events occur relative to each other?

8. **Account for Data Quality**: Missing data, coding variations, etc.

---

## Dataset-Specific Notes

### For Synthetic Data (Synthea)
- Expect lower prevalence rates
- Limited historical data depth
- Consistent coding (easier to query)

### For Real EHR Data
- Account for coding variability
- Consider data completeness
- Validate concept mappings
- Check vocabulary versions

### For Claims Data
- Focus on billed diagnoses
- Procedures well-documented
- May lack clinical details
- Consider claim timing

---

## Need Help?

- **No results?** Check concept IDs are in your vocabulary
- **Too many results?** Add more specific criteria or date ranges
- **Unexpected results?** Review sample patient records manually
- **Slow performance?** Consider date ranges to limit data scanned

