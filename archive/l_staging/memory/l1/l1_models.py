# l/memory/l1/l1_models.py

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class DirectiveModel(BaseModel):
    directive: Dict[str, Any]
    source: str
    priority: int = 1
    context_window: Optional[Dict] = None

class ReasoningPatternModel(BaseModel):
    directive_hash: Optional[str]
    reasoning_mode: str
    pattern_type: str
    pattern_signature: Dict[str, Any]
    effectiveness_score: Optional[float] = 0.0

class EvaluationModel(BaseModel):
    evaluation: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    confidence: Optional[float]
    category: Optional[str]

class DecisionModel(BaseModel):
    decision: str
    rationale: Optional[str]
    alternatives_considered: Optional[Dict]
    risk_profile: Optional[Dict]
    predicted_outcomes: Optional[Dict]
    confidence: Optional[float] = 0.0

class TraceModel(BaseModel):
    directive: Dict
    module_invoked: str
    latency_ms: Optional[int] = 0
    error_flag: Optional[bool] = False

class DriftModel(BaseModel):
    drift_type: str
    drift_signal: Dict
    severity: int

class AutonomyModel(BaseModel):
    previous_level: int
    new_level: int
    reason: str
    approved_by: str

