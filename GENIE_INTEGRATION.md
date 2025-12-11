# Databricks Genie API Integration - Vantage RWE

**Commercial Intelligence from Real-World Evidence**

This document explains how the Databricks Genie Conversation API is integrated into Vantage RWE.

## Overview

The application now uses the **Databricks Genie Conversation API** to process natural language queries about patient cohorts. Genie converts your questions into SQL queries and executes them against your OMOP data.

## Configuration

### Required Environment Variable

In your `backend/.env` file, make sure you have:

```env
DATABRICKS_GENIE_SPACE_ID=your_genie_space_id_here
```

You can find your Genie Space ID:
1. Open your Genie Space in Databricks
2. Look at the URL: `https://<host>/genie/rooms/<space-id>`
3. Copy the `<space-id>` portion

## How It Works

### API Flow

The integration follows the [Databricks Genie Conversation API](https://docs.databricks.com/aws/en/genie/conversation-api) workflow:

1. **Start Conversation** (`POST /api/2.0/genie/spaces/{space_id}/start-conversation`)
   - Sends your natural language question to Genie
   - Returns conversation_id and message_id

2. **Poll for Completion** (`GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}`)
   - Polls every 2-10 seconds (exponential backoff)
   - Waits up to 120 seconds for Genie to generate SQL
   - Checks for status: `IN_PROGRESS`, `COMPLETED`, `FAILED`, or `CANCELLED`

3. **Execute SQL**
   - Extracts the generated SQL from Genie's response
   - Executes it against your OMOP database
   - Returns patient count and results

### Fallback Behavior

If Genie is not configured or fails:
- The system automatically falls back to rule-based pattern matching
- Looks for keywords like "diabetes", "metformin", "surgery"
- Creates simple cohort criteria based on matched terms

## Usage

### Frontend - Natural Language Search

Users can type questions like:
- "Find patients with diabetes"
- "Show me patients with heart failure who visited the ER"
- "Patients on metformin with HbA1c > 7"

### Backend Endpoint

```
POST /api/v1/genai/query
{
  "query": "Find patients with diabetes and hypertension"
}
```

**Response:**
```json
{
  "query": "Find patients with diabetes and hypertension",
  "sql_generated": "SELECT DISTINCT person_id FROM ...",
  "cohort_definition": {...},
  "result_count": 1234,
  "explanation": "Genie's explanation of the query..."
}
```

## Implementation Details

### Code Location

**Backend Service:** `backend/app/services/genai_service.py`

### Key Methods

1. **`process_natural_language_query()`**
   - Main entry point for natural language queries
   - Orchestrates the Genie API workflow

2. **`_start_genie_conversation()`**
   - Initiates a new Genie conversation
   - Sends the user's question to Genie

3. **`_poll_message_status()`**
   - Polls for message completion
   - Uses exponential backoff (2s → 10s intervals)
   - Times out after 120 seconds

4. **`_fallback_rule_based_query()`**
   - Fallback when Genie is unavailable
   - Simple pattern matching approach

### SSL Handling

The integration respects your `DATABRICKS_VERIFY_SSL` setting:
```python
verify=not settings.databricks_verify_ssl
```

## Best Practices

Based on [Databricks recommendations](https://docs.databricks.com/aws/en/genie/conversation-api#best-practices-for-using-the-genie-api):

1. ✅ **Polling Strategy Implemented**
   - Poll every 2-10 seconds with exponential backoff
   - Maximum wait time: 120 seconds
   - Handles COMPLETED, FAILED, and CANCELLED states

2. ✅ **Error Handling**
   - Graceful fallback to rule-based approach
   - Comprehensive logging for debugging
   - SSL configuration support

3. ✅ **New Conversation Per Query**
   - Each query starts a fresh conversation
   - Avoids context pollution

## Testing

### Test the Integration

1. **Via Frontend:**
   - Navigate to the Natural Language Search component
   - Type a question about your patient data
   - Click "Search" or press Enter

2. **Via API:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/genai/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Find patients with diabetes"}'
   ```

### Check Logs

The backend logs will show:
```
INFO - Starting Genie conversation...
INFO - Genie message status: IN_PROGRESS
INFO - Genie message status: COMPLETED
INFO - Generated SQL: SELECT...
```

## Troubleshooting

### Genie Not Working

If queries aren't returning results:

1. **Check Configuration:**
   ```bash
   cd backend
   source ../.venv/bin/activate
   python -c "from app.config import settings; print(f'Genie Space ID: {settings.databricks_genie_space_id}')"
   ```

2. **Verify Space Access:**
   - Ensure your Databricks token has access to the Genie Space
   - Check that the Space ID is correct

3. **Check Logs:**
   - Look for "Genie Space ID not configured" warnings
   - Check for API errors in backend logs

4. **Fallback Behavior:**
   - System automatically falls back to rule-based matching
   - Logs will show: "falling back to rule-based approach"

### Common Issues

**"Failed to start Genie conversation"**
- Check your Databricks token permissions
- Verify the Genie Space ID is correct
- Ensure SSL settings are correct

**"Genie message did not complete successfully"**
- Query may be too complex
- Genie Space may need better curation
- Check Databricks Genie Space logs

**SSL Certificate Errors**
- Make sure `DATABRICKS_VERIFY_SSL=false` in your `.env` file

## Resources

- [Databricks Genie API Documentation](https://docs.databricks.com/aws/en/genie/conversation-api)
- [Genie Best Practices](https://docs.databricks.com/aws/en/genie/best-practices)
- [OMOP CDM Documentation](https://ohdsi.github.io/CommonDataModel/)

## Next Steps

To improve Genie accuracy:

1. **Curate Your Genie Space**
   - Add example SQL queries for common questions
   - Add table and column descriptions
   - Include domain-specific terminology

2. **Add Benchmark Questions**
   - Create test questions you expect from users
   - Run benchmarks to measure accuracy

3. **Monitor Usage**
   - Check the Genie Space monitoring tab
   - Review questions and responses
   - Refine based on user feedback

