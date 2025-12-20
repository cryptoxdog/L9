"""
L9 Root Test Configuration
==========================

This conftest.py at the project root ensures PYTHONPATH is set correctly
before any test imports happen.
"""

import sys
from pathlib import Path

# Add project root to path BEFORE any other imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

