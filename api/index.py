"""Vercel serverless entry point — wraps the Flask app."""

import sys
import os

# Add project root to path so ironforge package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ironforge.web import app

# Vercel expects a WSGI-compatible `app` object
