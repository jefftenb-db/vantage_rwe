# Databricks App Deployment Setup

This document summarizes the configuration for deploying Vantage RWE as a Databricks App with OAuth M2M authentication.

## Architecture Overview

**Production (Databricks Apps):**
- Single FastAPI server on port 8000
- Serves pre-built React static files
- OAuth M2M authentication with service principal
- All requests handled by one server (no CORS issues)

**Development (Local):**
- Backend on port 8000 (with hot reload)
- Frontend dev server on port 3000 (with hot reload)
- OAuth M2M authentication (same as production)
- Cross-origin requests between servers

## Files Created/Updated

### 1. **app.yaml** (Configuration)
- Defines the start command: `sh start.sh`
- References Databricks secrets for configuration
- Sets OMOP catalog/schema and API settings

### 2. **start.sh** (Production Start Script)
- Generates OAuth M2M token from service principal
- Starts FastAPI server on port 8000
- Used by Databricks Apps deployment

### 3. **package.json** (Root)
- Enables Node.js + Python deployment detection
- `postinstall`: Auto-installs frontend dependencies
- `build`: Builds React to static files
- `start`: Runs production server (FastAPI only)
- `dev`: Runs development servers (both with hot reload)

### 4. **backend/app/db/databricks.py** (OAuth Support)
- Implements OAuth M2M token generation
- Uses client credentials grant flow
- Auto-refreshes tokens (1 hour validity)

### 5. **backend/app/services/genai_service.py** (OAuth Support)
- Updated to use OAuth M2M for Genie API calls
- Consistent authentication across all services

### 6. **backend/app/main.py** (Static File Serving)
- Serves built React app from `/frontend/build`
- API routes at `/api/v1/*`
- React routing handled via catch-all route

### 7. **requirements.txt** (Dependencies)
- FastAPI, uvicorn, databricks-sql-connector
- Automatically installed during deployment

## Deployment Process

```
Databricks Apps Automatic Build & Deploy:
┌──────────────────────────────────────────────┐
│  1. npm install (root)                       │
│     - Installs root dependencies             │
│     - Triggers postinstall hook              │
├──────────────────────────────────────────────┤
│  2. postinstall hook                         │
│     - cd frontend && npm install             │
│     - Installs React dependencies            │
├──────────────────────────────────────────────┤
│  3. pip install -r requirements.txt          │
│     - Installs FastAPI, uvicorn, etc.        │
├──────────────────────────────────────────────┤
│  4. npm run build                            │
│     - Builds React to static files           │
│     - Output: frontend/build/                │
├──────────────────────────────────────────────┤
│  5. sh start.sh                              │
│     - Generates OAuth token                  │
│     - Starts FastAPI on port 8000            │
│     - Serves API + React static files        │
└──────────────────────────────────────────────┘
```

## How It Works

### During Deployment

Databricks detects `package.json` at the root and automatically:

1. **Runs `npm install`** → Installs root dependencies and triggers `postinstall`
2. **Runs `pip install -r requirements.txt`** → Installs Python dependencies
3. **Runs `npm run build`** → Builds React app to static files
4. **Executes command from `app.yaml`** → Runs `sh start.sh`

### Runtime Behavior (Production)

The `start.sh` script:
1. Uses `.venv/bin/python` (created by Databricks)
2. Changes to `backend/` directory
3. Starts: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

FastAPI server then:
- **Generates OAuth token** from `DATABRICKS_CLIENT_ID` + `DATABRICKS_CLIENT_SECRET`
- **Serves API** at `/api/v1/*`
- **Serves React app** from `/frontend/build/*` for all other routes
- **Single port (8000)** - no CORS issues

### Development Behavior (Local)

Run `./run_dev.sh` to start:
- **Backend** on port 8000 (with hot reload)
- **Frontend** on port 3000 (with hot reload)
- Uses same OAuth credentials from `backend/.env`

