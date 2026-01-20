# Creating Your .env File (Local Development)

**Note:** This guide is for **local development only**. If you're deploying to **Databricks Apps** (recommended for production), you don't need to create a `.env` file - see the [Databricks App Deployment Guide](./DATABRICKS_APP_DEPLOYMENT.md) instead.

The `.env` file is required to run the backend locally. It contains your Databricks OAuth credentials and configuration.

## Quick Setup

Run this command from the `backend` directory:

```bash
cp env.template .env
```

Then edit `.env` with your actual Databricks credentials.

## Required Configuration

You **must** update these three values in your `.env` file:

### 1. DATABRICKS_HOST

Your Databricks workspace URL (without `https://`)

**How to find it:**
- Look at your browser URL when logged into Databricks
- Example: If URL is `https://mycompany.cloud.databricks.com/`, use `mycompany.cloud.databricks.com`

```env
DATABRICKS_HOST=mycompany.cloud.databricks.com
```

### 2. OAuth Service Principal Credentials

This application uses **OAuth M2M (Machine-to-Machine)** authentication with service principals (recommended by Databricks for production-grade security).

**How to get OAuth credentials:**
1. Log into Databricks
2. Go to **Settings** → **User Management** → **Service Principals**
3. Create a new service principal or select an existing one
4. Click on the service principal name
5. Go to **Secrets** tab
6. Click **Generate secret**
7. **Copy both the Client ID and Secret immediately** (secret shown only once!)

```env
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-oauth-secret
```

**Important:** Make sure to grant the service principal:
- `CAN USE` permission on your SQL Warehouse
- `USE CATALOG` and `USE SCHEMA` on your OMOP data

### 3. DATABRICKS_HTTP_PATH

The HTTP path to your SQL Warehouse or Cluster

**How to find it:**
1. Go to **SQL Warehouses** (or **Compute** → **Clusters**)
2. Select your warehouse/cluster
3. Click **Connection Details** tab
4. Copy the **HTTP Path** value

```env
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123def456
```

## Optional Configuration

These have sensible defaults but you may need to update them:

### OMOP_CATALOG

The catalog where your OMOP tables are stored.

- Default: `hive_metastore` (classic Databricks)
- Unity Catalog: `your_catalog_name`

```env
OMOP_CATALOG=hive_metastore
```

### OMOP_SCHEMA

The schema/database name where your OMOP tables are stored.

```env
OMOP_SCHEMA=omop_cdm
```

**How to verify:**
Run this in Databricks SQL:
```sql
SHOW TABLES IN your_catalog.your_schema;
-- Should show: person, condition_occurrence, drug_exposure, etc.
```

## Complete Example

Here's what a complete `.env` file looks like for local development:

```env
# Databricks Configuration
DATABRICKS_HOST=mycompany.cloud.databricks.com
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123def456

# OAuth Service Principal (required)
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-oauth-secret

# OMOP Database Configuration
OMOP_CATALOG=vantage_rwe
OMOP_SCHEMA=omop

# GenAI Configuration (optional)
DATABRICKS_GENIE_SPACE_ID=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# SSL Configuration
DATABRICKS_VERIFY_SSL=true
```

## Verify Your Configuration

After creating your `.env` file, test the connection:

```bash
cd backend
python test_connection.py
```

You should see:
```
✅ Basic connection successful!
✅ person: XXX rows
✅ condition_occurrence: XXX rows
...
```

## Troubleshooting

### "File not found" error when starting backend

**Problem:** The `.env` file doesn't exist

**Solution:**
```bash
cd backend
cp env.template .env
# Edit .env with your credentials
```

### "Invalid access token" or "401 Unauthorized" error

**Problem:** OAuth credentials are wrong, expired, or malformed

**Solution:**
1. Generate a new OAuth secret for your service principal in Databricks
2. Make sure you copied both the Client ID and Secret completely
3. Don't include quotes around the values in .env
4. Verify the service principal has permissions on SQL Warehouse and OMOP data

### "Table not found" error

**Problem:** OMOP_CATALOG or OMOP_SCHEMA is wrong

**Solution:**
1. Run `SHOW DATABASES;` in Databricks to see available schemas
2. Update OMOP_SCHEMA in .env
3. If using Unity Catalog, also update OMOP_CATALOG

### Connection timeout

**Problem:** SQL Warehouse is stopped or HTTP path is wrong

**Solution:**
1. Start your SQL Warehouse in Databricks
2. Verify the HTTP Path in Connection Details
3. Check for typos in DATABRICKS_HOST

## Security Notes

⚠️ **Important Security Information:**

1. **Never commit `.env` to git** - It's already in `.gitignore`
2. **Don't share your OAuth credentials** - They provide access to your Databricks workspace
3. **Rotate secrets regularly** - Regenerate OAuth secrets periodically for security
4. **Use Databricks Apps for production** - Credentials are auto-managed securely
5. **Use service principals** - Never use personal user credentials for applications

## Why No Hard-Coded Values?

The `config.py` file uses **Pydantic Settings** which:

✅ Loads from environment variables and `.env` file  
✅ Provides type validation  
✅ Has sensible defaults for optional values  
✅ Keeps secrets out of code  
✅ Makes configuration easy to change  
✅ Same configuration format for local and production

The values in `config.py` like `"vantage_rwe"` and `"omop"` are just **defaults** that can be overridden by your `.env` file. The required values (`databricks_host`, `databricks_client_id`, `databricks_client_secret`, `databricks_http_path`) have no defaults - you **must** provide them in `.env` for local development.

**For Databricks Apps:** These values are provided automatically through `app.yaml` configuration and secrets, so no `.env` file is needed.


