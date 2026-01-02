"""
Trust Model for L9 Agent
Purpose: Track and manage trust scores for partners/users
"""


class TrustModel:
    def __init__(self, initial=0.5, decay=0.01):
        self.trust_score = initial
        self.decay_rate = decay
        self.history = []

    def decay(self):
        """Slowly decay trust toward neutral (0.5) over time."""
        diff = self.trust_score - 0.5
        self.trust_score -= diff * self.decay_rate
        self.trust_score = max(0.0, min(1.0, self.trust_score))

    def reinforce(self, amount):
        self.trust_score += amount
        self.trust_score = max(0.0, min(1.0, self.trust_score))

    def penalize(self, amount):
        self.trust_score -= amount
        self.trust_score = max(0.0, min(1.0, self.trust_score))

    def as_scalar(self):
        return self.trust_score

    def log(self, event):
        self.history.append((event, self.trust_score))
