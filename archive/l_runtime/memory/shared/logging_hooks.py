# l/memory/l1/logging_hooks.py

from l.memory.l1.l1_writer import writer
from l.memory.shared.hashing import hash_payload

class LoggingHooks:

    @staticmethod
    def log_reasoning(mode, signature: dict, directive: dict):
        payload = {
            "directive_hash": hash_payload(directive),
            "reasoning_mode": mode,
            "pattern_type": signature.get("type", "unknown"),
            "pattern_signature": signature,
        }
        writer.write_reasoning(payload)

    @staticmethod
    def log_decision(decision: dict):
        writer.write_decision(decision)

    @staticmethod
    def log_trace(entry: dict):
        writer.write_trace(entry)

hooks = LoggingHooks()

