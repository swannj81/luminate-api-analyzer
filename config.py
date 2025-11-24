"""
Configuration Management Module

This module handles loading and storing API credentials securely.
We use environment variables and a local .env file to avoid hardcoding
sensitive information in our source code.

Key Concepts:
- Environment variables: System-level variables that can store secrets
- .env file: A local file (not committed to git) that stores credentials
- python-dotenv: Library that loads .env files into environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This allows us to store credentials locally without hardcoding them
load_dotenv()

# API Configuration
# These values are loaded from environment variables or .env file
LUM_API_KEY = os.getenv('LUM_API_KEY', 'qrbtgVuVTgaJq0VbuE8y1lX1xaoKg9D2tQQu0yg7')
LUM_USERNAME = os.getenv('LUM_USERNAME', 'joshua.swann@themlc.com')
LUM_PASSWORD = os.getenv('LUM_PASSWORD', 'Music2025!')

# API Base URL
LUM_API_BASE_URL = 'https://api.luminatedata.com'

# API Headers
LUM_API_HEADERS = {
    'Accept': 'application/vnd.luminate-data.svc-apibff.v1+json',
    'x-api-key': LUM_API_KEY,
    'Content-Type': 'application/json'
}

