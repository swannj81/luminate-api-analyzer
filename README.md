# 🎵 Luminate API Analyzer

A Python application for analyzing music streaming data from the Luminate Music API to detect potential manipulation or fraud indicators.

## 📚 What This Application Does

This tool helps identify suspicious patterns in music streaming data by:

1. **Geographic Concentration Detection**: Flags ISRCs where over 80% of streams come from a single DMA (Designated Market Area), which may indicate artificial streaming from a specific location.

2. **Free Service Anomaly Detection**: 
   - Flags ISRCs with 100% free (ad-supported) streams (suspicious - no premium users)
   - Flags ISRCs with less than 3% free service streams (suspiciously low free tier usage)

3. **Content Removal Detection**: Flags ISRCs where streams have dropped to zero, which may indicate the content has been removed or flagged.

## 🏗️ Architecture & Learning Guide

### Project Structure

```
Luminate API/
├── app.py                 # Main Streamlit UI application
├── luminate_client.py     # API client for Luminate Music API
├── analysis.py            # Manipulation detection logic
├── config.py              # Configuration and credential management
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

### Key Concepts Explained

#### 1. **API (Application Programming Interface)**
- **What**: A way for different software systems to communicate
- **Analogy**: Like a restaurant menu - you order (request) what you want, and the kitchen (API) prepares and serves it
- **In this app**: We request music data from Luminate's servers using HTTP requests

#### 2. **Authentication**
- **What**: Proving you're authorized to access the API
- **How**: 
  1. Send username/password to get a temporary "token" (like a day pass)
  2. Use that token in all subsequent requests
- **Why**: Prevents unauthorized access to sensitive data

#### 3. **ISRC (International Standard Recording Code)**
- **What**: A unique identifier for each music recording
- **Format**: Like `USRC17607839` (Country + Registrant + Year + Designation)
- **Analogy**: Like a barcode, but for songs instead of products

#### 4. **DMA (Designated Market Area)**
- **What**: Geographic regions used for media market analysis
- **Example**: New York, Los Angeles, Chicago are each separate DMAs
- **Why it matters**: Organic streams are usually distributed across many DMAs. Concentration in one DMA can indicate manipulation.

#### 5. **Streaming Metrics**
- **Commercial Model**: 
  - **Ad-Supported (Free)**: Users listen with ads (like Spotify Free)
  - **Premium (Paid)**: Users pay for ad-free listening (like Spotify Premium)
- **Content Type**: Audio vs Video streams
- **Service Type**: On-demand (user chooses) vs Programmed (radio-like)

#### 6. **DataFrame (Pandas)**
- **What**: A table-like data structure (like Excel spreadsheets in code)
- **Why**: Makes it easy to work with CSV files and tabular data
- **In this app**: We use DataFrames to store ISRCs and analysis results

#### 7. **Streamlit**
- **What**: A Python library that turns scripts into web applications
- **How**: You write Python code, Streamlit creates a web UI automatically
- **Benefits**: No need to learn HTML/CSS/JavaScript - just Python!

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials** (optional):
   - The application will use default credentials from `config.py`
   - For production, create a `.env` file with:
     ```
     LUM_API_KEY=your_api_key_here
     LUM_USERNAME=your_username_here
     LUM_PASSWORD=your_password_here
     ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**:
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to that URL manually

## 📖 How to Use

1. **Upload CSV File**:
   - Click "Upload CSV File"
   - Select a CSV file containing ISRCs
   - The file should have a column named "ISRC" (case-insensitive)
   - If no ISRC column is found, the first column will be used

2. **Run Analysis**:
   - Click "🔍 Analyze ISRCs"
   - The app will:
     - Fetch data from Luminate API for each ISRC
     - Analyze the data for manipulation indicators
     - Display results

3. **Review Results**:
   - View summary statistics
   - Filter to show only flagged ISRCs
   - Click on individual ISRCs for detailed information
   - Download results as CSV

## 🔧 Configuration

### Adjustable Thresholds

In the sidebar, you can adjust:
- **DMA Concentration Threshold**: Default 80% (flag if more than this in one DMA)
- **Minimum Free Service Threshold**: Default 3% (flag if less than this)

### API Settings

The API client automatically handles:
- Authentication token management
- Rate limiting (delays between requests)
- Error handling and retries

## 🧠 Code Walkthrough

### `config.py` - Configuration Management
```python
# Loads credentials from environment variables
# This keeps sensitive data out of source code
LUM_API_KEY = os.getenv('LUM_API_KEY', 'default_value')
```

**Why**: Security best practice - never hardcode credentials in source code.

### `luminate_client.py` - API Communication
```python
def authenticate(self):
    # Sends credentials, receives token
    # Token is used for all subsequent requests
```

**Why**: Separates API logic from UI logic - makes code more maintainable.

### `analysis.py` - Detection Logic
```python
def check_dma_concentration(self, api_response):
    # Extracts DMA data from API response
    # Calculates percentages
    # Flags if over threshold
```

**Why**: Modular detection - easy to add new checks or modify existing ones.

### `app.py` - User Interface
```python
uploaded_file = st.file_uploader("Choose a CSV file")
# Streamlit automatically creates a file upload widget
```

**Why**: Streamlit handles all the web UI complexity - we just write Python.

## 🔒 Security Best Practices

1. **Never commit credentials to version control**
   - The `.gitignore` file prevents committing `.env` files
   - Always use environment variables for production

2. **Token Management**
   - Tokens expire - the client automatically re-authenticates
   - Tokens are stored in memory only (not saved to disk)

3. **Rate Limiting**
   - Built-in delays prevent overwhelming the API
   - Respects API terms of service

## 🎯 Future Enhancements

The architecture is designed to be scalable. Easy additions include:

1. **Multiple APIs**: Add Spotify, Apple Music, etc.
   - Create new client classes (e.g., `spotify_client.py`)
   - Add to the UI with tabs or dropdown selection

2. **Advanced Analysis**:
   - Machine learning for anomaly detection
   - Historical trend analysis
   - Comparative analysis across time periods

3. **Data Export**:
   - Export to Excel with formatting
   - Generate PDF reports
   - Schedule automated reports

4. **User Management**:
   - Multiple user accounts
   - Saved analysis configurations
   - Analysis history

## 🐛 Troubleshooting

### "Failed to authenticate"
- Check your credentials in `config.py` or `.env`
- Verify your API key is valid
- Check your internet connection

### "No streaming data available"
- The ISRC may not exist in Luminate's database
- The ISRC may not have streaming data for the requested period
- Check the API response in the "Detailed View" tab

### "Rate limit exceeded"
- The app includes rate limiting, but if you see this error:
  - Reduce the number of ISRCs per batch
  - Increase the delay in `luminate_client.py` (currently 0.1 seconds)

## 📚 Additional Resources

- [Luminate API Documentation](https://docs.luminatedata.com/docs/getting-started)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Requests Library Documentation](https://requests.readthedocs.io/)

## 💡 Learning Tips

1. **Start Simple**: Run the app with a small CSV (5-10 ISRCs) first
2. **Read the Code**: Each module has comments explaining concepts
3. **Experiment**: Try changing thresholds and see how results change
4. **Explore the API**: Use the "Raw API Response" view to understand the data structure
5. **Modify and Learn**: Try adding a new detection rule in `analysis.py`

## 📝 License

This project is for educational purposes. Please respect Luminate's API terms of service.

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new detection methods
- Improve the UI
- Add support for additional APIs
- Enhance documentation

---

**Happy Analyzing! 🎵**

