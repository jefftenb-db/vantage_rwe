# Databricks App Deployment Guide

This guide explains how to deploy Vantage RWE as a Databricks App.

## Overview

Vantage RWE is configured to run as a Databricks App with a FastAPI backend serving a built React frontend. The deployment process automatically:

1. Installs Node.js dependencies (`npm install`) - root and frontend
2. Installs Python dependencies (`pip install -r requirements.txt`)
3. Builds the React frontend to static files (`npm run build`)
4. Starts the FastAPI backend on port 8080, which serves both:
   - API endpoints at `/api/v1/*`
   - React static files for all other routes

**Note**: In production, the app runs as a single FastAPI server (not two concurrent servers). The backend serves the pre-built React static files, ensuring a single port and unified deployment suitable for Databricks Apps.

## Prerequisites

Before deploying, ensure you have:

- **Databricks Workspace** with Apps feature enabled
- **OMOP CDM data** loaded in your Databricks workspace
- **SQL Warehouse or Cluster** running with access to OMOP data
- **Personal Access Token** or service principal credentials
- **Databricks CLI** installed (for CLI deployment)

## Production Architecture

### Development vs Production

**Development Mode** (`npm run dev`):
- Frontend dev server on port 3000 (with hot reload)
- Backend API server on port 8000
- CORS enabled between the two servers

**Production Mode** (`npm start` - used by Databricks Apps):
- Single FastAPI server on port 8080
- Serves pre-built React static files from `/frontend/build`
- API routes at `/api/v1/*`
- React routing handled via catch-all route

### How It Works

1. **Build Phase**: React app is built to static HTML/CSS/JS in `frontend/build/`
2. **Runtime**: FastAPI mounts the build directory and serves:
   - Static assets (JS, CSS, images) at `/static/*`
   - React app entry point (`index.html`) for all non-API routes
   - API endpoints at `/api/v1/*`
3. **Routing**: React Router handles client-side routing after the initial page load

This architecture ensures:
- Single port deployment (required for Databricks Apps)
- No CORS issues (same origin for frontend and backend)
- Efficient static file serving
- Clean separation between API and UI routes

## Step 1: Set Up Databricks Secrets

Databricks Apps uses secrets to securely manage credentials. Create a secret scope and add your credentials:

### Using Databricks CLI

```bash
# Create a secret scope (if it doesn't exist)
databricks secrets create-scope omop-app

# Add secrets
databricks secrets put-secret omop-app databricks_host --string-value "your-workspace.cloud.databricks.com"
databricks secrets put-secret omop-app databricks_token --string-value "dapi1234567890abcdef"
databricks secrets put-secret omop-app databricks_http_path --string-value "/sql/1.0/warehouses/abc123xyz789"
databricks secrets put-secret omop-app genie_space_id --string-value "your-genie-space-id"  # Optional
```

### Using Databricks UI

