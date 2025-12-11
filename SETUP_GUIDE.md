# Vantage RWE - Setup Guide

**Commercial Intelligence from Real-World Evidence**

This guide will walk you through setting up the OMOP Cohort Builder application from scratch.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** ([Download Python](https://www.python.org/downloads/))
- **Node.js 18 or higher** ([Download Node.js](https://nodejs.org/))
- **Access to a Databricks workspace** with OMOP CDM data
- **Databricks SQL Warehouse or Cluster** for querying

## Step 1: Databricks Setup

### 1.1 Create Databricks Personal Access Token

1. Log into your Databricks workspace
2. Click on your username in the top-right corner
3. Select **Settings** → **Developer**
4. Click **Manage** next to Access tokens
5. Click **Generate new token**
6. Give it a name (e.g., "OMOP Cohort Builder")
7. Set expiration (recommended: 90 days or more)
8. Copy the token and save it securely

### 1.2 Get SQL Warehouse HTTP Path

1. In Databricks, go to **SQL Warehouses**
2. Select or create a warehouse
3. Click on **Connection Details**
4. Copy the **HTTP Path** (format: `/sql/1.0/warehouses/xxxxx`)

### 1.3 Verify OMOP Data

Ensure your OMOP CDM tables exist in Databricks:

```sql
-- Check if tables exist
SHOW TABLES IN your_catalog.your_schema;

-- Verify key tables
SELECT COUNT(*) FROM your_catalog.your_schema.person;
SELECT COUNT(*) FROM your_catalog.your_schema.condition_occurrence;
SELECT COUNT(*) FROM your_catalog.your_schema.drug_exposure;
```

## Step 2: Backend Setup

### 2.1 Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

For development with virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2.2 Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your Databricks credentials:

```env
# Databricks Configuration
DATABRICKS_HOST=your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123def456

# OMOP Database Configuration
OMOP_CATALOG=hive_metastore
OMOP_SCHEMA=omop_cdm

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

**Important Configuration Notes:**
- `DATABRICKS_HOST`: Your workspace URL without `https://`
- `DATABRICKS_TOKEN`: The token you generated in Step 1.1
- `DATABRICKS_HTTP_PATH`: The HTTP path from Step 1.2
- `OMOP_CATALOG`: Usually `hive_metastore` or your Unity Catalog name
- `OMOP_SCHEMA`: The schema/database where your OMOP tables are stored

### 2.3 Test Backend Connection

```bash
cd backend
python -c "from app.db.databricks import db; print('Testing connection...'); result = db.execute_scalar('SELECT 1'); print('✓ Connection successful!' if result == 1 else '✗ Connection failed')"
```

### 2.4 Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at:
- **API Endpoint**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Step 3: Frontend Setup

### 3.1 Install Node Dependencies

```bash
cd frontend
npm install
```

### 3.2 Configure Environment

Create a `.env` file in the `frontend` directory:

```bash
cd frontend
cp .env.example .env
```

The default configuration should work:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### 3.3 Start Frontend Server

```bash
cd frontend
npm start
```

The application will open automatically at:
- **Frontend**: http://localhost:3000

## Step 4: Verify Installation

### 4.1 Check API Health

Open http://localhost:8000/api/v1/health in your browser. You should see:

```json
{
  "status": "healthy",
  "service": "OMOP Cohort Builder"
}
```

### 4.2 Test Database Connection

1. Open http://localhost:3000
2. You should see database statistics at the top (Total Patients, Unique Conditions, etc.)
3. If you see numbers, the connection is working!

### 4.3 Test Cohort Builder

1. Click on the **"📊 Cohort Builder"** tab
2. Enter a cohort name (e.g., "Test Cohort")
3. Click **"+ Add Criteria"**
4. Select a criteria type (e.g., "Condition")
5. Search for a condition (e.g., "diabetes")
6. Select a concept from the search results
7. Click **"🚀 Build Cohort"**
8. You should see patient counts and demographics

### 4.4 Test GenAI Query

1. Click on the **"🤖 GenAI Query"** tab
2. Try an example query like: "Show me patients with Type 2 Diabetes"
3. Click **"🚀 Ask GenAI"**
4. You should see the generated SQL and results

## Troubleshooting

### Backend Issues

**Error: "Connection to Databricks failed"**
- Verify your `DATABRICKS_HOST` doesn't include `https://`
- Check that your access token is valid and hasn't expired
- Ensure your SQL Warehouse is running

**Error: "Table not found"**
- Verify `OMOP_CATALOG` and `OMOP_SCHEMA` are correct
- Check table permissions in Databricks
- Run `SHOW TABLES IN catalog.schema` to verify table names

**Error: "Module not found"**
- Make sure you're in the virtual environment
- Run `pip install -r requirements.txt` again

### Frontend Issues

**Error: "Cannot connect to API"**
- Ensure backend is running on port 8000
- Check `REACT_APP_API_URL` in frontend `.env`
- Look for CORS errors in browser console

**Error: "npm install fails"**
- Try deleting `node_modules` and `package-lock.json`
- Run `npm cache clean --force`
- Run `npm install` again

### Data Issues

**No search results appear**
- Check that OMOP concept tables are populated
- Verify the `concept` table has valid data
- Try searching with different terms

**Demographics not showing**
- Ensure `person` table has gender and birth date data
- Check that concept IDs are properly linked

## Next Steps

Now that your application is running:

1. **Explore the OMOP vocabulary**: Search for different conditions, drugs, and procedures
2. **Build complex cohorts**: Combine multiple inclusion and exclusion criteria
3. **Test GenAI queries**: Try natural language questions about patient populations
4. **Customize**: Modify the code to fit your specific use cases

## Additional Resources

- [OHDSI OMOP CDM Documentation](https://ohdsi.github.io/CommonDataModel/)
- [Databricks SQL Documentation](https://docs.databricks.com/sql/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check Databricks connection and permissions
4. Review application logs for detailed error messages

