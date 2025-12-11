# Quick Start Guide - Vantage RWE

**Commercial Intelligence from Real-World Evidence**

Get up and running with Vantage RWE in 5 minutes!

## 1. Prerequisites Check

```bash
# Check Python version (need 3.9+)
python --version

# Check Node.js version (need 18+)
node --version

# Check npm
npm --version
```

## 2. Clone and Setup

```bash
# Navigate to project directory
cd omop

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## 3. Configure Databricks

Create `backend/.env`:

```env
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-token-here
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/your-warehouse-id
OMOP_CATALOG=hive_metastore
OMOP_SCHEMA=omop_cdm
```

## 4. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## 5. Test

1. Open http://localhost:3000
2. See database stats load
3. Try building a cohort!

## Common Issues

**Port already in use?**
```bash
# Backend (8000)
lsof -ti:8000 | xargs kill -9

# Frontend (3000)
lsof -ti:3000 | xargs kill -9
```

**Can't connect to Databricks?**
- Remove `https://` from DATABRICKS_HOST
- Check token hasn't expired
- Verify warehouse is running

## Example Cohorts to Try

### Simple Diabetes Cohort
1. Add Criteria → Condition
2. Search "diabetes"
3. Select "Type 2 diabetes mellitus"
4. Build Cohort

### Complex Cohort
1. **Inclusion**: Condition → "hypertension"
2. **Inclusion**: Drug → "lisinopril"
3. **Exclusion**: Condition → "pregnancy"
4. Build Cohort

### GenAI Query
Switch to "GenAI Query" tab and try:
- "Show me patients with diabetes on metformin"
- "Find patients with hypertension who had a stroke"

## Next Steps

- Read [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Explore the API docs at http://localhost:8000/docs

