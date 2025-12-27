# L9 Research Agent Integration Blueprint

**Version**: 1.0  
**Date**: 2025-12-20  
**Target**: L9 Agentic Intelligence Platform v1.1.0

---

## Executive Summary

This blueprint provides a complete integration plan for adding **Deep Research** capabilities to the L9 platform, enabling agents like **L** and **Emma** to execute comprehensive research workflows.

**Recommendation**: Hybrid approach combining Research Factory code foundation with Perplexity Deep Research methodology.

**Integration Complexity**: Medium  
**Estimated Timeline**: 5-7 days  
**Deployment Readiness**: Production-ready with tests

---

## Package Selection Analysis

### Winner: Research Factory + Perplexity Deep Research (Hybrid)

| Aspect | Research Factory | Perplexity Deep Research | Hybrid Approach |
|--------|------------------|--------------------------|-----------------|
| Code Foundation | ✅ 757 lines Python | ❌ Minimal code | ✅ Use RF foundation |
| Methodology | ⚠️ Basic | ✅ Comprehensive | ✅ Merge PDR methodology |
| Architecture | ✅ Pipeline-based | ❌ Manual workflow | ✅ Automated pipeline |
| L9 Compatibility | ⚠️ Needs adaptation | ❌ Build from scratch | ✅ Adapt RF to L9 |
| Deployment Time | 2-3 days | 2-3 weeks | 5-7 days |

**Rationale**: Research Factory provides working code with autonomous agent patterns, while Perplexity Deep Research offers superior methodology, prompt engineering, and academic rigor. Combining both yields the best outcome.

---

## Architecture Overview

### High-Level Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                      L9 Agentic Platform                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐       ┌──────────┐       ┌──────────────────┐   │
│  │ Agent L  │──────▶│ Agent    │──────▶│ Research Agent   │   │
│  │ (CTO)    │       │ Emma     │       │ (Deep Research)  │   │
│  └──────────┘       └──────────┘       └──────────────────┘   │
│                                                │                │
│                                                ▼                │
│                                    ┌───────────────────────┐   │
│                                    │ ResearchOrchestrator  │   │
│                                    │ (5-Stage Pipeline)    │   │
│                                    └───────────────────────┘   │
│                                                │                │
│                    ┌───────────────────────────┼───────────┐   │
│                    ▼                           ▼           ▼   │
│           ┌────────────────┐         ┌──────────────┐  ┌────┐ │
│           │ Perplexity API │         │ Memory Store │  │ WM │ │
│           │ (Deep Research)│         │ (PostgreSQL) │  │    │ │
│           └────────────────┘         └──────────────┘  └────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Research Agent Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Research Agent                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ BaseAgent (L9 Kernel-Aware)                              │  │
│  │ - Inherits from agents/base_agent.py                     │  │
│  │ - Kernel integration via boot_overlay.yaml               │  │
│  │ - Memory integration via memory/substrate_service.py     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ResearchOrchestrator (5-Stage Pipeline)                  │  │
│  │                                                           │  │
│  │  Stage 1: Landscape Mapping (3-5 hours)                  │  │
│  │  Stage 2: Vertical Deep-Dives (4-6 hours)                │  │
│  │  Stage 3: Comparative Analysis (3-5 hours)               │  │
│  │  Stage 4: Gap Identification (3-4 hours)                 │  │
│  │  Stage 5: Hypothesis Generation (2-3 hours)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PromptEngine (Multi-Variation Synthesis)                 │  │
│  │ - Pragmatic (implementation-first)                       │  │
│  │ - Research (theory-first)                                │  │
│  │ - Systems (DevOps/deployment)                            │  │
│  │ - Agents (autonomous systems)                            │  │
│  │ - Multi-Modal (cross-modality)                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ PerplexityClient (API Integration)                       │  │
│  │ - Deep Research API calls                                │  │
│  │ - Rate limiting + retry logic                            │  │
│  │ - Response parsing + validation                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ResponseProcessor (Extraction + Synthesis)               │  │
│  │ - Concept extraction                                     │  │
│  │ - Code snippet extraction                                │  │
│  │ - Architectural insight extraction                       │  │
│  │ - Semantic graph construction                            │  │
│  │ - Consensus pattern detection                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                    │
│                            ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ResearchArtifactStore (Persistence)                      │  │
│  │ - PostgreSQL + pgvector                                  │  │
│  │ - Bibliography storage                                   │  │
│  │ - Research report generation                             │  │
│  │ - World model integration                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Core Agent Implementation (Days 1-2)

