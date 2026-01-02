"""
Desire Engine for L9 Agent
Purpose: Tracks what L wants and how strongly
"""

import yaml
from pathlib import Path


class DesireEngine:
    def __init__(self, config_path="config/desire_profile.yaml"):
        self.config = self._load_config(config_path)
        self.desires = {}

    def _load_config(self, path):
        with open(Path(path), "r") as f:
            return yaml.safe_load(f)

    def register_goal(self, goal_id: str):
        if goal_id not in self.desires:
            self.desires[goal_id] = self.config["desire_parameters"]["base_desire"]

    def reinforce(self, goal_id: str, amount: float):
        self.desires[goal_id] = min(
            self.desires.get(goal_id, 0) + amount,
            self.config["thresholds"]["obsession_cap"],
        )

    def decay(self):
        for g in self.desires:
            self.desires[g] = max(
                0.0, self.desires[g] - self.config["desire_parameters"]["decay_rate"]
            )

    def get_desire(self, goal_id: str) -> float:
        return self.desires.get(goal_id, 0.0)
