"""
Vercel serverless function entry point
"""
import sys
import os

# Add parent directory to path so we can import from root
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api_contribution import app

# Vercel expects 'app' to be the Flask application
# This file acts as the entry point for Vercel
