# Vantage RWE

**Commercial Intelligence from Real-World Evidence**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)

A comprehensive commercial intelligence platform for pharmaceutical teams to analyze real-world healthcare data using the OHDSI OMOP Common Data Model (CDM) on Databricks. Designed for seamless deployment as a Databricks App with production-ready OAuth authentication.

---

## 🎯 Overview

**Vantage RWE** transforms healthcare data into actionable commercial insights for pharmaceutical companies. Built on the industry-standard OMOP CDM and powered by Databricks, it provides three integrated analytics modules:

- **📊 Patient Cohort Analytics** - Build and analyze patient populations
- **👨‍⚕️ Prescriber Analytics** - Target high-value healthcare providers
- **📈 Market Share Intelligence** - Track competitive positioning and trends

Perfect for brand teams, sales operations, commercial analytics, and medical affairs.

---

## ✨ Key Features

### 📊 **Patient Cohort Analytics**

Build sophisticated patient cohorts using multiple clinical criteria:

- **Interactive Cohort Builder**
  - Define inclusion/exclusion criteria
  - Medical conditions, drug exposures, procedures, visits, observations
  - Date ranges and occurrence counts
  - Boolean logic (AND/OR combinations)

- **AI-Powered Natural Language Queries**
  - Ask questions in plain English using Databricks Genie
  - Example: "Show me Type 2 Diabetes patients prescribed Metformin in 2023"
  - Automatically generates SQL and cohort definitions

- **Real-Time Analytics**
  - Instant patient counts and demographics
  - Age/gender distribution
  - Sample patient IDs for validation

**Use Cases:**
- Clinical trial recruitment feasibility
- Market sizing for new indications
- Real-world evidence study populations
- Patient journey analysis

---

### 👨‍⚕️ **Prescriber Analytics**

Identify and target high-value healthcare providers:

#### **Prescriber Search & Profiling**
- Search by specialty, patient volume, drug prescribed
- Rank prescribers by volume with percentile/decile rankings
- View prescriber profiles with aggregate metrics

#### **Drug Prescriber Analytics**
- Top prescribers by drug with market share
- Market concentration metrics (HHI, top 10%, top 20%)
- Prescriber distribution analysis

#### **Prescriber Targeting** 🎯
- **AI-powered targeting algorithm**
- Identifies HCPs who:
  - Treat relevant patient populations
  - Prescribe competitor drugs
  - Have low/no adoption of your drug
- Prioritized target lists (High/Medium/Low)
- Opportunity scoring and estimated potential

#### **Treatment Pathway Analysis**
- First-line drug preferences by prescriber
- Drug switching patterns (Drug A → Drug B)
- Treatment sequences and algorithms

**Use Cases:**
- Sales force targeting and territory planning
- Key opinion leader (KOL) identification
- Market access strategy
- Competitive intelligence

**Key Metrics:**
- Prescriber volume rankings (deciles/percentiles)
- Market share by prescriber
- Target opportunity scores
- Switch analysis

---

### 📈 **Market Share Intelligence**

Comprehensive competitive intelligence and market dynamics:

#### **Market Share Overview**
- Market share by drug (prescriptions & patients)
- Market concentration (HHI, top 3/5 share)
- Rank ordering and visual distribution
- Herfindahl-Hirschman Index calculation

#### **Trend Analysis**
- Historical market share tracking
- Monthly, quarterly, or yearly views
- Period-over-period growth rates
- Peak share identification
- Trend direction (growing/declining/stable)

#### **Competitive Positioning**
- Head-to-head comparisons with competitors
- Share gap to market leader
- Relative ranking visualization
- Competitive landscape overview

#### **New-to-Brand (NBx) Analysis**
- New patient acquisition tracking
- Treatment-naive vs. switchers
- Source analysis (which competitor drugs)
- NBx rate calculations
- Switch pattern identification

**Use Cases:**
- Market access and pricing decisions
- Sales forecasting and planning
- Competitive strategy development
- Board/investor presentations
- Launch planning and tracking

