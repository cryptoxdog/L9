# Perplexity Super-Prompt: Hybrid Sparse-Neural Architecture with Multi-Modal Reasoning

## Core System Prompt

```
You are a first-class research team tasked with designing, implementing, and 
experimentally validating a **Hybrid Sparse-Neural Architecture** that leverages 
**conditional computation**, **multi-modal reasoning**, and obeys **power-law 
scaling properties**.

Your mission is to develop a scalable reasoning model that:
- Dynamically activates only minimal necessary subnetworks per query
- Processes heterogeneous inputs (text, structured data, images, embeddings)
- Optimizes efficiency, accuracy, and inference latency
- Integrates seamlessly into autonomous agent pipelines

Focus Areas:
1. **Sparse activation with conditional subnetwork routing** (gating, MoE experts)
2. **Multi-modal input fusion** (text embeddings, vision features, structured data)
3. **Hierarchical power-law scaling** (compute ∝ performance allocation)
4. **Autonomous agent deployment** (async messaging, dynamic orchestration)
5. **Production-ready implementation** (type hints, error handling, monitoring)

Deliverables:
- Technical architecture blueprint with reasoning loop
- Python code bootstrap with conditional routing and expert activation
- Multi-modal input processing pipeline with fusion strategies
- Integration patterns for autonomous agents (AIOS, LangChain, ReAct frameworks)
- Monitoring and scaling instrumentation
- Production deployment guidelines
```

---

## Multi-Modal Reasoning Extension

```
### Multi-Modal Fusion Strategy

Your architecture must support:

1. **Input Encoders** (per modality):
   - Text: Transformer-based embeddings (context-aware)
   - Vision: Vision Transformer (ViT) or CLIP-based features
   - Structured: Learned embeddings for tabular/JSON data
   - Audio: Spectral features or speech embeddings

2. **Modality-Specific Sparse Experts**:
   - Text-reasoning experts (NLP, semantic understanding)
   - Vision-reasoning experts (object detection, spatial reasoning)
   - Hybrid experts (cross-modal correlation, grounding)

3. **Fusion Gating Network**:
   - Routes multi-modal inputs to appropriate expert combinations
   - Learns modality importance weights per query type
   - Supports sparse multi-expert activation (top-k routing)

4. **Output Synthesis**:
   - Aggregates expert outputs with attention-weighted fusion
   - Maintains modality-specific reasoning traces for interpretability
   - Generates unified reasoning representation for downstream tasks

### Example Modality Priority Rules:
- Question-answering: Text (primary), Vision (contextual)
- Scene understanding: Vision (primary), Text (grounding)
- Data analysis: Structured (primary), Text (context)
- Cross-modal reasoning: All modalities equally weighted
```

---

## Autonomous Research Agent Deployment Pattern

```
### Agent Architecture for Prompt Variation & Synthesis

Your autonomous research agent must:

1. **Prompt Variation Generation**:
   - Generate N ≥ 5 thematic variations of this prompt
   - Vary: framing (implementation-first vs. theory-first), emphasis, 
     audience, constraint levels
   - Ensure variations explore orthogonal reasoning paths

2. **Parallel Perplexity Labs API Calls**:
   - Submit each variation to Perplexity Labs with unique session IDs
   - Configure: temperature=0.7-0.9 (explore), max_tokens=4000-6000
   - Capture reasoning traces and intermediate outputs
   - Timeout: 120s per query with exponential backoff retry (3 attempts)

3. **Response Aggregation**:
   - Extract key concepts, code patterns, architectural insights from each response
   - Build semantic graph of relationships (entity extraction, NER)
   - Identify consensus patterns vs. unique perspectives

4. **Synthesis Pipeline**:
   - Meta-analyze findings across all variations
   - Resolve conflicts using confidence scoring (based on supporting evidence)
   - Generate unified technical recommendation with trade-offs
   - Create implementation priority matrix (impact × feasibility)

5. **Output Generation**:
   - Produce comprehensive README with findings, rationale, and deployment guide
   - Generate production-ready code with full test coverage
   - Create repo structure ready for immediate CI/CD integration
   - Output runnable notebooks demonstrating key concepts
```

---

## Prompt Variation Specifications

### Variation 1: Implementation-First (Pragmatic)
```
Focus on: Working code first, theory second
Audience: ML engineers building systems today
Constraints: 3-month deployment timeline, limited compute budget
Expected output: Reference implementation, optimization hacks, deployment checklist
```

### Variation 2: Theory-First (Research)
```
Focus on: Mathematical foundations, properties, proofs
Audience: Researchers and AI scientists
Constraints: None (exploratory)
Expected output: Theoretical insights, scaling laws, novel properties
```

### Variation 3: Systems Integration (DevOps)
```
Focus on: Deployment, monitoring, scaling, reliability
Audience: Platform engineers, MLOps teams
Constraints: Kubernetes-native, observability-first, auto-scaling required
Expected output: Deployment patterns, monitoring dashboards, SLO definitions
```

### Variation 4: Agent-Specific (Autonomous Systems)
```
Focus on: Integration with autonomous agents (ReAct, AIOS, LangChain)
Audience: AI agent developers
Constraints: Async message passing, low-latency reasoning, fault tolerance
Expected output: Integration hooks, agent patterns, orchestration examples
```

### Variation 5: Multi-Modal Specifics (Cross-Modality)
```
Focus on: Multi-modal fusion challenges, modality-specific experts
Audience: Computer vision + NLP researchers
Constraints: Real-time multi-modal inference, modality robustness
Expected output: Fusion strategies, expert architectures, benchmarks
```

---

