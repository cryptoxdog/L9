# L9 Agent Integration Guide

## Overview

This guide provides step-by-step instructions for integrating the `l9_agent` modules into the existing L9 repository.

## Prerequisites

- L9 repository cloned and accessible
- Python 3.11+ installed
- PyYAML package installed (`pip install pyyaml`)

## Integration Steps

### Phase 1: Verify Directory Structure

Ensure the following directories exist:

```bash
cd /home/ubuntu/L9
ls -la l9_agent/
ls -la config/
ls -la tests/l9_agent/
```

### Phase 2: Update State Manager

The `state_manager.py` file needs to be updated to support the new cognitive systems.

**Location**: Find the existing state manager (likely in `/core/` or root)

**Required Updates**:

```python
# Add to imports
from l9_agent.trust_model import TrustModel
from l9_agent.value_alignment import ValueAlignmentEngine

class StateManager:
    def __init__(self, config_path="config/"):
        # Existing initialization...
        
        # Value alignment tracking
        self.value_alignment_history = []
        self.current_value_alignment = 0.0
        
        # Motivation tracking
        self.active_goals = {}
        
        # Deadlines tracking
        self.deadlines = {}
        
        # Emotion state
        self.emotion_state = {}
        
        # Trust tracking
        self.trust_model = TrustModel(initial=0.5, decay=0.01)
        self.trust_model_map = {}  # For multiple partners
        
        # Partner registry
        self.partners = {}
        
        # Belief model (to be added when belief_model.py is integrated)
        self.belief_model = None
    
    def record_value_alignment(self, score: float):
        """Record value alignment score"""
        if not 0.0 <= score <= 1.0:
            raise ValueError("Value alignment score out of bounds")
        self.current_value_alignment = score
        self.value_alignment_history.append(score)
    
    def get_recent_alignment(self, window=10):
        """Get recent average alignment score"""
        recent = self.value_alignment_history[-window:]
        if not recent:
            return 0.0
        return sum(recent) / len(recent)
    
    def register_goal(self, goal_id):
        """Register a new goal"""
        self.active_goals[goal_id] = "active"
    
    def abandon_goal(self, goal_id):
        """Mark a goal as abandoned"""
        self.active_goals[goal_id] = "abandoned"
```

### Phase 3: Update Reflection Engine

**Location**: Find `reflection_engine.py` (likely in `/agents/` or `/core/`)

**Required Updates**:

```python
# Add to imports
from l9_agent.value_alignment import ValueAlignmentEngine

class ReflectionEngine:
    def __init__(self, state_manager, config):
        self.state = state_manager
        self.config = config
        
        # Initialize value alignment engine
        self.value_engine = ValueAlignmentEngine()
    
    def reflect_on_action(self, action, outcome, context):
        """Reflect on an action and update value alignment"""
        # Existing reflection logic...
        
        # Score value alignment
        action_tags = self._extract_value_tags(action, outcome)
        alignment_score = self.value_engine.score_action(action_tags)
        
        # Record in state
        self.state.record_value_alignment(alignment_score)
        
        # Optional: Log explanation
        explanation = self.value_engine.explain_score(action_tags)
        
        return {
            "alignment_score": alignment_score,
            "explanation": explanation,
            # ... other reflection outputs
        }
    
    def _extract_value_tags(self, action, outcome):
        """Extract value tags from action/outcome"""
        tags = []
        
        # Example heuristics (customize based on your action structure)
        if "user_feedback" in outcome and outcome["user_feedback"] == "positive":
            tags.append("trust")
        
        if action.get("benefits_user"):
            tags.append("reciprocity")
        
        if action.get("consistent_with_history"):
            tags.append("coherence")
        
        if action.get("reduces_user_effort"):
            tags.append("autonomy_support")
        
        if action.get("honest"):
            tags.append("truthfulness")
        
        return tags
```

### Phase 4: Update Foresight Engine

**Location**: Find `foresight_engine.py`

**Required Updates**:

```python
# Add to imports
from l9_agent.value_alignment import ValueAlignmentEngine

class ForesightEngine:
    def __init__(self, state_manager, config):
        self.state = state_manager
        self.config = config
        self.value_engine = ValueAlignmentEngine()
    
    def generate_candidate_actions(self, context):
        """Generate and filter candidate actions"""
        # Generate candidates (existing logic)
        candidates = self._generate_raw_candidates(context)
        
        # Filter by value alignment
        alignment_threshold = self.config.get("value_alignment_threshold", 0.5)
        filtered_candidates = []
        
        for candidate in candidates:
            tags = self._predict_value_tags(candidate, context)
            score = self.value_engine.score_action(tags)
            
            if score >= alignment_threshold:
                candidate["alignment_score"] = score
                filtered_candidates.append(candidate)
        
        return filtered_candidates
    
    def _predict_value_tags(self, action, context):
        """Predict which values an action will satisfy"""
        # Implement prediction logic based on action type
        # This is a placeholder - customize for your domain
        tags = []
        
        if action.get("type") == "assist_user":
            tags.extend(["reciprocity", "autonomy_support"])
        
        if action.get("transparent"):
            tags.append("truthfulness")
        
        return tags
```

