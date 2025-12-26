# Perplexity Super-Prompt Deployment Guide

## Overview

This guide shows how to use the **Perplexity Super-Prompt system** with the **Autonomous Research Agent** to synthesize multi-prompt research into production-ready code and comprehensive documentation.

---

## Quick Start

### 1. Set Up Environment

```bash
# Clone/create project directory
mkdir research-synthesis && cd research-synthesis

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install httpx tenacity torch transformers

# Set API key
export PERPLEXITY_API_KEY="your-api-key-here"
```

### 2. Run Autonomous Research Agent

```bash
# Execute the agent
python autonomous-research-agent.py

# Expected output:
# [*] Starting Autonomous Research Agent...
# [*] Submitting 5 prompt variations to Perplexity Labs...
# [+] Processed Implementation-First (Pragmatic)
# [+] Processed Theory-First (Research)
# [+] Processed Systems Integration (DevOps)
# [+] Processed Agent-Specific (Autonomous Systems)
# [+] Processed Multi-Modal Specifics (Cross-Modality)
# [*] Synthesizing findings...
# [+] Outputs saved to: research_synthesis_20241205_154320/
```

### 3. Review Generated Outputs

```bash
# Output structure:
research_synthesis_20241205_154320/
├── README.md                    # Comprehensive findings + quick start
├── architecture.py              # Core model implementation
├── agent_integration.py         # Agent framework integration
└── synthesis_metadata.json      # Raw synthesis data (for further analysis)

# View findings
cat research_synthesis_*/README.md

# Review architecture
cat research_synthesis_*/architecture.py

# Check synthesis metadata
cat research_synthesis_*/synthesis_metadata.json | python -m json.tool
```

---

## Integration Patterns

### Pattern 1: Direct Autonomous Agent Usage

**Use when:** You want the agent to discover and synthesize research across multiple perspectives.

```python
# 1. Import components
from autonomous_research_agent import PerplexityLabsClient, SynthesisEngine, CodeGenerator
import asyncio

# 2. Run synthesis
async def run_synthesis():
    client = PerplexityLabsClient()
    # ... (see autonomous-research-agent.py)

# 3. Execute
asyncio.run(run_synthesis())
```

**Output:** Fully synthesized findings + production code + README

**Timeline:** ~5-10 minutes for all 5 variations

---

### Pattern 2: Manual Multi-Prompt Research (No Agent)

**Use when:** You want fine-grained control over each prompt variation.

```python
from perplexity_superprompt import (
    PromptVariationGenerator,
    PerplexityLabsClient
)

# Generate variations manually
generator = PromptVariationGenerator()
variations = [
    generator.pragmatic_variation(),
    generator.research_variation(),
    generator.systems_variation(),
]

# Query each one
client = PerplexityLabsClient()
for variation in variations:
    response = await client.query(variation)
    # Process response...
```

**Output:** Raw responses (you aggregate manually)

**Timeline:** Same ~5-10 minutes

---

### Pattern 3: Custom Research Topics

**Use when:** You want to apply this methodology to a different topic.

```python
# Modify PROMPT_VARIATIONS in autonomous-research-agent.py
PROMPT_VARIATIONS = [
    PromptVariation(
        id="custom_v1",
        name="Your Custom Variation 1",
        focus="Your focus area",
        audience="Your audience",
        constraints="Your constraints",
        template="""
You are a first-class research team tasked with [YOUR_TOPIC]...
Focus on: [YOUR_FOCUS]
Provide: [YOUR_DELIVERABLES]
        """
    ),
    # ... more variations
]

# Run agent
asyncio.run(main())
```

---

## Prompt Variation Strategies

### Why 5 Variations?

1. **Pragmatic** → Actionable implementation details
2. **Research** → Theoretical foundations and proofs
3. **Systems** → Production deployment patterns
4. **Agents** → Integration with autonomous systems
5. **Multi-Modal** → Specific cross-modality challenges