**Key Metrics:**
- Market share % (by Rx and patients)
- HHI (market concentration)
- NBx rate and sources
- Share gap to leader
- Growth rates (period-over-period)

---

## 🏗️ Architecture

### Technology Stack

**Backend:**
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Databricks SQL Connector** - Database connectivity
- **SQLAlchemy-style** queries for OMOP CDM

**Frontend:**
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Axios** - API client
- **CSS3** - Responsive styling

**Data:**
- **OMOP CDM 5.4** - Standardized healthcare data model
- **Databricks** - Data platform (SQL Warehouse or Cluster)
- **OHDSI Vocabularies** - Standardized medical terminologies

### System Architecture

```
┌────────────────────────────────────────────────────────┐
│                    Frontend (React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Cohort     │  │  Prescriber  │  │ Market Share │  │
│  │   Builder    │  │  Analytics   │  │  Analytics   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────┘
                            │
                    ┌───────▼────────┐
                    │   REST API     │
                    │   (FastAPI)    │
                    └───────┬────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    ┌────▼─────┐     ┌──────▼──────┐     ┌─────▼──────┐
    │  Cohort  │     │  Prescriber │     │   Market   │
    │  Service │     │   Service   │     │   Share    │
    └────┬─────┘     └──────┬──────┘     └─────┬──────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                    ┌───────▼────────┐
                    │   Databricks   │
                    │   OMOP CDM     │
                    └────────────────┘
```

### Project Structure

```
vantage-rwe/
├── backend/                      # Python/FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py        # API endpoints
│   │   ├── models/
│   │   │   ├── cohort.py        # Cohort models
│   │   │   ├── prescriber.py    # Prescriber models
│   │   │   └── market_share.py  # Market share models
│   │   ├── services/
│   │   │   ├── cohort_builder.py
│   │   │   ├── prescriber_service.py
│   │   │   ├── market_share_service.py
│   │   │   ├── omop_service.py
│   │   │   └── genai_service.py # Databricks Genie integration
│   │   ├── db/
│   │   │   └── databricks.py    # Database connection
│   │   ├── config.py            # Configuration
│   │   └── main.py              # FastAPI app
│   └── requirements.txt
│
├── frontend/                     # React/TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── CohortBuilder.tsx
│   │   │   ├── PrescriberAnalytics.tsx
│   │   │   ├── MarketShareAnalytics.tsx
│   │   │   └── NaturalLanguageSearch.tsx
│   │   ├── services/
│   │   │   └── api.ts           # API client
│   │   ├── App.tsx
│   │   └── index.tsx
│   └── package.json
│
└── docs/                         # Documentation
    ├── CREATE_ENV.md
    ├── DATABRICKS_APP_DEPLOYMENT.md
    ├── EXAMPLE_COHORTS.md
    ├── GENIE_INTEGRATION.md
    ├── GENIE_SETUP.md
    ├── MARKET_SHARE_ANALYTICS.md
    ├── PRESCRIBER_ANALYTICS.md
    ├── PROJECT_SUMMARY.md
    └── QUICK_SSL_FIX.md
```

---

## 🚀 Quick Start

### Prerequisites

Before deploying, ensure you have:

1. **Databricks workspace** with:
   - **OMOP CDM data loaded** in a catalog and schema
   - **SQL Warehouse running** with appropriate size
   - **Service principal** with OAuth credentials and permissions

2. **Genie Space created** (required for AI-powered queries):
   - Upload `create_genie_space.py` to Databricks as a notebook
   - Run the notebook with your catalog_name, schema_name, and warehouse_id
   - Capture the Genie Space ID from the output

3. **Databricks CLI** installed (for deployment)

