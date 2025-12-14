# Databricks App Setup - Changes Summary

This document summarizes the changes made to enable Databricks App deployment.

## Files Created/Updated

### 1. **app.yaml** (Created)
- Configures the Databricks App deployment
- Specifies the start command: `npm run start`
- Defines environment variables using Databricks secrets
- Maps secrets from `omop-app` secret scope

### 2. **package.json** (Created at root)
- Enables Node.js + Python deployment
- Includes `concurrently` to run both frontend and backend
- Build script: `npm run build` - builds React frontend
- Start script: `npm run start` - runs both services concurrently

### 3. **requirements.txt** (Already exists at root)
- Contains all Python dependencies for FastAPI backend
- Will be automatically installed during deployment

### 4. **docs/DATABRICKS_APP_DEPLOYMENT.md** (Created)
- Complete deployment guide for Databricks Apps
- Step-by-step instructions for CLI and UI deployment
- Secret management guide
- Troubleshooting tips

## Deployment Architecture

```
Databricks App Deployment Process:
┌─────────────────────────────────────────┐
│  1. npm install (root)                  │
│     - Installs concurrently             │
├─────────────────────────────────────────┤
│  2. pip install -r requirements.txt     │
│     - Installs FastAPI, uvicorn, etc.   │
├─────────────────────────────────────────┤
│  3. npm run build                       │
│     - Builds React frontend             │
├─────────────────────────────────────────┤
│  4. npm run start                       │
│     - Starts backend (FastAPI on :8000) │
│     - Starts frontend (React on :3000)  │
│     - Runs concurrently                 │
└─────────────────────────────────────────┘
```

## How It Works

### During Deployment

Databricks detects `package.json` at the root and executes:

1. **Install Node dependencies**: `npm install` → Installs `concurrently`
2. **Install Python dependencies**: `pip install -r requirements.txt` → Installs FastAPI, etc.
3. **Build frontend**: `npm run build` → Creates optimized React build
4. **Start application**: Executes command from `app.yaml` → `npm run start`

### Runtime Behavior

The `npm run start` script in `package.json` uses `concurrently` to:

- Launch backend: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Launch frontend: `cd frontend && PORT=3000 npm start`
- Both services run in parallel

## Environment Configuration

### Secrets Required

Create these secrets in Databricks secret scope `omop-app`:

| Secret Key | Description |
|------------|-------------|
| `databricks_host` | Workspace URL (without https://) |
| `databricks_token` | Access token for authentication |
| `databricks_http_path` | SQL Warehouse HTTP path |
| `genie_space_id` | (Optional) Genie Space ID |

### Environment Variables

Set in `app.yaml` and available to both frontend and backend:

- **DATABRICKS_HOST**, **DATABRICKS_TOKEN**, **DATABRICKS_HTTP_PATH**
- **OMOP_CATALOG**, **OMOP_SCHEMA** (database configuration)
- **API_HOST**, **API_PORT** (backend settings)
- **CORS_ORIGINS** (security)
- **REACT_APP_API_URL** (frontend API endpoint)

## Quick Deployment Steps

### Using Databricks CLI

```bash
# 1. Create secrets
databricks secrets create-scope omop-app
databricks secrets put-secret omop-app databricks_host --string-value "workspace.cloud.databricks.com"
databricks secrets put-secret omop-app databricks_token --string-value "dapi..."
databricks secrets put-secret omop-app databricks_http_path --string-value "/sql/1.0/warehouses/..."

# 2. Sync code to workspace
databricks sync . /Workspace/Users/your-email@org.com/vantage-rwe

# 3. Deploy app
databricks apps deploy vantage-rwe \
   --source-code-path /Workspace/Users/your-email@org.com/vantage-rwe
```

### Using Databricks UI

1. Create secret scope `omop-app` with required secrets
2. Upload code to Workspace folder
3. Go to **Compute** → **Apps** → **Create App**
4. Select source code path and click **Deploy**

## Testing Locally Before Deployment

You can still test locally using the existing development script:

```bash
./run_dev.sh
```

This runs both services with hot-reload for development.

## Migration Notes

**No changes required to existing code!**

The application code remains unchanged. Only deployment configuration was added:

- ✅ Backend code unchanged (`backend/app/`)
- ✅ Frontend code unchanged (`frontend/src/`)
- ✅ Local development script unchanged (`run_dev.sh`)
- ✅ Environment files unchanged (`backend/.env`, `frontend/.env`)

**What's new:**

- ✅ Root `package.json` for Databricks Apps
- ✅ `app.yaml` for deployment configuration
- ✅ Deployment documentation

## Next Steps

1. **Set up secrets** in Databricks workspace
2. **Test locally** to ensure everything works: `./run_dev.sh`
3. **Deploy** using CLI or UI (see `docs/DATABRICKS_APP_DEPLOYMENT.md`)
4. **Access** your app via the Databricks Apps URL
5. **Monitor** logs in the Databricks UI

## Support

For detailed instructions, see:
- **[docs/DATABRICKS_APP_DEPLOYMENT.md](./docs/DATABRICKS_APP_DEPLOYMENT.md)** - Full deployment guide
- **[README.md](./README.md)** - Project overview and features
- **[docs/CREATE_ENV.md](./docs/CREATE_ENV.md)** - Environment setup

## References

- [Databricks Apps Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [Databricks Apps Deployment Logic](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy#deployment-logic)