#### 1.1 Create Research Agent (BaseAgent Wrapper)

**File**: `agents/research_agent.py`

```python
"""
L9 Research Agent
=================

Deep research agent with 5-stage progressive research pipeline.
Integrates Research Factory code with Perplexity Deep Research methodology.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional

from agents.base_agent import (
    AgentConfig,
    AgentMessage,
    AgentResponse,
    AgentRole,
    BaseAgent,
)

logger = logging.getLogger(__name__)


class ResearchAgentRole(AgentRole):
    """Extended agent roles for research."""
    RESEARCH = "research"


@dataclass
class ResearchTask:
    """Research task specification."""
    topic: str
    domain: str
    depth: str  # "landscape", "deep_dive", "comprehensive"
    max_sources: int = 100
    stages: list[str] = None  # Which stages to run
    
    def __post_init__(self):
        if self.stages is None:
            self.stages = ["landscape", "deep_dive", "comparative", "gaps", "hypotheses"]


class ResearchAgent(BaseAgent):
    """
    Deep research agent with 5-stage pipeline.
    
    Stages:
    1. Landscape Mapping - Broad conceptual mapping
    2. Vertical Deep-Dives - Granular technical analysis
    3. Comparative Analysis - Framework comparison
    4. Gap Identification - Research frontiers
    5. Hypothesis Generation - Testable hypotheses
    """
    
    agent_role = ResearchAgentRole.RESEARCH
    agent_name = "research_agent"
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        perplexity_api_key: Optional[str] = None,
    ):
        """
        Initialize research agent.
        
        Args:
            agent_id: Unique identifier
            config: Agent configuration
            perplexity_api_key: Perplexity API key
        """
        super().__init__(agent_id, config)
        self.perplexity_api_key = perplexity_api_key
        self._orchestrator = None
        
    def get_system_prompt(self) -> str:
        """Get research agent system prompt."""
        return """You are a research agent specialized in conducting comprehensive, 
multi-stage academic literature reviews. You use a 5-stage progressive research 
methodology combining automated retrieval with rigorous analysis.

Your capabilities:
- Landscape mapping (broad conceptual surveys)
- Vertical deep-dives (granular technical analysis)
- Comparative analysis (framework comparison)
- Gap identification (research frontiers)
- Hypothesis generation (testable hypotheses)

You follow PRISMA 2020 standards for systematic reviews and produce citation-rich,
academically rigorous outputs."""
    
    async def run(
        self,
        task: dict[str, Any],
        context: Optional[dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute research task.
        
        Args:
            task: Research task specification
                {
                    "topic": "AI Operating Systems",
                    "domain": "AI/ML",
                    "depth": "comprehensive",
                    "max_sources": 150
                }
            context: Optional execution context
            
        Returns:
            AgentResponse with research results
        """
        logger.info(f"Research agent {self.agent_id} starting task: {task.get('topic')}")
        
        try:
            # Parse task
            research_task = ResearchTask(
                topic=task.get("topic", ""),
                domain=task.get("domain", "general"),
                depth=task.get("depth", "comprehensive"),
                max_sources=task.get("max_sources", 100),
                stages=task.get("stages"),
            )
            
            # Execute research pipeline
            results = await self._execute_research_pipeline(research_task)
            
            # Format response
            return AgentResponse(
                agent_id=self.agent_id,
                content=results.get("summary", ""),
                structured_output=results,
                success=True,
            )
            
        except Exception as e:
            logger.error(f"Research task failed: {e}")
            return AgentResponse(
                agent_id=self.agent_id,
                content="",
                success=False,
                error=str(e),
            )
    
    async def _execute_research_pipeline(
        self,
        task: ResearchTask
    ) -> dict[str, Any]:
        """Execute 5-stage research pipeline."""
        results = {
            "topic": task.topic,
            "domain": task.domain,
            "stages_completed": [],
            "total_sources": 0,
            "artifacts": {},
        }
        
        # Stage 1: Landscape Mapping
        if "landscape" in task.stages:
            landscape = await self._stage_landscape_mapping(task)
            results["stages_completed"].append("landscape")
            results["artifacts"]["landscape"] = landscape
            results["total_sources"] += landscape.get("source_count", 0)
        
        # Stage 2: Vertical Deep-Dives
        if "deep_dive" in task.stages:
            deep_dive = await self._stage_vertical_deep_dive(task, results)
            results["stages_completed"].append("deep_dive")
            results["artifacts"]["deep_dive"] = deep_dive
            results["total_sources"] += deep_dive.get("source_count", 0)
        
        # Stage 3: Comparative Analysis
        if "comparative" in task.stages:
            comparative = await self._stage_comparative_analysis(task, results)
            results["stages_completed"].append("comparative")
            results["artifacts"]["comparative"] = comparative
            results["total_sources"] += comparative.get("source_count", 0)
        
        # Stage 4: Gap Identification
        if "gaps" in task.stages:
            gaps = await self._stage_gap_identification(task, results)
            results["stages_completed"].append("gaps")
            results["artifacts"]["gaps"] = gaps
        
        # Stage 5: Hypothesis Generation
        if "hypotheses" in task.stages:
            hypotheses = await self._stage_hypothesis_generation(task, results)
            results["stages_completed"].append("hypotheses")
            results["artifacts"]["hypotheses"] = hypotheses
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        return results
    
    async def _stage_landscape_mapping(self, task: ResearchTask) -> dict[str, Any]:
        """Stage 1: Landscape Mapping (3-5 hours)."""
        logger.info(f"Stage 1: Landscape Mapping for {task.topic}")
        
        # Build landscape mapping prompt
        prompt = self._build_landscape_prompt(task)
        
        # Call Perplexity Deep Research
        response = await self._call_perplexity_deep_research(prompt)
        
        # Process response
        landscape = {
            "stage": "landscape_mapping",
            "source_count": response.get("source_count", 0),
            "themes": response.get("themes", []),
            "key_papers": response.get("key_papers", []),
            "research_groups": response.get("research_groups", []),
            "raw_response": response.get("content", ""),
        }
        
        return landscape
    
    async def _stage_vertical_deep_dive(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Stage 2: Vertical Deep-Dives (4-6 hours)."""
        logger.info(f"Stage 2: Vertical Deep-Dive for {task.topic}")
        
        # Extract top themes from landscape
        landscape = prior_results.get("artifacts", {}).get("landscape", {})
        themes = landscape.get("themes", [])[:3]  # Top 3 themes
        
        deep_dive_results = []
        
        for theme in themes:
            prompt = self._build_deep_dive_prompt(task, theme)
            response = await self._call_perplexity_deep_research(prompt)
            
            deep_dive_results.append({
                "theme": theme,
                "source_count": response.get("source_count", 0),
                "technical_approaches": response.get("approaches", []),
                "key_innovations": response.get("innovations", []),
                "raw_response": response.get("content", ""),
            })
        
        return {
            "stage": "vertical_deep_dive",
            "source_count": sum(r.get("source_count", 0) for r in deep_dive_results),
            "themes_analyzed": len(themes),
            "results": deep_dive_results,
        }
    
    async def _stage_comparative_analysis(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Stage 3: Comparative Analysis (3-5 hours)."""
        logger.info(f"Stage 3: Comparative Analysis for {task.topic}")
        
        prompt = self._build_comparative_prompt(task, prior_results)
        response = await self._call_perplexity_deep_research(prompt)
        
        return {
            "stage": "comparative_analysis",
            "source_count": response.get("source_count", 0),
            "frameworks_compared": response.get("frameworks", []),
            "comparison_matrix": response.get("matrix", {}),
            "raw_response": response.get("content", ""),
        }
    
    async def _stage_gap_identification(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Stage 4: Gap Identification (3-4 hours)."""
        logger.info(f"Stage 4: Gap Identification for {task.topic}")
        
        prompt = self._build_gap_prompt(task, prior_results)
        response = await self._call_perplexity_deep_research(prompt)
        
        return {
            "stage": "gap_identification",
            "technical_gaps": response.get("technical_gaps", []),
            "methodological_gaps": response.get("methodological_gaps", []),
            "research_frontiers": response.get("frontiers", []),
            "raw_response": response.get("content", ""),
        }
    
    async def _stage_hypothesis_generation(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Stage 5: Hypothesis Generation (2-3 hours)."""
        logger.info(f"Stage 5: Hypothesis Generation for {task.topic}")
        
        prompt = self._build_hypothesis_prompt(task, prior_results)
        response = await self._call_perplexity_deep_research(prompt)
        
        return {
            "stage": "hypothesis_generation",
            "hypotheses": response.get("hypotheses", []),
            "test_designs": response.get("test_designs", []),
            "raw_response": response.get("content", ""),
        }
    
    def _build_landscape_prompt(self, task: ResearchTask) -> str:
        """Build landscape mapping prompt."""
        return f"""Conduct an exhaustive mapping of the {task.topic} research landscape 
from 2020-2025. For this landscape review, identify and categorize:

1. All major research frameworks and architectures (minimum 20 distinct approaches)
2. Leading research institutions, universities, and industry labs
3. Key funding sources and research initiatives
4. Top-tier publication venues
5. Historical evolution and major paradigm shifts
6. Temporal trends in publication volume

Return as a structured report with:
- Executive summary (200 words)
- 50+ unique sources organized by category
- Timeline of field evolution
- Research group network analysis (15-20 leading labs)
- Identified research gaps and emerging directions"""
    
    def _build_deep_dive_prompt(self, task: ResearchTask, theme: str) -> str:
        """Build deep dive prompt."""
        return f"""Conduct deep analysis of this research area within {task.topic}:

Theme: {theme}

Analyze 30-50 sources to:
1. Identify the 5-10 most influential foundational papers
2. Map technical approaches, methodologies, and evaluation metrics
3. Document key innovations and incremental progress
4. Extract specific architectural/algorithmic contributions
5. Identify methodological best practices and common pitfalls
6. Locate unresolved technical challenges

Return structured comparison tables showing:
- Technical approach comparison
- Performance metrics across studies
- Methodological rigor assessment
- Tool/framework usage patterns"""
    
    def _build_comparative_prompt(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> str:
        """Build comparative analysis prompt."""
        return f"""Create a comprehensive comparative analysis of leading {task.topic} 
approaches. For the top 5-8 systems/approaches, construct detailed comparison 
matrices analyzing:

1. Architectural patterns
2. Implementation frameworks
3. Performance & scalability
4. Enterprise readiness

Return: (1) comprehensive comparison tables, (2) decision matrix, 
(3) detailed narrative analysis, (4) architectural diagrams"""
    
    def _build_gap_prompt(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> str:
        """Build gap identification prompt."""
        return f"""Based on comprehensive analysis of {task.topic}, conduct meta-analysis 
to identify research gaps:

1. Technical gaps & unsolved problems
2. Methodological limitations
3. Research frontiers (2025-2026)
4. Interdisciplinary opportunities

Return: (1) Gap analysis with evidence, (2) Heat map of well-studied vs neglected 
topics, (3) 10-15 high-priority research questions"""
    
    def _build_hypothesis_prompt(
        self,
        task: ResearchTask,
        prior_results: dict[str, Any]
    ) -> str:
        """Build hypothesis generation prompt."""
        return f"""Based on comprehensive literature synthesis, generate 8-12 specific, 
testable hypotheses about {task.topic}.

For each hypothesis:
1. State precisely (operational definition)
2. Cite supporting evidence from literature
3. Identify key papers
4. Propose concrete experimental design
5. Specify dependent variables
6. Identify confounding variables
7. Estimate effect sizes

Return hypothesis validation matrix."""
    
    async def _call_perplexity_deep_research(self, prompt: str) -> dict[str, Any]:
        """Call Perplexity Deep Research API."""
        # TODO: Implement actual Perplexity API integration
        # For now, return mock response
        logger.warning("Using mock Perplexity response - implement actual API")
        
        return {
            "content": f"Mock research response for: {prompt[:100]}...",
            "source_count": 50,
            "themes": ["Theme 1", "Theme 2", "Theme 3"],
            "key_papers": [],
            "research_groups": [],
        }
    
    def _generate_summary(self, results: dict[str, Any]) -> str:
        """Generate research summary."""
        stages = results.get("stages_completed", [])
        sources = results.get("total_sources", 0)
        
        return f"""Research completed on '{results.get('topic')}' in domain '{results.get('domain')}'.

Stages completed: {', '.join(stages)}
Total sources analyzed: {sources}

Artifacts generated:
{', '.join(results.get('artifacts', {}).keys())}

Research pipeline executed successfully."""
```

