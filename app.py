"""
Streamlit Application for Luminate API Analysis

This is the main user interface for the application. Streamlit creates
a web-based UI that runs in your browser.

Key Concepts:
- Streamlit: Python library that turns scripts into web apps
- Session State: Stores data between user interactions
- File Upload: Allows users to upload CSV files through the browser
- Data Processing: Reads CSV, calls API, analyzes results
"""

import streamlit as st
import pandas as pd
import time
import hashlib
import os
from typing import Dict, List, Optional
from luminate_client import LuminateAPIClient
from analysis import ManipulationDetector
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Luminate API Analyzer",
    page_icon="🎵",
    layout="wide"
)

# Authentication Configuration
# Store credentials in environment variables for security
APP_USERNAME = os.getenv('APP_USERNAME', 'admin')
APP_PASSWORD_HASH = os.getenv('APP_PASSWORD_HASH', '')

# Default password hash (CHANGE THIS IN PRODUCTION!)
# To generate: hashlib.sha256("your_password".encode()).hexdigest()
DEFAULT_PASSWORD_HASH = hashlib.sha256('Luminate2025!'.encode()).hexdigest()

if not APP_PASSWORD_HASH:
    APP_PASSWORD_HASH = DEFAULT_PASSWORD_HASH

def check_password(password: str) -> bool:
    """Check if the provided password matches the stored hash."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == APP_PASSWORD_HASH

def show_login():
    """Display login form."""
    st.title("🔐 Luminate API Analyzer - Login")
    st.markdown("Please enter your credentials to access the application.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Login", type="primary")
            
            if submit:
                if username == APP_USERNAME and check_password(password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
    
    st.markdown("---")
    st.info("💡 **Note**: Contact your administrator for login credentials.")

# Authentication check
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login()
    st.stop()

# Initialize session state (only after authentication)
# Session state persists data across user interactions (like a database for the session)
if 'api_client' not in st.session_state:
    st.session_state.api_client = None
if 'detector' not in st.session_state:
    st.session_state.detector = ManipulationDetector()
if 'results' not in st.session_state:
    st.session_state.results = None
if 'error_log' not in st.session_state:
    st.session_state.error_log = []


def initialize_api_client():
    """Initialize and authenticate the API client."""
    if st.session_state.api_client is None:
        with st.spinner("Initializing API client..."):
            client = LuminateAPIClient()
            auth_result = client.authenticate()
            if auth_result:
                st.session_state.api_client = client
                st.success("✅ API client initialized and authenticated!")
                return True
            else:
                error_msg = """
                ❌ **Failed to authenticate with Luminate API**
                
                **Possible issues:**
                1. Check your API credentials in `config.py`
                2. Verify your API key is correct
                3. Check your username and password
                4. Ensure you have internet connection
                
                **Check the terminal** for detailed error messages.
                """
                st.error(error_msg)
                return False
    return True


def process_csv(uploaded_file) -> pd.DataFrame:
    """
    Read and validate the uploaded CSV file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        DataFrame with ISRCs
    """
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(uploaded_file)
        
        # Try to find ISRC column (case-insensitive)
        isrc_column = None
        for col in df.columns:
            if 'isrc' in col.lower():
                isrc_column = col
                break
        
        if isrc_column is None:
            # If no ISRC column found, assume first column
            isrc_column = df.columns[0]
            st.warning(f"No 'ISRC' column found. Using first column '{isrc_column}' as ISRC.")
        
        # Extract ISRCs and clean them
        isrcs = df[isrc_column].dropna().astype(str).str.strip().unique().tolist()
        
        return pd.DataFrame({'ISRC': isrcs})
    
    except Exception as e:
        st.error(f"Error reading CSV file: {str(e)}")
        return pd.DataFrame()


def fetch_isrc_data(isrcs: List[str], progress_bar, status_text, 
                   start_date: Optional[str] = None, 
                   end_date: Optional[str] = None,
                   location: Optional[str] = None) -> Dict[str, Optional[Dict]]:
    """
    Fetch data from API for all ISRCs with progress tracking.
    
    Args:
        isrcs: List of ISRC codes to fetch
        progress_bar: Streamlit progress bar widget
        status_text: Streamlit text widget for status updates
        start_date: Start date for data range (format: YYYY-MM-DD)
        end_date: End date for data range (format: YYYY-MM-DD)
        location: Location code (e.g., 'US' for United States)
        
    Returns:
        Dictionary mapping ISRC to API response
    """
    results = {}
    total = len(isrcs)
    errors = []
    
    for i, isrc in enumerate(isrcs):
        # Update progress
        progress = (i + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"Fetching {i+1}/{total}: {isrc}")
        
        try:
            # Fetch data from API with date range parameters
            data = st.session_state.api_client.get_musical_recording(
                isrc,
                start_date=start_date,
                end_date=end_date,
                location=location
            )
            
            # Log errors to error log
            if data is None:
                # None means actual error (404, 500, etc.)
                error_msg = f"Error fetching data (404, 500, or other error)"
                errors.append(f"{isrc}: {error_msg}")
                st.session_state.error_log.append({
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'API Error',
                    'isrc': isrc,
                    'message': error_msg,
                    'details': {
                        'start_date': start_date,
                        'end_date': end_date,
                        'location': location
                    }
                })
            elif isinstance(data, dict) and len(data) == 0:
                # Empty dict means 204 - ISRC found but no data for this period
                # This is valid, not an error - just no data for the requested time period
                # Don't log as error, but note it
                pass  # 204 is valid - ISRC exists but no data for this period
            elif not isinstance(data, dict):
                error_msg = f"Unexpected data type: {type(data)}"
                errors.append(f"{isrc}: {error_msg}")
                st.session_state.error_log.append({
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'Data Type Error',
                    'isrc': isrc,
                    'message': error_msg
                })
            elif 'error' in data:
                error_msg = data.get('error', {}).get('message', 'Unknown error')
                errors.append(f"{isrc}: API error - {error_msg}")
                st.session_state.error_log.append({
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'type': 'API Error',
                    'isrc': isrc,
                    'message': error_msg,
                    'details': data.get('error', {})
                })
            else:
                # Check if we have any metrics/consumption data
                has_metrics = 'metrics' in data or 'consumption_data' in data
                if not has_metrics:
                    error_msg = "No metrics or consumption_data found in response"
                    errors.append(f"{isrc}: {error_msg}")
                    st.session_state.error_log.append({
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'type': 'No Metrics',
                        'isrc': isrc,
                        'message': error_msg,
                        'details': {'response_keys': list(data.keys()) if isinstance(data, dict) else 'Not a dict'}
                    })
            
            results[isrc] = data
            
        except Exception as e:
            error_msg = f"Exception - {str(e)}"
            errors.append(f"{isrc}: {error_msg}")
            st.session_state.error_log.append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'Exception',
                'isrc': isrc,
                'message': error_msg
            })
            results[isrc] = None
        
        # Small delay to respect rate limits
        time.sleep(0.1)
    
    # Display errors if any
    if errors:
        error_container = st.container()
        with error_container:
            st.warning(f"⚠️ {len(errors)} ISRCs had issues. Check the **Error Log** tab for details.")
            with st.expander("Quick Error Summary", expanded=False):
                for error in errors[:10]:  # Show first 10 errors
                    st.text(error)
                if len(errors) > 10:
                    st.text(f"... and {len(errors) - 10} more errors (see Error Log tab)")
    
    return results


def main():
    """Main application function."""
    
    # Title and description
    st.title("🎵 Luminate API Analyzer")
    st.markdown("""
    This tool analyzes ISRCs (International Standard Recording Codes) using the Luminate Music API
    to detect potential signs of manipulation or fraud.
    
    **What it checks:**
    - 🗺️ **Geographic Concentration**: Flags ISRCs with >80% of streams from a single DMA
    - 💰 **Free Service Anomalies**: Flags ISRCs with 100% free streams or <3% free streams
    - 📉 **Zero Streams**: Flags ISRCs where streams dropped to zero (possible removal)
    """)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.api_client = None
            st.rerun()
        
        st.markdown("---")
        
        # API Status
        if st.session_state.api_client:
            st.success("✅ API Connected")
            if st.button("Re-authenticate"):
                st.session_state.api_client = None
                st.rerun()
        else:
            st.warning("⚠️ API Not Connected")
            if st.button("Connect to API"):
                initialize_api_client()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📅 Date Range Settings")
        
        # Date range inputs
        use_date_range = st.checkbox(
            "Use date range filter",
            value=False,
            help="Filter data by specific date range"
        )
        
        if use_date_range:
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=None,
                    help="Start date for data analysis (YYYY-MM-DD)"
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=None,
                    help="End date for data analysis (YYYY-MM-DD)"
                )
            
            # Validate date range
            if start_date and end_date:
                if start_date > end_date:
                    st.error("⚠️ Start date must be before end date")
                else:
                    st.info(f"📊 Analyzing data from {start_date} to {end_date}")
        else:
            start_date = None
            end_date = None
        
        # Location filter
        location = st.text_input(
            "Location Code (optional)",
            value="",
            help="Filter by location code (e.g., 'US' for United States). Leave empty for all locations.",
            placeholder="US"
        )
        location = location.strip() if location else None
        
        st.markdown("---")
        st.markdown("### 📊 Analysis Settings")
        
        # Configurable thresholds
        dma_threshold = st.slider(
            "DMA Concentration Threshold (%)",
            min_value=50,
            max_value=100,
            value=80,
            help="Flag ISRCs with more than this percentage of streams from a single DMA"
        )
        
        free_min_threshold = st.slider(
            "Minimum Free Service Threshold (%)",
            min_value=0,
            max_value=10,
            value=3,
            help="Flag ISRCs with less than this percentage of free service streams"
        )
        
        # Update detector thresholds
        st.session_state.detector.dma_threshold = dma_threshold / 100
        st.session_state.detector.free_min_threshold = free_min_threshold / 100
        
        # Store date range in session state for use in main tab
        # Always store location, but only store dates if use_date_range is checked
        if use_date_range:
            st.session_state.date_range = {
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                'location': location
            }
        else:
            st.session_state.date_range = {
                'start_date': None,
                'end_date': None,
                'location': location
            }
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Analyze", "📊 Results", "📋 Error Log", "ℹ️ Help & About"])
    
    with tab1:
        st.header("Upload CSV File")
        st.markdown("""
        Upload a CSV file containing ISRCs. The file should have a column named 'ISRC' 
        (case-insensitive), or the first column will be used.
        """)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload a CSV file with ISRC codes"
        )
        
        if uploaded_file is not None:
            # Read and display CSV
            df = process_csv(uploaded_file)
            
            if not df.empty:
                st.success(f"✅ Loaded {len(df)} unique ISRCs")
                st.dataframe(df.head(10), use_container_width=True)
                
                if len(df) > 10:
                    st.info(f"... and {len(df) - 10} more ISRCs")
                
                # Initialize API if needed
                if st.session_state.api_client is None:
                    if not initialize_api_client():
                        st.stop()
                
                # Display date range info if set
                date_info = st.session_state.get('date_range', {})
                if date_info.get('start_date') or date_info.get('end_date'):
                    date_str = ""
                    if date_info.get('start_date') and date_info.get('end_date'):
                        date_str = f"📅 Date Range: {date_info['start_date']} to {date_info['end_date']}"
                    elif date_info.get('start_date'):
                        date_str = f"📅 From: {date_info['start_date']}"
                    elif date_info.get('end_date'):
                        date_str = f"📅 Until: {date_info['end_date']}"
                    
                    if date_info.get('location'):
                        date_str += f" | 📍 Location: {date_info['location']}"
                    
                    if date_str:
                        st.info(date_str)
                
                # Analyze button
                if st.button("🔍 Analyze ISRCs", type="primary", use_container_width=True):
                    isrcs = df['ISRC'].tolist()
                    
                    # Get date range from session state
                    date_range = st.session_state.get('date_range', {})
                    start_date = date_range.get('start_date')
                    end_date = date_range.get('end_date')
                    location = date_range.get('location')
                    
                    # Create progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Fetch data from API with date range
                    with st.spinner("Fetching data from Luminate API..."):
                        api_data = fetch_isrc_data(
                            isrcs, 
                            progress_bar, 
                            status_text,
                            start_date=start_date,
                            end_date=end_date,
                            location=location
                        )
                    
                    # Store API data in session state BEFORE rerun so we can show debug after
                    st.session_state.api_data = api_data
                    st.session_state.isrcs_for_debug = isrcs
                    
                    # Analyze the data
                    status_text.text("Analyzing data for manipulation indicators...")
                    
                    results_df = st.session_state.detector.analyze_batch(api_data)
                    
                    # Store results in session state
                    st.session_state.results = {
                        'dataframe': results_df,
                        'api_data': api_data,
                        'isrcs': isrcs,
                        'date_range': date_range
                    }
                    
                    progress_bar.progress(1.0)
                    status_text.text("✅ Analysis complete!")
                    
                    st.success(f"Analysis complete! Found {len(results_df[results_df['Flagged'] == True])} flagged ISRCs.")
                    st.rerun()
                
                # Show debug section if we have API data (either from just running or from previous run)
                if st.session_state.get('api_data'):
                    api_data = st.session_state.api_data
                    isrcs = st.session_state.get('isrcs_for_debug', [])
                    
                    st.markdown("---")
                    st.markdown("### 🔍 Debug Information")
                    
                    # Debug: Check API responses
                    # Count successful (has data), no data (204 - empty dict), and errors (None)
                    successful_fetches = sum(1 for v in api_data.values() if v is not None and len(v) > 0)
                    no_data_fetches = sum(1 for v in api_data.values() if isinstance(v, dict) and len(v) == 0)
                    failed_fetches = sum(1 for v in api_data.values() if v is None)
                    
                    # Show fetch statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("✅ With Data", successful_fetches)
                    with col2:
                        st.metric("ℹ️ No Data (204)", no_data_fetches)
                    with col3:
                        st.metric("❌ Errors", failed_fetches)
                    
                    if no_data_fetches > 0:
                        st.info(f"ℹ️ {no_data_fetches} ISRCs returned 204 (no data for this time period). This is normal - the ISRC exists but has no streaming data for the requested date range.")
                        no_data_isrcs = [isrc for isrc, data in api_data.items() if isinstance(data, dict) and len(data) == 0]
                        if no_data_isrcs:
                            with st.expander(f"ℹ️ ISRCs with No Data ({len(no_data_isrcs)})", expanded=False):
                                st.write(", ".join(no_data_isrcs[:20]))
                                if len(no_data_isrcs) > 20:
                                    st.write(f"... and {len(no_data_isrcs) - 20} more")
                                st.info("💡 **Note:** 204 means the ISRC was found but has no data for this time period. Try adjusting the date range or removing location filter.")
                    
                    if failed_fetches > 0:
                        st.warning(f"⚠️ {failed_fetches} out of {len(api_data)} ISRCs had errors. Check **Error Log** tab for details.")
                        # Show which ISRCs failed
                        failed_isrcs = [isrc for isrc, data in api_data.items() if data is None]
                        if failed_isrcs:
                            with st.expander("❌ Failed ISRCs", expanded=True):
                                st.write(", ".join(failed_isrcs[:20]))
                                if len(failed_isrcs) > 20:
                                    st.write(f"... and {len(failed_isrcs) - 20} more")
                                st.warning("💡 **Note:** These are actual errors (404, 500, etc.). Check Error Log for details.")
                    
                    # Debug: Show sample API response and extracted data
                    sample_isrc = isrcs[0] if isrcs else None
                    if sample_isrc:
                        with st.expander("🔍 Debug: View Sample API Response", expanded=True):
                            sample_data = api_data.get(sample_isrc)
                            if sample_data:
                                st.markdown(f"**ISRC: {sample_isrc}**")
                                
                                # Show raw API response
                                st.markdown("**1. Raw API Response:**")
                                st.json(sample_data)
                                
                                # Also show what the analysis module sees
                                st.markdown("---")
                                st.markdown("**2. Extracted Streams Data:**")
                                streams_data = st.session_state.detector.extract_streams_data(sample_data)
                                if streams_data:
                                    st.json(streams_data)
                                    
                                    # Specifically show DMA-related keys
                                    st.markdown("---")
                                    st.markdown("**3. DMA-Related Keys Found:**")
                                    dma_keys = [k for k in streams_data.keys() if 'dma' in k.lower() or 'location' in k.lower() or 'market' in k.lower() or 'geographic' in k.lower()]
                                    if dma_keys:
                                        st.success(f"✅ Found {len(dma_keys)} DMA-related keys:")
                                        for key in dma_keys:
                                            value = streams_data[key]
                                            st.text(f"  - {key}: {type(value).__name__}")
                                            if isinstance(value, dict):
                                                st.text(f"    Keys: {list(value.keys())[:10]}")
                                            elif isinstance(value, list):
                                                st.text(f"    Length: {len(value)} items")
                                            else:
                                                st.text(f"    Value: {str(value)[:100]}")
                                    else:
                                        st.warning("⚠️ No DMA-related keys found in extracted data")
                                        st.info("💡 Available keys: " + ", ".join(list(streams_data.keys())[:20]))
                                    
                                    # Show DMA check result
                                    st.markdown("---")
                                    st.markdown("**4. DMA Concentration Check:**")
                                    from analysis import ManipulationDetector
                                    temp_detector = ManipulationDetector()
                                    dma_check = temp_detector.check_dma_concentration(sample_data)
                                    st.json(dma_check)
                                    
                                else:
                                    st.error("❌ Could not extract streams data from this response")
                                    st.info("💡 This might mean the API response structure is different than expected. Check the raw response above.")
                            else:
                                st.error(f"❌ No data returned for ISRC: {sample_isrc}")
                                st.info("💡 Check terminal for error messages about this ISRC")
                                
                        st.info("💡 **Tip**: Check your terminal/console for detailed DEBUG output showing what DMA data was found (or not found)")
    
    with tab2:
        st.header("Analysis Results")
        
        if st.session_state.results is None:
            st.info("👆 Upload a CSV file and run analysis to see results here.")
        else:
            results_df = st.session_state.results['dataframe']
            date_range = st.session_state.results.get('date_range', {})
            
            # Display date range used for analysis
            if date_range.get('start_date') or date_range.get('end_date'):
                date_info = []
                if date_range.get('start_date'):
                    date_info.append(f"From: {date_range['start_date']}")
                if date_range.get('end_date'):
                    date_info.append(f"To: {date_range['end_date']}")
                if date_range.get('location'):
                    date_info.append(f"Location: {date_range['location']}")
                
                if date_info:
                    st.info("📅 " + " | ".join(date_info))
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total ISRCs", len(results_df))
            with col2:
                flagged_count = len(results_df[results_df['Flagged'] == True])
                st.metric("Flagged ISRCs", flagged_count, delta=f"{flagged_count/len(results_df)*100:.1f}%")
            with col3:
                avg_flags = results_df['Flag Count'].mean()
                st.metric("Avg Flags per ISRC", f"{avg_flags:.2f}")
            with col4:
                flag_rate = (flagged_count / len(results_df) * 100) if len(results_df) > 0 else 0
                st.metric("Flag Rate", f"{flag_rate:.1f}%")
            
            st.markdown("---")
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                show_only_flagged = st.checkbox("Show only flagged ISRCs", value=False)
            with col2:
                if st.button("📥 Download Results as CSV"):
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="Click to download",
                        data=csv,
                        file_name=f"luminate_analysis_{int(time.time())}.csv",
                        mime="text/csv"
                    )
            
            # Display results table
            display_df = results_df[results_df['Flagged'] == True] if show_only_flagged else results_df
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Detailed view for selected ISRC
            if len(display_df) > 0:
                st.markdown("### 🔍 Detailed View")
                selected_isrc = st.selectbox(
                    "Select an ISRC to view detailed information",
                    display_df['ISRC'].tolist()
                )
                
                if selected_isrc and st.session_state.results['api_data'].get(selected_isrc):
                    api_response = st.session_state.results['api_data'][selected_isrc]
                    
                    # Show raw API response in expander
                    with st.expander("📋 Raw API Response"):
                        st.json(api_response)
                    
                    # Show analysis details
                    analysis = st.session_state.detector.analyze_isrc(selected_isrc, api_response)
                    
                    if analysis['flags']:
                        st.warning("⚠️ **Flags Detected:**")
                        for flag in analysis['flags']:
                            st.markdown(f"- **{flag['type']}**: {flag['message']}")
                    
                    if analysis['details']:
                        st.markdown("**Details:**")
                        st.json(analysis['details'])
    
    with tab3:
        st.header("📋 Error Log")
        st.markdown("This log shows errors and warnings from your analysis sessions.")
        
        if not st.session_state.error_log:
            st.info("✅ No errors logged. All requests are working correctly!")
        else:
            # Show error summary
            error_count = len(st.session_state.error_log)
            st.metric("Total Errors/Warnings", error_count)
            
            # Clear log button
            if st.button("🗑️ Clear Error Log"):
                st.session_state.error_log = []
                st.rerun()
            
            st.markdown("---")
            
            # Display errors
            for i, error in enumerate(reversed(st.session_state.error_log[-50:]), 1):  # Show last 50
                with st.expander(f"⚠️ {error['type']}: {error['isrc']} - {error['timestamp']}", expanded=False):
                    st.markdown(f"**ISRC:** {error['isrc']}")
                    st.markdown(f"**Type:** {error['type']}")
                    st.markdown(f"**Time:** {error['timestamp']}")
                    st.markdown(f"**Message:** {error['message']}")
                    if 'details' in error:
                        st.markdown("**Details:**")
                        st.json(error['details'])
            
            if len(st.session_state.error_log) > 50:
                st.info(f"Showing last 50 errors. Total: {len(st.session_state.error_log)}")
    
    with tab4:
        st.header("ℹ️ Help & About")
        
        # Quick Help Section
        st.markdown("### 🆘 Quick Help")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### Common Issues
            
            **"No flags showing"**
            - Check if ISRCs have streaming data
            - Some ISRCs may return 204 (no data)
            - Check Error Log tab for details
            
            **"Authentication failed"**
            - Verify credentials in `config.py`
            - Check API key permissions
            - Ensure internet connection
            
            **"All ISRCs failed"**
            - Check date range (may be too restrictive)
            - Verify ISRCs exist in Luminate database
            - Check Error Log for specific errors
            """)
        
        with col2:
            st.markdown("""
            #### Status Codes
            
            **200** = Success with data ✅
            **204** = Success but no data ℹ️
            **401** = Authentication failed ❌
            **403** = Permission denied ❌
            **404** = ISRC not found ⚠️
            **500** = Server error ❌
            
            #### Getting Help
            
            - Check **Error Log** tab for details
            - Review terminal output
            - See troubleshooting guide in README.md
            """)
        
        st.markdown("---")
        
        # About Section
        st.markdown("### 📚 About This Application")
        st.markdown("""
        ### 🎓 Educational Overview
        
        This application demonstrates several important software engineering concepts:
        
        #### 1. **API Integration**
        - **What**: Connecting to external services (Luminate API) to retrieve data
        - **Why**: APIs allow us to access data without managing databases ourselves
        - **How**: We use HTTP requests (GET/POST) to communicate with the API
        
        #### 2. **Authentication & Security**
        - **What**: Securely storing and using API credentials
        - **Why**: Prevents unauthorized access and protects sensitive information
        - **How**: We use environment variables and token-based authentication
        
        #### 3. **Data Processing**
        - **What**: Reading CSV files, transforming data, analyzing patterns
        - **Why**: Real-world data comes in various formats and needs processing
        - **How**: We use pandas (DataFrame) to handle tabular data efficiently
        
        #### 4. **User Interface**
        - **What**: Creating a web-based interface for non-technical users
        - **Why**: Makes complex tools accessible to everyone
        - **How**: Streamlit automatically generates a UI from Python code
        
        #### 5. **Anomaly Detection**
        - **What**: Identifying patterns that deviate from normal behavior
        - **Why**: Helps detect fraud, manipulation, or data quality issues
        - **How**: We define thresholds and check data against them
        
        ### 🏗️ Architecture
        
        The application is structured in modules:
        - **config.py**: Manages credentials and configuration
        - **luminate_client.py**: Handles API communication
        - **analysis.py**: Contains detection logic
        - **app.py**: Main UI (this file)
        
        This modular design makes the code:
        - **Maintainable**: Easy to update individual components
        - **Testable**: Each module can be tested independently
        - **Scalable**: Easy to add new APIs or analysis methods
        
        ### 🚀 Future Enhancements
        
        The architecture supports adding:
        - Additional APIs (Spotify, Apple Music, etc.)
        - More sophisticated detection algorithms
        - Historical trend analysis
        - Machine learning-based anomaly detection
        """)


if __name__ == "__main__":
    # Initialize API on startup
    if st.session_state.api_client is None:
        initialize_api_client()
    
    main()

