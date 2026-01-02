"""
L9 Agent - High-Agency Autonomy System
Phase 5: Cognitive Architecture for L Agent

This module contains the core cognitive systems for the L9 agent including:
- Value alignment
- Motivation (desire, will, persistence)
- Emotion regulation
- Belief modeling
- Trust tracking
- Foresight and planning
- Judgment and decision making
- Theory of mind
- Multi-agent coordination
- Partner intent modeling
- Belief calibration
"""

__version__ = "0.1.0"
__author__ = "L9 Team"

from .value_alignment import ValueAlignmentEngine

__all__ = [
    "ValueAlignmentEngine",
]