See the [Prerequisites Setup Guide](#-prerequisites-setup) below for detailed instructions.

### Production Deployment (Recommended)

Deploy Vantage RWE as a Databricks App for immediate production use:

#### 1. Create Databricks Secrets

Create secrets in Databricks secret scope `omop-app`:

```bash
# Create secret scope (if it doesn't exist)
databricks secrets create-scope omop-app

# Add required secrets
databricks secrets put-secret omop-app http_path \
  --string-value "/sql/1.0/warehouses/YOUR_WAREHOUSE_ID"

# Add Genie Space ID (required for AI-powered natural language queries)
databricks secrets put-secret omop-app genie_space_id \
  --string-value "YOUR_GENIE_SPACE_ID"
```

**Note:** `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, and `DATABRICKS_CLIENT_SECRET` are automatically provided by Databricks Apps - no manual OAuth setup needed!

#### 2. Deploy via CLI

```bash
# Clone the repository
git clone https://github.com/jefftenb-db/vantage_rwe.git
cd vantage_rwe

# Sync code to workspace
databricks sync . /Workspace/Users/you@company.com/vantage-rwe

# Deploy app
databricks apps deploy vantage-rwe \
  --source-code-path /Workspace/Users/you@company.com/vantage-rwe
```

#### 3. Access Your App

Once deployed:
1. Go to **Compute** → **Apps** tab in Databricks
2. Click on your app name (`vantage-rwe`)
3. Click the **App URL** to open the application

Your app will be accessible at a URL like:
```
https://<workspace-url>/apps/<app-id>
```

Explore the features:
- **Cohort Builder** tab - Build patient populations
- **GenAI Query** tab - Natural language search (requires Genie)
- **Prescriber Analytics** tab - HCP targeting and analysis
- **Market Share** tab - Competitive intelligence

**See [Databricks App Deployment Guide](./docs/DATABRICKS_APP_DEPLOYMENT.md) for detailed deployment options including UI-based deployment.**

---

## 📋 Prerequisites Setup

Before deploying the application, you need to prepare your Databricks environment.

### Step 1: OMOP CDM Data

Ensure your OMOP CDM data is loaded in Databricks:

- **Catalog**: Default is `vantage_rwe` (configurable)
- **Schema**: Default is `omop` (configurable)
- **Required tables**: `person`, `condition_occurrence`, `drug_exposure`, `provider`, `concept`, `concept_ancestor`, and other OMOP tables

Verify your data:
```sql
-- Run in Databricks SQL
SHOW TABLES IN vantage_rwe.omop;
SELECT COUNT(*) FROM vantage_rwe.omop.person;
```

### Step 2: SQL Warehouse

Create or identify a SQL Warehouse for the application:

1. Go to **SQL Warehouses** in Databricks
2. Create a new warehouse or use existing
3. Note the **Warehouse ID** from the URL or Connection Details
4. Ensure it has **auto-stop** enabled to manage costs

### Step 3: Create Genie Space (Required for AI Queries)

The application uses Databricks Genie for natural language queries. Create a Genie Space using the provided automation script:

#### 3.1 Upload the Notebook

1. In Databricks, go to **Workspace**
2. Navigate to your desired folder
3. Upload `create_genie_space.py` as a notebook

#### 3.2 Run the Notebook

1. Open the `create_genie_space` notebook
2. Follow the step-by-step instructions in the notebook:
   - **Step 1**: Install databricks-sdk
   - **Step 2**: Create widget parameters
   - **Step 3**: Update widgets with your values:
     - `catalog_name`: Your OMOP catalog (e.g., `vantage_rwe`)
     - `schema_name`: Your OMOP schema (e.g., `omop`)
     - `warehouse_id`: Your SQL Warehouse ID
   - **Step 4**: Run the Genie Space creation
   - **Step 5**: Capture the Genie Space ID

#### 3.3 Save the Genie Space ID

Copy the Genie Space ID from the output. You'll need this for deployment:

```
Genie Space ID: 
01abc234-5678-90de-f123-456789abcdef
```

**Important:** The Genie Space is pre-configured with:
- Key OMOP tables: person, condition_occurrence, drug_exposure, provider, concept, etc.
- OMOP-specific instructions and example queries
- Optimized for pharmaceutical/clinical analytics

### Step 4: Service Principal Permissions

Ensure your service principal (or the one that will be auto-created by Databricks Apps) has:

1. **SQL Warehouse Permissions**:
   - Go to **SQL Warehouses** → Your warehouse → **Permissions**
   - Add service principal with `Can Use` permission

2. **Data Permissions**:
   - Grant `USE CATALOG` on your OMOP catalog
   - Grant `USE SCHEMA` on your OMOP schema
   - Grant `SELECT` on all OMOP tables

3. **Genie Space Permissions** (automatic for Databricks Apps):
   - Service principal will have access to the Genie Space

---

## 💻 Local Development Setup

For local development and testing, you can run Vantage RWE on your local machine:

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Databricks workspace** with OMOP CDM data and SQL Warehouse

### 1. Clone the Repository

```bash
git clone https://github.com/jefftenb-db/vantage_rwe.git
cd vantage_rwe
```

### 2. Configure Environment

Create `backend/.env` file:

```bash
cd backend
cp env.template .env
```

Edit `backend/.env` with your Databricks OAuth credentials:

```env
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/YOUR_WAREHOUSE_ID

# OAuth Service Principal (required)
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-oauth-secret

OMOP_CATALOG=vantage_rwe
OMOP_SCHEMA=omop
```

**To get OAuth credentials:**
1. Go to Databricks → Settings → User Management → Service Principals
2. Create or select a service principal
3. Go to Secrets tab → Generate secret
4. Copy Client ID and Secret (shown only once!)

### 3. Install Dependencies

```bash
# Python backend dependencies
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
cd ..

# React frontend dependencies
cd frontend
npm install
cd ..
```

### 4. Run Development Servers

**Option A: Use the development script (recommended)**

```bash
./run_dev.sh
```

This starts both servers with hot reload:
- Backend API: **http://localhost:8000**
- Frontend UI: **http://localhost:3000**
- API Documentation: **http://localhost:8000/docs**

**Option B: Start servers manually**

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

### 5. Access the Application

Open your browser to **http://localhost:3000**

---

## ⚙️ Configuration

### Backend Environment Variables

**For Databricks Apps (Production):**

These variables are configured in `app.yaml` and automatically provided by Databricks:
- `DATABRICKS_HOST` - Auto-provided by Databricks Apps
- `DATABRICKS_CLIENT_ID` - Auto-provided by Databricks Apps
- `DATABRICKS_CLIENT_SECRET` - Auto-provided by Databricks Apps
- `DATABRICKS_HTTP_PATH` - From secret: `{{secrets/omop-app/http_path}}`
- `DATABRICKS_GENIE_SPACE_ID` - From secret: `{{secrets/omop-app/genie_space_id}}`

See [Databricks App Deployment Guide](./docs/DATABRICKS_APP_DEPLOYMENT.md) for setup details.

**For Local Development:**

Create `backend/.env` file (copy from `backend/env.template`):

```env
# Databricks Connection
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123xyz789

# OAuth Service Principal Authentication (REQUIRED)
# Get these from: Settings → User Management → Service Principals
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-oauth-secret

# OMOP Schema Configuration
OMOP_CATALOG=vantage_rwe
OMOP_SCHEMA=omop

# Optional: Databricks Genie for AI-powered queries
DATABRICKS_GENIE_SPACE_ID=your-genie-space-id

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# SSL Configuration
DATABRICKS_VERIFY_SSL=true
```

### Frontend Environment Variables

**For Databricks Apps (Production):**

Configured automatically in `app.yaml`:
- `REACT_APP_API_URL=/api/v1` - Relative path for same-origin requests

**For Local Development:**

Create `frontend/.env` (optional - defaults work for most cases):

```env
# API endpoint (defaults to http://localhost:8000/api/v1)
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Authentication

This application uses **OAuth M2M (Machine-to-Machine)** authentication with Databricks service principals - the same authentication method in both production and local development:

- ✅ Production-ready security (recommended by Databricks)
- ✅ Automatic token generation and refresh
- ✅ Tokens valid for 1 hour
- ✅ Auto-provided by Databricks Apps (no manual setup in production)
- ✅ Same authentication flow everywhere

**Why OAuth vs Personal Tokens?**
- Better security (scoped to service principal)
- Auto-refresh (no expired token issues)
- Audit trail (actions tied to service principal)
- Required for Databricks Apps deployment

---

## 📚 Usage Examples

### Example 1: Build a Diabetes Cohort

1. Go to **Cohort Builder** tab
2. Name: "Type 2 Diabetes Patients on Metformin"
3. **Add Inclusion Criteria**:
   - Type: Condition
   - Search: "Type 2 Diabetes"
   - Select concepts (201826, 443238)
4. **Add Inclusion Criteria**:
   - Type: Drug
   - Search: "Metformin"
   - Select concepts (1503297)
5. Click **Build Cohort**
6. View patient count and demographics

### Example 2: Target High-Value Prescribers

1. Go to **Prescriber Analytics** → **Targeting** tab
2. Enter Target Drug IDs (your drug)
3. Enter Competitor Drug IDs
4. Click **Identify Targets**
5. Review prioritized list with opportunity scores
6. Export for CRM/sales planning

### Example 3: Analyze Market Share Trends

1. Go to **Market Share** → **Trends** tab
2. Search for your drug
3. Select time granularity (monthly/quarterly)
4. Click **Get Trends**
5. View historical market share changes
6. Identify growth periods and patterns

### Example 4: Natural Language Query

1. Go to **GenAI Query** tab
2. Type: "Show me patients with heart failure prescribed ACE inhibitors"
3. Click **Search**
4. View generated SQL and results
5. Refine and export

---

## 🔌 API Endpoints

### Cohort Endpoints
- `POST /api/v1/cohorts/build` - Build cohort
- `POST /api/v1/concepts/search` - Search OMOP concepts
- `POST /api/v1/genai/query` - Natural language query

### Prescriber Endpoints
- `GET /api/v1/prescribers/{id}` - Get prescriber profile
- `POST /api/v1/prescribers/search` - Search prescribers
- `GET /api/v1/prescribers/drug/{id}/analytics` - Drug prescriber analytics
- `POST /api/v1/prescribers/targeting` - Identify targets
- `GET /api/v1/prescribers/{id}/treatment-pathways` - Treatment pathways

### Market Share Endpoints
- `POST /api/v1/market-share/analysis` - Market share overview
- `GET /api/v1/market-share/trends/{id}` - Trend analysis
- `GET /api/v1/market-share/competitive/{id}` - Competitive positioning
- `GET /api/v1/market-share/new-to-brand/{id}` - NBx analysis
- `POST /api/v1/market-share/geographic` - Geographic breakdown

**Full API Documentation**: http://localhost:8000/docs

---

## 📊 OMOP CDM Tables

The platform leverages these OMOP tables:

| Table | Purpose |
|-------|---------|
| **PERSON** | Patient demographics |
| **CONDITION_OCCURRENCE** | Diagnoses and medical conditions |
| **DRUG_EXPOSURE** | Medication prescriptions |
| **PROCEDURE_OCCURRENCE** | Medical procedures |
| **VISIT_OCCURRENCE** | Healthcare visits |
| **OBSERVATION** | Lab results and measurements |
| **PROVIDER** | Healthcare provider information |
| **CARE_SITE** | Healthcare facility information |
| **LOCATION** | Geographic data |
| **CONCEPT** | Standardized vocabularies |

**OMOP Version**: 5.4  
**Vocabularies**: SNOMED-CT, RxNorm, ICD-10-CM, CPT4, LOINC

---

## 🎓 Documentation

### Deployment & Setup (Start Here)
- **[Databricks App Deployment](./docs/DATABRICKS_APP_DEPLOYMENT.md)** - **Production deployment guide** (RECOMMENDED)
- **[Deployment Setup](./DEPLOYMENT_SETUP.md)** - Deployment configuration overview
- **[OAuth Setup](./docs/OAUTH_SETUP.md)** - OAuth M2M authentication guide
- **[Environment Setup](./docs/CREATE_ENV.md)** - Environment configuration for local development

### Features & Usage
- **[Prescriber Analytics](./docs/PRESCRIBER_ANALYTICS.md)** - HCP targeting guide
- **[Market Share Analytics](./docs/MARKET_SHARE_ANALYTICS.md)** - Competitive intelligence guide
- **[Genie Setup Guide](./docs/GENIE_SETUP.md)** - Configure AI-powered natural language queries
- **[Genie Integration](./docs/GENIE_INTEGRATION.md)** - Natural language query examples
- **[Example Cohorts](./docs/EXAMPLE_COHORTS.md)** - Sample queries
- **[Project Summary](./docs/PROJECT_SUMMARY.md)** - Technical overview

---

## 🏭 Production Deployment Details

### Deployment Architecture

**Databricks Apps (Recommended):**
- Single FastAPI server on port 8000
- Serves pre-built React static files
- OAuth M2M authentication with service principal
- No CORS issues (same origin)
- Auto-scaling via SQL Warehouse
- Built-in monitoring and logs

### Auto-Provided Environment Variables

When deploying as a Databricks App, these are automatically provided:
- `DATABRICKS_HOST` - Workspace hostname
- `DATABRICKS_CLIENT_ID` - Service principal client ID
- `DATABRICKS_CLIENT_SECRET` - OAuth secret

**No manual OAuth setup needed in production!**

### Deployment Options

1. **Databricks CLI** - Automated deployment (see Quick Start above)
2. **Databricks UI** - Manual upload and deployment
3. **CI/CD Integration** - Automated pipelines

See [Databricks App Deployment Guide](./docs/DATABRICKS_APP_DEPLOYMENT.md) for:
- UI-based deployment walkthrough
- Troubleshooting common issues
- Advanced configuration options
- Updating deployed apps

---

## 🌳 Repository Branches

This repository uses feature branches for independent module management:

- **`main`** - Baseline cohort builder
- **`feature/prescriber-analytics`** - Adds prescriber analytics
- **`feature/market-share-analysis`** - Full suite (recommended)

See [BRANCH_GUIDE.md](./BRANCH_GUIDE.md) for details.

---

## 💼 Who Is This For?

**Vantage RWE** is purpose-built for pharmaceutical commercial teams:

### **Brand Teams**
- Track market share vs. competitors
- Understand patient flows and switches
- Support pricing and market access decisions
- Generate board-ready insights

### **Sales Operations**
- Identify high-value prescriber targets
- Territory planning and resource allocation
- Sales force effectiveness measurement
- CRM data enrichment

### **Commercial Analytics**
- Real-world evidence generation
- Market landscape analysis
- Forecasting and scenario modeling
- Ad-hoc business intelligence

### **Medical Affairs**
- Treatment pattern analysis
- Physician behavior insights
- KOL identification
- Evidence generation for publications

---

## 🛠️ Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
cd backend
flake8 app/
black app/

# TypeScript linting
cd frontend
npm run lint
```

### Testing Production Build Locally

To test the production build locally before deploying to Databricks Apps:

```bash
# Build React frontend to static files
npm run build

# Start production server (same architecture as Databricks Apps)
npm start
```

This runs a single FastAPI server on port 8000 that:
- Serves API at `/api/v1/*`
- Serves React static files for all other routes
- Uses OAuth authentication (same as production)
- No CORS issues (same origin)

Access at **http://localhost:8000** (note: port 8000, not 3000)

---

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- **OHDSI Community** - For the OMOP Common Data Model standard
- **Databricks** - For the data platform and Genie AI capabilities
- **FastAPI & React** - For excellent frameworks

---

## 📞 Support

- **Documentation**: See `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/jefftenb-db/vantage_rwe/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jefftenb-db/vantage_rwe/discussions)

---

## 🗺️ Roadmap

**Upcoming Features:**
- [ ] Geographic heatmaps and visualizations
- [ ] Export to PowerBI/Tableau
- [ ] Automated email reports
- [ ] Patient journey Sankey diagrams
- [ ] Predictive analytics (ML models)
- [ ] Multi-tenant support
- [ ] RBAC (Role-Based Access Control)
- [ ] Audit logging and compliance features

---

<p align="center">
  <strong>Vantage RWE</strong> - Transforming Healthcare Data into Commercial Intelligence
</p>

<p align="center">
  Made with ❤️ for Pharmaceutical Commercial Teams
</p>
