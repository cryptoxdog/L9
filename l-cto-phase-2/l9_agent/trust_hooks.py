"""
Trust Hooks for L9 Agent
Purpose: Integration hooks for trust updates
"""


def after_task_feedback(task_id, outcome, user_feedback, trust_engine):
    """
    Called after user responds to agent proposal/decision
    """
    if user_feedback == "positive":
        trust_engine.on_success()
    elif user_feedback == "negative":
        trust_engine.on_failure()
    elif user_feedback == "neutral":
        trust_engine.on_clarification()


def on_conflict_detected(context, trust_engine):
    trust_engine.on_conflict()