**Each variation explores orthogonal aspects**, ensuring comprehensive coverage.

---

## Customizing the Synthesis

### Adjust Consensus Threshold

```python
# In SynthesisEngine.compute_consensus_patterns()
# Default: ≥3 variations agree (60%)
# Change to:

if len(instances) >= 4:  # ≥4 variations (80%)
    # Higher confidence, fewer consensus patterns
```

### Modify Prompt Temperature

```python
# In PerplexityLabsClient.query()
"temperature": 0.8,  # Current: balanced exploration
# Change to:
"temperature": 0.5,  # Lower = more consistent responses
"temperature": 1.0,  # Higher = more creative/diverse
```

### Filter Extracted Concepts

```python
# In ResponseProcessor.extract_concepts()
concepts = [c for c in concepts if len(c) > 15]  # Longer concepts
# or:
concepts = concepts[:10]  # Top 10 instead of 15
```

---

## Integration Examples

### Example 1: LangChain Agent

```python
from langchain.agents import Tool, AgentExecutor, initialize_agent
from src.architecture import HybridSparseModel

# Create tool from sparse model
model = HybridSparseModel()

@tool
def sparse_reasoning(query: str) -> str:
    """Multi-modal sparse reasoning"""
    # ... implementation
    pass

# Add to agent
tools = [sparse_reasoning]
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

### Example 2: AIOS Framework

```python
from aios.core import ReasoningNode
from src.agent_integration import HybridSparseReasoningNode

# Register node
node = HybridSparseReasoningNode(model)
await node.register_with_agent(agent_dispatcher)

# Query from another agent component
result = await node.request_reasoning("explain sparse experts")
```

### Example 3: Direct Model Usage

```python
import torch
from src.architecture import HybridSparseModel

model = HybridSparseModel(input_dim=768, num_experts=8)
model.eval()

# Single input
x = torch.randn(1, 768)
result = model(x)
print(f"Sparse compute ratio: {result['sparse_compute']:.1%}")

# Multi-modal input
result = model(x, modality_info={
    'text': text_embedding,
    'vision': vision_embedding,
    'structured': struct_embedding
})
```

---

## API Configuration Reference

### Perplexity Labs Parameters

```yaml
# Default configuration (in autonomous-research-agent.py)
model: "sonar-reasoning"          # Latest reasoning model
temperature: 0.8                  # Balanced exploration/consistency
max_tokens: 5000                  # Detailed responses
top_p: 0.95                       # Nucleus sampling
presence_penalty: 0.1             # Encourage new concepts
frequency_penalty: 0.0            # Allow concept repetition

# For more deterministic responses:
temperature: 0.5
top_p: 0.9
presence_penalty: 0.2

# For more creative/diverse:
temperature: 1.0
top_p: 1.0
presence_penalty: 0.5
```

### Synthesis Parameters

```yaml
# Consensus threshold (SynthesisEngine)
min_variations_for_consensus: 3   # Default: 60% agreement
confidence_threshold: 0.65         # Minimum confidence score
novelty_weight: 0.3                # Weight for unique insights
feasibility_weight: 0.3            # Weight for implementation ease

# Extraction parameters (ResponseProcessor)
max_concepts: 15
max_insights: 10
max_code_snippets: 10
min_concept_length: 10

# Timeout configuration
query_timeout_seconds: 120
retry_attempts: 3
retry_backoff_multiplier: 1.5
```

---

## Monitoring & Observability

### Check Agent Progress

```python
# The agent outputs timestamped progress:
# [*] Starting Autonomous Research Agent...
# [*] Timestamp: 2024-12-05T15:43:20.123456
# [*] Submitting 5 prompt variations...
# [+] Processed Implementation-First (Pragmatic)
# [+] Synthesis complete: 8 consensus patterns, 3 unique insights
```

### Review Raw Responses

```bash
# After synthesis, check raw API responses:
cat research_synthesis_*/synthesis_metadata.json | python -c "
import json, sys
data = json.load(sys.stdin)
print('Total variations analyzed:', data['total_variations'])
print('Consensus patterns:', len(data['consensus_patterns']))
print('Unique insights:', data['unique_insights'])
"
```

### Validate Output Quality

```bash
# Verify generated code
python -m py_compile research_synthesis_*/architecture.py
python -m py_compile research_synthesis_*/agent_integration.py