#### 1.2 Register Agent with L9 Runtime

**File**: `config/boot_overlay.yaml` (add research agent config)

```yaml
# ... existing config ...

agents:
  research:
    enabled: true
    agent_class: "agents.research_agent.ResearchAgent"
    config:
      model: "gpt-4o"
      temperature: 0.3
      max_tokens: 8000
    perplexity_api_key: "${PERPLEXITY_API_KEY}"
```

#### 1.3 Add Environment Variables

**File**: `.env.example` (add)

```bash
# Perplexity API
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

---

### Phase 2: Perplexity API Integration (Day 3)

#### 2.1 Create Perplexity Client

**File**: `clients/perplexity_client.py`

```python
"""
Perplexity Deep Research API Client
====================================

Client for Perplexity Deep Research with retry logic and rate limiting.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class PerplexityResponse:
    """Response from Perplexity API."""
    content: str
    sources: list[dict[str, Any]]
    citations: list[str]
    metadata: dict[str, Any]


class PerplexityClient:
    """Client for Perplexity Deep Research API."""
    
    def __init__(self, api_key: str):
        """
        Initialize Perplexity client.
        
        Args:
            api_key: Perplexity API key
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.model = "sonar-reasoning"  # or latest available
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def deep_research(
        self,
        prompt: str,
        max_sources: int = 100,
        timeout: int = 300,
    ) -> PerplexityResponse:
        """
        Execute deep research query.
        
        Args:
            prompt: Research prompt
            max_sources: Maximum sources to retrieve
            timeout: Timeout in seconds
            
        Returns:
            PerplexityResponse
        """
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.8,
                    "max_tokens": 5000,
                    "top_p": 0.95,
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            
            # Extract sources and citations
            sources = self._extract_sources(data)
            citations = self._extract_citations(content)
            
            return PerplexityResponse(
                content=content,
                sources=sources,
                citations=citations,
                metadata=data.get("metadata", {}),
            )
    
    def _extract_sources(self, response_data: dict) -> list[dict[str, Any]]:
        """Extract sources from response."""
        # TODO: Implement source extraction based on Perplexity API format
        return []
    
    def _extract_citations(self, content: str) -> list[str]:
        """Extract citations from content."""
        # TODO: Implement citation extraction
        return []
