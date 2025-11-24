# 🏗️ Architecture Overview

## System Design

This application follows a **modular architecture** that separates concerns and makes the code maintainable and scalable.

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                 │
│  - User interface                                        │
│  - File upload handling                                  │
│  - Results display                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Uses
                   ▼
┌─────────────────────────────────────────────────────────┐
│            Analysis Module (analysis.py)                  │
│  - Manipulation detection logic                          │
│  - Flagging algorithms                                   │
│  - Data parsing                                          │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Uses
                   ▼
┌─────────────────────────────────────────────────────────┐
│         API Client (luminate_client.py)                  │
│  - Authentication                                        │
│  - HTTP requests                                         │
│  - Error handling                                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Uses
                   ▼
┌─────────────────────────────────────────────────────────┐
│          Configuration (config.py)                        │
│  - Credential management                                 │
│  - API settings                                          │
└──────────────────────────────────────────────────────────┘
```

## Data Flow

1. **User uploads CSV** → `app.py` reads file → Extracts ISRCs
2. **For each ISRC** → `luminate_client.py` → Makes API request → Returns data
3. **API data** → `analysis.py` → Applies detection rules → Returns flags
4. **Results** → `app.py` → Displays in UI → User can download

## Key Design Decisions

### 1. Modular Structure
**Why**: Each module has a single responsibility
- `config.py`: Only handles configuration
- `luminate_client.py`: Only handles API communication
- `analysis.py`: Only handles analysis logic
- `app.py`: Only handles UI

**Benefit**: Easy to modify one part without affecting others

### 2. Session State
**Why**: Streamlit apps are stateless by default
- We use `st.session_state` to persist data between interactions
- Stores API client, results, detector instance

**Benefit**: Avoids re-initializing on every interaction

### 3. Flexible Authentication
**Why**: API documentation may not specify exact endpoint
- Tries multiple common authentication patterns
- Falls back to API key if token auth unavailable

**Benefit**: Works with different API configurations

### 4. Rate Limiting
**Why**: APIs have usage limits
- Built-in delays between requests
- Prevents overwhelming the API

**Benefit**: Respects API terms, avoids being blocked

## Scalability Considerations

### Adding New APIs

To add a new API (e.g., Spotify):

1. **Create new client** (`spotify_client.py`):
   ```python
   class SpotifyAPIClient:
       def authenticate(self): ...
       def get_track_data(self, track_id): ...
   ```

2. **Update UI** (`app.py`):
   - Add API selector dropdown
   - Route to appropriate client based on selection

3. **Reuse analysis**:
   - `analysis.py` can work with any API response
   - Just need to adapt data extraction

### Adding New Detection Rules

To add a new flagging rule:

1. **Add method to `ManipulationDetector`**:
   ```python
   def check_new_rule(self, api_response):
       # Your detection logic
       return {'flagged': True/False, 'reason': '...'}
   ```

2. **Call in `analyze_isrc`**:
   ```python
   new_check = self.check_new_rule(api_response)
   if new_check['flagged']:
       results['flags'].append(...)
   ```

3. **Update UI** (if needed):
   - Add threshold slider in sidebar
   - Update display logic

## Error Handling Strategy

### API Errors
- **401 Unauthorized**: Try re-authenticating
- **404 Not Found**: ISRC doesn't exist (not an error, just no data)
- **429 Rate Limited**: Shouldn't happen (we rate limit), but handle gracefully
- **500 Server Error**: Log and continue with next ISRC

### Data Errors
- **Missing CSV column**: Use first column as fallback
- **Invalid ISRC format**: Skip and continue
- **Malformed API response**: Log and mark as "no data"

## Performance Optimizations

1. **Batch Processing**: Process all ISRCs in one go
2. **Progress Tracking**: Show user what's happening
3. **Caching**: Could add caching for repeated ISRCs (future enhancement)
4. **Parallel Requests**: Could add threading for faster processing (future enhancement)

## Security Best Practices

1. **Credentials**: Never hardcoded, use environment variables
2. **Token Storage**: Only in memory, never saved to disk
3. **Git Ignore**: `.env` file excluded from version control
4. **API Keys**: Rotated regularly (user responsibility)

## Testing Strategy (Future)

1. **Unit Tests**: Test each module independently
2. **Integration Tests**: Test API client with mock responses
3. **UI Tests**: Test Streamlit app with sample data
4. **End-to-End**: Test full workflow with real API (limited)

## Future Enhancements

### Short Term
- [ ] Add caching for API responses
- [ ] Export to Excel with formatting
- [ ] Historical trend analysis

### Medium Term
- [ ] Multiple API support (Spotify, Apple Music)
- [ ] Machine learning anomaly detection
- [ ] Scheduled reports

### Long Term
- [ ] User authentication
- [ ] Database for storing results
- [ ] API for programmatic access

