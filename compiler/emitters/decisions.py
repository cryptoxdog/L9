def emit(decisions):
    return {
        "decisions": [
            {
                "decision_id": f"auto.{i}",
                "statement": d["statement"],
                "status": "proposed",
            }
            for i, d in enumerate(decisions)
        ]
    }
