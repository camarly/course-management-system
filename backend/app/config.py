"""
Application configuration.

Loads all required environment variables from the .env file and
exposes a Config class consumed by the app factory in __init__.py.
Raises a clear error on startup if any required variable is missing.
"""

import os
from dotenv import load_dotenv
