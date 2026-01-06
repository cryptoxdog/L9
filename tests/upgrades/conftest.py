"""
Conftest for upgrades tests
Ensures proper path resolution for imports
"""

import sys
import os
from pathlib import Path

# Add project root to path for upgrades imports
# Use realpath to resolve symlinks and case differences
PROJECT_ROOT = os.path.realpath(str(Path(__file__).resolve().parent.parent.parent))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Force import of upgrades package to verify path is correct
try:
    import upgrades
    import upgrades.packet_envelope
except ImportError:
    # If still not found, try adding explicitly
    pass

