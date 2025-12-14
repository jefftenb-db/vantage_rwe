# Databricks Genie Setup Guide

This guide explains how to set up Databricks Genie for natural language queries in Vantage RWE.

## What is Databricks Genie?

Databricks Genie is an AI-powered conversational interface that allows you to ask questions about your data in natural language. It automatically generates SQL queries and returns results.

## Prerequisites

- Databricks workspace with Genie enabled
- Access to create or use Genie Spaces
- Personal Access Token with appropriate permissions

## Step 1: Find or Create a Genie Space

### Finding Your Genie Space

1. Log into your Databricks workspace
2. Click on **Genie** in the left sidebar (or go to `/genie` in your workspace URL)
3. You'll see a list of available Genie Spaces

### Creating a New Genie Space

If you need to create a new Genie Space:

1. Go to **Genie** in your workspace
2. Click **Create Space** (or **New Space**)
3. Configure the space:
   - **Name**: "OMOP CDM Space" (or similar)
   - **Description**: "Natural language queries for OMOP clinical data"
   - **Catalog/Schema**: Select your OMOP catalog and schema (e.g., `hive_metastore.omop_cdm`)
   - **Tables**: Include all OMOP tables you want to query
4. Click **Create**

### Getting the Genie Space ID

Once you have a Genie Space:

1. Open the Genie Space
2. Look at the URL in your browser:
   ```
   https://your-workspace.cloud.databricks.com/genie/spaces/<SPACE_ID>
   ```
3. Copy the **SPACE_ID** (it's a UUID like `01f0d5f6-f7a7-148a-ac7e-609bbd32aa31`)

## Step 2: Configure Vantage RWE

### For Local Development

Add the Genie Space ID to your `backend/.env` file:

```env
DATABRICKS_GENIE_SPACE_ID=01f0d5f6-f7a7-148a-ac7e-609bbd32aa31
```

### For Databricks Apps Deployment

Add the Genie Space ID to your secrets:

```bash
databricks secrets put-secret omop-app genie_space_id --string-value "01f0d5f6-f7a7-148a-ac7e-609bbd32aa31"
```

Or update your `app.yaml` to use a static value instead of a secret:

```yaml
env:
  - name: DATABRICKS_GENIE_SPACE_ID
    value: "01f0d5f6-f7a7-148a-ac7e-609bbd32aa31"  # Your actual Space ID
```

## Step 3: Verify Permissions

Make sure your token has permission to access the Genie Space:

1. Go to your Genie Space in Databricks
2. Click **Permissions** or **Share**
3. Ensure your user account (or service principal) has at least **Can Use** permission

## Step 4: Test the Configuration

### Test from the UI

1. Start your application
2. Go to the **GenAI Query** tab
3. Enter a test query like:
   ```
   Show me patients with Type 2 Diabetes
   ```
4. Click **Search**
5. You should see AI-generated results

### Test from the Backend

You can test the connection directly:

```python
from app.services.genai_service import genai_service
from app.models.cohort import NaturalLanguageQuery

query = NaturalLanguageQuery(query="Show me patients with diabetes")
response = genai_service.process_natural_language_query(query)
print(response.explanation)
```

## Troubleshooting

### Error: 404 Not Found

**Symptoms**: Error message like "404 Client Error: Not Found for url: .../start-conversation"

**Possible Causes**:
1. **Incorrect Genie Space ID** - Double-check the ID from the URL
2. **Space doesn't exist** - Verify the space is still available in your workspace
3. **Wrong workspace** - Make sure you're using the correct Databricks host

**Solution**:
```bash
# Check your .env file
cat backend/.env | grep GENIE

# Verify the space exists by visiting:
# https://YOUR_WORKSPACE/genie/spaces/YOUR_SPACE_ID
```

### Error: 403 Forbidden

**Symptoms**: Error message about access denied

**Possible Causes**:
1. Token doesn't have permission to access the Genie Space
2. Service principal not granted access

**Solution**:
1. Go to the Genie Space in Databricks UI
2. Click **Permissions**
3. Add your user/service principal with "Can Use" permission

### Genie Not Configured (Fallback Mode)

**Symptoms**: Warning message "Genie Space ID not configured, falling back to rule-based approach"

**Cause**: `DATABRICKS_GENIE_SPACE_ID` environment variable is not set or is empty

**Solution**:
```bash
# Add to backend/.env
echo "DATABRICKS_GENIE_SPACE_ID=your-space-id-here" >> backend/.env

# Restart the backend
```

### SSL Certificate Errors

**Symptoms**: SSL verification errors when connecting to Genie

**Solution**: Temporarily disable SSL verification (development only):

```env
# In backend/.env
DATABRICKS_VERIFY_SSL=false
```

⚠️ **Warning**: Do not disable SSL verification in production!

## Fallback Behavior

If Genie is not configured or encounters an error, Vantage RWE automatically falls back to a rule-based pattern matching approach:

1. **Pattern Matching**: Extracts medical terms from the query
2. **Concept Search**: Searches OMOP concepts for matched terms
3. **Cohort Building**: Creates a cohort definition with found concepts
4. **Execution**: Runs the cohort query

This provides basic functionality even without Genie, but with limited capabilities compared to AI-powered queries.

## Genie Space Best Practices

### Include Relevant Tables

Make sure your Genie Space includes these OMOP tables:
- `person` - Patient demographics
- `condition_occurrence` - Diagnoses
- `drug_exposure` - Medications
- `procedure_occurrence` - Procedures
- `visit_occurrence` - Healthcare visits
- `observation` - Lab results and measurements
- `concept` - Vocabulary lookups

### Add Instructions (Optional)

You can add custom instructions to your Genie Space to guide query generation:

```
This space contains OMOP CDM 5.4 healthcare data. 
When counting patients, use person_id from the person table.
For drug prescriptions, join drug_exposure with drug_concept table.
```

### Sample Queries

Add sample queries to help users:
- "How many patients have Type 2 Diabetes?"
- "Show me patients prescribed Metformin in 2023"
- "What are the most common conditions in patients over 65?"

## Advanced: Using Genie API Directly

If you want to use the Genie API outside of Vantage RWE:

```python
import requests

# Configuration
workspace = "your-workspace.cloud.databricks.com"
token = "your-token"
space_id = "your-space-id"

# Start conversation
url = f"https://{workspace}/api/2.0/genie/spaces/{space_id}/start-conversation"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
payload = {
    "content": "Show me patients with diabetes"
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

print(f"Conversation ID: {data['conversation']['id']}")
print(f"Message ID: {data['message']['id']}")
```

## Resources

- [Databricks Genie Documentation](https://docs.databricks.com/genie/)
- [Genie API Reference](https://docs.databricks.com/api/workspace/genie)
- [OMOP CDM Documentation](https://ohdsi.github.io/CommonDataModel/)

## Support

If you continue to have issues:
1. Check the backend logs for detailed error messages
2. Verify all environment variables are set correctly
3. Test the Genie Space directly in the Databricks UI
4. Ensure your token has the necessary permissions

