# Vantage RWE - Architecture

**Commercial Intelligence from Real-World Evidence**

## System Overview

The OMOP Cohort Builder is a full-stack application for creating patient cohorts from healthcare data stored in the OHDSI OMOP Common Data Model (CDM) format within Databricks.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Cohort    │  │   GenAI      │  │   Database       │  │
│  │   Builder   │  │   Search     │  │   Stats          │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
┌────────────────────────┴────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    API Layer                            │ │
│  │  /concepts/search  /cohorts/build  /genai/query       │ │
│  └──────────────┬─────────────────────────────────────────┘ │
│                 │                                             │
│  ┌──────────────┴──────────────┬──────────────────────────┐ │
│  │     Service Layer            │                          │ │
│  │  ┌────────────┐  ┌──────────┴──────┐  ┌─────────────┐ │ │
│  │  │   OMOP     │  │    Cohort       │  │   GenAI     │ │ │
│  │  │  Service   │  │    Builder      │  │  Service    │ │ │
│  │  └────────────┘  └─────────────────┘  └─────────────┘ │ │
│  └────────────────────────┬────────────────────────────────┘ │
└───────────────────────────┴──────────────────────────────────┘
                            │
┌───────────────────────────┴──────────────────────────────────┐
│              Databricks SQL Connector                         │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────┴──────────────────────────────────┐
│                    Databricks Platform                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  SQL Warehouse / Cluster                │  │
│  └──────────────────────────┬─────────────────────────────┘  │
│                             │                                 │
│  ┌──────────────────────────┴─────────────────────────────┐  │
│  │                   OMOP CDM Tables                       │  │
│  │  person, condition_occurrence, drug_exposure,          │  │
│  │  procedure_occurrence, visit_occurrence, concept       │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (React + TypeScript)

**Technology Stack:**
- React 18.2
- TypeScript
- Axios for API calls
- CSS Modules for styling

**Key Components:**

1. **CohortBuilder**: Main interface for building cohorts
   - Manages cohort definition state
   - Coordinates inclusion/exclusion criteria
   - Triggers cohort execution

2. **CriteriaBuilder**: Individual criteria editor
   - Concept search functionality
   - Date range and occurrence filters
   - Supports multiple criteria types

3. **NaturalLanguageSearch**: GenAI query interface
   - Natural language input
   - Query parsing and visualization
   - Results display

4. **CohortResults**: Results visualization
   - Patient counts
   - Demographics breakdown
   - Sample patient IDs
   - Export functionality

5. **DatabaseStats**: Dashboard statistics
   - Total patients
   - Unique conditions, drugs, procedures
   - Real-time updates

### Backend (FastAPI + Python)

**Technology Stack:**
- FastAPI 0.109
- Pydantic for data validation
- Databricks SQL Connector
- Python 3.9+

**API Endpoints:**

```
GET  /api/v1/health                    - Health check
POST /api/v1/concepts/search           - Search OMOP concepts
GET  /api/v1/concepts/{id}             - Get concept by ID
POST /api/v1/cohorts/build             - Build cohort
POST /api/v1/cohorts/preview-count     - Quick count preview
POST /api/v1/genai/query               - Natural language query
GET  /api/v1/stats/summary             - Database statistics
```

**Service Layer:**

1. **OMOPService**: OMOP CDM data access
   - Concept search across vocabularies
   - Patient counts by criteria type
   - Demographics aggregation

2. **CohortBuilder**: Cohort execution logic
   - SQL generation from criteria
   - Inclusion/exclusion logic (INTERSECT/EXCEPT)
   - Performance optimization

3. **GenAIService**: Natural language processing
   - Query parsing
   - Entity extraction
   - Concept mapping
   - SQL generation

### Database Layer

**Databricks Connection:**
- Connection pooling via context manager
- SQL query execution
- Result serialization
- Error handling and retries

**OMOP CDM Tables Used:**

| Table | Purpose |
|-------|---------|
| `person` | Patient demographics |
| `condition_occurrence` | Medical conditions/diagnoses |
| `drug_exposure` | Medication prescriptions |
| `procedure_occurrence` | Medical procedures |
| `visit_occurrence` | Healthcare visits |
| `observation` | Lab results, vitals |
| `concept` | Standardized vocabulary |

## Data Flow

### Cohort Building Flow

```
1. User defines criteria in UI
   ↓
2. Frontend sends CohortDefinition to /cohorts/build
   ↓
3. Backend validates request
   ↓
4. CohortBuilder generates SQL query
   - Creates CTEs for each criteria
   - Combines with INTERSECT (inclusion)
   - Applies EXCEPT (exclusion)
   ↓
5. Execute query on Databricks
   ↓
6. Retrieve patient IDs
   ↓
7. Calculate demographics
   ↓
8. Return CohortResult to frontend
   ↓
9. Display results with visualizations
```

