"""
L9 Research Agent CLI
=====================

Command-line interface for the unified research-to-code pipeline.

Usage:
    python -m l9.agents "topic" [--mode fast|deep|full]
    python -m l9.agents "topic" --synthesize-only
    python -m l9.agents "topic" --discover-only
    python -m l9.agents "topic" --generate-spec
"""

import asyncio
import sys

from l9.agents.research_agent import main

if __name__ == "__main__":
    asyncio.run(main())