## Environment Configuration

### Auto-Provided by Databricks Apps

These environment variables are **automatically injected** by Databricks Apps:

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABRICKS_HOST` | Auto | Workspace hostname |
| `DATABRICKS_CLIENT_ID` | Auto | App's service principal client ID |
| `DATABRICKS_CLIENT_SECRET` | Auto | App's service principal OAuth secret |

### Secrets You Must Create

Create these secrets in Databricks secret scope `omop-app`:

| Secret Key | Description | Required |
|------------|-------------|----------|
| `http_path` | SQL Warehouse HTTP path | ✅ Yes |
| `genie_space_id` | Genie Space ID for AI queries (from `create_genie_space.py` output) | ✅ Yes (for GenAI features) |

**Note:** The `genie_space_id` is required for the natural language query features. Create the Genie Space using the `create_genie_space.py` notebook before deployment.

**Create secrets via CLI:**
```bash
databricks secrets put-secret omop-app http_path \
  --string-value "/sql/1.0/warehouses/YOUR_WAREHOUSE_ID"

databricks secrets put-secret omop-app genie_space_id \
  --string-value "YOUR_GENIE_SPACE_ID"
```

### Environment Variables in app.yaml

Configured in `app.yaml`:

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABRICKS_HTTP_PATH` | `{{secrets/omop-app/http_path}}` | SQL Warehouse path |
| `DATABRICKS_GENIE_SPACE_ID` | `{{secrets/omop-app/genie_space_id}}` | Genie Space ID |
| `OMOP_CATALOG` | `vantage_rwe` | OMOP catalog name |
| `OMOP_SCHEMA` | `omop` | OMOP schema name |
| `API_HOST` | `0.0.0.0` | Server bind address |
| `API_PORT` | `8000` | Server port |
| `CORS_ORIGINS` | `http://localhost:3000,https://*.databricks.com` | Allowed origins |
| `REACT_APP_API_URL` | `/api/v1` | Frontend API URL (relative) |
| `DATABRICKS_VERIFY_SSL` | `true` | SSL verification |

## Deployment Steps

### Prerequisites

1. **OMOP CDM data** loaded in Databricks (catalog and schema)
2. **SQL Warehouse** running with appropriate size
3. **Genie Space** created using `create_genie_space.py` notebook
   - Requires: catalog_name, schema_name, warehouse_id
   - Outputs: Genie Space ID (save this for deployment)
4. **Service Principal** with OAuth secret generated
5. **Service principal permissions**:
   - `Can Use` on SQL Warehouse
   - Access to OMOP catalog/schema
   - Access to Genie Space

### Step 1: Create Secrets

```bash
# Create secret scope (if doesn't exist)
databricks secrets create-scope omop-app

# Add required secrets
databricks secrets put-secret omop-app http_path \
  --string-value "/sql/1.0/warehouses/YOUR_WAREHOUSE_ID"

# Add optional Genie Space ID
databricks secrets put-secret omop-app genie_space_id \
  --string-value "YOUR_GENIE_SPACE_ID"
```

### Step 2: Deploy via CLI

```bash
# Sync code to workspace
databricks sync . /Workspace/Users/your-email@org.com/vantage-rwe

# Deploy app
databricks apps deploy vantage-rwe \
   --source-code-path /Workspace/Users/your-email@org.com/vantage-rwe
```

### Step 3: Deploy via UI

1. **Upload code** to Workspace folder
2. Go to **Compute** → **Apps** → **Create App**
3. **Name:** `vantage-rwe`
4. **Source code path:** Select your uploaded folder
5. Click **Deploy**

### Step 4: Verify Deployment

Expected logs:
```
Starting Vantage RWE application...
Using Python from .venv
Serving static files from: /app/python/source_code/frontend/build
Using OAuth M2M authentication with service principal
OAuth credentials detected:
  - client_id: abc12345... (length: 36)
  - client_secret: ****** (length: 64)
Requesting OAuth token from https://...
OAuth M2M token obtained successfully
✓ Startup complete - API is ready
Uvicorn running on http://0.0.0.0:8000
```

