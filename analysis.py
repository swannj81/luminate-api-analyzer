"""
Analysis Module for Detecting Potential Manipulation

This module analyzes streaming data to identify potential signs of manipulation:
1. Over 80% of streams in one DMA (suspicious geographic concentration)
2. All free service streams (100% ad-supported, no premium)
3. Less than 3% free services (suspiciously low free tier usage)
4. Streams dropping to zero (content removed)

Key Concepts:
- DMA: Designated Market Area (geographic regions for media markets)
- Commercial Model: How users access content (free/ad-supported vs premium/paid)
- Anomaly Detection: Identifying patterns that deviate from normal behavior
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd


class ManipulationDetector:
    """
    Detects potential manipulation indicators in streaming data.
    
    Why these flags matter:
    - Geographic concentration: Real organic streams are usually distributed
    - Free vs Premium mix: Organic content typically has a mix of both
    - Zero streams: May indicate content was removed or flagged
    """
    
    def __init__(self):
        """Initialize the detector with threshold values."""
        self.dma_threshold = 0.80  # 80% threshold for DMA concentration
        self.free_min_threshold = 0.03  # 3% minimum free service threshold
        self.free_max_threshold = 1.0  # 100% free service threshold
    
    def extract_streams_data(self, api_response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract streaming metrics from API response.
        
        Args:
            api_response: Raw API response data (can be empty dict for 204 No Content)
            
        Returns:
            Dictionary with extracted metrics, or None if data unavailable
            
        The API returns nested data structures. This function "flattens" them
        to make analysis easier.
        
        Note: 204 No Content responses return empty dict {}, meaning no data available.
        """
        if not api_response:
            return None
        
        if not isinstance(api_response, dict):
            return None
        
        # Empty dict means 204 No Content - no data available
        if len(api_response) == 0:
            return None
        
        # Try different possible response structures
        metrics = api_response.get('metrics', [])
        if not metrics:
            consumption_data = api_response.get('consumption_data', {})
            if isinstance(consumption_data, dict):
                metrics = consumption_data.get('metrics', [])
        
        if not metrics:
            # Try looking for data directly in response
            # Maybe the data is structured differently - let's check
            for key in ['data', 'results', 'streaming_data', 'consumption']:
                if key in api_response:
                    potential_data = api_response[key]
                    if isinstance(potential_data, dict) and 'metrics' in potential_data:
                        metrics = potential_data['metrics']
                        break
                    elif isinstance(potential_data, list):
                        metrics = potential_data
                        break
            
            if not metrics:
                # Last resort: check if the response itself is a list of metrics
                if isinstance(api_response, list):
                    metrics = api_response
                else:
                    return None
        
        # Find the Streams metric (case-insensitive, flexible matching)
        streams_metric = None
        for metric in metrics:
            if not isinstance(metric, dict):
                continue
            metric_name = metric.get('name', '')
            # Try exact match first, then case-insensitive, then partial match
            if (metric_name == 'Streams' or 
                metric_name.lower() == 'streams' or 
                'stream' in metric_name.lower()):
                streams_metric = metric
                break
        
        if not streams_metric:
            return None
        
        value = streams_metric.get('value', [])
        if not isinstance(value, list):
            # If value is not a list, wrap it
            value = [value] if value is not None else []
        
        return self._parse_metrics(value)
    
    def _parse_metrics(self, value_list: List[Dict]) -> Dict[str, Any]:
        """
        Recursively parse nested metric structure.
        
        The API returns metrics in a nested tree structure like:
        {
          "name": "total",
          "value": 1000000
        }
        or
        {
          "name": "commercial_model",
          "value": [
            {"name": "ad_supported", "value": 500000},
            {"name": "premium", "value": 500000}
          ]
        }
        
        This function flattens this into a simple dictionary.
        """
        result = {}
        
        for item in value_list:
            name = item.get('name')
            value = item.get('value')
            
            if isinstance(value, list):
                # Nested structure - recurse
                nested = self._parse_metrics(value)
                for key, val in nested.items():
                    result[f"{name}_{key}"] = val
            else:
                # Leaf node - store the value
                result[name] = value
        
        return result
    
    def check_dma_concentration(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if over 80% of streams come from a single DMA.
        
        Returns:
            Dictionary with flag status and details
        """
        streams_data = self.extract_streams_data(api_response)
        
        if not streams_data:
            return {
                'flagged': False,
                'reason': 'No streaming data available',
                'details': None
            }
        
        # Look for DMA breakdown in the data
        # The API may structure DMA data differently, so we check multiple possibilities
        total_streams = streams_data.get('total', 0)
        
        if total_streams == 0:
            return {
                'flagged': False,
                'reason': 'No streams found',
                'details': None
            }
        
        # Check for DMA data in various possible locations
        # Try multiple field name variations
        dma_data = None
        possible_dma_keys = [
            'dma',
            'location_dma',
            'dma_location',
            'location_dma_location',
            'geographic_dma',
            'dma_breakdown',
            'location_breakdown'
        ]
        
        for key in possible_dma_keys:
            if key in streams_data:
                dma_data = streams_data[key]
                print(f"DEBUG: Found DMA data in key '{key}'")
                break
        
        # Also check for nested location data
        if not dma_data:
            # Check if there's a location field that might contain DMA
            if 'location' in streams_data:
                location_data = streams_data['location']
                if isinstance(location_data, dict):
                    # Check if location dict contains DMA data
                    for loc_key in ['dma', 'dma_breakdown', 'markets']:
                        if loc_key in location_data:
                            dma_data = location_data[loc_key]
                            print(f"DEBUG: Found DMA data in location.{loc_key}")
                            break
        
        if not dma_data:
            # Debug: print available keys to help identify DMA data
            print(f"DEBUG DMA Check: Available keys in streams_data: {list(streams_data.keys())}")
            print(f"DEBUG DMA Check: Total streams: {total_streams}")
            # If DMA data isn't in the response, we can't check this
            return {
                'flagged': False,
                'reason': 'DMA data not available in response',
                'details': {
                    'available_keys': list(streams_data.keys()),
                    'total_streams': total_streams
                }
            }
        
        # Find the DMA with the highest percentage
        max_dma_share = 0
        max_dma_name = None
        
        if isinstance(dma_data, dict):
            for dma_name, dma_streams in dma_data.items():
                if isinstance(dma_streams, (int, float)) and dma_streams > 0:
                    share = dma_streams / total_streams if total_streams > 0 else 0
                    if share > max_dma_share:
                        max_dma_share = share
                        max_dma_name = dma_name
        elif isinstance(dma_data, list):
            # Handle case where DMA data is a list of objects
            for item in dma_data:
                if isinstance(item, dict):
                    dma_name = item.get('name') or item.get('dma') or item.get('market')
                    dma_streams = item.get('value') or item.get('streams') or item.get('count')
                    if dma_name and isinstance(dma_streams, (int, float)) and dma_streams > 0:
                        share = dma_streams / total_streams if total_streams > 0 else 0
                        if share > max_dma_share:
                            max_dma_share = share
                            max_dma_name = dma_name
        
        print(f"DEBUG DMA Check: max_dma_share={max_dma_share:.2%}, max_dma_name={max_dma_name}, threshold={self.dma_threshold:.2%}")
        
        # Flag if over threshold
        flagged = max_dma_share > self.dma_threshold
        
        # Create detailed reason message
        if flagged and max_dma_name:
            reason = f'{max_dma_share*100:.1f}% of streams from DMA: {max_dma_name} (threshold: {self.dma_threshold*100:.0f}%)'
        elif flagged:
            reason = f'{max_dma_share*100:.1f}% of streams from single DMA (threshold: {self.dma_threshold*100:.0f}%)'
        else:
            reason = f'DMA distribution normal (max: {max_dma_share*100:.1f}% from {max_dma_name or "unknown"})'
        
        return {
            'flagged': flagged,
            'reason': reason,
            'details': {
                'max_dma_share': max_dma_share,
                'max_dma_percentage': max_dma_share * 100,
                'max_dma_name': max_dma_name,
                'threshold': self.dma_threshold,
                'threshold_percentage': self.dma_threshold * 100
            }
        }
    
    def check_free_service_ratio(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if streams are all free (100%) or too few free (<3%).
        
        Returns:
            Dictionary with flag status and details
        """
        streams_data = self.extract_streams_data(api_response)
        
        if not streams_data:
            return {
                'flagged': False,
                'reason': 'No streaming data available',
                'details': None
            }
        
        total_streams = streams_data.get('total', 0)
        
        if total_streams == 0:
            return {
                'flagged': False,
                'reason': 'No streams found',
                'details': None
            }
        
        # Extract free (ad-supported) and premium streams
        # Try multiple possible field names (API may structure data differently)
        ad_supported = 0
        premium = 0
        
        # Try different possible field name variations
        possible_ad_names = [
            'commercial_model_ad_supported',
            'ad_supported',
            'commercial_model_ad-supported',  # With hyphen
            'free',
            'ad_supported_streams',
            'commercial_model_free'
        ]
        
        possible_premium_names = [
            'commercial_model_premium',
            'premium',
            'premium_streams',
            'paid',
            'commercial_model_paid'
        ]
        
        # Find ad_supported value
        for name in possible_ad_names:
            if name in streams_data:
                value = streams_data[name]
                if isinstance(value, (int, float)) and value > 0:
                    ad_supported = value
                    break
        
        # Find premium value
        for name in possible_premium_names:
            if name in streams_data:
                value = streams_data[name]
                if isinstance(value, (int, float)) and value > 0:
                    premium = value
                    break
        
        # If we still don't have values, check all keys for debugging
        if ad_supported == 0 and premium == 0:
            # Debug: print available keys
            print(f"DEBUG: Available keys in streams_data: {list(streams_data.keys())}")
            print(f"DEBUG: Total streams: {total_streams}")
            # Try to find any commercial_model related data
            for key, value in streams_data.items():
                if 'ad' in key.lower() or 'free' in key.lower():
                    print(f"DEBUG: Found potential ad/free key: {key} = {value}")
                if 'premium' in key.lower() or 'paid' in key.lower():
                    print(f"DEBUG: Found potential premium/paid key: {key} = {value}")
        
        # Calculate free ratio
        free_ratio = ad_supported / total_streams if total_streams > 0 else 0
        
        # Debug output
        print(f"DEBUG Free Service Check: ad_supported={ad_supported}, premium={premium}, total={total_streams}, free_ratio={free_ratio:.2%}")
        
        # Flag conditions
        all_free = free_ratio >= self.free_max_threshold
        too_low_free = free_ratio < self.free_min_threshold and total_streams > 0
        
        flagged = all_free or too_low_free
        
        if all_free:
            reason = f'100% free service streams (suspicious - no premium users)'
        elif too_low_free:
            reason = f'Only {free_ratio*100:.1f}% free service streams (suspiciously low)'
        else:
            reason = f'Free service ratio normal ({free_ratio*100:.1f}%)'
        
        return {
            'flagged': flagged,
            'reason': reason,
            'details': {
                'free_ratio': free_ratio,
                'ad_supported_streams': ad_supported,
                'premium_streams': premium,
                'total_streams': total_streams
            }
        }
    
    def check_zero_streams(self, api_response: Dict[str, Any], 
                          historical_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Check if streams have dropped to zero (indication removed).
        
        Args:
            api_response: Current API response
            historical_data: Previous period's data for comparison
            
        Returns:
            Dictionary with flag status and details
        """
        streams_data = self.extract_streams_data(api_response)
        
        if not streams_data:
            return {
                'flagged': False,
                'reason': 'No streaming data available',
                'details': None
            }
        
        current_streams = streams_data.get('total', 0)
        
        # Flag if current streams are zero
        if current_streams == 0:
            # Check if we have historical data showing it wasn't always zero
            had_streams = False
            if historical_data:
                hist_data = self.extract_streams_data(historical_data)
                if hist_data and hist_data.get('total', 0) > 0:
                    had_streams = True
            
            return {
                'flagged': True,
                'reason': 'Streams dropped to zero (possible content removal)' if had_streams else 'No streams found (may indicate content removal)',
                'details': {
                    'current_streams': current_streams,
                    'had_previous_streams': had_streams
                }
            }
        
        return {
            'flagged': False,
            'reason': f'Active streams: {current_streams:,}',
            'details': {
                'current_streams': current_streams
            }
        }
    
    def analyze_isrc(self, isrc: str, api_response: Dict[str, Any], 
                    historical_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Run all checks on a single ISRC.
        
        Args:
            isrc: The ISRC being analyzed
            api_response: Current API response for this ISRC
            historical_data: Optional historical data for comparison
            
        Returns:
            Dictionary with all flag results
        """
        results = {
            'isrc': isrc,
            'flags': [],
            'total_flags': 0,
            'details': {}
        }
        
        # Run each check
        dma_check = self.check_dma_concentration(api_response)
        if dma_check['flagged']:
            results['flags'].append({
                'type': 'dma_concentration',
                'message': dma_check['reason']
            })
            results['details']['dma'] = dma_check['details']
        
        free_check = self.check_free_service_ratio(api_response)
        if free_check['flagged']:
            results['flags'].append({
                'type': 'free_service_anomaly',
                'message': free_check['reason']
            })
            results['details']['free_service'] = free_check['details']
        
        zero_check = self.check_zero_streams(api_response, historical_data)
        if zero_check['flagged']:
            results['flags'].append({
                'type': 'zero_streams',
                'message': zero_check['reason']
            })
            results['details']['zero_streams'] = zero_check['details']
        
        results['total_flags'] = len(results['flags'])
        
        return results
    
    def analyze_batch(self, isrc_data: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        Analyze multiple ISRCs and return results as a DataFrame.
        
        Args:
            isrc_data: Dictionary mapping ISRC to API response data
            
        Returns:
            Pandas DataFrame with analysis results
        """
        results = []
        
        for isrc, api_response in isrc_data.items():
            analysis = self.analyze_isrc(isrc, api_response)
            
            # Extract DMA info if available
            dma_info = ""
            if 'dma' in analysis['details']:
                dma_details = analysis['details']['dma']
                if dma_details and dma_details.get('max_dma_name'):
                    dma_info = f"{dma_details.get('max_dma_name', 'Unknown')}: {dma_details.get('max_dma_percentage', 0):.1f}%"
            
            results.append({
                'ISRC': isrc,
                'Flagged': analysis['total_flags'] > 0,
                'Flag Count': analysis['total_flags'],
                'Flags': '; '.join([f['message'] for f in analysis['flags']]) if analysis['flags'] else 'None',
                'DMA Info': dma_info if dma_info else 'N/A',
                'Details': str(analysis['details'])
            })
        
        return pd.DataFrame(results)

