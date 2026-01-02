# L9 Agent Quick Start Guide

## Installation

The l9_agent modules are already installed in your repository at `/home/ubuntu/L9/l9_agent/`.

## Running Tests

To verify everything is working:

```bash
cd /home/ubuntu/L9

# Set Python path
export PYTHONPATH=/home/ubuntu/L9:$PYTHONPATH

# Run all tests
python3 l9_agent/value_tests.py
python3 l9_agent/desire_tests.py
python3 l9_agent/trust_tests.py
```

Expected output:
```
✅ Value alignment tests passed
✅ Desire/Will/Persistence tests passed
✅ All trust tests passed
```

## Basic Usage Examples

### 1. Value Alignment

```python
import sys
sys.path.insert(0, '/home/ubuntu/L9')

from l9_agent.value_alignment import ValueAlignmentEngine

# Initialize engine
engine = ValueAlignmentEngine()

# Score an action
score = engine.score_action(["trust", "coherence", "truthfulness"])
print(f"Alignment score: {score}")

# Get explanation
explanation = engine.explain_score(["trust", "coherence"])
print(f"Explanation: {explanation}")
```

### 2. Motivation Core

```python
import sys
sys.path.insert(0, '/home/ubuntu/L9')

from l9_agent.desire_engine import DesireEngine
from l9_agent.will_engine import WillEngine
from l9_agent.persistence_engine import PersistenceEngine
from l9_agent.goal_commitment import GoalCommitmentTracker

# Initialize engines
desire = DesireEngine()
will = WillEngine()
persist = PersistenceEngine({"activation": 0.6, "abandonment": 0.2})

# Create tracker
tracker = GoalCommitmentTracker(desire, will, persist)

# Register and track a goal
desire.register_goal("complete_project")
desire.reinforce("complete_project", 0.3)

# Check if should persist
should_continue = tracker.update_goal("complete_project")
print(f"Should persist: {should_continue}")

# Check desire and will levels
print(f"Desire: {desire.get_desire('complete_project')}")
print(f"Will: {will.get_will('complete_project')}")
```

### 3. Trust Modeling

```python
import sys
sys.path.insert(0, '/home/ubuntu/L9')

from l9_agent.trust_model import TrustModel
from l9_agent.trust_engine import TrustEngine

# Initialize trust model
trust = TrustModel(initial=0.5, decay=0.01)

# Create mock state
class MockState:
    def __init__(self):
        self.trust_model = trust

state = MockState()

# Initialize trust engine
config = {
    "reinforce_step_positive": 0.1,
    "reinforce_step_negative": 0.15
}
engine = TrustEngine(state, config)

# Update trust based on events
print(f"Initial trust: {trust.as_scalar()}")

engine.on_success()
print(f"After success: {trust.as_scalar()}")

engine.on_failure()
print(f"After failure: {trust.as_scalar()}")

# View history
print(f"Trust history: {trust.history}")
```

## Configuration

### Modifying Core Values

Edit `/home/ubuntu/L9/config/core_values.yaml`:

```yaml
core_values:
  trust:
    description: "Preserve and strengthen user trust over time"
    weight: 1.0  # Adjust weight here
```

### Modifying Motivation Parameters

Edit `/home/ubuntu/L9/config/desire_profile.yaml`:

```yaml
desire_parameters:
  base_desire: 0.5
  decay_rate: 0.03  # Adjust decay rate
  reinforcement_gain: 0.15
  frustration_penalty: 0.1

thresholds:
  activation: 0.6  # Adjust activation threshold
  abandonment: 0.2
  obsession_cap: 1.5
```

### Modifying Trust Parameters

Edit `/home/ubuntu/L9/config/trust_config.yaml`:

```yaml
initial_trust: 0.5
decay_rate: 0.01
reinforce_step_positive: 0.1  # Adjust reinforcement
reinforce_step_negative: 0.15  # Adjust penalty
```

## Integration with Existing Code

See `INTEGRATION_GUIDE.md` for detailed integration instructions.

### Quick Integration Snippet

```python
import sys
sys.path.insert(0, '/home/ubuntu/L9')

from l9_agent.value_alignment import ValueAlignmentEngine
from l9_agent.trust_model import TrustModel

class MyAgent:
    def __init__(self):
        self.value_engine = ValueAlignmentEngine()
        self.trust_model = TrustModel(initial=0.5)
        self.value_history = []
    
    def evaluate_action(self, action_tags):
        # Score value alignment
        score = self.value_engine.score_action(action_tags)
        self.value_history.append(score)
        
        # Use trust in decision
        trust_score = self.trust_model.as_scalar()
        
        return {
            "alignment": score,
            "trust": trust_score,
            "should_execute": score > 0.5 and trust_score > 0.4
        }
    
    def process_feedback(self, positive):
        if positive:
            self.trust_model.reinforce(0.1)
        else:
            self.trust_model.penalize(0.15)

# Usage
agent = MyAgent()
result = agent.evaluate_action(["trust", "coherence"])
print(result)
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError: No module named 'l9_agent'`:

```python
# Add this at the top of your script
import sys
sys.path.insert(0, '/home/ubuntu/L9')
```

Or set environment variable:

```bash
export PYTHONPATH=/home/ubuntu/L9:$PYTHONPATH
```

### Config File Not Found

Ensure you're running from the correct directory:

```bash
cd /home/ubuntu/L9
python3 your_script.py
```

Or use absolute paths in your code:

```python
engine = ValueAlignmentEngine(config_path="/home/ubuntu/L9/config/core_values.yaml")
```

## Next Steps

1. Read `README.md` for comprehensive documentation
2. Read `INTEGRATION_GUIDE.md` for integration instructions
3. Explore the source code in `l9_agent/`
4. Customize configuration files in `config/`
5. Add your own modules following the established patterns

## Support

For detailed information:
- Module documentation: `l9_agent/README.md`
- Integration guide: `l9_agent/INTEGRATION_GUIDE.md`
- Delivery summary: `/home/ubuntu/L9_AGENT_DELIVERY_SUMMARY.md`
- Module analysis: `/home/ubuntu/module_analysis.md`

## File Locations

- **Modules**: `/home/ubuntu/L9/l9_agent/`
- **Config**: `/home/ubuntu/L9/config/`
- **Tests**: `/home/ubuntu/L9/l9_agent/*_tests.py`
- **Docs**: `/home/ubuntu/L9/l9_agent/*.md`
