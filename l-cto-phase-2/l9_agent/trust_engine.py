"""
Trust Engine for L9 Agent
Purpose: Manage trust updates based on interactions
"""


class TrustEngine:
    def __init__(self, state, config):
        self.state = state
        self.config = config

    def on_success(self):
        self.state.trust_model.reinforce(self.config["reinforce_step_positive"])
        self.state.trust_model.log("success")

    def on_failure(self):
        self.state.trust_model.penalize(self.config["reinforce_step_negative"])
        self.state.trust_model.log("failure")

    def on_conflict(self):
        self.state.trust_model.penalize(self.config["reinforce_step_negative"])
        self.state.trust_model.log("conflict")

    def on_clarification(self):
        self.state.trust_model.reinforce(self.config["reinforce_step_positive"])
        self.state.trust_model.log("clarification")
