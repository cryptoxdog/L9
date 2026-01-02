"""
Trust Visualization Helpers for L9 Agent
Purpose: Map trust scores to visual representations
"""


def scalar_to_color(score: float):
    """
    Map trust score to a color scale for UI/hypergraph overlay
    Low trust -> red
    Medium -> yellow/orange
    High -> green
    """
    if score < 0.4:
        return "red"
    elif score < 0.75:
        return "orange"
    else:
        return "green"
