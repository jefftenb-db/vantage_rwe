# OAuth Service Principal Setup for Databricks Apps

This document explains how authentication works for the Vantage RWE application when deployed as a Databricks App versus running locally.

## 🚀 Databricks Apps Deployment (Automatic)

When deployed as a Databricks App, authentication **happens automatically**:

✅ **No configuration needed!** 

Databricks Apps automatically provides these environment variables:
- `DATABRICKS_HOST` - Your workspace hostname
- `DATABRICKS_HTTP_PATH` - SQL Warehouse HTTP path
- `DATABRICKS_GENIE_SPACE_ID` - Genie Space ID (if configured)
- `DATABRICKS_CLIENT_ID` - Your app's service principal client ID
- `DATABRICKS_CLIENT_SECRET` - Your app's service principal OAuth secret

The application will automatically use OAuth M2M authentication with these credentials.

**You only need to configure in `app.yaml`:**
- `OMOP_CATALOG` - Your OMOP catalog name
- `OMOP_SCHEMA` - Your OMOP schema name
- API and CORS settings (already pre-configured)

### What You Need to Verify:

1. **Service Principal Permissions**
   - Go to **Compute** → **SQL Warehouses**
   - Select your warehouse → **Permissions** tab
   - Ensure your app's service principal has `Can Use` permission

2. **Data Access**
   - Verify the service principal has access to:
     - Catalog: `vantage_rwe` (or your OMOP catalog)
     - Schema: `omop` (or your OMOP schema)
     - All OMOP tables

## 💻 Local Development

For local development, you **must use OAuth** service principal authentication (same as production):

### Setting Up OAuth for Local Development:

1. **Create a Service Principal**:
   - Settings → User Management → Service Principals
   - Add service principal

2. **Generate OAuth Secret**:
   - Select your service principal
   - Secrets tab → Generate secret
   - Copy Client ID and Secret

3. **Grant Permissions**:
   - SQL Warehouse access
   - OMOP data access

4. **Update your `.env` file**:
   ```bash
   DATABRICKS_HOST=your-workspace.cloud.databricks.com
   DATABRICKS_CLIENT_ID=your-service-principal-client-id
   DATABRICKS_CLIENT_SECRET=your-oauth-secret
   DATABRICKS_HTTP_PATH=/sql/1.0/warehouses/abc123
   OMOP_CATALOG=vantage_rwe
   OMOP_SCHEMA=omop
   ```

## 🔍 Authentication Flow

The application **requires OAuth M2M authentication**:

**OAuth M2M** (required):
- Uses `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET`
- Automatically generates and refreshes access tokens
- Tokens valid for 1 hour, auto-refreshed
- ✅ Same behavior in all environments
- ✅ Production-ready security

## 📊 Verification

Check the application logs to confirm authentication:

### Expected Logs (OAuth M2M):
```
Using OAuth M2M authentication with service principal
OAuth credentials detected:
  - client_id: abc12345... (length: 36)
  - client_secret: ****** (length: 64)
GenAI service using OAuth M2M authentication
Requesting OAuth token from https://your-host/oidc/v1/token
OAuth M2M token obtained successfully
Connecting to Databricks using OAuth M2M (service principal)
```

## 🔧 Troubleshooting

### "Error 500" or Authentication Errors

**In Databricks Apps:**
1. Check that the service principal has SQL Warehouse access
2. Verify data permissions on the OMOP catalog/schema
3. Check app logs for specific error messages

**Locally:**
1. Verify your `.env` file has the correct credentials
2. Test your token/credentials work in Databricks SQL directly
3. Check that SSL verification is appropriate for your network (`DATABRICKS_VERIFY_SSL`)

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Invalid credentials | Regenerate token or OAuth secret |
| `403 Forbidden` | Missing permissions | Grant SQL Warehouse and data access |
| `SSL certificate verify failed` | Corporate proxy | Set `DATABRICKS_VERIFY_SSL=false` (dev only!) |
| `No module named uvicorn` | Wrong Python environment | Activate virtual environment |

## 📚 References

- [Databricks OAuth M2M Authentication](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m)
- [Databricks Apps Documentation](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy)
- [Service Principals](https://docs.databricks.com/administration-guide/users-groups/service-principals.html)

## 🎯 Best Practices

**All Environments (Production & Development):**
- ✅ Use OAuth M2M with service principal
- ✅ Grant least-privilege access
- ✅ Monitor service principal usage
- ✅ Keep `.env` file in `.gitignore`
- ✅ Rotate OAuth secrets regularly (max 2 years)
- ✅ Consistent authentication everywhere

## 🔒 Security Notes

1. **Never commit secrets** - `.env` is in `.gitignore`
2. **Rotate credentials regularly** - OAuth secrets can be rotated without downtime
3. **Use service principals for apps** - Don't use personal tokens in production
4. **Monitor access** - Review service principal activity in Databricks audit logs

