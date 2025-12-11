# OMOP Cohort Builder

An interactive application for creating patient cohorts from healthcare data stored in OHDSI OMOP Common Data Model (CDM) format within Databricks.

## Features

- 🏥 **OMOP CDM Integration**: Work with standardized healthcare data
- 🔍 **Interactive Cohort Building**: Define patient populations based on:
  - Medical conditions (CONDITION_OCCURRENCE)
  - Drug exposures (DRUG_EXPOSURE)
  - Procedures (PROCEDURE_OCCURRENCE)
  - Visits (VISIT_OCCURRENCE)
  - Observations (OBSERVATION)
- 🤖 **GenAI Natural Language Queries**: Use Databricks AI to query data with natural language
- 📊 **Real-time Results**: See cohort counts and demographics instantly
- 💾 **Save & Export**: Save cohort definitions and export patient lists

## Architecture

```
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Pydantic models
│   │   ├── services/    # Business logic
│   │   └── db/          # Database connections
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API clients
│   │   └── App.tsx
│   └── package.json
└── config/              # Configuration files
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- Databricks workspace with OMOP CDM data
- Databricks SQL Warehouse or Cluster

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Databricks credentials
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-access-token
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/xxxxx
OMOP_CATALOG=hive_metastore
OMOP_SCHEMA=omop_cdm
```

## Usage

1. **Start with a base population**: Define initial criteria (e.g., all patients with diabetes)
2. **Add inclusion criteria**: Filter by drug exposures, procedures, or visits
3. **Add exclusion criteria**: Remove patients based on conditions
4. **Use GenAI**: Ask questions like "Show me patients with Type 2 Diabetes who were prescribed Metformin"
5. **Review results**: See patient counts and demographics
6. **Export**: Download patient IDs or save cohort definition

## OMOP CDM Tables Used

- **PERSON**: Demographics and basic patient info
- **CONDITION_OCCURRENCE**: Diagnoses and medical conditions
- **DRUG_EXPOSURE**: Medication prescriptions and administrations
- **PROCEDURE_OCCURRENCE**: Medical procedures performed
- **VISIT_OCCURRENCE**: Healthcare visits (inpatient, outpatient, ER)
- **OBSERVATION**: Lab results and clinical observations
- **CONCEPT**: Standardized medical vocabularies

## Development

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Frontend: http://localhost:3000

## License

MIT