### GenAI Query Flow

```
1. User enters natural language query
   ↓
2. Frontend sends query to /genai/query
   ↓
3. GenAIService parses query
   - Extract medical entities (conditions, drugs)
   - Search OMOP concepts
   - Map to concept IDs
   ↓
4. Generate CohortDefinition
   ↓
5. Build and execute cohort
   ↓
6. Return results with explanation
   ↓
7. Display SQL, explanation, and results
```

## SQL Generation Strategy

The cohort builder uses Common Table Expressions (CTEs) for clean, maintainable SQL:

```sql
WITH base_population AS (
  SELECT DISTINCT person_id FROM person
),
inclusion_1 AS (
  -- Criteria 1: Has diabetes
  SELECT person_id FROM condition_occurrence
  WHERE condition_concept_id IN (201826, 443238)
),
inclusion_2 AS (
  -- Criteria 2: Prescribed metformin
  SELECT person_id FROM drug_exposure
  WHERE drug_concept_id IN (1503297)
),
exclusion_1 AS (
  -- Exclusion: Had stroke
  SELECT person_id FROM condition_occurrence
  WHERE condition_concept_id IN (443454)
)
SELECT person_id FROM base_population
INTERSECT SELECT person_id FROM inclusion_1
INTERSECT SELECT person_id FROM inclusion_2
EXCEPT SELECT person_id FROM exclusion_1
```

**Benefits:**
- Clear, readable queries
- Easy to debug
- Efficient execution on Databricks
- Supports complex boolean logic

## Security Considerations

1. **Authentication**: Currently uses Databricks token authentication
   - Tokens stored in environment variables
   - Not committed to version control

2. **Authorization**: Inherited from Databricks
   - Table-level permissions
   - Warehouse access control

3. **Input Validation**: 
   - Pydantic models validate all inputs
   - SQL injection prevention via parameterized queries
   - Concept ID validation

4. **CORS**: Configurable origins for API access

## Performance Optimizations

1. **Query Optimization**:
   - Use of CTEs for query planning
   - DISTINCT to avoid duplicates
   - Index-friendly concept ID lookups

2. **Caching Opportunities** (Future):
   - Concept search results
   - Frequently used cohorts
   - Database statistics

3. **Lazy Loading**:
   - Demographics only calculated on demand
   - Sample patient IDs limited to 10

4. **Connection Management**:
   - Context managers for automatic cleanup
   - Connection pooling via Databricks connector

## Scalability Considerations

1. **Databricks Scaling**:
   - Leverage Databricks auto-scaling
   - Use SQL Warehouses for concurrent queries
   - Consider Unity Catalog for governance

2. **API Scaling**:
   - Stateless design supports horizontal scaling
   - Can deploy behind load balancer
   - Consider async query execution for large cohorts

3. **Frontend Optimization**:
   - Component-level code splitting
   - Debounced search inputs
   - Virtual scrolling for large result sets

## Future Enhancements

1. **Advanced GenAI Integration**:
   - Databricks Genie Space API
   - SQL AI functions (ai_query, ai_generate_text)
   - LangChain integration

2. **Cohort Management**:
   - Save and load cohort definitions
   - Version control for cohorts
   - Cohort comparison

3. **Advanced Analytics**:
   - Survival analysis
   - Cohort trends over time
   - Propensity score matching

4. **Collaboration**:
   - Share cohorts with team
   - Comments and annotations
   - Audit trail

5. **Export Options**:
   - CSV/Excel export
   - Direct to Delta table
   - Integration with downstream tools

## Technology Choices

**Why FastAPI?**
- High performance (async support)
- Automatic API documentation
- Built-in validation
- Modern Python features

**Why React?**
- Component reusability
- Rich ecosystem
- TypeScript support
- Developer experience

**Why Databricks?**
- Native OMOP support
- Scalable SQL execution
- GenAI capabilities
- Enterprise security

## Deployment Options

1. **Development**:
   - Local backend + frontend
   - Direct Databricks connection

2. **Production** (Recommended):
   - Backend: Databricks Jobs/Apps
   - Frontend: Vercel/Netlify
   - Database: Databricks SQL Warehouse

3. **Enterprise**:
   - Containerized deployment (Docker/Kubernetes)
   - API Gateway (Kong/Apigee)
   - CI/CD pipeline
   - Monitoring and logging