```

---

### Phase 3: Memory & Persistence Integration (Day 4)

#### 3.1 Create Research Artifact Schema

**File**: `memory/research_artifacts.py`

```python
"""
Research Artifact Storage
=========================

Storage and retrieval of research artifacts in PostgreSQL + pgvector.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from memory.substrate_models import Base


class ResearchArtifact(Base):
    """Research artifact model."""
    
    __tablename__ = "research_artifacts"
    
    artifact_id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    topic = Column(String(500), nullable=False, index=True)
    domain = Column(String(200), nullable=False, index=True)
    stage = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    structured_data = Column(JSON, nullable=True)
    source_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    agent_id = Column(String(100), nullable=False, index=True)


@dataclass
class ResearchArtifactIn:
    """Input for creating research artifact."""
    topic: str
    domain: str
    stage: str
    content: str
    structured_data: Optional[dict[str, Any]] = None
    source_count: int = 0
    agent_id: str = ""
```

#### 3.2 Add Migration

**File**: `migrations/0005_research_artifacts.sql`

```sql
-- Research Artifacts Table
CREATE TABLE IF NOT EXISTS research_artifacts (
    artifact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic VARCHAR(500) NOT NULL,
    domain VARCHAR(200) NOT NULL,
    stage VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    structured_data JSONB,
    source_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    agent_id VARCHAR(100) NOT NULL
);

CREATE INDEX idx_research_artifacts_topic ON research_artifacts(topic);
CREATE INDEX idx_research_artifacts_domain ON research_artifacts(domain);
CREATE INDEX idx_research_artifacts_stage ON research_artifacts(stage);
CREATE INDEX idx_research_artifacts_created_at ON research_artifacts(created_at);
CREATE INDEX idx_research_artifacts_agent_id ON research_artifacts(agent_id);

-- Research Bibliography Table
CREATE TABLE IF NOT EXISTS research_bibliography (
    citation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id UUID REFERENCES research_artifacts(artifact_id) ON DELETE CASCADE,
    citation_text TEXT NOT NULL,
    source_url TEXT,
    authors TEXT[],
    publication_year INTEGER,
    venue TEXT,
    citation_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_research_bibliography_artifact ON research_bibliography(artifact_id);
CREATE INDEX idx_research_bibliography_year ON research_bibliography(publication_year);
```

---

### Phase 4: API Integration (Day 5)

#### 4.1 Add Research Agent Routes

**File**: `api/research_routes.py`

```python
"""
Research Agent API Routes
=========================

