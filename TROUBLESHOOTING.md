# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### Issue: "No flags showing" or "UI not showing any flags"

This usually means one of these problems:

#### 1. **API Authentication Failed**
**Symptoms**: 
- Terminal shows "401 Unauthorized" or "403 Forbidden"
- "Failed to authenticate" message in UI

**Solutions**:
- Check your API credentials in `config.py`
- Verify your API key is correct
- Make sure your username/password are correct
- The API may require token-based auth - check terminal for auth errors

#### 2. **API Response Structure Different Than Expected**
**Symptoms**:
- ISRCs fetch successfully but no flags appear
- Check the "Debug: View Sample API Response" expander in the UI
- Terminal shows "No metrics found" or "No Streams metric found"

**Solutions**:
- The Luminate API may return data in a different structure
- Look at the sample API response in the debug panel
- We may need to update `analysis.py` to match the actual API structure

#### 3. **No Data for ISRCs**
**Symptoms**:
- Terminal shows "404 Not Found" for ISRCs
- "No streaming data available" in results

**Solutions**:
- Verify your ISRCs are valid and exist in Luminate's database
- Some ISRCs may not have streaming data for the selected date range
- Try removing date filters to see all available data

#### 4. **Data Structure Mismatch**
**Symptoms**:
- API returns data but analysis can't parse it
- Check terminal for "DEBUG" messages about data structure

**Solutions**:
- The API response structure may differ from what we expect
- Check the debug panel in the UI to see the actual response
- We may need to update the parsing logic in `analysis.py`

## Debugging Steps

### Step 1: Check Terminal Output
When you run the app, the terminal will show:
- API request URLs
- Response status codes
- Debug information about data structure
- Any errors that occur

**Look for**:
- ✅ `Status Code: 200` (success)
- ❌ `Status Code: 401` (authentication failed)
- ❌ `Status Code: 404` (ISRC not found)
- ❌ `Status Code: 403` (permission denied)

### Step 2: Check UI Debug Panel
After running analysis:
1. Look for the "🔍 Debug: View Sample API Response" expander
2. Click it to see what the API actually returned
3. Check if there's a "metrics" or "consumption_data" field
4. Look for "Streams" in the data

### Step 3: Verify API Response Structure
The API should return data in one of these formats:

**Expected Format 1:**
```json
{
  "metrics": [
    {
      "name": "Streams",
      "value": [
        {
          "name": "total",
          "value": 1000000
        },
        {
          "name": "commercial_model",
          "value": [
            {"name": "ad_supported", "value": 500000},
            {"name": "premium", "value": 500000}
          ]
        }
      ]
    }
  ]
}
```

**Expected Format 2:**
```json
{
  "consumption_data": {
    "metrics": [
      {
        "name": "Streams",
        "value": [...]
      }
    ]
  }
}
```

If your API returns something different, we need to update the parsing code.

### Step 4: Test with a Known Good ISRC
Try with a well-known ISRC that you know has streaming data to verify the API is working.

## Getting Help

### Information to Provide

When asking for help, please provide:

1. **Error Messages**: Copy the full error from terminal
2. **API Response Sample**: From the debug panel in UI
3. **ISRCs Used**: Which ISRCs you're testing with
4. **Date Range**: If you're using date filters
5. **Terminal Output**: The debug output showing API requests/responses

### Common Error Messages

**"Error fetching ISRC: 401"**
- Authentication issue
- Check credentials in `config.py`

**"Error fetching ISRC: 404"**
- ISRC doesn't exist in database
- Try a different ISRC

**"No metrics or consumption_data found"**
- API response structure is different
- Check debug panel to see actual structure
- May need to update parsing code

**"No Streams metric found"**
- API returned data but no "Streams" metric
- Check what metrics are available in debug panel

## Quick Fixes

### Enable More Debugging
The code now includes debug output. Check:
- Terminal for detailed API request/response info
- UI debug panel for sample API responses
- Analysis details in the Results tab

### Disable Debug Output
If debug output is too verbose, you can comment out the `print()` statements in:
- `luminate_client.py` (lines with `print("DEBUG:")`)
- `analysis.py` (lines with `print("DEBUG:")`)

### Test API Connection
You can test the API directly:

```python
from luminate_client import LuminateAPIClient

client = LuminateAPIClient()
client.authenticate()
data = client.get_musical_recording("YOUR_ISRC_HERE")
print(data)
```

## Next Steps

If you're still having issues:
1. Check the terminal output carefully
2. Look at the debug panel in the UI
3. Share the error messages and API response structure
4. We can update the code to match your API's actual response format

