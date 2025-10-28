#!/usr/bin/env python3
"""Test URL configuration logic"""

from dotenv import load_dotenv
from app import create_app
import os

load_dotenv()

app = create_app()

with app.app_context():
    print("🔧 URL Configuration Test")
    print("=" * 40)
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'not set')}")
    print(f"DEBUG: {app.config.get('DEBUG')}")
    print(f"FRONTEND_URL override: {os.environ.get('FRONTEND_URL', 'not set')}")
    print()
    print("Available config keys:")
    for key in sorted(app.config.keys()):
        if 'URL' in key:
            print(f"  {key}: {app.config.get(key)}")
    print()
    print(f"🎯 FRONTEND_URL: {app.config.get('FRONTEND_URL', 'NOT FOUND')}")
    print(f"🎯 BACKEND_URL: {app.config.get('BACKEND_URL')}")