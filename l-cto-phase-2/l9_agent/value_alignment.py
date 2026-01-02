"""
Value Alignment Engine for L9 Agent
Purpose: Score actions, outcomes, and reflections against core values
"""

import yaml
from pathlib import Path


class ValueAlignmentEngine:
    def __init__(self, config_path="config/core_values.yaml"):
        self.config_path = Path(config_path)
        self._load_values()

    def _load_values(self):
        if not self.config_path.exists():
            raise FileNotFoundError(f"Missing core values file: {self.config_path}")

        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)

        self.core_values = data.get("core_values", {})
        self.constraints = data.get("constraints", {})

        if not self.core_values:
            raise ValueError("core_values.yaml contains no values")

        self._validate_values()

    def _validate_values(self):
        min_w = self.constraints.get("weight_min", 0.0)
        max_w = self.constraints.get("weight_max", 1.0)

        for key, meta in self.core_values.items():
            w = meta.get("weight")
            if w is None:
                raise ValueError(f"Value '{key}' missing weight")
            if not (min_w <= w <= max_w):
                raise ValueError(f"Value '{key}' weight out of bounds: {w}")

    def score_action(self, action_tags: list[str]) -> float:
        """
        Deterministic weighted alignment score ∈ [0, 1]
        """
        total_weight = 0.0
        matched_weight = 0.0

        for key, meta in self.core_values.items():
            w = meta["weight"]
            total_weight += w
            if key in action_tags:
                matched_weight += w

        if total_weight == 0:
            return 0.0

        return round(matched_weight / total_weight, 4)

    def explain_score(self, action_tags: list[str]) -> dict:
        explanation = {}
        for key, meta in self.core_values.items():
            explanation[key] = {"matched": key in action_tags, "weight": meta["weight"]}
        return explanation
