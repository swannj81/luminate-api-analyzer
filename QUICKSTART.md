# 🚀 Quick Start Guide

## Installation (5 minutes)

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser**:
   - The app will open automatically at `http://localhost:8501`
   - If not, navigate there manually

## First Use (2 minutes)

1. **Upload a CSV file**:
   - Click "Upload CSV File" in the app
   - Use the provided `sample_isrcs.csv` or create your own
   - Your CSV should have a column named "ISRC"

2. **Click "Analyze ISRCs"**:
   - The app will fetch data from the Luminate API
   - Wait for the analysis to complete

3. **View Results**:
   - Check the "Results" tab
   - See which ISRCs are flagged
   - Click on individual ISRCs for details

## Understanding the Results

### Flag Types

- **DMA Concentration**: >80% of streams from one geographic area
- **Free Service Anomaly**: 100% free OR <3% free streams
- **Zero Streams**: No current streams (possible removal)

### What to Do Next

1. Review flagged ISRCs in detail
2. Download results as CSV for further analysis
3. Adjust thresholds in the sidebar if needed

## Troubleshooting

**"Failed to authenticate"**
- Check that your credentials are correct in `config.py`
- The API may use API key directly (already configured)

**"No streaming data available"**
- The ISRC may not exist in Luminate's database
- Check the "Raw API Response" in detailed view

**App won't start**
- Make sure you've installed requirements: `pip install -r requirements.txt`
- Check Python version: `python --version` (need 3.8+)

## Next Steps

- Read `README.md` for detailed explanations
- Explore the code in each module
- Try modifying thresholds to see how results change
- Add your own detection rules in `analysis.py`