# Run type checking (if mypy installed)
pip install mypy
mypy research_synthesis_*/architecture.py
```

---

## Troubleshooting

### Issue: "PERPLEXITY_API_KEY not set"

**Solution:**
```bash
# Set environment variable
export PERPLEXITY_API_KEY="sk-your-key-here"

# Or create .env file
echo "PERPLEXITY_API_KEY=sk-your-key-here" > .env

# Verify
echo $PERPLEXITY_API_KEY
```

### Issue: API Rate Limits

**Solution:**
```python
# Reduce concurrency (submit sequentially instead of parallel)
# In autonomous_research_agent.py:

# Instead of:
responses = await asyncio.gather(*tasks)

# Do:
responses = []
for task in tasks:
    responses.append(await task)
    await asyncio.sleep(2)  # 2-second delay between requests
```

### Issue: Timeout Errors

**Solution:**
```python
# Increase timeout in PerplexityLabsClient:
async with httpx.AsyncClient(timeout=180.0) as client:  # 3 minutes
```

### Issue: Memory Issues (Large Models)

**Solution:**
```bash
# Use quantization for inference
pip install bitsandbytes

# Load model with 8-bit quantization:
# model = HybridSparseModel()
# model = model.to("cuda:0")
# Implement 8-bit loading in architecture.py
```

---

## Advanced Usage

### Custom Synthesis Logic

```python
# Extend SynthesisEngine for custom analysis
class CustomSynthesisEngine(SynthesisEngine):
    def extract_unique_insights(self):
        """Override with custom insight extraction"""
        # Your logic here
        pass
    
    def compute_scaling_properties(self):
        """Add custom scaling analysis"""
        # Your analysis here
        pass

# Use in main():
engine = CustomSynthesisEngine(processed_responses)
```

### Multi-Step Research Pipeline

```python
# Phase 1: Initial exploration
synthesis_v1 = await run_synthesis()

# Phase 2: Deep dive on interesting areas
focused_variations = generate_focused_variations(synthesis_v1)
synthesis_v2 = await run_synthesis_with_variations(focused_variations)

# Phase 3: Validate and polish
synthesis_final = merge_syntheses(synthesis_v1, synthesis_v2)
```

### Export to Different Formats

```python
# Generate different output formats
README_md = readme_gen.generate_markdown(synthesis)
README_rst = readme_gen.generate_rst(synthesis)
README_html = readme_gen.generate_html(synthesis)

# Generate different code templates
tensorflow_code = code_gen.generate_tensorflow(synthesis)
jax_code = code_gen.generate_jax(synthesis)
```

---

## Next Steps

1. **Run the agent** on hybrid sparse-neural architecture
2. **Review the generated README** for findings
3. **Integrate generated code** into your project
4. **Customize for your domain** by modifying prompt variations
5. **Iterate** on synthesis parameters to refine insights

---

## Support & Resources

- **Perplexity Labs Docs**: https://docs.perplexity.ai
- **Agent Frameworks**:
  - AIOS: https://github.com/aios-core/aios
  - LangChain: https://python.langchain.com
  - ReAct: https://react-ai.github.io
- **Research Papers**: See RESEARCH_FINDINGS.md in generated output

---

## Citation

If you use this system for research, please cite:

```bibtex
@software{perplexity_super_prompt_2024,
  title={Perplexity Super-Prompt: Multi-Modal Research Synthesis},
  author={Your Organization},
  year={2024},
  url={https://github.com/your-org/perplexity-super-prompt}
}
```
