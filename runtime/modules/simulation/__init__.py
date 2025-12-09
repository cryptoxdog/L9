"""
Simulation Module - Dreamer-V3 Model-Based RL

This module provides model-based reinforcement learning with latent dynamics
for imagination-based planning and simulation.
"""

from .dreamer_adapter import handles, run

__all__ = ['handles', 'run']

# Module metadata
MODULE_NAME = "simulation"
MODULE_VERSION = "1.0.0"
MODULE_CAPABILITIES = [
    "latent_rollouts",
    "model_based_planning",
    "imagination_simulation",
    "reward_prediction"
]