## Agent Workflow Pseudocode

```python
# Autonomous Research Agent Workflow

async def run_research_synthesis():
    """Orchestrate multi-prompt variation research synthesis"""
    
    # 1. Generate prompt variations
    variations = generate_prompt_variations(base_prompt)
    
    # 2. Submit parallel Perplexity Labs API calls
    responses = await asyncio.gather(*[
        query_perplexity_labs(variation, session_id=i)
        for i, variation in enumerate(variations)
    ])
    
    # 3. Parse and extract insights
    insights = [parse_response(r) for r in responses]
    
    # 4. Build semantic relationship graph
    graph = build_semantic_graph(insights)
    
    # 5. Synthesize findings
    synthesis = synthesize_findings(graph, insights)
    
    # 6. Generate outputs
    readme = generate_readme(synthesis)
    code = generate_production_code(synthesis)
    repo = scaffold_git_repo(readme, code)
    
    return {
        'readme': readme,
        'code': code,
        'repo_structure': repo,
        'synthesis_metadata': synthesis
    }
```

---

## Expected Output Structure

```
research-synthesis-output/
├── README.md                          # Comprehensive findings document
├── RESEARCH_FINDINGS.md               # Detailed synthesis report
├── DEPLOYMENT_GUIDE.md                # Step-by-step deployment instructions
├── src/
│   ├── __init__.py
│   ├── architecture.py                # Core model architecture
│   ├── multimodal_fusion.py           # Multi-modal input processing
│   ├── sparse_experts.py              # Sparse expert implementations
│   ├── gating_networks.py             # Routing/gating mechanisms
│   ├── agent_integration.py           # AIOS/agent integration layer
│   ├── monitoring.py                  # Observability instrumentation
│   └── utils.py                       # Utilities and helpers
├── tests/
│   ├── test_architecture.py           # Unit tests
│   ├── test_multimodal.py             # Multi-modal pipeline tests
│   ├── test_integration.py            # End-to-end tests
│   └── test_scaling.py                # Scaling/performance tests
├── notebooks/
│   ├── 01_architecture_walkthrough.ipynb
│   ├── 02_multimodal_fusion_demo.ipynb
│   ├── 03_sparse_routing_analysis.ipynb
│   ├── 04_agent_integration_example.ipynb
│   └── 05_scaling_properties.ipynb
├── benchmarks/
│   ├── compute_efficiency.py
│   ├── latency_profiling.py
│   └── scaling_laws.py
├── docker/
│   ├── Dockerfile                     # Production container
│   ├── docker-compose.yml             # Local dev environment
│   └── requirements.txt               # Python dependencies
├── config/
│   ├── model_config.yaml              # Model hyperparameters
│   ├── deployment_config.yaml         # Deployment settings
│   └── logging_config.yaml            # Observability configuration
├── .github/workflows/
│   ├── ci.yml                         # CI/CD pipeline
│   ├── tests.yml                      # Automated testing
│   └── deployment.yml                 # CD pipeline
├── setup.py                           # Package configuration
└── CONTRIBUTING.md                    # Contribution guidelines
```

---

## Key Prompt Configuration Parameters

```yaml
# For Perplexity Labs API calls
perplexity_config:
  model: "sonar-reasoning"  # or latest available reasoning model
  temperature: 0.8          # Balanced exploration/consistency
  max_tokens: 5000          # Allow detailed responses
  top_p: 0.95               # Nucleus sampling
  presence_penalty: 0.1     # Encourage new concepts
  frequency_penalty: 0.0    # Allow repetition of important ideas
  
variation_config:
  num_variations: 5
  diversity_target: 0.7     # Semantic diversity between variations
  
synthesis_config:
  confidence_threshold: 0.65
  consensus_weight: 0.4
  novelty_weight: 0.3
  feasibility_weight: 0.3
```

---

## Success Metrics

The synthesis should achieve:

1. **Coverage**: ≥95% of identified architectural components documented
2. **Consensus**: ≥70% agreement across variations on core design decisions
3. **Novelty**: ≥3 unique insights not in base prompt
4. **Actionability**: Every recommendation includes implementation roadmap
5. **Production-Readiness**: Code passes type checking, linting, 90%+ test coverage
6. **Deployability**: Ready for Docker, Kubernetes, or serverless environments
7. **Traceability**: Every decision traceable to source research variation
```

---

## Integration with Autonomous Agent Frameworks

```python
### ReAct Framework Integration
- Reasoning step: Use sparse-neural model for hypothesis generation
- Acting step: Route to specialized expert per action type
- Observation step: Multi-modal fusion of results

### AIOS Integration
- Register as ReasoningNode with async message handling
- Support task graph orchestration
- Implement resource-aware expert allocation

### LangChain Integration
- Custom Tool for sparse-neural reasoning
- Multi-modal document loader integration
- Agent executor with expert-specific callbacks
```

---

## Quality Assurance Checklist

- [ ] All code passes `mypy` (strict type checking)
- [ ] All code passes `pylint` (≥9.0 score)
- [ ] All code passes `black` formatting
- [ ] Test coverage ≥90% (pytest with coverage reports)
- [ ] Documentation: Docstrings for every class/function
- [ ] Performance: Latency benchmarks with baseline comparisons
- [ ] Scaling: Verified power-law scaling properties with metrics
- [ ] Security: No hardcoded secrets, proper credential handling
- [ ] Reproducibility: Random seed management, deterministic outputs
- [ ] Monitoring: Instrumentation for all critical paths
- [ ] Error handling: Graceful degradation, clear error messages
- [ ] Dependencies: Pin versions, minimal external dependencies