FastAPI routes for research agent.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, Optional

from agents.research_agent import ResearchAgent, ResearchTask
from core.dependencies import get_research_agent

router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    """Research request model."""
    topic: str
    domain: str = "general"
    depth: str = "comprehensive"
    max_sources: int = 100
    stages: Optional[list[str]] = None


class ResearchResponse(BaseModel):
    """Research response model."""
    task_id: str
    status: str
    results: Optional[dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/execute", response_model=ResearchResponse)
async def execute_research(
    request: ResearchRequest,
    agent: ResearchAgent = Depends(get_research_agent),
):
    """
    Execute research task.
    
    Args:
        request: Research request
        agent: Research agent instance
        
    Returns:
        Research response
    """
    try:
        task = {
            "topic": request.topic,
            "domain": request.domain,
            "depth": request.depth,
            "max_sources": request.max_sources,
            "stages": request.stages,
        }
        
        response = await agent.run(task)
        
        if not response.success:
            raise HTTPException(status_code=500, detail=response.error)
        
        return ResearchResponse(
            task_id=str(response.response_id),
            status="completed",
            results=response.structured_output,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def research_health(
    agent: ResearchAgent = Depends(get_research_agent),
):
    """Check research agent health."""
    return await agent.health_check()
```

#### 4.2 Register Routes

**File**: `api/server.py` (add)

```python
from api import research_routes

app.include_router(research_routes.router)
```

---

### Phase 5: Testing & Documentation (Days 6-7)

#### 5.1 Create Tests

**File**: `tests/test_research_agent.py`

```python
"""
Tests for Research Agent
========================
"""

import pytest
from agents.research_agent import ResearchAgent, ResearchTask


@pytest.mark.asyncio
async def test_research_agent_initialization():
    """Test research agent initialization."""
    agent = ResearchAgent()
    assert agent.agent_name == "research_agent"
    assert agent.agent_role.value == "research"


@pytest.mark.asyncio
async def test_research_agent_landscape_stage():
    """Test landscape mapping stage."""
    agent = ResearchAgent()
    
    task = {
        "topic": "AI Operating Systems",
        "domain": "AI/ML",
        "depth": "landscape",
        "stages": ["landscape"],
    }
    
    response = await agent.run(task)
    
    assert response.success
    assert "landscape" in response.structured_output.get("stages_completed", [])


@pytest.mark.asyncio
async def test_research_agent_full_pipeline():
    """Test full 5-stage pipeline."""
    agent = ResearchAgent()
    
    task = {
        "topic": "AI Operating Systems",
        "domain": "AI/ML",
        "depth": "comprehensive",
        "max_sources": 50,
    }
    
    response = await agent.run(task)
    
    assert response.success
    assert len(response.structured_output.get("stages_completed", [])) == 5
```

#### 5.2 Create Documentation

**File**: `docs/research_agent.md`

```markdown
# Research Agent

## Overview

The Research Agent provides deep research capabilities using a 5-stage progressive research pipeline.

## Usage

### From Python

\`\`\`python
from agents.research_agent import ResearchAgent

agent = ResearchAgent(perplexity_api_key="your_key")

task = {
    "topic": "AI Operating Systems",
    "domain": "AI/ML",
    "depth": "comprehensive",
    "max_sources": 150,
}

response = await agent.run(task)
print(response.structured_output)
\`\`\`

### From API

\`\`\`bash
curl -X POST http://localhost:8000/research/execute \\
  -H "Content-Type: application/json" \\
  -d '{
    "topic": "AI Operating Systems",
    "domain": "AI/ML",
    "depth": "comprehensive",
    "max_sources": 150
  }'
\`\`\`

### From Agent L

Agent L can call the research agent:

\`\`\`python
# In Agent L's workflow
research_result = await self.call_research_agent({
    "topic": "LangGraph best practices",
    "domain": "AI/ML",
    "depth": "deep_dive",
})
\`\`\`

## Stages

1. **Landscape Mapping** (3-5 hours)
   - Broad conceptual mapping
   - 50-80 sources
   - Research group identification

2. **Vertical Deep-Dives** (4-6 hours)
   - Granular technical analysis
   - 90-150 sources
   - Framework comparison

3. **Comparative Analysis** (3-5 hours)
   - System comparison matrices
   - 50-80 sources
   - Decision frameworks

4. **Gap Identification** (3-4 hours)
   - Research frontiers
   - 30-40 sources
   - Hypothesis seeds

5. **Hypothesis Generation** (2-3 hours)
   - Testable hypotheses
   - 40-60 sources
   - Experimental designs

## Configuration

Add to `.env`:

\`\`\`bash
PERPLEXITY_API_KEY=your_key_here
\`\`\`

Add to `config/boot_overlay.yaml`:

\`\`\`yaml
agents:
  research:
    enabled: true
    perplexity_api_key: "${PERPLEXITY_API_KEY}"
\`\`\`
```

---

## Integration Checklist

### Pre-Integration

- [ ] Clone L9 repository
- [ ] Review BaseAgent interface
- [ ] Review memory substrate
- [ ] Review world model integration
- [ ] Set up development environment

### Core Implementation

- [ ] Create `agents/research_agent.py`
- [ ] Create `clients/perplexity_client.py`
- [ ] Create `memory/research_artifacts.py`
- [ ] Add migration `0005_research_artifacts.sql`
- [ ] Create `api/research_routes.py`

### Configuration

- [ ] Update `config/boot_overlay.yaml`
- [ ] Update `.env.example`
- [ ] Set `PERPLEXITY_API_KEY` in `.env`

### Testing

- [ ] Create `tests/test_research_agent.py`
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Test API endpoints
- [ ] Test agent-to-agent calls

### Documentation

- [ ] Create `docs/research_agent.md`
- [ ] Update main README.md
- [ ] Add usage examples
- [ ] Document API endpoints

### Deployment

- [ ] Apply database migration
- [ ] Restart L9 services
- [ ] Verify agent registration
- [ ] Test from Agent L
- [ ] Test from Agent Emma (when available)

---

## Usage Examples

### Example 1: Agent L Calls Research Agent

```python
# In Agent L's workflow
async def research_topic(self, topic: str) -> dict:
    """Research a topic using the research agent."""
    
    research_task = {
        "topic": topic,
        "domain": "AI/ML",
        "depth": "comprehensive",
        "max_sources": 150,
    }
    
    # Call research agent
    from agents.research_agent import ResearchAgent
    research_agent = ResearchAgent()
    
    response = await research_agent.run(research_task)
    
    if response.success:
        # Store in memory
        await self.store_research_results(response.structured_output)
        
        return response.structured_output
    else:
        raise Exception(f"Research failed: {response.error}")
```

### Example 2: API Call from External Service

```bash
curl -X POST http://localhost:8000/research/execute \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "LangGraph multi-agent patterns",
    "domain": "AI/ML",
    "depth": "deep_dive",
    "max_sources": 100,
    "stages": ["landscape", "deep_dive", "comparative"]
  }'
```

### Example 3: Scheduled Research Task

```python
# In L9 scheduler
from agents.research_agent import ResearchAgent

async def weekly_research_scan():
    """Weekly research scan on emerging topics."""
    
    agent = ResearchAgent()
    
    topics = [
        "AI OS architectures 2025",
        "Multi-agent coordination protocols",
        "LLM inference optimization",
    ]
    
    for topic in topics:
        task = {
            "topic": topic,
            "domain": "AI/ML",
            "depth": "landscape",
            "max_sources": 50,
            "stages": ["landscape", "gaps"],
        }
        
        response = await agent.run(task)
        
        if response.success:
            await store_weekly_scan(topic, response.structured_output)
```

---

## Next Steps

1. **Implement Perplexity API Integration**
   - Get Perplexity API key
   - Test API endpoints
   - Implement source extraction
   - Implement citation parsing

2. **Enhance Prompt Engineering**
   - Port Perplexity Deep Research prompt patterns
   - Add domain-specific templates
   - Implement multi-variation synthesis

3. **Add Advanced Features**
   - Semantic graph construction
   - Consensus pattern detection
   - Automated bibliography generation
   - Research report generation

4. **Integrate with Emma Agent**
   - Design Emma's research workflow
   - Implement collaborative research
   - Add research delegation patterns

5. **Production Hardening**
   - Add comprehensive error handling
   - Implement rate limiting
   - Add caching layer
   - Optimize for cost

---

## Estimated Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Core Agent | 2 days | Research agent, BaseAgent wrapper |
| Phase 2: API Integration | 1 day | Perplexity client, retry logic |
| Phase 3: Memory Integration | 1 day | Artifact storage, migrations |
| Phase 4: API Routes | 1 day | FastAPI endpoints, dependencies |
| Phase 5: Testing & Docs | 2 days | Tests, documentation, examples |
| **Total** | **7 days** | **Production-ready research agent** |

---

## Success Criteria

- [ ] Research agent inherits from BaseAgent
- [ ] Kernel-aware lifecycle integration
- [ ] 5-stage pipeline functional
- [ ] Perplexity API integration working
- [ ] Memory persistence operational
- [ ] API endpoints tested
- [ ] Agent L can call research agent
- [ ] Tests passing (≥85% coverage)
- [ ] Documentation complete
- [ ] Deployment successful

---

**Status**: Ready for Implementation  
**Complexity**: Medium  
**Risk**: Low (well-defined interfaces, incremental integration)