1. Go to your Databricks workspace
2. Navigate to **Settings** → **Secrets**
3. Create a new scope named `omop-app`
4. Add the following secrets:
   - `databricks_host` - Your Databricks workspace URL (without https://)
   - `databricks_token` - Your personal access token or service principal token
   - `databricks_http_path` - SQL Warehouse or cluster HTTP path
   - `genie_space_id` - (Optional) Genie Space ID for natural language queries

## Step 2: Prepare Your Code

Ensure your project structure matches:

```
vantage-rwe/
├── app.yaml                    # Databricks App configuration
├── package.json                # Root package.json with concurrently
├── requirements.txt            # Python dependencies
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   └── .env.example
└── frontend/                   # React frontend
    ├── package.json
    ├── src/
    └── ...
```

## Step 3: Deploy Using Databricks CLI

### Install Databricks CLI

```bash
pip install databricks-cli
databricks configure --token
```

### Sync Your Code to Workspace

```bash
# Navigate to your project directory
cd /path/to/vantage-rwe

# Sync files to workspace (excluding common dev files)
databricks sync --watch . /Workspace/Users/your-email@org.com/vantage-rwe
```

**Tip**: Create a `.gitignore` file to exclude unnecessary files from syncing:

```gitignore
# Development files
node_modules/
__pycache__/
*.pyc
.DS_Store
.env
.env.local
venv/
logs/

# Build artifacts
frontend/build/
dist/
*.egg-info/
```

### Deploy the App

```bash
# Deploy the app
databricks apps deploy vantage-rwe \
   --source-code-path /Workspace/Users/your-email@org.com/vantage-rwe
```

The CLI will display deployment progress and confirm when the app is running.

## Step 4: Deploy Using Databricks UI

1. **Upload Files**:
   - Go to **Workspace** in the sidebar
   - Navigate to your desired folder (e.g., `/Users/your-email@org.com/`)
   - Create a new folder called `vantage-rwe`
   - Upload your project files (excluding `node_modules/`, `venv/`, etc.)

2. **Create App**:
   - Click **Compute** in the sidebar
   - Go to the **Apps** tab
   - Click **Create App**
   - Name: `vantage-rwe`
   - Source Code Path: `/Workspace/Users/your-email@org.com/vantage-rwe`

3. **Deploy**:
   - Click **Deploy**
   - Wait for deployment to complete (this may take several minutes)

## Step 5: Access Your App

Once deployed, you can access your app:

1. Go to **Compute** → **Apps** tab
2. Click on your app name (`vantage-rwe`)
3. Click the **App URL** to open the application

The app will be accessible at a URL like:
```
https://<workspace-url>/apps/<app-id>
```

## Configuration Reference

### app.yaml Structure

```yaml
command: ["npm", "run", "start"]  # Command to start the app

env:
  # Environment variables (can reference secrets)
  - name: VARIABLE_NAME
    value: "{{secrets/scope-name/secret-key}}"
```

### Environment Variables

The `app.yaml` file configures these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABRICKS_HOST` | Databricks workspace URL | `your-workspace.cloud.databricks.com` |
| `DATABRICKS_TOKEN` | Access token | `dapi1234567890abcdef` |
| `DATABRICKS_HTTP_PATH` | SQL Warehouse path | `/sql/1.0/warehouses/abc123xyz789` |
| `OMOP_CATALOG` | OMOP catalog name | `hive_metastore` |
| `OMOP_SCHEMA` | OMOP schema name | `omop_cdm` |
| `DATABRICKS_GENIE_SPACE_ID` | Genie Space ID (optional) | `01abc234-5678-90de-f123-456789abcdef` |
| `API_HOST` | Backend host | `0.0.0.0` |
| `API_PORT` | Backend port | `8080` (Databricks Apps standard) |
| `REACT_APP_API_URL` | Frontend API URL | `/api/v1` (relative path for same-origin) |
| `CORS_ORIGINS` | Allowed CORS origins (supports wildcards) | `http://localhost:3000,https://*.databricks.com` |

**Note on CORS_ORIGINS**: The application supports both exact origins and wildcard patterns:
- Exact origins: `http://localhost:3000` (matched literally)
- Wildcard patterns: `https://*.databricks.com` (converted to regex automatically)
- Multiple origins: Separate with commas
- The wildcard `*` matches any characters, allowing all Databricks workspace URLs

## Troubleshooting

### Deployment Fails

**Check logs**:
1. Go to your app in the Databricks UI
2. Click the **Logs** tab
3. Review error messages

**Common issues**:
- **Missing secrets**: Ensure all secrets are created in the correct scope
- **Wrong paths**: Verify the HTTP path points to a running SQL Warehouse
- **Permissions**: Ensure the app service principal has access to OMOP data

### App Won't Start / "App is currently unavailable"

This error typically means the app isn't listening on the correct port or hasn't started properly.

**Check the port configuration**:
- Databricks Apps expects port **8080** by default
- Verify `API_PORT` in `app.yaml` is set to `8080`
- Ensure your start command properly uses this port

**Check the command**:
- Verify `app.yaml` has the correct command: `["npm", "run", "start"]`
- Ensure `package.json` has the `start` script that runs the production server
- The start script should run FastAPI on port 8080, NOT `concurrently` with two servers

**Check dependencies**:
- Verify `requirements.txt` includes all Python packages (especially `uvicorn`)
- Verify frontend dependencies are installed via `postinstall` script
- Check logs for any import errors or missing packages

**Check build artifacts**:
- Ensure the React build completed successfully
- Verify `frontend/build/` directory exists with static files
- Check logs for build errors during deployment

**Common fix**:
If you see "npm build: exit status 127", it means frontend dependencies aren't installed. Add this to `package.json`:
```json
"postinstall": "cd frontend && npm install"
```

### Can't Connect to Database

**Verify credentials**:
```bash
# Test connection using Python
cd backend
python test_connection.py
```

**Check SQL Warehouse**:
- Ensure the SQL Warehouse is running
- Verify the HTTP path is correct
- Check that the token has access permissions

### Frontend Can't Reach Backend

**Check CORS settings**:
- The default `CORS_ORIGINS` includes `https://*.databricks.com` which matches all Databricks workspaces
- Wildcard patterns are automatically converted to regex for proper matching
- For specific workspaces, you can use exact URLs: `https://myworkspace.cloud.databricks.com`
- Verify `REACT_APP_API_URL` points to the correct backend URL
- Check browser console for CORS errors (they typically mention "Origin 'https://...' has been blocked")

**For Databricks Apps**, you may need to update the frontend API URL to use relative paths or the app's URL.

## Updating the App

To update your deployed app after making changes:

1. **Sync changes**:
```bash
databricks sync . /Workspace/Users/your-email@org.com/vantage-rwe
```

2. **Redeploy**:
```bash
databricks apps deploy vantage-rwe \
   --source-code-path /Workspace/Users/your-email@org.com/vantage-rwe
```

Or use the UI:
1. Go to **Compute** → **Apps**
2. Click your app
3. Click **Deploy** (or **Deploy using different source code path**)

## Best Practices

1. **Use secrets** for all sensitive credentials (never hardcode tokens)
2. **Exclude dev files** from deployment using `.gitignore`
3. **Test locally first** using `./run_dev.sh` before deploying
4. **Monitor logs** after deployment to catch issues early
5. **Use service principals** for production deployments (not personal tokens)
6. **Version your deployments** by tagging releases in git

## Production Considerations

### Security
- Use service principal tokens instead of personal access tokens
- Rotate secrets regularly
- Limit access to the app and secrets using Databricks ACLs
- Enable audit logging

### Performance
- Use a SQL Warehouse (not cluster) for better cost management
- Configure warehouse auto-stop to save costs
- Consider caching frequently accessed data
- Monitor query performance using Databricks SQL Query History

### Scaling
- SQL Warehouse auto-scales based on demand
- For high traffic, consider using a larger warehouse size
- Implement rate limiting in the backend if needed

## Additional Resources

- [Databricks Apps Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [Databricks Secrets Management](https://docs.databricks.com/security/secrets/index.html)
- [Databricks CLI Reference](https://docs.databricks.com/dev-tools/cli/index.html)
- [OMOP CDM Documentation](https://ohdsi.github.io/CommonDataModel/)

## Support

For issues or questions:
- Check the `/docs` folder for additional guides
- Review Databricks Apps logs for error messages
- Consult the OMOP CDM documentation for data model questions

