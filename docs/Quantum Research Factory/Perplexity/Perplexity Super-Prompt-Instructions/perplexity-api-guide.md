# Comprehensive Guide to Perplexity API for Semi-Autonomous Research

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication & Setup](#authentication--setup)
4. [Understanding Perplexity Models](#understanding-perplexity-models)
5. [Search Types & When to Use Each](#search-types--when-to-use-each)
6. [API Endpoints](#api-endpoints)
7. [Semi-Autonomous Research Architecture](#semi-autonomous-research-architecture)
8. [Best Practices for Scale & Autonomy](#best-practices-for-scale--autonomy)
9. [Code Examples by Query Type](#code-examples-by-query-type)
10. [Rate Limits & Cost Optimization](#rate-limits--cost-optimization)
11. [Error Handling & Recovery](#error-handling--recovery)
12. [Advanced Patterns](#advanced-patterns)

---

## Introduction

Perplexity's Sonar API combines real-time web search with advanced language models, enabling developers to build semi-autonomous research agents that can:

- Perform real-time web searches with detailed citations
- Conduct deep multi-step research across hundreds of sources
- Reason through complex queries with Chain-of-Thought capabilities
- Process and analyze documents, images, and PDFs
- Generate comprehensive reports with verifiable sources

This guide focuses on building scalable, autonomous research systems with minimal manual intervention.

---

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Perplexity API account
- Payment method (API requires paid credits)
- Internet connection for API calls

### Quick Installation

```bash
# Install Perplexity SDK
pip install perplexity

# Or using OpenAI SDK (Perplexity is OpenAI-compatible)
pip install openai
```

---

## Authentication & Setup

### Step 1: Obtain API Key

1. Visit [perplexity.ai](https://www.perplexity.ai)
2. Log in to your account
3. Navigate to Settings → API
4. Add a payment method (required)
5. Click "Generate" to create a new API key
6. Copy and securely store your API key

**⚠️ Security Note**: Treat your API key like a password. Never commit it to version control or share it publicly.

### Step 2: Configure Environment

**Option 1: Environment Variable (Recommended)**

```bash
export PERPLEXITY_API_KEY="your-api-key-here"
```

**Option 2: .env File**

```bash
# Create .env file in your project root
PERPLEXITY_API_KEY=your-api-key-here
```

**Option 3: Direct Configuration (Development Only)**

```python
from perplexity import Perplexity

client = Perplexity(api_key="your-api-key-here")
```

### Step 3: Verify Setup

```python
from perplexity import Perplexity

client = Perplexity()

# Test connection
try:
    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": "Test connection"}]
    )
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

---

## Understanding Perplexity Models

Perplexity offers several specialized models, each optimized for different research scenarios:

### 1. **Sonar** (Lightweight & Fast)

**Best For**: Quick searches, straightforward Q&A, simple fact-checking

**Characteristics**:
- Fastest response time (~1200 tokens/second)
- Cost-effective ($1 per 1M input tokens, $1 per 1M output tokens)
- 128K context window
- Real-time web search with citations
- Non-reasoning model

**Pricing**: $5-12 per 1,000 requests (varies by search context size)

**Use Cases**:
- Looking up definitions or quick facts
- Browsing news, sports, health, finance
- Summarizing books, TV shows, movies
- Simple product lookups

**When to Use**:
- Speed is critical
- Query is straightforward
- Budget constraints
- High-volume, simple queries

---

### 2. **Sonar Pro** (Enhanced Search)

**Best For**: Complex multi-step queries, detailed analysis, comprehensive citations

**Characteristics**:
- 2-3x more citations than standard Sonar
- Deeper search capabilities
- Larger context window
- Better at multi-layered follow-ups
- More precise search execution

**Pricing**: Same token costs as Sonar but with enhanced search fees

**Use Cases**:
- Academic research with extensive citations
- Market analysis requiring multiple perspectives
- Competitive intelligence
- Technical documentation research

**When to Use**:
- Need comprehensive source coverage
- Query requires nuanced understanding
- Multiple perspectives needed
- Citation depth is critical

---

### 3. **Sonar Reasoning** (Logic & Chain-of-Thought)

**Best For**: Logical reasoning, multi-step analysis, maintaining context

**Characteristics**:
- Chain-of-Thought (CoT) capabilities
- Better at logical evaluations
- Maintains multiple pieces of information
- Live search integration
- Step-by-step inference

**Use Cases**:
- Mathematical problem-solving
- Technical troubleshooting
- Comparative analysis
- Decision-making support

**When to Use**:
- Query requires logical progression
- Need to evaluate multiple factors
- Complex decision trees
- Step-by-step reasoning needed

---

### 4. **Sonar Reasoning Pro** (Advanced Logic)

**Best For**: Expert-level reasoning, complex synthesis, research requiring deep analysis

**Characteristics**:
- Powered by DeepSeek-R1 1776
- Superior step-by-step inference
- Excellent at comparison and synthesis
- Multiple search queries per request
- Enhanced reasoning capabilities

**Rate Limit**: 50 requests per minute

**Use Cases**:
- Research synthesis across multiple papers
- Investment analysis with multiple factors
- Scientific hypothesis evaluation
- Strategic planning and forecasting

**When to Use**:
- Highest reasoning quality needed
- Complex research requiring synthesis
- Expert-level analysis required
- Budget allows for premium model

---

### 5. **Sonar Deep Research** (Autonomous Multi-Step Research)

**Best For**: Comprehensive research reports, exhaustive analysis, autonomous investigation

**Characteristics**:
- Performs dozens of searches autonomously
- Reads hundreds of sources
- 200,000 token context window
- Self-directed research planning
- Generates detailed expert reports
- Reasoning effort levels: low, medium, high

**Rate Limit**: 5 requests per minute

**Pricing**: Higher cost due to extensive searching (typically $0.50-$2 per request)

**Use Cases**:
- Academic research and comprehensive reports
- Market analysis and competitive intelligence
- Due diligence and investigative research
- Financial analysis
- Marketing campaign research
- Technology landscape analysis

**When to Use**:
- Need comprehensive, expert-level report
- Topic requires breadth and depth
- Time to conduct manual research not available
- Budget allows for premium service
- Research requires 50+ sources

**Reasoning Effort Settings**:
- `low`: Faster, fewer citations, lower cost
- `medium`: Balanced (default)
- `high`: Most citations, deepest insights, highest cost and latency

---

### Model Comparison Table

| Model | Speed | Citations | Reasoning | Cost | Rate Limit | Best Use Case |
|-------|-------|-----------|-----------|------|------------|---------------|
| Sonar | ⚡⚡⚡⚡⚡ | ⭐⭐ | ❌ | $ | 50/min | Quick facts, simple queries |
| Sonar Pro | ⚡⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ❌ | $$ | 50/min | Comprehensive citations |
| Sonar Reasoning | ⚡⚡⚡ | ⭐⭐⭐ | ✅ | $$ | 50/min | Logical analysis |
| Sonar Reasoning Pro | ⚡⚡ | ⭐⭐⭐⭐ | ✅✅ | $$$ | 50/min | Complex synthesis |
| Sonar Deep Research | ⚡ | ⭐⭐⭐⭐⭐ | ✅✅✅ | $$$$ | 5/min | Autonomous research reports |

---

## Search Types & When to Use Each

Perplexity offers two main API approaches for research:

### 1. Chat Completions API (Model-Based)

**Endpoint**: `/chat/completions`

**What It Does**: Uses Sonar models to generate conversational responses with real-time web search integrated into the model's response generation.

**Search Types**:

#### A. **Auto Search** (Recommended)

Automatically determines whether to use fast or Pro search based on query complexity.

```python
response = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Analyze quantum computing market trends"}],
    search_type="auto"  # Default
)
```

**When to Use**:
- Uncertain about query complexity
- Want cost optimization
- Building general-purpose agents
- Variable query types

---

#### B. **Fast Search**

Optimized for speed with lightweight context retrieval.

```python
response = client.chat.completions.create(
    model="sonar",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    search_type="fast"
)
```

**When to Use**:
- Simple factual queries
- Speed is priority
- Cost-sensitive applications
- High-volume requests

---

#### C. **Pro Search**

Deep search with extensive source analysis and reasoning.

```python
response = client.chat.completions.create(
    model="sonar-pro",
    messages=[{"role": "user", "content": "Comprehensive analysis of renewable energy policies"}],
    search_type="pro"
)
```

**When to Use**:
- Complex analysis needed
- Comprehensive citations required
- Multi-faceted topics
- Expert-level insights needed

---

### 2. Search API (Direct Web Search)

**Endpoint**: `/search`

**What It Does**: Returns ranked web search results without language model generation. Direct access to Perplexity's search index.

```python
search = client.search.create(
    query="artificial intelligence breakthroughs 2024",
    max_results=10,
    max_tokens_per_page=1024
)

for result in search.results:
    print(f"{result.title}: {result.url}")
    print(f"Date: {result.date}")
    print(f"Snippet: {result.snippet}\n")
```

**Rate Limit**: 3 requests per second (burst capacity: 3 instant requests)

**When to Use**:
- Need raw search results without AI synthesis
- Building custom research pipelines
- Want control over result processing
- Integrating with your own LLMs
- Collecting data for fine-tuning

---

### Search API vs Chat Completions: Decision Matrix

| Scenario | Use Search API | Use Chat Completions |
|----------|----------------|---------------------|
| Need raw URLs and snippets | ✅ | ❌ |
| Want AI-synthesized answer | ❌ | ✅ |
| Building custom pipeline | ✅ | ❌ |
| Need citations in narrative | ❌ | ✅ |
| Batch data collection | ✅ | ❌ |
| Conversational context | ❌ | ✅ |
| Cost-per-query sensitive | ✅ | ❌ |
| Need reasoning/synthesis | ❌ | ✅ |

---

## API Endpoints

### 1. Chat Completions Endpoint

**URL**: `https://api.perplexity.ai/chat/completions`

**Method**: POST

**Headers**:
```json
{
  "Authorization": "Bearer YOUR_API_KEY",
  "Content-Type": "application/json"
}
```

**Request Body**:
```json
{
  "model": "sonar-pro",
  "messages": [
    {
      "role": "system",
      "content": "You are a research assistant."
    },
    {
      "role": "user",
      "content": "What are the latest AI developments?"
    }
  ],
  "max_tokens": 1000,
  "temperature": 0.7,
  "stream": false,
  "search_type": "auto"
}
```

**Response**:
```json
{
  "id": "uuid",
  "model": "sonar-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on recent developments..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 400,
    "total_tokens": 420
  },
  "citations": [
    "https://example.com/article1",
    "https://example.com/article2"
  ],
  "search_results": [
    {
      "title": "AI Breakthrough 2024",
      "url": "https://example.com/article1",
      "date": "2024-12-15",
      "snippet": "Recent developments in AI..."
    }
  ]
}
```

---

### 2. Search Endpoint

**URL**: `https://api.perplexity.ai/search`

**Method**: POST

**Request Body**:
```json
{
  "query": "renewable energy innovations 2024",
  "max_results": 10,
  "max_tokens": 25000,
  "max_tokens_per_page": 1024,
  "country": "US",
  "search_recency_filter": "week",
  "search_domain_filter": ["science.org", "nature.com"],
  "return_images": true,
  "return_snippets": true
}
```

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string or array | required | Search query(ies) |
| `max_results` | integer | 10 | Results per query (1-20) |
| `max_tokens` | integer | 25000 | Total token budget (1-1,000,000) |
| `max_tokens_per_page` | integer | 1024 | Tokens per result |
| `country` | string | null | ISO country code (e.g., "US") |
| `search_recency_filter` | string | null | "day", "week", "month", "year" |
| `search_domain_filter` | array | null | Allowlist/denylist domains (max 20) |
| `return_images` | boolean | false | Include images in results |
| `return_snippets` | boolean | true | Include text snippets |

---

### 3. Async Chat Completions (For Long-Running Research)

**Create Async Request**: `POST /async/chat/completions`

**Rate Limit**: 5 requests per minute

**Poll for Results**: `GET /async/chat/completions/{request_id}`

**Rate Limit**: 6000 requests per minute

**Use Case**: Sonar Deep Research queries that take 5+ minutes

```python
# Submit async request
async_response = client.async_chat.completions.create(
    model="sonar-deep-research",
    messages=[{"role": "user", "content": "Comprehensive market analysis..."}]
)

request_id = async_response.id

# Poll for completion
import time
while True:
    status = client.async_chat.completions.retrieve(request_id)
    if status.status == "completed":
        result = status.result
        break
    time.sleep(10)  # Check every 10 seconds
```

---

## Semi-Autonomous Research Architecture

Building effective semi-autonomous research agents requires thoughtful architecture. Here are proven patterns:

### Pattern 1: Multi-Agent Parallel Research

**Use Case**: Break complex research into subtopics, research in parallel, synthesize results.

**Architecture**:

```
Lead Agent (Planner)
    ↓
    ├─→ Subagent 1: Core concepts → Sonar Pro
    ├─→ Subagent 2: Recent trends → Sonar Pro
    └─→ Subagent 3: Applications → Sonar Pro
    ↓
Lead Agent (Synthesizer) → Sonar Reasoning Pro
```

**Benefits**:
- 3x faster than sequential research
- Better topic coverage
- Parallel API calls = efficient rate limit usage

**Implementation**:

```python
import asyncio
from perplexity import AsyncPerplexity

async def multi_agent_research(main_query):
    async with AsyncPerplexity() as client:
        # Step 1: Plan subtopics
        plan_prompt = f"""Break down '{main_query}' into 3 distinct research subtopics.
        
        SUBTOPIC 1: [Foundational aspects]
        SUBTOPIC 2: [Recent developments]
        SUBTOPIC 3: [Real-world applications]"""
        
        plan = await client.chat.completions.create(
            model="sonar-reasoning",
            messages=[{"role": "user", "content": plan_prompt}]
        )
        
        # Step 2: Extract subtopics (simplified - use regex or LLM parsing)
        subtopics = [
            f"{main_query} fundamentals",
            f"{main_query} latest developments 2024",
            f"{main_query} real world applications"
        ]
        
        # Step 3: Parallel subagent research
        async def research_subtopic(subtopic):
            return await client.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "user", "content": f"Research: {subtopic}"}]
            )
        
        tasks = [research_subtopic(topic) for topic in subtopics]
        subagent_results = await asyncio.gather(*tasks)
        
        # Step 4: Synthesize findings
        synthesis_prompt = f"""ORIGINAL QUERY: {main_query}
        
        SUBAGENT FINDINGS:
        
        Subagent 1 (Fundamentals):
        {subagent_results[0].choices[0].message.content}
        
        Subagent 2 (Recent Developments):
        {subagent_results[1].choices[0].message.content}
        
        Subagent 3 (Applications):
        {subagent_results[2].choices[0].message.content}
        
        Synthesize these findings into a comprehensive report with:
        1. Executive Summary
        2. Integrated Findings
        3. Key Insights
        4. Sources Analyzed: {sum(len(r.citations) for r in subagent_results)}"""
        
        final_report = await client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        
        return final_report

# Usage
report = asyncio.run(multi_agent_research("quantum computing commercialization"))
print(report.choices[0].message.content)
```

---

### Pattern 2: Iterative Deep Dive

**Use Case**: Start broad, progressively narrow based on findings.

**Architecture**:

```
Initial Query → Sonar
    ↓
Extract Key Topics
    ↓
For each topic → Sonar Pro (parallel)
    ↓
Identify Knowledge Gaps
    ↓
Fill gaps → Sonar Reasoning Pro
    ↓
Final Synthesis → Sonar Deep Research
```

**Implementation**:

```python
from perplexity import Perplexity

def iterative_research(query, depth=3):
    client = Perplexity()
    research_trail = []
    
    # Level 1: Broad overview
    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": f"Overview of {query}"}]
    )
    research_trail.append(("overview", response))
    
    # Level 2: Extract and research key aspects
    content = response.choices[0].message.content
    # Simple topic extraction (use LLM or NLP for production)
    aspects = extract_key_aspects(content)  # Custom function
    
    aspect_results = []
    for aspect in aspects[:3]:  # Top 3 aspects
        aspect_response = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": f"Deep dive into {aspect} of {query}"}]
        )
        aspect_results.append(aspect_response)
        research_trail.append((aspect, aspect_response))
    
    # Level 3: Identify gaps and fill
    all_citations = set()
    for result in aspect_results:
        all_citations.update(result.citations)
    
    gaps = identify_gaps(query, aspect_results)  # Custom function
    
    if gaps:
        gap_response = client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=[{"role": "user", "content": f"Research these underexplored areas: {gaps}"}]
        )
        research_trail.append(("gaps", gap_response))
    
    # Final synthesis
    synthesis = synthesize_research(research_trail)
    return synthesis

def extract_key_aspects(content):
    # Simplified - use LLM for production
    # Extract main topics mentioned in content
    return ["aspect1", "aspect2", "aspect3"]

def identify_gaps(query, results):
    # Compare what was found vs. what should be covered
    return []

def synthesize_research(trail):
    # Combine all findings into final report
    return "Final comprehensive report"
```

---

### Pattern 3: Autonomous Deep Research with Quality Control

**Use Case**: Fully autonomous research with validation checkpoints.

**Architecture**:

```
Query → Sonar Deep Research (reasoning_effort: high)
    ↓
Quality Check Agent → Validate completeness
    ↓
    [Pass] → Return Report
    [Fail] → Identify gaps → Additional research → Re-synthesize
```

**Implementation**:

```python
from perplexity import Perplexity

def autonomous_deep_research_with_qc(query, quality_threshold=0.8):
    client = Perplexity()
    
    # Step 1: Initial deep research
    deep_research = client.chat.completions.create(
        model="sonar-deep-research",
        messages=[{"role": "user", "content": query}],
        # Optional: specify reasoning effort
        # reasoning_effort="high"  # More citations, slower, higher cost
    )
    
    report = deep_research.choices[0].message.content
    citations = deep_research.citations
    
    # Step 2: Quality validation
    quality_check = client.chat.completions.create(
        model="sonar-reasoning-pro",
        messages=[{
            "role": "user",
            "content": f"""Evaluate this research report for completeness:
            
            ORIGINAL QUERY: {query}
            
            REPORT:
            {report}
            
            SOURCES: {len(citations)} citations
            
            Rate completeness (0-1) and identify any gaps:
            - Completeness Score: [0-1]
            - Missing Topics: [list]
            - Weak Areas: [list]"""
        }]
    )
    
    # Step 3: Parse quality score (simplified)
    quality_text = quality_check.choices[0].message.content
    quality_score = extract_quality_score(quality_text)  # Custom parser
    
    if quality_score >= quality_threshold:
        return {
            "report": report,
            "citations": citations,
            "quality_score": quality_score,
            "status": "complete"
        }
    
    # Step 4: Fill identified gaps
    gaps = extract_gaps(quality_text)  # Custom parser
    
    gap_research = client.chat.completions.create(
        model="sonar-pro",
        messages=[{"role": "user", "content": f"Research these gaps: {gaps}"}]
    )
    
    # Step 5: Re-synthesize
    final_report = client.chat.completions.create(
        model="sonar-reasoning-pro",
        messages=[{
            "role": "user",
            "content": f"""Synthesize final report:
            
            ORIGINAL REPORT:
            {report}
            
            ADDITIONAL RESEARCH:
            {gap_research.choices[0].message.content}
            
            Create comprehensive final report."""
        }]
    )
    
    return {
        "report": final_report.choices[0].message.content,
        "citations": citations + gap_research.citations,
        "quality_score": 1.0,
        "status": "enhanced"
    }

def extract_quality_score(text):
    # Parse quality score from LLM response
    # Use regex or structured output
    return 0.85

def extract_gaps(text):
    # Extract identified gaps
    return ["gap1", "gap2"]

# Usage
result = autonomous_deep_research_with_qc(
    "Comprehensive analysis of carbon capture technology viability",
    quality_threshold=0.85
)
print(f"Status: {result['status']}")
print(f"Quality: {result['quality_score']}")
print(f"Citations: {len(result['citations'])}")
print(result['report'])
```

---

## Best Practices for Scale & Autonomy

### 1. Rate Limit Management

**Challenge**: Different models have different rate limits.

**Solution**: Implement intelligent rate limiting with token bucket algorithm.

```python
import time
import asyncio
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.limits = {
            "sonar": {"rpm": 50, "rps": 0.83},
            "sonar-pro": {"rpm": 50, "rps": 0.83},
            "sonar-reasoning": {"rpm": 50, "rps": 0.83},
            "sonar-reasoning-pro": {"rpm": 50, "rps": 0.83},
            "sonar-deep-research": {"rpm": 5, "rps": 0.083},
            "search": {"rps": 3, "burst": 3}
        }
        self.buckets = defaultdict(lambda: {"tokens": 0, "last_update": time.time()})
    
    def acquire(self, model, tokens=1):
        limit = self.limits.get(model, {"rps": 1})
        bucket = self.buckets[model]
        
        now = time.time()
        elapsed = now - bucket["last_update"]
        
        # Refill tokens based on elapsed time
        refill = elapsed * limit["rps"]
        bucket["tokens"] = min(bucket["tokens"] + refill, limit.get("burst", limit["rps"]))
        bucket["last_update"] = now
        
        if bucket["tokens"] >= tokens:
            bucket["tokens"] -= tokens
            return True
        
        # Calculate wait time
        wait_time = (tokens - bucket["tokens"]) / limit["rps"]
        return wait_time
    
    async def wait_for_token(self, model):
        while True:
            result = self.acquire(model)
            if result is True:
                return
            await asyncio.sleep(result)

# Usage
limiter = RateLimiter()

async def rate_limited_request(client, model, messages):
    await limiter.wait_for_token(model)
    return await client.chat.completions.create(model=model, messages=messages)
```

---

### 2. Batch Processing for Maximum Throughput

**Strategy**: Process queries in batches with controlled concurrency.

```python
import asyncio
from typing import List
from perplexity import AsyncPerplexity

class BatchProcessor:
    def __init__(self, batch_size=5, delay_between_batches=1.0):
        self.batch_size = batch_size
        self.delay = delay_between_batches
    
    async def process_batch(self, queries: List[str], model="sonar-pro"):
        results = []
        
        async with AsyncPerplexity() as client:
            for i in range(0, len(queries), self.batch_size):
                batch = queries[i:i + self.batch_size]
                
                # Process batch concurrently
                tasks = [
                    client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": q}]
                    )
                    for q in batch
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter exceptions
                for result in batch_results:
                    if not isinstance(result, Exception):
                        results.append(result)
                
                # Delay between batches
                if i + self.batch_size < len(queries):
                    await asyncio.sleep(self.delay)
        
        return results

# Usage
async def main():
    processor = BatchProcessor(batch_size=3, delay_between_batches=0.5)
    
    queries = [
        "Latest AI developments",
        "Quantum computing breakthroughs",
        "Renewable energy innovations",
        "Biotechnology advances",
        "Space exploration updates"
    ]
    
    results = await processor.process_batch(queries)
    print(f"Processed {len(results)}/{len(queries)} queries successfully")

asyncio.run(main())
```

---

### 3. Intelligent Query Routing

**Strategy**: Route queries to appropriate models based on complexity.

```python
from perplexity import Perplexity
import re

class IntelligentRouter:
    def __init__(self):
        self.client = Perplexity()
        
        # Complexity indicators
        self.simple_patterns = [
            r"what is", r"who is", r"when did", r"where is",
            r"define", r"meaning of"
        ]
        
        self.complex_patterns = [
            r"analyze", r"compare", r"evaluate", r"synthesize",
            r"comprehensive", r"detailed analysis", r"research"
        ]
        
        self.reasoning_patterns = [
            r"why", r"how does", r"explain the reasoning",
            r"what factors", r"implications of"
        ]
    
    def classify_query(self, query):
        query_lower = query.lower()
        
        # Check for deep research indicators
        if any(word in query_lower for word in ["comprehensive", "detailed report", "in-depth analysis"]):
            if len(query.split()) > 10:  # Long, complex query
                return "sonar-deep-research"
        
        # Check for reasoning requirements
        if any(re.search(pattern, query_lower) for pattern in self.reasoning_patterns):
            return "sonar-reasoning-pro"
        
        # Check for complex analysis
        if any(re.search(pattern, query_lower) for pattern in self.complex_patterns):
            return "sonar-pro"
        
        # Default to fast sonar
        return "sonar"
    
    def execute_query(self, query):
        model = self.classify_query(query)
        
        print(f"Routing to: {model}")
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query}]
        )
        
        return {
            "model_used": model,
            "response": response.choices[0].message.content,
            "citations": response.citations,
            "cost_estimate": self.estimate_cost(response)
        }
    
    def estimate_cost(self, response):
        # Rough cost estimation
        usage = response.usage
        input_cost = usage.prompt_tokens / 1_000_000 * 3
        output_cost = usage.completion_tokens / 1_000_000 * 15
        return input_cost + output_cost

# Usage
router = IntelligentRouter()

queries = [
    "What is quantum computing?",  # → sonar
    "Comprehensive analysis of quantum computing market trends",  # → sonar-deep-research
    "Why is quantum computing important for cryptography?",  # → sonar-reasoning-pro
    "Compare quantum computing approaches across companies"  # → sonar-pro
]

for query in queries:
    result = router.execute_query(query)
    print(f"\nQuery: {query}")
    print(f"Model: {result['model_used']}")
    print(f"Estimated cost: ${result['cost_estimate']:.4f}")
```

---

### 4. Caching & Deduplication

**Strategy**: Cache results to avoid redundant API calls.

```python
import hashlib
import json
import time
from functools import wraps

class ResearchCache:
    def __init__(self, ttl=3600):  # 1 hour default TTL
        self.cache = {}
        self.ttl = ttl
    
    def _hash_query(self, query, model):
        """Create cache key from query and model"""
        key = f"{model}:{query}".encode()
        return hashlib.md5(key).hexdigest()
    
    def get(self, query, model):
        """Retrieve cached result if valid"""
        key = self._hash_query(query, model)
        
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                print(f"✅ Cache hit: {query[:50]}...")
                return entry["result"]
            else:
                del self.cache[key]
        
        return None
    
    def set(self, query, model, result):
        """Store result in cache"""
        key = self._hash_query(query, model)
        self.cache[key] = {
            "result": result,
            "timestamp": time.time()
        }
    
    def clear_expired(self):
        """Remove expired entries"""
        now = time.time()
        expired = [
            k for k, v in self.cache.items()
            if now - v["timestamp"] >= self.ttl
        ]
        for k in expired:
            del self.cache[k]

# Decorator for automatic caching
def cached_research(cache, ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(query, model="sonar-pro", **kwargs):
            # Check cache
            cached = cache.get(query, model)
            if cached:
                return cached
            
            # Execute function
            result = func(query, model=model, **kwargs)
            
            # Store in cache
            cache.set(query, model, result)
            
            return result
        return wrapper
    return decorator

# Usage
cache = ResearchCache(ttl=3600)

@cached_research(cache)
def research_query(query, model="sonar-pro"):
    from perplexity import Perplexity
    client = Perplexity()
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}]
    )
    
    return {
        "content": response.choices[0].message.content,
        "citations": response.citations
    }

# First call - hits API
result1 = research_query("What is machine learning?")

# Second call - uses cache
result2 = research_query("What is machine learning?")

# Different query - hits API
result3 = research_query("What is deep learning?")
```

---

### 5. Multi-Query Search for Comprehensive Coverage

**Strategy**: Break broad topics into multiple targeted searches.

```python
from perplexity import Perplexity

def multi_query_research(main_topic, num_queries=5):
    client = Perplexity()
    
    # Step 1: Generate targeted sub-queries
    query_generation = client.chat.completions.create(
        model="sonar-reasoning",
        messages=[{
            "role": "user",
            "content": f"""Generate {num_queries} specific, diverse search queries to comprehensively research: "{main_topic}"
            
            Each query should explore a different angle:
            1. [Foundational concepts]
            2. [Latest developments]
            3. [Industry applications]
            4. [Challenges/limitations]
            5. [Future trends]
            
            Return only the queries, numbered."""
        }]
    )
    
    # Step 2: Parse generated queries (simplified)
    queries_text = query_generation.choices[0].message.content
    sub_queries = [
        line.split(". ", 1)[1] for line in queries_text.split("\n")
        if ". " in line
    ][:num_queries]
    
    # Step 3: Execute multi-query search API
    search_results = client.search.create(
        query=sub_queries,
        max_results=5
    )
    
    # Step 4: Process results (grouped by query)
    all_sources = []
    for i, query_results in enumerate(search_results.results):
        print(f"\n📌 Query {i+1}: {sub_queries[i]}")
        for result in query_results:
            print(f"  - {result.title}")
            all_sources.append({
                "query": sub_queries[i],
                "title": result.title,
                "url": result.url,
                "snippet": result.snippet,
                "date": result.date
            })
    
    # Step 5: Synthesize findings
    synthesis_input = "\n\n".join([
        f"QUERY: {s['query']}\nFINDING: {s['title']}\n{s['snippet']}"
        for s in all_sources[:20]  # Limit to avoid token limits
    ])
    
    synthesis = client.chat.completions.create(
        model="sonar-reasoning-pro",
        messages=[{
            "role": "user",
            "content": f"""Synthesize these research findings into a comprehensive report on "{main_topic}":
            
            {synthesis_input}
            
            Create a structured report with:
            1. Executive Summary
            2. Key Findings by Theme
            3. Trends and Insights
            4. Conclusion"""
        }]
    )
    
    return {
        "topic": main_topic,
        "sub_queries": sub_queries,
        "sources": all_sources,
        "report": synthesis.choices[0].message.content
    }

# Usage
result = multi_query_research("sustainable urban transportation", num_queries=5)
print(f"\nResearched {len(result['sources'])} sources across {len(result['sub_queries'])} queries")
print(f"\n{result['report']}")
```

---

## Code Examples by Query Type

### Example 1: Simple Fact Lookup (Sonar)

```python
from perplexity import Perplexity

client = Perplexity()

response = client.chat.completions.create(
    model="sonar",
    messages=[{
        "role": "user",
        "content": "What is the current population of Tokyo?"
    }]
)

print(response.choices[0].message.content)
print(f"\nSources: {response.citations}")
```

**Output**:
```
The current population of Tokyo is approximately 14 million as of 2024.

Sources: ['https://example.com/tokyo-stats', 'https://census.example.com']
```

**Cost**: ~$0.005 per request

---

### Example 2: Comprehensive Topic Research (Sonar Pro)

```python
from perplexity import Perplexity

client = Perplexity()

response = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": "Provide a comprehensive overview of CRISPR gene editing technology, including recent breakthroughs, ethical concerns, and commercial applications."
    }]
)

print(response.choices[0].message.content)
print(f"\nCitations: {len(response.citations)} sources")
for i, citation in enumerate(response.citations[:5], 1):
    print(f"{i}. {citation}")
```

**Output**:
```
CRISPR (Clustered Regularly Interspaced Short Palindromic Repeats) is a revolutionary gene-editing technology...

[Detailed multi-paragraph response]

Citations: 15 sources
1. https://nature.com/crispr-breakthrough-2024
2. https://science.org/gene-editing-ethics
3. https://biotech.com/crispr-commercial
4. https://nih.gov/crispr-research
5. https://cell.com/crispr-applications
```

**Cost**: ~$0.015 per request

---

### Example 3: Logical Analysis with Reasoning (Sonar Reasoning Pro)

```python
from perplexity import Perplexity

client = Perplexity()

response = client.chat.completions.create(
    model="sonar-reasoning-pro",
    messages=[{
        "role": "user",
        "content": """Compare the energy efficiency, cost, and scalability of three renewable energy sources: 
        solar, wind, and geothermal. 
        
        Provide a reasoned analysis of which is most viable for developing countries."""
    }]
)

print(response.choices[0].message.content)
```

**Output**:
```
Let me analyze these three renewable energy sources systematically:

ENERGY EFFICIENCY:
- Solar: 15-22% conversion efficiency...
- Wind: 35-45% conversion efficiency...
- Geothermal: 10-15% conversion efficiency...

[Step-by-step reasoning through each criterion]

CONCLUSION FOR DEVELOPING COUNTRIES:
Based on the analysis, solar energy emerges as the most viable option because...
```

**Cost**: ~$0.025 per request

---

### Example 4: Autonomous Deep Research Report (Sonar Deep Research)

```python
from perplexity import Perplexity

client = Perplexity()

# This will take 2-5 minutes to complete
response = client.chat.completions.create(
    model="sonar-deep-research",
    messages=[{
        "role": "user",
        "content": "Conduct a comprehensive market analysis of the electric vehicle battery industry, including supply chain dynamics, key players, technological innovations, market size projections through 2030, and geopolitical factors."
    }]
)

report = response.choices[0].message.content
citations = response.citations

print(f"Generated report: {len(report)} characters")
print(f"Sources analyzed: {len(citations)}")
print(f"\n{report}")
```

**Output**:
```
Generated report: 15,000 characters
Sources analyzed: 127

# COMPREHENSIVE MARKET ANALYSIS: ELECTRIC VEHICLE BATTERY INDUSTRY

## Executive Summary
The global EV battery market is projected to reach $250 billion by 2030...

[Extensive multi-section report with deep analysis]

## Supply Chain Dynamics
...

## Key Players
...

## Technological Innovations
...

[etc.]
```

**Cost**: ~$0.50-$2.00 per request

---

### Example 5: Multi-Query Batch Search

```python
from perplexity import Perplexity

client = Perplexity()

# Search API with multiple queries
queries = [
    "quantum computing commercialization 2024",
    "quantum computing hardware challenges",
    "quantum computing software ecosystem"
]

search = client.search.create(
    query=queries,
    max_results=5,
    max_tokens_per_page=1024
)

# Results are grouped by query
for i, query_results in enumerate(search.results):
    print(f"\n{'='*60}")
    print(f"QUERY {i+1}: {queries[i]}")
    print('='*60)
    
    for result in query_results:
        print(f"\n📄 {result.title}")
        print(f"🔗 {result.url}")
        print(f"📅 {result.date}")
        print(f"📝 {result.snippet[:200]}...")
```

**Output**:
```
============================================================
QUERY 1: quantum computing commercialization 2024
============================================================

📄 IBM Announces Commercial Quantum System
🔗 https://ibm.com/quantum-commercial
📅 2024-11-15
📝 IBM has launched its first commercial quantum computing system available to enterprises...

[Additional results]

============================================================
QUERY 2: quantum computing hardware challenges
============================================================

📄 Overcoming Quantum Error Rates
🔗 https://nature.com/quantum-errors
📅 2024-10-20
📝 Researchers have identified key challenges in quantum hardware stability...

[etc.]
```

---

### Example 6: Domain-Filtered Academic Research

```python
from perplexity import Perplexity

client = Perplexity()

# Restrict search to academic sources
search = client.search.create(
    query="neuroplasticity and learning mechanisms",
    max_results=10,
    search_domain_filter=[
        "pubmed.ncbi.nlm.nih.gov",
        "science.org",
        "nature.com",
        "cell.com",
        "pnas.org"
    ],
    search_recency_filter="year",  # Last year only
    max_tokens_per_page=2048  # More content per result
)

print(f"Found {len(search.results)} peer-reviewed sources:\n")

for result in search.results:
    print(f"📚 {result.title}")
    print(f"   {result.url}")
    print(f"   Published: {result.date}")
    print(f"   {result.snippet[:150]}...\n")
```

**Output**:
```
Found 10 peer-reviewed sources:

📚 Molecular Mechanisms of Neuroplasticity in Adult Learning
   https://nature.com/articles/neuro-2024-1234
   Published: 2024-09-15
   Recent studies have identified key molecular pathways that facilitate synaptic plasticity during adult learning processes...

[Additional academic sources]
```

---

### Example 7: Regional Search with Country Filter

```python
from perplexity import Perplexity

client = Perplexity()

countries = ["US", "GB", "DE", "JP"]
query = "renewable energy policy incentives"

for country in countries:
    print(f"\n{'='*60}")
    print(f"REGION: {country}")
    print('='*60)
    
    search = client.search.create(
        query=query,
        country=country,
        max_results=3
    )
    
    for result in search.results:
        print(f"  • {result.title}")
        print(f"    {result.url}\n")
```

**Output**:
```
============================================================
REGION: US
============================================================
  • IRA Tax Credits for Renewable Energy 2024
    https://irs.gov/renewable-credits

  • Federal Renewable Energy Incentives
    https://energy.gov/incentives

============================================================
REGION: GB
============================================================
  • UK Green Energy Subsidies 2024
    https://gov.uk/green-subsidies

[etc.]
```

---

### Example 8: Streaming Response for Real-Time Display

```python
from perplexity import Perplexity

client = Perplexity()

print("Streaming response:\n")

stream = client.chat.completions.create(
    model="sonar-pro",
    messages=[{
        "role": "user",
        "content": "Explain the process of photosynthesis in plants"
    }],
    stream=True
)

full_content = ""
citations = []

for chunk in stream:
    if chunk.choices[0].delta.content:
        content_piece = chunk.choices[0].delta.content
        print(content_piece, end='', flush=True)
        full_content += content_piece
    
    # Collect metadata from final chunks
    if hasattr(chunk, 'citations') and chunk.citations:
        citations = chunk.citations
    
    if chunk.choices[0].finish_reason:
        print(f"\n\n📚 Sources: {len(citations)}")
```

**Output**:
```
Streaming response:

Photosynthesis is the process by which plants convert light energy into chemical energy... [content appears character by character in real-time]

📚 Sources: 8
```

---

### Example 9: Error Handling with Exponential Backoff

```python
import time
import random
from perplexity import Perplexity
import perplexity

def research_with_retry(query, model="sonar-pro", max_retries=3):
    client = Perplexity()
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": query}]
            )
            return response
            
        except perplexity.RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            print(f"⚠️ Rate limited. Retrying in {delay:.2f}s...")
            time.sleep(delay)
            
        except perplexity.APIConnectionError as e:
            if attempt == max_retries - 1:
                raise
            
            delay = 1 + random.uniform(0, 1)
            print(f"⚠️ Connection error. Retrying in {delay:.2f}s...")
            time.sleep(delay)
            
        except perplexity.AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            print("Check your PERPLEXITY_API_KEY environment variable")
            raise
            
        except perplexity.APIStatusError as e:
            print(f"❌ API Error {e.status_code}: {e.message}")
            raise

# Usage
try:
    result = research_with_retry("What is artificial intelligence?")
    print(result.choices[0].message.content)
except Exception as e:
    print(f"Failed after retries: {e}")
```

---

### Example 10: Async Batch Processing for Maximum Throughput

```python
import asyncio
from perplexity import AsyncPerplexity

async def batch_research(queries, model="sonar-pro", max_concurrent=3):
    """Process multiple queries with controlled concurrency"""
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_query(client, query):
        async with semaphore:
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": query}]
                )
                return {
                    "query": query,
                    "success": True,
                    "content": response.choices[0].message.content,
                    "citations": response.citations
                }
            except Exception as e:
                return {
                    "query": query,
                    "success": False,
                    "error": str(e)
                }
    
    async with AsyncPerplexity() as client:
        tasks = [process_query(client, q) for q in queries]
        results = await asyncio.gather(*tasks)
    
    return results

# Usage
async def main():
    queries = [
        "Latest developments in AI",
        "Climate change solutions 2024",
        "Quantum computing breakthroughs",
        "Renewable energy trends",
        "Space exploration updates"
    ]
    
    print(f"Processing {len(queries)} queries with max 3 concurrent...")
    results = await batch_research(queries, max_concurrent=3)
    
    successful = sum(1 for r in results if r["success"])
    print(f"\n✅ Completed: {successful}/{len(queries)}")
    
    for result in results:
        if result["success"]:
            print(f"\n📌 {result['query']}")
            print(f"   Citations: {len(result['citations'])}")
            print(f"   Preview: {result['content'][:100]}...")

asyncio.run(main())
```

**Output**:
```
Processing 5 queries with max 3 concurrent...

✅ Completed: 5/5

📌 Latest developments in AI
   Citations: 12
   Preview: Recent advances in artificial intelligence include breakthrough developments in large language mod...

[Additional results]
```

---

## Rate Limits & Cost Optimization

### Rate Limits by Model

| Model | Requests Per Minute | Requests Per Second | Burst Capacity |
|-------|-------------------|-------------------|----------------|
| sonar | 50 | 0.83 | 50 |
| sonar-pro | 50 | 0.83 | 50 |
| sonar-reasoning | 50 | 0.83 | 50 |
| sonar-reasoning-pro | 50 | 0.83 | 50 |
| sonar-deep-research | 5 | 0.083 | 5 |
| Search API | 180/min (3/sec) | 3 | 3 |

### Rate Limit Behavior (Leaky Bucket Algorithm)

**Example: Search API (3 QPS)**

```
Time 0.0s: Bucket full (3 tokens)
  → Send 3 requests instantly → ALL ALLOWED ✅
  → Send 4th request → REJECTED ❌ (bucket empty)

Time 0.333s: 1 token refilled
  → Send 1 request → ALLOWED ✅

Time 0.666s: 1 more token refilled
  → Send 1 request → ALLOWED ✅
```

**Recovery Times**:
- 3 QPS limit: 1 token refills every 333ms
- 50 QPS limit: 1 token refills every 20ms
- 500 QPS limit: 1 token refills every 2ms

---

### Cost Optimization Strategies

#### 1. Choose the Right Model

```python
# Cost comparison for same query
query = "What is machine learning?"

# Option 1: Sonar (cheapest)
# Input: $1/1M tokens, Output: $1/1M tokens, Request: $5-12
# Total: ~$0.005

# Option 2: Sonar Pro (moderate)
# Input: $3/1M tokens, Output: $15/1M tokens, Request: $14-24
# Total: ~$0.020

# Option 3: Sonar Deep Research (expensive)
# Performs dozens of searches, reads hundreds of sources
# Total: ~$0.50-$2.00

# Rule: Use simplest model that meets requirements
```

#### 2. Optimize max_results

```python
from perplexity import Perplexity

client = Perplexity()

# ❌ Over-requesting (wastes money)
search = client.search.create(
    query="AI news",
    max_results=20  # Requesting more than needed
)

# ✅ Request only what you need
search = client.search.create(
    query="AI news",
    max_results=5  # Sufficient for most use cases
)
```

#### 3. Control max_tokens_per_page

```python
# ❌ Retrieving full content (expensive)
search = client.search.create(
    query="research paper",
    max_tokens_per_page=4096  # Full page content
)

# ✅ Retrieve only necessary snippets
search = client.search.create(
    query="research paper",
    max_tokens_per_page=512  # Just enough for context
)
```

#### 4. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_research(query):
    client = Perplexity()
    response = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": query}]
    )
    return response.choices[0].message.content

# First call: hits API
result1 = cached_research("What is Python?")

# Second call: uses cache (free!)
result2 = cached_research("What is Python?")
```

#### 5. Use Multi-Query for Efficiency

```python
# ❌ Sequential single queries (5 API calls)
queries = ["AI", "ML", "DL", "NLP", "CV"]
for q in queries:
    search = client.search.create(query=q)

# ✅ Multi-query batch (1 API call)
search = client.search.create(
    query=["AI", "ML", "DL", "NLP", "CV"]
)
# Saves 80% on API calls!
```

#### 6. Set Appropriate max_tokens Budget

```python
# ❌ Default (may be excessive)
search = client.search.create(
    query="example",
    max_tokens=25000  # Default
)

# ✅ Set budget based on needs
search = client.search.create(
    query="example",
    max_tokens=5000  # Sufficient for most summaries
)
```

---

### Cost Estimation Example

```python
def estimate_cost(model, prompt_tokens, completion_tokens, search_context="medium"):
    """Estimate API call cost"""
    
    # Token costs
    costs = {
        "sonar": {"input": 1, "output": 1},
        "sonar-pro": {"input": 3, "output": 15},
        "sonar-reasoning": {"input": 3, "output": 15},
        "sonar-reasoning-pro": {"input": 3, "output": 15},
    }
    
    # Search context costs (per 1000 requests)
    search_costs = {
        "low": 5,
        "medium": 8,
        "high": 12
    }
    
    # Calculate token cost
    input_cost = (prompt_tokens / 1_000_000) * costs[model]["input"]
    output_cost = (completion_tokens / 1_000_000) * costs[model]["output"]
    search_cost = search_costs.get(search_context, 8) / 1000
    
    total = input_cost + output_cost + search_cost
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "search_cost": search_cost,
        "total": total
    }

# Example
cost = estimate_cost(
    model="sonar-pro",
    prompt_tokens=100,
    completion_tokens=500,
    search_context="medium"
)

print(f"Estimated cost: ${cost['total']:.4f}")
# Output: Estimated cost: $0.0153
```

---

## Error Handling & Recovery

### Common Error Types

```python
import perplexity

# 1. APIConnectionError - Network issues
try:
    response = client.chat.completions.create(...)
except perplexity.APIConnectionError as e:
    print(f"Network error: {e.__cause__}")
    # Retry with exponential backoff

# 2. RateLimitError - Rate limit exceeded
except perplexity.RateLimitError as e:
    print(f"Rate limited: {e}")
    # Wait and retry

# 3. AuthenticationError - Invalid API key
except perplexity.AuthenticationError as e:
    print(f"Auth failed: {e}")
    # Check API key

# 4. ValidationError - Invalid parameters
except perplexity.ValidationError as e:
    print(f"Invalid parameters: {e}")
    # Fix request parameters

# 5. APIStatusError - HTTP errors (4xx, 5xx)
except perplexity.APIStatusError as e:
    print(f"API error {e.status_code}: {e.message}")
    # Handle specific status codes
```

### Comprehensive Error Handler

```python
import time
import random
import logging
from perplexity import Perplexity
import perplexity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResilientPerplexityClient:
    def __init__(self, max_retries=3):
        self.client = Perplexity()
        self.max_retries = max_retries
    
    def execute_with_retry(self, model, messages, **kwargs):
        """Execute request with automatic retry and error handling"""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    **kwargs
                )
                return {
                    "success": True,
                    "response": response,
                    "attempt": attempt + 1
                }
                
            except perplexity.RateLimitError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Rate limit exceeded after {self.max_retries} attempts")
                    return {"success": False, "error": "rate_limit", "details": str(e)}
                
                # Exponential backoff with jitter
                delay = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited. Retrying in {delay:.2f}s... (attempt {attempt + 1})")
                time.sleep(delay)
                
            except perplexity.APIConnectionError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Connection failed after {self.max_retries} attempts")
                    return {"success": False, "error": "connection", "details": str(e)}
                
                delay = 1 + random.uniform(0, 1)
                logger.warning(f"Connection error. Retrying in {delay:.2f}s...")
                time.sleep(delay)
                
            except perplexity.AuthenticationError as e:
                logger.error("Authentication failed. Check API key.")
                return {"success": False, "error": "auth", "details": str(e)}
                
            except perplexity.ValidationError as e:
                logger.error(f"Validation error: {e}")
                return {"success": False, "error": "validation", "details": str(e)}
                
            except perplexity.APIStatusError as e:
                logger.error(f"API error {e.status_code}: {e.message}")
                
                # Handle specific status codes
                if e.status_code == 429:
                    # Rate limit (shouldn't happen if caught above, but just in case)
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                
                return {"success": False, "error": f"status_{e.status_code}", "details": str(e)}
                
            except Exception as e:
                logger.error(f"Unexpected error: {type(e).__name__}: {e}")
                return {"success": False, "error": "unexpected", "details": str(e)}
        
        return {"success": False, "error": "max_retries_exceeded"}

# Usage
client = ResilientPerplexityClient(max_retries=3)

result = client.execute_with_retry(
    model="sonar-pro",
    messages=[{"role": "user", "content": "What is AI?"}]
)

if result["success"]:
    print(f"✅ Success (attempt {result['attempt']})")
    print(result["response"].choices[0].message.content)
else:
    print(f"❌ Failed: {result['error']}")
    print(f"Details: {result['details']}")
```

---

## Advanced Patterns

### Pattern 1: Progressive Enhancement Research

Start with fast model, progressively enhance if needed.

```python
from perplexity import Perplexity

def progressive_research(query):
    client = Perplexity()
    
    # Stage 1: Quick overview (Sonar)
    print("🔍 Stage 1: Quick overview...")
    overview = client.chat.completions.create(
        model="sonar",
        messages=[{"role": "user", "content": query}]
    )
    
    content = overview.choices[0].message.content
    
    # Stage 2: Assess if more depth needed
    assessment = client.chat.completions.create(
        model="sonar-reasoning",
        messages=[{
            "role": "user",
            "content": f"""Assess if this answer is comprehensive enough for: "{query}"
            
            ANSWER:
            {content}
            
            Respond with:
            - SUFFICIENT: if answer is complete
            - NEEDS_MORE: if answer needs more depth/sources
            - NEEDS_REASONING: if answer needs logical analysis"""
        }]
    )
    
    assessment_text = assessment.choices[0].message.content.strip()
    
    # Stage 3: Enhance if needed
    if "NEEDS_MORE" in assessment_text:
        print("📚 Stage 2: Deep research...")
        enhanced = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": query}]
        )
        return enhanced.choices[0].message.content
    
    elif "NEEDS_REASONING" in assessment_text:
        print("🧠 Stage 2: Reasoning analysis...")
        enhanced = client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=[{"role": "user", "content": query}]
        )
        return enhanced.choices[0].message.content
    
    else:
        print("✅ Initial answer sufficient")
        return content

# Usage
result = progressive_research("Explain blockchain technology")
print(result)
```

---

### Pattern 2: Fact-Checking with Cross-Validation

Validate research findings across multiple sources.

```python
from perplexity import Perplexity

def fact_check_research(claim):
    client = Perplexity()
    
    # Step 1: Research the claim
    research = client.chat.completions.create(
        model="sonar-pro",
        messages=[{"role": "user", "content": f"Research this claim: {claim}"}]
    )
    
    findings = research.choices[0].message.content
    sources = research.citations
    
    # Step 2: Cross-validate with different search angles
    validation_queries = [
        f"Evidence supporting: {claim}",
        f"Evidence against: {claim}",
        f"Scientific consensus on: {claim}"
    ]
    
    validations = []
    for query in validation_queries:
        result = client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": query}]
        )
        validations.append(result.choices[0].message.content)
    
    # Step 3: Synthesize fact-check report
    synthesis = client.chat.completions.create(
        model="sonar-reasoning-pro",
        messages=[{
            "role": "user",
            "content": f"""Fact-check this claim: "{claim}"
            
            INITIAL RESEARCH:
            {findings}
            
            SUPPORTING EVIDENCE:
            {validations[0]}
            
            CONTRADICTING EVIDENCE:
            {validations[1]}
            
            SCIENTIFIC CONSENSUS:
            {validations[2]}
            
            Provide:
            - Verdict: TRUE / PARTIALLY TRUE / FALSE / UNVERIFIABLE
            - Confidence: 0-100%
            - Explanation
            - Key sources used"""
        }]
    )
    
    return {
        "claim": claim,
        "verdict": synthesis.choices[0].message.content,
        "total_sources": len(sources) + sum(len(v.citations) for v in validations)
    }

# Usage
result = fact_check_research("Coffee improves cognitive performance")
print(result["verdict"])
print(f"\nSources analyzed: {result['total_sources']}")
```

---

### Pattern 3: Continuous Learning Agent

Agent that builds knowledge over time.

```python
from perplexity import Perplexity
import json

class LearningAgent:
    def __init__(self):
        self.client = Perplexity()
        self.knowledge_base = {}
        self.research_history = []
    
    def research_and_learn(self, topic):
        """Research a topic and add to knowledge base"""
        
        # Check if already know about topic
        if topic in self.knowledge_base:
            print(f"📚 Found existing knowledge on: {topic}")
            return self.knowledge_base[topic]
        
        # Research the topic
        print(f"🔍 Learning about: {topic}")
        response = self.client.chat.completions.create(
            model="sonar-pro",
            messages=[{
                "role": "user",
                "content": f"Provide a comprehensive overview of: {topic}"
            }]
        )
        
        knowledge = {
            "topic": topic,
            "content": response.choices[0].message.content,
            "citations": response.citations,
            "timestamp": time.time()
        }
        
        # Store in knowledge base
        self.knowledge_base[topic] = knowledge
        self.research_history.append(topic)
        
        return knowledge
    
    def answer_with_context(self, question):
        """Answer question using accumulated knowledge"""
        
        # Identify relevant topics from knowledge base
        relevant_topics = [
            topic for topic in self.knowledge_base.keys()
            if any(word in question.lower() for word in topic.lower().split())
        ]
        
        # Build context from knowledge base
        context = "\n\n".join([
            f"KNOWN: {self.knowledge_base[topic]['content']}"
            for topic in relevant_topics
        ])
        
        # Answer with context
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Use this background knowledge:\n\n{context}"
            })
        
        messages.append({
            "role": "user",
            "content": question
        })
        
        response = self.client.chat.completions.create(
            model="sonar-reasoning-pro",
            messages=messages
        )
        
        return {
            "answer": response.choices[0].message.content,
            "used_knowledge": relevant_topics,
            "new_citations": response.citations
        }
    
    def save_knowledge(self, filename="knowledge_base.json"):
        """Persist knowledge to disk"""
        with open(filename, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def load_knowledge(self, filename="knowledge_base.json"):
        """Load knowledge from disk"""
        with open(filename, 'r') as f:
            self.knowledge_base = json.load(f)

# Usage
agent = LearningAgent()

# Learn about topics
agent.research_and_learn("machine learning")
agent.research_and_learn("neural networks")
agent.research_and_learn("deep learning")

# Answer questions using learned knowledge
result = agent.answer_with_context(
    "How do neural networks relate to deep learning?"
)

print(result["answer"])
print(f"\nUsed knowledge: {result['used_knowledge']}")

# Save for future use
agent.save_knowledge()
```

---

## Conclusion

This guide provides a comprehensive foundation for building semi-autonomous research agents with Perplexity's API. Key takeaways:

### ✅ Best Practices Summary

1. **Choose the right model**: Match model capabilities to query complexity
2. **Implement rate limiting**: Use token bucket algorithm to respect limits
3. **Cache aggressively**: Avoid redundant API calls
4. **Batch requests**: Use async operations for maximum throughput
5. **Handle errors gracefully**: Implement exponential backoff
6. **Monitor costs**: Track token usage and optimize model selection
7. **Leverage multi-query**: Batch related searches for efficiency
8. **Use domain filtering**: Focus searches on authoritative sources
9. **Stream responses**: Provide real-time feedback to users
10. **Validate findings**: Cross-check critical research with multiple sources

### 🚀 Scaling to Maximum Autonomy

- **Multi-agent architectures**: Parallel research with specialized agents
- **Progressive enhancement**: Start fast, enhance as needed
- **Continuous learning**: Build persistent knowledge bases
- **Quality control loops**: Automated validation of research depth
- **Intelligent routing**: Automatic model selection based on complexity

### 📊 Cost vs. Autonomy Trade-offs

| Autonomy Level | Models Used | Cost/Query | Manual Labor |
|----------------|-------------|------------|--------------|
| Low | Sonar | $0.005 | High |
| Medium | Sonar Pro | $0.02 | Medium |
| High | Sonar Reasoning Pro | $0.03 | Low |
| Maximum | Sonar Deep Research | $0.50-$2 | Minimal |

### 🔗 Resources

- **API Documentation**: https://docs.perplexity.ai
- **Support**: api@perplexity.ai
- **Rate Limit Increases**: https://docs.perplexity.ai/guides/rate-limits-usage-tiers
- **Python SDK**: `pip install perplexity`

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Author**: Perplexity API Research Team