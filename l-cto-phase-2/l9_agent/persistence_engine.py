"""
Persistence Engine for L9 Agent
Purpose: Determines whether L keeps going
Note: This is where grit lives.
"""


class PersistenceEngine:
    def __init__(self, thresholds):
        self.thresholds = thresholds

    def should_persist(self, desire, will):
        if desire < self.thresholds["abandonment"]:
            return False
        if will > self.thresholds["activation"]:
            return True
        return False
