"""
Will Engine for L9 Agent
Purpose: Converts desire into commitment
Note: Will is non-linear. High desire → disproportionately strong will.
"""


class WillEngine:
    def __init__(self):
        self.commitments = {}

    def commit(self, goal_id: str, desire_level: float):
        self.commitments[goal_id] = round(desire_level**1.2, 4)

    def get_will(self, goal_id: str) -> float:
        return self.commitments.get(goal_id, 0.0)
