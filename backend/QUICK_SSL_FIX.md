# Quick SSL Fix for Corporate Proxy/Firewall

If you're getting SSL certificate verification errors, follow these steps:

## 1. Check Your .env File

Make sure your `backend/.env` file has this line:

```env
DATABRICKS_VERIFY_SSL=false
```

## 2. Verify Your Complete .env

Your `backend/.env` should look like this:

```env
# Databricks Configuration
DATABRICKS_HOST=dbc-78714b34-ad30.cloud.databricks.com
DATABRICKS_TOKEN=your_actual_token_here
DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/fb2df48581a44595

# OMOP Database Configuration
OMOP_CATALOG=hive_metastore
OMOP_SCHEMA=omop_cdm

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# SSL Configuration - CRITICAL FOR CORPORATE PROXIES
DATABRICKS_VERIFY_SSL=false
```

## 3. Test the Connection

```bash
cd backend

# Make sure you're in the virtual environment
source ../.venv/bin/activate

# Test the connection
python test_connection.py
```

## 4. If Still Not Working

Try setting these environment variables before running:

```bash
# Option 1: Set for single command
DATABRICKS_VERIFY_SSL=false python test_connection.py

# Option 2: Export for session
export DATABRICKS_VERIFY_SSL=false
export PYTHONHTTPSVERIFY=0
python test_connection.py
```

## 5. Start the Backend

Once the connection test works:

```bash
uvicorn app.main:app --reload
```

## Troubleshooting

### Still Getting SSL Errors?

1. **Check the .env file exists:**
   ```bash
   ls -la .env
   cat .env | grep VERIFY_SSL
   ```

2. **Make sure the virtual environment is activated:**
   ```bash
   which python
   # Should show: /Users/jeff.tenbosch/code/cursor/omop/.venv/bin/python
   ```

3. **Try the nuclear option (development only):**
   ```bash
   export PYTHONHTTPSVERIFY=0
   export CURL_CA_BUNDLE=""
   export REQUESTS_CA_BUNDLE=""
   python test_connection.py
   ```

### Why This Happens

Your network has a corporate proxy or firewall that:
- Intercepts HTTPS connections
- Uses its own SSL certificate (self-signed)
- Causes Python to reject the connection

This is common in enterprise environments and the fix is safe for development/testing.

### Security Note

⚠️ **IMPORTANT:** 
- This is **safe for development** behind a corporate firewall
- **DO NOT** use `DATABRICKS_VERIFY_SSL=false` in production
- For production, work with IT to install proper certificates

