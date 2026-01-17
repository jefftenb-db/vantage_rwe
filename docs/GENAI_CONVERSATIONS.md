# GenAI Conversations Feature

## Overview

The GenAI Query feature now supports **conversational interactions** with Databricks Genie Spaces API. Users can have multi-turn conversations where follow-up questions retain context from previous messages.

## What's New

### Before
- Single question → single answer
- No context retention
- Had to rephrase entire question for refinements

### After
- Multi-turn conversations with context
- Follow-up questions understand previous context
- Conversation history displayed
- Easy to refine and explore data iteratively

## Architecture

### Backend Changes

#### 1. **Models** (`backend/app/models/cohort.py`)
- **`ConversationMessage`**: Represents a single message in a conversation
  - `message_id`: Unique identifier
  - `role`: 'user' or 'assistant'
  - `content`: Message text
  - `sql_generated`: SQL query (for assistant messages)
  - `result_count`: Number of results (for assistant messages)
  - `timestamp`: When the message was created

- **`NaturalLanguageQuery`**: Updated with optional `conversation_id` field
  - If provided, continues existing conversation
  - If null, starts new conversation

- **`NaturalLanguageResponse`**: Enhanced with conversation fields
  - `conversation_id`: ID for continuing the conversation
  - `message_id`: ID of this specific message
  - `conversation_history`: Full list of messages in conversation

#### 2. **Service** (`backend/app/services/genai_service.py`)
- **`_continue_genie_conversation()`**: New method to send follow-up messages
  - Uses `POST /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages`
  - Genie uses conversation context to interpret follow-ups

- **In-memory conversation storage**: 
  - `self.conversation_histories`: Dict mapping conversation_id → list of messages
  - In production, consider using Redis or database for persistence

- **`_add_to_conversation_history()`**: Helper to track messages
  - Stores both user queries and assistant responses
  - Maintains chronological order

#### 3. **API Routes** (`backend/app/api/routes.py`)
- Updated `/genai/query` endpoint documentation
- Accepts optional `conversation_id` in request
- Returns `conversation_id` in response for continuation

### Frontend Changes

#### 1. **API Service** (`frontend/src/services/api.ts`)
- **`ConversationMessage`**: TypeScript interface for messages
- **`NaturalLanguageResponse`**: Updated with conversation fields
- **`naturalLanguageQuery()`**: Updated to accept optional `conversationId` parameter

#### 2. **Component** (`frontend/src/components/NaturalLanguageSearch.tsx`)

**New State Variables:**
- `conversationId`: Tracks active conversation
- `conversationHistory`: Array of all messages
- `currentResponse`: Latest response (replaces `response`)

**New Features:**
- **Conversation History Display**: Shows all previous messages in chronological order
  - User messages on the right with blue accent
  - Assistant messages on the left with teal accent
  - Timestamps for each message
  - Result counts for assistant responses

- **Conversation Status Badge**: Shows when a conversation is active
  
- **New Conversation Button**: Allows user to start fresh conversation

- **Smart Input Placeholder**: Changes based on whether in conversation mode

- **Example Queries**: Only shown when NOT in a conversation

#### 3. **Styling** (`frontend/src/components/NaturalLanguageSearch.css`)
- `.conversation-history`: Container for message history
- `.message-user` / `.message-assistant`: Different styling for each role
- `.status-badge`: Indicates active conversation
- Responsive and accessible design

## How to Use

### Starting a New Conversation

1. Go to the "GenAI Query" tab
2. Enter your question (e.g., "Show me patients with Type 2 Diabetes")
3. Click "Ask GenAI"
4. The system starts a new conversation with Genie

### Continuing a Conversation

1. After receiving a response, the conversation status badge appears
2. Enter a follow-up question (e.g., "How many are on Metformin?")
3. Click "Continue Conversation"
4. Genie interprets the question in context of the conversation

### Starting a New Conversation

1. Click the "🔄 New Conversation" button in the header
2. This clears all state and starts fresh

## Example Conversation Flow

```
User: Show me patients with Type 2 Diabetes
Assistant: [Returns SQL and 15,234 patients]

User: Filter to those prescribed Metformin
Assistant: [Understands context, returns 8,456 patients]

User: What's the average age?
Assistant: [Understands "those" refers to the filtered cohort]

User: Show me by gender
Assistant: [Provides breakdown of the 8,456 patients by gender]
```

