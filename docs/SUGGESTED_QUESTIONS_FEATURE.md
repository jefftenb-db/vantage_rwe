# Suggested Follow-up Questions Feature

## Overview

The GenAI conversation feature now displays **suggested follow-up questions** provided by the Databricks Genie API. Users can click on any suggested question to instantly submit it as their next query, making conversations more intuitive and exploratory.

## How It Works

### API Integration

According to the [Databricks Genie API documentation](https://docs.databricks.com/api/workspace/genie/getmessage#attachments-suggested_questions), Genie returns `attachments.suggested_questions` in the message response. These are contextually relevant follow-up questions that Genie thinks would be useful based on the current query results.

### Backend Implementation

**Models (`backend/app/models/cohort.py`):**
- Added `suggested_questions: Optional[List[str]]` to `ConversationMessage`
- Added `suggested_questions: Optional[List[str]]` to `NaturalLanguageResponse`

**Service (`backend/app/services/genai_service.py`):**
- Extracts `suggested_questions` from Genie API response attachments
- Stores suggested questions in conversation history
- Returns suggested questions in API response

### Frontend Implementation

**API Service (`frontend/src/services/api.ts`):**
- Updated `ConversationMessage` interface with `suggested_questions?: string[]`
- Updated `NaturalLanguageResponse` interface with `suggested_questions?: string[]`

**Component (`frontend/src/components/NaturalLanguageSearch.tsx`):**
- Added `handleSuggestedQuestionClick()` handler
- Displays suggested questions as clickable buttons
- Clicking a suggestion automatically submits it as the next query
- Buttons are disabled while loading

**Styling (`frontend/src/components/NaturalLanguageSearch.css`):**
- Gradient styling for suggested question buttons
- Hover effects with color change and slide animation
- Speech bubble emoji (💬) prefix
- Responsive design

## User Experience

### Visual Layout

```
┌─────────────────────────────────────────────────┐
│ 🤖 GenAI: Found 15,234 patients with Type 2... │
│   📊 15,234 results                             │
│   ▶️ Show SQL                                   │
│                                                 │
│   💡 Suggested follow-ups:                      │
│   ┌─────────────────────────────────────────┐  │
│   │ 💬 How many are on Metformin?          │  │
│   ├─────────────────────────────────────────┤  │
│   │ 💬 What's the average age?             │  │
│   ├─────────────────────────────────────────┤  │
│   │ 💬 Show breakdown by gender            │  │
│   └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Interaction Flow

1. **User asks initial question**: "Show me patients with Type 2 Diabetes"
2. **Genie responds** with results and suggested questions:
   - "How many are on Metformin?"
   - "What's the average age?"
   - "Show breakdown by gender"
3. **User clicks** on "How many are on Metformin?"
4. **System automatically submits** the question
5. **Genie responds** with new results and new suggested questions
6. Repeat...

### Benefits

✅ **Faster Exploration**: Click instead of typing
✅ **Guided Discovery**: Genie suggests relevant questions
✅ **Better Questions**: Learn how to phrase queries effectively
✅ **Context-Aware**: Suggestions based on current results
✅ **Reduced Friction**: No need to think of follow-ups

## Example Conversation

```
👤 You: Show me patients with Type 2 Diabetes

🤖 GenAI: Found 15,234 patients with Type 2 Diabetes...
   💡 Suggested follow-ups:
   💬 How many are on Metformin?
   💬 What's the average age?
   💬 Show breakdown by gender

👤 You: [Clicks "How many are on Metformin?"]

🤖 GenAI: Found 8,456 patients on Metformin...
   💡 Suggested follow-ups:
   💬 What's the average dosage?
   💬 Show patients on combination therapy
   💬 Compare to insulin therapy

👤 You: [Clicks "Compare to insulin therapy"]

🤖 GenAI: Comparing Metformin vs Insulin usage...
   💡 Suggested follow-ups:
   💬 Show cost comparison
   💬 Which has better outcomes?
   💬 Show switching patterns
```

## Technical Details

### API Response Structure

From Genie API:
```json
{
  "attachments": [
    {
      "text": {
        "content": "Found 15,234 patients..."
      },
      "query": {
        "query": "SELECT ..."
      },
      "suggested_questions": [
        "How many are on Metformin?",
        "What's the average age?",
        "Show breakdown by gender"
      ]
    }
  ]
}
```

### Frontend State Flow

```typescript
handleSuggestedQuestionClick(question: string)
  ↓
setLoading(true)
  ↓
naturalLanguageQuery(question, conversationId)
  ↓
Update conversation state
  ↓
Display new response with new suggestions
  ↓
setLoading(false)
```

## Styling Details

### Button States

**Default:**
- Light gradient background
- Gray border
- Dark text

**Hover:**
- Purple gradient background
- White text
- Slide right animation
- Box shadow

**Disabled (while loading):**
- Reduced opacity
- No pointer cursor
- No hover effects

### Responsive Design

- Buttons stack vertically for easy clicking
- Full width on mobile
- Clear spacing between options
- Touch-friendly tap targets

## Edge Cases Handled

1. **No Suggestions**: Section hidden if Genie doesn't provide suggestions
2. **Loading State**: Buttons disabled during API calls
3. **Long Questions**: Text wraps properly
4. **Multiple Messages**: Each message can have its own suggestions
5. **Conversation Reset**: Suggestions cleared when starting new conversation

## Future Enhancements

Potential improvements:
- [ ] Show "Recently used" suggestions
- [ ] Allow users to edit suggested questions before submitting
- [ ] Display suggested questions in input field on click (instead of auto-submit)
- [ ] Track which suggestions are most clicked
- [ ] Customize suggestion display (chips vs buttons)
- [ ] Add keyboard navigation for suggestions

## Testing

### Manual Testing Steps

1. **Test Suggestion Display:**
   ```
   Query: "Show me patients with diabetes"
   Expected: Suggestions appear below response
   ```

2. **Test Suggestion Click:**
   ```
   Action: Click on a suggested question
   Expected: Question submitted automatically, new results shown
   ```

3. **Test Loading State:**
   ```
   Action: Click suggestion, then try to click another
   Expected: Buttons disabled while loading
   ```

4. **Test No Suggestions:**
   ```
   Query: Very specific query that yields no suggestions
   Expected: Suggestion section not displayed
   ```

5. **Test Multiple Messages:**
   ```
   Action: Have a 3-message conversation
   Expected: Each assistant message can have different suggestions
   ```

## Troubleshooting

### Suggestions Not Appearing

**Symptoms:** No suggested questions shown

**Causes:**
- Genie Space not returning suggestions
- API response parsing error
- No suggestions for this query type

**Solutions:**
- Check backend logs for `suggested_questions` in API response
- Verify Genie Space configuration
- Try different queries (some may not generate suggestions)

### Click Not Working

**Symptoms:** Clicking suggestion doesn't submit query

**Causes:**
- JavaScript error
- Button disabled
- Loading state stuck

**Solutions:**
- Check browser console for errors
- Verify `handleSuggestedQuestionClick` is called
- Check loading state management

## Related Documentation

- [Databricks Genie API - Suggested Questions](https://docs.databricks.com/api/workspace/genie/getmessage#attachments-suggested_questions)
- [GENAI_CONVERSATIONS.md](./GENAI_CONVERSATIONS.md) - Main conversation feature documentation
- [CONVERSATION_IMPLEMENTATION_SUMMARY.md](./CONVERSATION_IMPLEMENTATION_SUMMARY.md) - Implementation details
