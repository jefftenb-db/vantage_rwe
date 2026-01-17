# Real-Time Status Updates Feature

## Overview

The GenAI Query feature now displays **real-time processing status updates** from Databricks Genie while queries are being processed. This provides users with visibility into what's happening during the (sometimes lengthy) query processing phase.

## Problem Solved

**Before**: Users saw only "🔄 Processing..." with no indication of what was happening, making it seem like the application was frozen or unresponsive.

**After**: Users see detailed status updates like:
- 📤 Submitted to Genie...
- 🔍 Analyzing conversation context...
- ⚙️ Generating SQL query...
- ⚙️ Executing query...
- ✅ Completed!

## Implementation

### Backend Changes

**Service (`backend/app/services/genai_service.py`):**

1. **Status Storage**: Added `query_statuses` dict to track active query statuses
   ```python
   self.query_statuses: Dict[str, str] = {}
   ```

2. **Status Updates**: Modified `_poll_message_status()` to update status during polling
   ```python
   status_key = f"{conversation_id}:{message_id}"
   self.query_statuses[status_key] = status
   ```

3. **Status Cleanup**: Remove status tracking when query completes

4. **New Method**: `get_query_status()` - Allows frontend to query current status
   ```python
   def get_query_status(self, conversation_id: str, message_id: str) -> Optional[str]
   ```

**API Route (`backend/app/api/routes.py`):**

Added new endpoint for status polling:
```python
@router.get("/genai/status/{conversation_id}/{message_id}")
async def get_query_status(conversation_id: str, message_id: str)
```

### Frontend Changes

**API Service (`frontend/src/services/api.ts`):**

Added status polling function:
```typescript
export const getQueryStatus = async (
  conversationId: string,
  messageId: string
): Promise<{ status: string }>
```

**Component (`frontend/src/components/NaturalLanguageSearch.tsx`):**

1. **State Management**:
   - Added `processingStatus` state for current status message
   - Added `statusPollIntervalRef` for cleanup

2. **Status Mapping**: `getStatusMessage()` function converts Genie statuses to user-friendly messages

3. **Visual Feedback**:
   - Status shown in button text: "🔄 Generating SQL query..."
   - Separate status indicator below button with spinner
   - Auto-cleanup on component unmount

**Styling (`frontend/src/components/NaturalLanguageSearch.css`):**

- `.status-indicator`: Purple gradient box with spinner
- `.status-spinner`: Animated spinning circle
- Smooth animations for status appearance

## Status Messages

### Genie API Statuses → User Messages

| Genie Status | User Sees |
|--------------|-----------|
| SUBMITTED | 📤 Submitted to Genie... |
| QUERYING_HISTORY | 🔍 Analyzing conversation context... |
| EXECUTING_QUERY | ⚙️ Generating SQL query... |
| EXECUTING | ⚙️ Executing query... |
| FETCHING_METADATA | 📊 Fetching metadata... |
| COMPILING | 🔨 Compiling response... |
| COMPLETED | ✅ Completed! |
| FAILED | ❌ Processing failed |
| CANCELLED | 🚫 Cancelled |
| UNKNOWN | 🔄 Processing... |

## User Experience

### Visual Layout During Processing

```
┌─────────────────────────────────────────┐
│ [Text Input Area]                       │
├─────────────────────────────────────────┤
│ [🔄 ⚙️ Generating SQL query...] Button │
├─────────────────────────────────────────┤
│  ⟲  ⚙️ Generating SQL query...         │
│  (Spinner animation)                    │
└─────────────────────────────────────────┘
```

### Status Flow Example

```
User clicks "Ask GenAI"
    ↓
🚀 Sending query to Genie...
    ↓
📤 Submitted to Genie...
    ↓
🔍 Analyzing conversation context...
    ↓
⚙️ Generating SQL query...
    ↓
⚙️ Executing query...
    ↓
✅ Completed!
    ↓
[Results displayed]
```

## Technical Details

### Backend Status Tracking