## Local Development

### Setup

1. **Create `backend/.env`** (copy from `backend/env.template`):
   ```bash
   cp backend/env.template backend/.env
   ```

2. **Add OAuth credentials** to `backend/.env`:
   ```bash
   DATABRICKS_HOST=your-workspace.cloud.databricks.com
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/YOUR_WAREHOUSE_ID
   
   # OAuth Service Principal (same as production)
   DATABRICKS_CLIENT_ID=your-service-principal-client-id
   DATABRICKS_CLIENT_SECRET=your-service-principal-secret
   
   OMOP_CATALOG=vantage_rwe
   OMOP_SCHEMA=omop
   DATABRICKS_GENIE_SPACE_ID=your-genie-space-id
   ```

3. **Run development servers:**
   ```bash
   ./run_dev.sh
   ```

This starts:
- Backend on http://localhost:8000 (with hot reload)
- Frontend on http://localhost:3000 (with hot reload)

### Production Mode Locally

To test production setup locally:

```bash
# Build React app
npm run build

# Start production server
npm start
```

This runs the same setup as Databricks Apps (single server on port 8000).

## Authentication: OAuth M2M Only

This app **requires OAuth M2M authentication** in all environments for consistency.

### Benefits
- ✅ Same authentication flow everywhere (local & production)
- ✅ Auto token refresh (1 hour validity)
- ✅ Production-grade security
- ✅ Service principal tracking and auditing

### How It Works

**Token Generation:**
1. App sends client credentials to `/oidc/v1/token`
2. Databricks returns access token (valid 1 hour)
3. Token used for SQL Warehouse and Genie API calls
4. Automatically refreshed on each connection

**Production:** Uses service principal auto-provided by Databricks Apps
**Local:** Uses service principal from `backend/.env`

## Troubleshooting

### 401 Unauthorized (OAuth)
**Issue:** OAuth token request fails
**Fix:** 
- Verify service principal OAuth secret is valid
- Regenerate OAuth secret if expired
- Check service principal has access to workspace

### 502 Bad Gateway
**Issue:** App not responding on expected port
**Fix:**
- Ensure app listens on port 8000 (not 8080)
- Check `start.sh` is executable: `chmod +x start.sh`
- Verify Python venv has uvicorn installed

### 500 Internal Server Error
**Issue:** Database connection fails
**Fix:**
- Check service principal has `Can Use` on SQL Warehouse
- Verify service principal has access to OMOP catalog/schema
- Check `http_path` secret is correct

### Frontend Not Loading
**Issue:** Blank page or 404 errors
**Fix:**
- Verify `npm run build` completed successfully
- Check `frontend/build/` directory exists
- Ensure FastAPI is serving static files

## Next Steps

1. ✅ **Create service principal** with OAuth secret
2. ✅ **Grant permissions** to SQL Warehouse and OMOP data  
3. ✅ **Create secrets** (`http_path`, optional `genie_space_id`)
4. ✅ **Test locally** with OAuth: `./run_dev.sh`
5. ✅ **Deploy to Databricks Apps**
6. ✅ **Monitor logs** and verify OAuth authentication
7. ✅ **Access app** via Databricks Apps URL

## Documentation

- **[docs/DATABRICKS_APP_DEPLOYMENT.md](./docs/DATABRICKS_APP_DEPLOYMENT.md)** - Full deployment guide
- **[docs/OAUTH_SETUP.md](./docs/OAUTH_SETUP.md)** - OAuth configuration details
- **[README.md](./README.md)** - Project overview and features

## References

- [Databricks Apps Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [Databricks OAuth M2M](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m)
- [Databricks Apps Deployment Logic](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy#deployment-logic)

