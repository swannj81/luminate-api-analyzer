# Luminate API Support Request

## Issue Summary
Getting 204 No Content responses for ISRCs that have data available on the Luminate web interface. The API requests are not returning the expected streaming/consumption data.

## API Details
- **Endpoint**: `GET /musical_recordings/{isrc}`
- **Base URL**: `https://api.luminatedata.com`
- **Authentication**: Using API key in `x-api-key` header and token in `authorization` header

## What We're Sending

### Request Format
```
GET https://api.luminatedata.com/musical_recordings/{ISRC}
Headers:
  Accept: application/vnd.luminate-data.svc-apibff.v1+json
  x-api-key: [API_KEY]
  authorization: [TOKEN]
  Content-Type: application/json
Query Parameters:
  ID_Type: ISRC
  start_date: 2025-09-01 (optional)
  end_date: 2025-09-30 (optional)
  location: US (optional)
```

### Example Request
```
GET https://api.luminatedata.com/musical_recordings/GXD7G2249344?ID_Type=ISRC&start_date=2025-09-01&end_date=2025-09-30&location=US
```

## Response We're Getting
- **Status Code**: 204 No Content
- **Response Body**: Empty (no content)
- **Issue**: Same ISRCs show data on the web interface, so 204 seems incorrect

## What We've Tried

1. ✅ **Authentication**: Successfully authenticating and receiving tokens
2. ✅ **ID_Type Parameter**: Added `ID_Type=ISRC` parameter (required per documentation)
3. ✅ **Authorization Header**: Using token without "Bearer" prefix (per docs)
4. ✅ **Date Parameters**: Tried with and without date ranges
5. ✅ **Location Parameter**: Tried with and without location filter
6. ✅ **Parameter Formats**: Tried different case variations of ID_Type
7. ✅ **Retry Logic**: Tried requests without optional parameters

## Questions for Luminate Support

1. **Is 204 the correct response when data exists?**
   - We're getting 204 for ISRCs that have data on the web
   - Should we be using a different endpoint or parameter?

2. **Is the ID_Type parameter format correct?**
   - We're using `ID_Type=ISRC` as a query parameter
   - Is this the correct format/case?

3. **Are date range parameters required?**
   - Do we need to specify date ranges to get consumption data?
   - What's the default date range if not specified?

4. **Is there a different endpoint for consumption data?**
   - Should we be using a different endpoint specifically for streaming/consumption data?
   - The docs mention `/musical_recordings` but maybe there's a consumption-specific endpoint?

5. **What parameters are required vs optional?**
   - Which parameters are mandatory for getting consumption data?
   - Are there any required parameters we're missing?

## Sample ISRCs That Return 204
- GXD7G2249344
- QZ5AB2469209
- QZTB82365856
- AUGBT2487215
- GXF9Q2424054

(These all show data on the web interface)

## Expected Response Format
Based on documentation, we expect:
```json
{
  "metrics": [
    {
      "name": "Streams",
      "value": [
        {
          "name": "total",
          "value": 19892402
        },
        {
          "name": "commercial_model",
          "value": [...]
        }
      ]
    }
  ]
}
```

## Environment
- **API Version**: v1.0.1 (based on Accept header)
- **Request Method**: GET
- **Authentication**: Token-based (from /auth endpoint)

## Next Steps Requested
1. Clarification on why 204 is returned when data exists
2. Correct parameter format for ISRC queries
3. Required vs optional parameters
4. Any additional configuration needed

---

**Contact Information:**
- Email: joshua.swann@themlc.com
- API Key: [Your API Key]
- Account: The MLC

