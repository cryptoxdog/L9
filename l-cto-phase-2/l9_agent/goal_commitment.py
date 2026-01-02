"""
Goal Commitment Tracker for L9 Agent
Purpose: Single source of truth for goal state
Answers the question: "Do I keep going, or do I let this go?"
"""


class GoalCommitmentTracker:
    def __init__(self, desire_engine, will_engine, persistence_engine):
        self.desire = desire_engine
        self.will = will_engine
        self.persistence = persistence_engine

    def update_goal(self, goal_id):
        d = self.desire.get_desire(goal_id)
        self.will.commit(goal_id, d)
        w = self.will.get_will(goal_id)
        return self.persistence.should_persist(d, w)
