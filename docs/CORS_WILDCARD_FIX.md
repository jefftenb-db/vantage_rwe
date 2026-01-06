# CORS Wildcard Pattern Fix

## Problem

The `app.yaml` configuration set `CORS_ORIGINS` to `https://*.databricks.com`, but FastAPI's `CORSMiddleware` does not support wildcard patterns in the `allow_origins` parameter. It treats wildcards as literal strings, which means:

- Configuration: `https://*.databricks.com`
- Actual request origin: `https://myworkspace.cloud.databricks.com`
- Result: **CORS validation fails** ❌

This would cause the frontend (running in Databricks Apps) to be blocked when trying to call the backend API.

## Solution

The fix implements proper wildcard pattern support by:

1. **Detecting wildcard patterns** in `CORS_ORIGINS`
2. **Converting wildcards to regex patterns** automatically
3. **Using `allow_origin_regex`** for wildcard patterns
4. **Using `allow_origins`** for exact domain matches

### How It Works

#### Before (Broken)
```python
# FastAPI treats this as a literal string, not a pattern
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.databricks.com"],  # ❌ Won't work
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### After (Fixed)
```python
# Separates exact origins from wildcard patterns
cors_config = {
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Exact origins
if settings.cors_origins_list:
    cors_config["allow_origins"] = ["http://localhost:3000"]  # ✓ Exact matches

# Regex for wildcards
if settings.cors_origin_regex:
    cors_config["allow_origin_regex"] = r"^(https://.*\.databricks\.com)$"  # ✓ Regex pattern

app.add_middleware(CORSMiddleware, **cors_config)
```

## Files Modified

### 1. `backend/app/config.py`
- Added `cors_origin_regex` property to convert wildcard patterns to regex
- Modified `cors_origins_list` to exclude wildcard patterns
- Patterns like `https://*.databricks.com` → `^(https://.*\.databricks\.com)$`

### 2. `backend/app/main.py`
- Updated CORS middleware configuration to use both `allow_origins` and `allow_origin_regex`
- Added logging to show CORS configuration at startup

### 3. `app.yaml`
- Added comments explaining wildcard support

### 4. Documentation Updates
- Updated `docs/DATABRICKS_APP_DEPLOYMENT.md` with CORS pattern explanation
- Updated `DEPLOYMENT_SETUP.md` to mention wildcard support

## Testing

A test script (`backend/test_cors_config.py`) verifies the CORS configuration:

```bash
cd backend
python3 test_cors_config.py
```

### Test Results
```
✓ All tests PASSED!

The CORS configuration correctly:
  1. Allows exact localhost origins
  2. Matches Databricks wildcard patterns with regex
  3. Blocks malicious/incorrect domains
```

### Example Matches

| Origin URL | Pattern | Matches? |
|------------|---------|----------|
| `http://localhost:3000` | Exact match | ✓ Yes |
| `https://myworkspace.cloud.databricks.com` | `https://*.databricks.com` | ✓ Yes |
| `https://e2-demo-field-eng.cloud.databricks.com` | `https://*.databricks.com` | ✓ Yes |
| `https://company.databricks.com` | `https://*.databricks.com` | ✓ Yes |
| `https://databricks.com.evil.com` | `https://*.databricks.com` | ✗ No (security) |
| `http://notdatabricks.com` | `https://*.databricks.com` | ✗ No |

## Configuration Examples

### Development (localhost only)
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Production (Databricks Apps - all workspaces)
```bash
CORS_ORIGINS=http://localhost:3000,https://*.databricks.com
```

### Production (specific workspace only)
```bash
CORS_ORIGINS=https://myworkspace.cloud.databricks.com
```

### Mixed (local dev + specific production workspace)
```bash
CORS_ORIGINS=http://localhost:3000,https://prod.cloud.databricks.com,https://dev.cloud.databricks.com
```

## How CORS Works with Databricks Apps

When a user accesses your app in Databricks Apps:

1. **User navigates to**: `https://workspace.databricks.com/apps/01234567-89ab-cdef`
2. **Browser sends Origin header**: `https://workspace.databricks.com` (note: no path)
3. **Backend checks CORS**: Matches against `https://*.databricks.com` pattern
4. **Backend responds with**: `Access-Control-Allow-Origin: https://workspace.databricks.com`
5. **Browser allows the request**: ✓ CORS validation passes

**Important**: The Origin header never includes the path (`/apps/...`), only the scheme, host, and port.

## Verification

To verify the fix is working:

1. **Check startup logs**:
```bash
# Look for these log messages when the app starts
INFO - CORS Exact Origins: ['http://localhost:3000']
INFO - CORS Regex Pattern: ^(https://.*\.databricks\.com)$
```

2. **Run tests**:
```bash
cd backend
python3 test_cors_config.py
```

3. **Test in browser**:
- Open browser developer tools (F12)
- Navigate to your Databricks App
- Check Console for any CORS errors
- Check Network tab → Response Headers for `Access-Control-Allow-Origin`

## Security Considerations

✓ **Safe**: `https://*.databricks.com` - Matches all Databricks workspaces
✗ **Unsafe**: `https://*` - Matches ANY domain (DO NOT USE)
✓ **Safe**: Exact domains like `https://prod.cloud.databricks.com`

The regex pattern properly validates the domain structure to prevent attacks like:
- `https://databricks.com.evil.com` ✗ Blocked
- `http://databricks.com` ✗ Blocked (wrong protocol)

## Migration Notes

No changes required for existing deployments. The fix is **backward compatible**:
- Existing exact origins continue to work
- Wildcard patterns now work correctly (previously broken)
- No environment variable changes needed

## References

- [FastAPI CORS Middleware Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN Web Docs: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/)


