# Creating Your .env File

The `.env` file is required to run the backend. It contains your Databricks credentials and configuration.

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

### 2. DATABRICKS_TOKEN

A personal access token for authentication

**How to get it:**
1. Log into Databricks
2. Click your username (top right) → **Settings**
3. Go to **Developer** → **Access tokens**
4. Click **Manage** → **Generate new token**
5. Give it a name (e.g., "OMOP Cohort Builder")
6. Set expiration (recommended: 90 days)
7. Click **Generate**
8. **Copy the token immediately** (it only shows once!)

```env
DATABRICKS_TOKEN=dapi1234567890abcdef1234567890ab
```

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

Here's what a complete `.env` file looks like:

```env
# Databricks Configuration
DATABRICKS_HOST=mycompany.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef1234567890ab
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123def456

# OMOP Database Configuration
OMOP_CATALOG=hive_metastore
OMOP_SCHEMA=omop_cdm

# GenAI Configuration (optional)
DATABRICKS_GENIE_SPACE_ID=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
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

### "Invalid access token" error

**Problem:** Token is wrong, expired, or malformed

**Solution:**
1. Generate a new token in Databricks
2. Make sure you copied the entire token
3. Don't include quotes around the token in .env

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
2. **Don't share your token** - It provides full access to your Databricks workspace
3. **Rotate tokens regularly** - Set expiration dates and regenerate periodically
4. **Use service principals in production** - Personal tokens are for development only

## Why No Hard-Coded Values?

The `config.py` file uses **Pydantic Settings** which:

✅ Loads from environment variables and `.env` file  
✅ Provides type validation  
✅ Has sensible defaults for optional values  
✅ Keeps secrets out of code  
✅ Makes configuration easy to change  

The values in `config.py` like `"hive_metastore"` and `"omop_cdm"` are just **defaults** that can be overridden by your `.env` file. The required values (`databricks_host`, `databricks_token`, `databricks_http_path`) have no defaults - you **must** provide them in `.env`.