## Technical Details

### Databricks Genie API Endpoints Used

1. **Start Conversation**
   - `POST /api/2.0/genie/spaces/{space_id}/start-conversation`
   - Creates new conversation, returns `conversation_id`

2. **Continue Conversation**
   - `POST /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages`
   - Sends follow-up message with context

3. **Poll Message Status**
   - `GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}`
   - Checks if Genie has completed processing

### Conversation Limits

According to Databricks documentation:
- Up to **10,000 conversations** per space
- Up to **10,000 messages** per conversation
- Query results capped at **5,000 rows**
- Throughput: ~**5 queries per minute** per workspace (during preview)

### State Management

**Current Implementation (Development):**
- In-memory storage on backend
- Lost on server restart
- Suitable for single-user development

**Production Recommendations:**
- Store conversation history in database
- Use Redis for fast access to recent conversations
- Add conversation TTL (time-to-live) to clean up old conversations
- Consider user authentication to associate conversations with users

## Future Enhancements

### Persistence
- [ ] Store conversations in database
- [ ] Allow users to view past conversations
- [ ] Export entire conversation as report

### UX Improvements
- [ ] Edit previous messages
- [ ] Branch conversations from any point
- [ ] Share conversations with colleagues
- [ ] Bookmark important conversations

### Advanced Features
- [ ] Conversation templates for common workflows
- [ ] Auto-suggest follow-up questions
- [ ] Merge insights from multiple conversations
- [ ] Collaborative conversations (multiple users)

## Testing

### Manual Testing Steps

1. **Test New Conversation:**
   ```
   Query: "Show me patients with hypertension"
   Expected: New conversation_id, results displayed
   ```

2. **Test Follow-up:**
   ```
   Follow-up: "Filter to those over 65"
   Expected: Same conversation_id, context-aware results
   ```

3. **Test History Display:**
   ```
   Expected: All messages shown in order with timestamps
   ```

4. **Test New Conversation Button:**
   ```
   Action: Click "New Conversation"
   Expected: History cleared, ready for fresh start
   ```

5. **Test Export/Save:**
   ```
   Action: Export results or save cohort
   Expected: Works with latest response
   ```

### API Testing

Test the backend directly:

```bash
# Start a conversation
curl -X POST http://localhost:8000/api/v1/genai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me patients with diabetes"}'

# Note the conversation_id from response, then continue:
curl -X POST http://localhost:8000/api/v1/genai/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How many are on insulin?",
    "conversation_id": "<conversation_id_from_above>"
  }'
```

## Troubleshooting

### Conversation Not Retaining Context

**Symptoms:** Follow-up questions don't understand context

**Causes:**
- `conversation_id` not being passed correctly
- Genie Space not properly configured
- Conversation expired or deleted

**Solutions:**
- Check browser console for `conversation_id` in request
- Verify Genie Space has proper instructions and context
- Check backend logs for Genie API errors

### Conversation History Not Showing

**Symptoms:** Messages not displayed in history

**Causes:**
- Frontend not receiving `conversation_history` in response
- Backend not storing messages correctly

**Solutions:**
- Check network tab to verify `conversation_history` in API response
- Check backend logs for errors in `_add_to_conversation_history()`

### Performance Issues

**Symptoms:** Slow response times in long conversations

**Causes:**
- Large conversation history being sent back and forth
- Genie processing time increases with context

**Solutions:**
- Limit conversation history to last N messages
- Implement pagination for history display
- Start new conversation after certain number of turns

## Best Practices

1. **Start Fresh When Changing Topics**: If switching from diabetes to heart disease, start a new conversation

2. **Be Specific in Follow-ups**: "How many are on insulin?" is better than just "How many?"

3. **Review History**: Scroll through history to remember context before asking follow-ups

4. **Save Important Results**: Use Export or Save Cohort before starting new conversation

5. **Monitor Conversation Length**: Very long conversations may become slow or lose coherence

## Related Documentation

- [Databricks Genie Conversation API](https://docs.databricks.com/api/workspace/genie)
- [GENIE_INTEGRATION.md](./GENIE_INTEGRATION.md) - Original Genie setup guide
- [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - Overall project documentation
