"""
Luminate API Client Module

This module provides a Python interface to interact with the Luminate Music API.
It handles authentication, API requests, and data retrieval.

Key Concepts:
- OAuth2 Authentication: Secure token-based authentication
- REST API: HTTP-based API using GET/POST requests
- Error Handling: Graceful handling of API errors
- Rate Limiting: Respecting API limits to avoid being blocked
"""

import requests
import time
from typing import Dict, List, Optional, Any
from config import LUM_API_BASE_URL, LUM_API_HEADERS, LUM_USERNAME, LUM_PASSWORD


class LuminateAPIClient:
    """
    Client for interacting with the Luminate Music API.
    
    This class encapsulates all API interactions, handling:
    - Authentication (getting and refreshing tokens)
    - Making API requests
    - Error handling
    - Rate limiting
    """
    
    def __init__(self):
        """Initialize the API client with base configuration."""
        self.base_url = LUM_API_BASE_URL
        self.headers = LUM_API_HEADERS.copy()
        self.auth_token = None
        self.token_expiry = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with the Luminate API to obtain an access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        How it works:
        1. Sends username/password to /auth endpoint with API key in headers
        2. Receives an access token
        3. Stores the token to use in subsequent requests
        
        Based on Luminate API documentation:
        - Endpoint: POST /auth
        - Headers: x-api-key, Content-Type: application/x-www-form-urlencoded
        - Body: username and password as form data
        - Response: access_token and expires_in
        """
        auth_url = f"{self.base_url}/auth"
        
        # Prepare authentication headers (API key is required)
        auth_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-api-key': self.headers.get('x-api-key', '')
        }
        
        # Prepare form data
        auth_data = {
            'username': LUM_USERNAME,
            'password': LUM_PASSWORD
        }
        
        try:
            # Make authentication request with form data
            response = requests.post(
                auth_url,
                data=auth_data,  # Form data, not JSON
                headers=auth_headers,
                timeout=30
            )
            
            print(f"Auth Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token') or data.get('token')
                
                if self.auth_token:
                    # Based on Luminate API docs, authorization header should be just the token
                    # Example: 'authorization: AUTHTOKEN123' (not 'Bearer AUTHTOKEN123')
                    self.headers['authorization'] = self.auth_token
                    print("✅ Authentication successful!")
                    print(f"   Token: {self.auth_token[:20]}...")
                    return True
                else:
                    print(f"❌ No access_token in response: {data}")
                    return False
            else:
                # Try to get error message
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    print(f"❌ Authentication failed ({response.status_code}): {error_msg}")
                except:
                    print(f"❌ Authentication failed ({response.status_code}): {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Authentication timeout - server took too long to respond")
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection error during authentication: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
    
    def _ensure_authenticated(self):
        """Ensure we have a valid authentication token before making requests."""
        if not self.auth_token:
            if not self.authenticate():
                raise Exception("Failed to authenticate with Luminate API. Please check your credentials.")
    
    def get_musical_recording(self, isrc: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Retrieve data for a musical recording by ISRC.
        
        Args:
            isrc: International Standard Recording Code (unique identifier for a recording)
            **kwargs: Additional query parameters (e.g., date ranges, filters)
            
        Returns:
            Dictionary containing recording data, or None if request fails
            
        What is an ISRC?
        - ISRC = International Standard Recording Code
        - Unique identifier for each recording (like a barcode for songs)
        - Format: USRC17607839 (country code + registrant + year + designation)
        
        Important: The API requires ID_Type parameter to be explicitly set to "ISRC"
        when querying by ISRC, otherwise it defaults to "luminate" ID type.
        """
        self._ensure_authenticated()
        
        # Build the API endpoint URL
        url = f"{self.base_url}/musical_recordings/{isrc}"
        
        # Add query parameters if provided (for date ranges, filters, etc.)
        # CRITICAL: Must specify ID_Type=ISRC, otherwise API assumes "luminate" ID type
        params = {
            'ID_Type': 'ISRC'  # Explicitly specify we're querying by ISRC
        }
        
        # Only add parameters if they have actual values (not None or empty string)
        if 'start_date' in kwargs and kwargs.get('start_date'):
            params['start_date'] = kwargs['start_date']
        if 'end_date' in kwargs and kwargs.get('end_date'):
            params['end_date'] = kwargs['end_date']
        if 'location' in kwargs and kwargs.get('location'):
            params['location'] = kwargs['location']
        
        try:
            # Debug: Print the exact request being made
            print(f"\n📡 Request for ISRC: {isrc}")
            print(f"   URL: {url}")
            print(f"   Params: {params}")
            print(f"   Headers (keys): {list(self.headers.keys())}")
            
            # Make the API request
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return data
            elif response.status_code == 204:
                # 204 No Content - but user reports data exists on web
                # This might indicate a parameter issue or API problem
                print(f"   ⚠️ 204 No Content for ISRC {isrc} - but data may exist on web")
                print(f"   This might indicate: date range issue, location filter, or API parameter problem")
                # Return None to indicate error (not empty dict)
                return None
            elif response.status_code == 401:
                # Token expired, try re-authenticating
                print(f"⚠️ 401 Unauthorized for {isrc} - attempting re-authentication...")
                if self.authenticate():
                    response = requests.get(url, headers=self.headers, params=params, timeout=30)
                    if response.status_code == 200:
                        return response.json()
                print(f"❌ Authentication failed for ISRC {isrc} after retry")
                return None
            elif response.status_code == 404:
                print(f"⚠️ ISRC {isrc} not found (404)")
                return None
            elif response.status_code == 403:
                print(f"❌ Access forbidden for ISRC {isrc} - check API permissions (403)")
                return None
            elif response.status_code == 500:
                # Server error - show more details
                print(f"❌ Server error (500) for ISRC {isrc}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Server error')
                    error_details = error_data.get('error', {}).get('errors', [])
                    print(f"   Error message: {error_msg}")
                    if error_details:
                        print(f"   Error details: {error_details}")
                    print(f"   Request URL: {url}")
                    print(f"   Parameters: {params}")
                    print(f"   Full error response: {error_data}")
                except:
                    print(f"   Response (text): {response.text[:1000]}")
                    print(f"   Response headers: {dict(response.headers)}")
                
                # Try retry without optional parameters if we have them
                # Date ranges or location might be causing the 500 error
                retry_success = False
                if params.get('start_date') or params.get('end_date') or params.get('location'):
                    print(f"   ⚠️ Retrying without date/location parameters...")
                    minimal_params = {'ID_Type': 'ISRC'}
                    retry_response = requests.get(url, headers=self.headers, params=minimal_params, timeout=30)
                    print(f"   Retry Status: {retry_response.status_code}")
                    if retry_response.status_code == 200:
                        print(f"   ✅ Success without date/location params!")
                        return retry_response.json()
                    elif retry_response.status_code != 500:
                        print(f"   Different error ({retry_response.status_code}) - date/location might not be the issue")
                        try:
                            retry_error = retry_response.json()
                            print(f"   Retry error: {retry_error}")
                        except:
                            print(f"   Retry error text: {retry_response.text[:200]}")
                    else:
                        # Still 500, try different ID_Type parameter formats
                        print(f"   ⚠️ Still 500, trying alternative ID_Type parameter formats...")
                        for param_name in ['id_type', 'idType', 'ID_TYPE']:
                            alt_params = {param_name: 'ISRC'}
                            alt_response = requests.get(url, headers=self.headers, params=alt_params, timeout=30)
                            if alt_response.status_code == 200:
                                print(f"   ✅ Success with {param_name} parameter!")
                                return alt_response.json()
                            elif alt_response.status_code != 500:
                                print(f"   {param_name} gave status {alt_response.status_code} (not 500)")
                                break
                
                return None
            else:
                # Try to parse error response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    print(f"❌ Error for ISRC {isrc} ({response.status_code}): {error_msg}")
                except:
                    print(f"❌ Error for ISRC {isrc} ({response.status_code}): {response.text[:200]}")
                return None
            
        except requests.exceptions.Timeout:
            print(f"Timeout fetching ISRC {isrc}: Request took too long")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error fetching ISRC {isrc}: {str(e)}")
            return None
        except Exception as e:
            print(f"Error fetching ISRC {isrc}: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def get_consumption_data(self, isrc: str, start_date: str = None, 
                            end_date: str = None, location: str = None) -> Optional[Dict[str, Any]]:
        """
        Get consumption (streaming) data for an ISRC.
        
        Args:
            isrc: The ISRC to query
            start_date: Start date for data range (format: YYYY-MM-DD)
            end_date: End date for data range (format: YYYY-MM-DD)
            location: Location code (e.g., 'US' for United States)
            
        Returns:
            Dictionary containing consumption metrics
            
        Consumption Data includes:
        - Total streams
        - Breakdown by service type (on-demand, programmed)
        - Breakdown by content type (audio, video)
        - Breakdown by commercial model (ad-supported/free, premium/paid)
        - DMA (Designated Market Area) breakdowns
        """
        data = self.get_musical_recording(
            isrc, 
            start_date=start_date, 
            end_date=end_date, 
            location=location
        )
        
        if data and 'consumption_data' in data:
            return data['consumption_data']
        elif data and 'metrics' in data:
            return data
        return data
    
    def batch_get_recordings(self, isrcs: List[str], delay: float = 0.1) -> Dict[str, Optional[Dict]]:
        """
        Retrieve data for multiple ISRCs with rate limiting.
        
        Args:
            isrcs: List of ISRC codes to query
            delay: Delay between requests (seconds) to respect rate limits
            
        Returns:
            Dictionary mapping ISRC to its data (or None if failed)
            
        Rate Limiting:
        - APIs often limit how many requests you can make per second
        - We add a small delay between requests to avoid being blocked
        - This is a "good citizen" practice when using APIs
        """
        results = {}
        
        for i, isrc in enumerate(isrcs):
            print(f"Fetching {i+1}/{len(isrcs)}: {isrc}")
            results[isrc] = self.get_musical_recording(isrc)
            
            # Add delay to respect rate limits (except for last request)
            if i < len(isrcs) - 1:
                time.sleep(delay)
        
        return results

