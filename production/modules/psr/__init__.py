"""
PSR Module - Predictive State Representation v2

This module provides predictive state inference capabilities for modeling
dynamical systems and POMDPs.
"""

from .psr_adapter import handles, run

__all__ = ['handles', 'run']

# Module metadata
MODULE_NAME = "psr"
MODULE_VERSION = "1.0.0"
MODULE_CAPABILITIES = [
    "predictive_state_update",
    "belief_update",
    "long_horizon_prediction",
    "likelihood_computation"
]