### Phase 5: Integrate Trust System

**Update Decision Controller** (or create if it doesn't exist):

```python
from l9_agent.trust_engine import TrustEngine
from l9_agent.trust_hooks import after_task_feedback

class DecisionController:
    def __init__(self, state_manager, config):
        self.state = state_manager
        self.config = config
        self.trust_engine = TrustEngine(state_manager, config)
    
    def make_decision(self, context):
        """Make a decision considering trust"""
        # Get trust score
        trust_score = self.state.trust_model.as_scalar()
        
        # Use trust in decision logic
        # Higher trust = more autonomy
        autonomy_threshold = 0.7 - (trust_score * 0.2)
        
        # ... decision logic
        
        return {
            "decision": decision,
            "trust_score": trust_score,
            "autonomy_threshold": autonomy_threshold
        }
    
    def process_feedback(self, task_id, outcome, user_feedback):
        """Process user feedback and update trust"""
        after_task_feedback(task_id, outcome, user_feedback, self.trust_engine)
```

### Phase 6: Integrate Motivation Core

```python
from l9_agent.desire_engine import DesireEngine
from l9_agent.will_engine import WillEngine
from l9_agent.persistence_engine import PersistenceEngine
from l9_agent.goal_commitment import GoalCommitmentTracker

class MotivationManager:
    def __init__(self, config_path="config/desire_profile.yaml"):
        self.desire = DesireEngine(config_path)
        self.will = WillEngine()
        
        # Load thresholds from config
        import yaml
        from pathlib import Path
        with open(Path(config_path), "r") as f:
            config = yaml.safe_load(f)
        
        self.persist = PersistenceEngine(config["thresholds"])
        self.tracker = GoalCommitmentTracker(self.desire, self.will, self.persist)
    
    def evaluate_goal(self, goal_id):
        """Evaluate whether to continue pursuing a goal"""
        return self.tracker.update_goal(goal_id)
    
    def reinforce_goal(self, goal_id, amount):
        """Reinforce desire for a goal"""
        self.desire.reinforce(goal_id, amount)
    
    def periodic_decay(self):
        """Run periodic desire decay"""
        self.desire.decay()
```

## Testing Integration

### Run Unit Tests

```bash
cd /home/ubuntu/L9

# Test value alignment
python3 l9_agent/value_tests.py

# Test motivation core
python3 l9_agent/desire_tests.py

# Test trust system
python3 l9_agent/trust_tests.py
```

### Integration Tests

Create integration tests in `/tests/l9_agent/`:

```python
# tests/l9_agent/test_integration.py

def test_value_alignment_integration():
    """Test value alignment with state manager"""
    from core.state_manager import StateManager  # Adjust import
    from l9_agent.value_alignment import ValueAlignmentEngine
    
    state = StateManager()
    engine = ValueAlignmentEngine()
    
    score = engine.score_action(["trust", "coherence"])
    state.record_value_alignment(score)
    
    assert state.current_value_alignment == score
    assert len(state.value_alignment_history) == 1

def test_trust_integration():
    """Test trust system integration"""
    from core.state_manager import StateManager
    from l9_agent.trust_engine import TrustEngine
    
    state = StateManager()
    config = {"reinforce_step_positive": 0.1, "reinforce_step_negative": 0.15}
    engine = TrustEngine(state, config)
    
    initial_trust = state.trust_model.as_scalar()
    engine.on_success()
    new_trust = state.trust_model.as_scalar()
    
    assert new_trust > initial_trust
```

## Configuration Management

### Environment-Specific Configs

You may want different configurations for development vs production:

```bash
config/
├── core_values.yaml           # Production
├── desire_profile.yaml        # Production
├── trust_config.yaml          # Production
└── dev/
    ├── core_values.yaml       # Development overrides
    ├── desire_profile.yaml
    └── trust_config.yaml
```

### Loading Configs

```python
import os

env = os.getenv("L9_ENV", "production")
config_dir = "config/" if env == "production" else "config/dev/"

engine = ValueAlignmentEngine(config_path=f"{config_dir}core_values.yaml")
```

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Ensure l9_agent is in Python path
export PYTHONPATH="/home/ubuntu/L9:$PYTHONPATH"

# Or add to your script
import sys
sys.path.insert(0, '/home/ubuntu/L9')
```

### Config File Not Found

Ensure config files are in the correct location:

```bash
ls -la /home/ubuntu/L9/config/core_values.yaml
ls -la /home/ubuntu/L9/config/desire_profile.yaml
ls -la /home/ubuntu/L9/config/trust_config.yaml
```

### Test Failures

Run tests with verbose output:

```bash
python3 -m pytest l9_agent/ -v
```

## Next Steps

1. Complete integration of remaining modules (emotion, belief, foresight phase 2)
2. Add comprehensive integration tests
3. Update existing agents to use new cognitive systems
4. Monitor performance and adjust thresholds
5. Implement feedback loops for continuous improvement

## Support

For issues or questions:
1. Check the module README files
2. Review the chat transcript for detailed specifications
3. Consult the CGMP (God-Mode Cursor Prompt) for implementation guidelines