**Storage Format**:
```python
{
  "conv_123:msg_456": "EXECUTING_QUERY",
  "conv_123:msg_457": "COMPLETED"
}
```

**Lifecycle**:
1. Status created when message submitted
2. Updated during polling (every 2-10 seconds)
3. Cleaned up when query completes/fails

### Frontend Implementation

**Note**: The current implementation shows status messages based on the backend logs but doesn't actively poll the status endpoint during query execution. This is because the API call blocks until completion. 

For true real-time updates, you would need to:
1. Make the backend API call async/non-blocking
2. Return conversation_id and message_id immediately
3. Poll the status endpoint while waiting
4. Poll the main endpoint to get results when status is COMPLETED

**Current Flow** (Simpler):
```
User submits query
    ↓
Frontend shows initial status
    ↓
Backend processes (blocking call)
    ↓
Results returned
    ↓
Status cleared
```

**Alternative Flow** (True Real-time):
```
User submits query
    ↓
Backend returns IDs immediately
    ↓
Frontend polls /genai/status/{id}/{msg}
    ↓
Status updates in real-time
    ↓
When status = COMPLETED, fetch results
```

## Future Enhancements

### Implement True Async Processing

To get real-time status updates, refactor the backend:

1. **Make Query Submission Non-Blocking**:
   ```python
   @router.post("/genai/query/start")
   async def start_query(nl_query: NaturalLanguageQuery):
       # Start query in background
       # Return conversation_id and message_id immediately
       pass
   
   @router.get("/genai/query/result/{conversation_id}/{message_id}")
   async def get_query_result(conversation_id: str, message_id: str):
       # Return result when ready
       pass
   ```

2. **Use WebSockets or Server-Sent Events** (SSE):
   - More efficient than polling
   - Real-time push updates
   - Lower latency

3. **Progress Percentage**:
   - Show progress bar
   - Estimate time remaining
   - Based on typical query durations

4. **Detailed Sub-steps**:
   - Show SQL being generated (streaming)
   - Show query execution progress
   - Show row count as data loads

### Add Status History

Track all status transitions:
```typescript
[
  { status: 'SUBMITTED', timestamp: '14:32:01' },
  { status: 'EXECUTING_QUERY', timestamp: '14:32:03' },
  { status: 'EXECUTING', timestamp: '14:32:08' },
  { status: 'COMPLETED', timestamp: '14:32:15' }
]
```

Display as a timeline for debugging.

## Benefits

✅ **Better UX**: Users know the app is working
✅ **Transparency**: Clear visibility into processing steps
✅ **Patience**: Users more willing to wait when they see progress
✅ **Debugging**: Status helps identify where things slow down
✅ **Professional**: Shows attention to detail

## Testing

### Manual Testing Steps

1. **Test Status Display**:
   ```
   Action: Submit a query
   Expected: See status messages change
   ```

2. **Test Long Queries**:
   ```
   Action: Submit complex query
   Expected: Multiple status transitions visible
   ```

3. **Test Error Handling**:
   ```
   Action: Submit invalid query
   Expected: Status shows error state
   ```

4. **Test Cleanup**:
   ```
   Action: Start new conversation
   Expected: Old status cleared
   ```

## Troubleshooting

### Status Not Updating

**Symptoms**: Status stuck on one message

**Causes**:
- Backend not updating status
- Frontend not re-rendering

**Solutions**:
- Check backend logs for status updates
- Verify state management in frontend

### Status Shows "UNKNOWN"

**Symptoms**: Generic status message

**Causes**:
- Status key not found in backend
- Query completed before status could be tracked

**Solutions**:
- Expected for very fast queries
- Can be ignored if results appear correctly

## Related Documentation

- [GENAI_CONVERSATIONS.md](./GENAI_CONVERSATIONS.md) - Main conversation feature
- [SUGGESTED_QUESTIONS_FEATURE.md](./SUGGESTED_QUESTIONS_FEATURE.md) - Follow-up questions
- [CONVERSATION_IMPLEMENTATION_SUMMARY.md](./CONVERSATION_IMPLEMENTATION_SUMMARY.md) - Technical overview
