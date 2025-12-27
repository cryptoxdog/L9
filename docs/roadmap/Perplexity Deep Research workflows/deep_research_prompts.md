# Quick Start Guide: Deep Research Prompts for AI OS & Autonomous Agents

## Overview

This document provides immediately actionable prompts optimized for Perplexity Deep Research Labs mode to conduct comprehensive literature reviews on AI Operating Systems and autonomous agents. Copy-paste these prompts directly into Perplexity for fastest results.

---

## Pre-Research Checklist

Before beginning, prepare:
- [ ] Perplexity Pro subscription with Deep Research access
- [ ] Research objective clearly defined (what decision does this review inform?)
- [ ] Time allocation: 52-67 hours over 3-4 weeks
- [ ] Tools ready: Zotero/Mendeley for reference management, spreadsheet for data extraction
- [ ] Notification system setup (calendar reminders for each stage)

---

## STAGE 1: LANDSCAPE MAPPING (Copy-Paste Prompt)

### Primary Prompt

```
You are a senior AI systems researcher conducting a comprehensive literature review 
of AI Operating Systems and autonomous agent architectures from 2020-2025. Your 
objective is to map the complete landscape of this research domain to understand 
its scope, key players, and evolution.

TASK: Conduct an exhaustive landscape mapping of the AI OS and autonomous agents 
research domain from 2020-2025. Return a structured report with:

1. RESEARCH EVOLUTION (500+ words)
   - Major milestones and paradigm shifts (2020 → 2025)
   - Timeline of key innovations and when they emerged
   - How the field's focus has shifted over 5 years

2. MAJOR FRAMEWORKS AND ARCHITECTURES (list all distinct approaches)
   - Single-agent reasoning patterns (ReAct, Tree-of-Thought, Graph-of-Thought, etc.)
   - Multi-agent coordination models (hierarchical, peer-to-peer, swarm, etc.)
   - AI OS architectural approaches (AIOS, CosmOS, custom enterprise solutions, etc.)
   - For each: originating paper, current implementations, key differentiators

3. LEADING RESEARCH INSTITUTIONS AND LABS
   - Top 20-30 research groups publishing in this space
   - Their key focus areas and contributions
   - Notable papers from each group
   - Geographic distribution of research

4. TOP PUBLICATION VENUES
   - Which conferences dominate? (NeurIPS, ICML, ICLR, AAAI, etc.)
   - Which journals are key? (Nature MI, JMLR, TPAMI, etc.)
   - Preprint servers (arXiv sections)
   - Industry research blogs (OpenAI, Anthropic, Google DeepMind, etc.)

5. FUNDING SOURCES AND RESEARCH INITIATIVES
   - DARPA programs related to AI agents
   - NSF funding initiatives
   - Corporate research funding (Microsoft, Google, Meta, OpenAI)
   - Startup funding trends

6. MARKET AND ADOPTION LANDSCAPE
   - Current market size estimates for AI agent platforms
   - Industry adoption rates and use cases
   - Key commercial systems and their market share
   - Barriers to adoption

7. RESEARCH GAPS IDENTIFIED IN SURVEYS AND REVIEWS
   - Which problems do researchers explicitly identify as unsolved?
   - What are the admitted limitations of current approaches?

DELIVERABLES:
- 50+ unique, high-quality sources with full citations
- Organized by thematic category with cross-references
- Identified list of 20-30 leading research institutions
- Ranking of top publication venues by relevance
- Timeline visualization of field evolution (describe in text)
- Initial identification of 3-5 emerging themes for deeper investigation

QUALITY CRITERIA:
- Source diversity: Mix of conferences (40%), journals (40%), arXiv (15%), industry (5%)
- Temporal distribution: Prioritize 2023-2025 (50%), include 2020-2022 foundations (40%), 
  older seminal work (10%)
- Geographic diversity: Represent research from 10+ countries
- Citation credibility: Prefer papers with 10+ citations or from known researchers

CITE YOUR SOURCES: Include full citations in APA format for all referenced papers.
After completing this initial mapping, identify the 5 most promising areas for 
deeper investigation in Stage 2.
```

### Follow-Up Prompt (if gaps identified)

```
Based on your landscape mapping, I notice gaps in [specific area]. Conduct targeted 
follow-up research on:
1. [Specific gap 1 - e.g., "Agent-to-agent communication protocols from 2025"]
2. [Specific gap 2 - e.g., "Enterprise AI OS deployments"]
3. [Specific gap 3 - e.g., "Safety mechanisms for autonomous agents"]

For each area, find 5-10 recent papers (2024-2025) and provide:
- Citation details
- Key finding summary (100 words)
- How it addresses the gap
- Relevance to overall research question
```

---

## STAGE 2: VERTICAL DEEP-DIVES (Copy-Paste Prompt)

### Primary Prompt

```
Based on the landscape mapping from Stage 1, I want to conduct intensive technical 
analysis of the 3 most promising research areas. For each area below, analyze 
30-50 recent papers to understand the current state of art, key technical approaches, 
and open challenges.

RESEARCH AREAS TO ANALYZE:
[Area 1: from Stage 1 results]
[Area 2: from Stage 1 results]
[Area 3: from Stage 1 results]

FOR EACH RESEARCH AREA, PROVIDE:

1. TECHNICAL FOUNDATIONS (200+ words)
   - Core concepts and definitions
   - How this area connects to broader AI OS/agent research
   - Key innovations that advanced the field
   - Current theoretical frameworks

2. METHODOLOGICAL APPROACHES (300+ words)
   - What research methodologies dominate this area?
   - How do researchers evaluate solutions?
   - What metrics and benchmarks are standard?
   - What are the limitations of current evaluation approaches?

3. PERFORMANCE METRICS AND COMPARISONS
   - Identify the 3-5 most important performance metrics
   - Create comparison table showing top systems' performance
   - Explain what the metrics mean and why they matter
   - Note any inconsistencies in how metrics are reported

4. LEADING SYSTEMS AND IMPLEMENTATIONS
   - Top 5-8 implementations or frameworks in this area
   - Key papers describing each implementation
   - Notable benchmarks or case studies
   - Comparative strengths and limitations

5. RESEARCH COMMUNITIES AND KEY PLAYERS
   - Which institutions lead work in this area?
   - Major research groups and their focus areas
   - Key researchers and their contributions
   - Geographic distribution of research effort

6. CURRENT LIMITATIONS AND CHALLENGES
   - Which technical problems remain unsolved?
   - What are the acknowledged limitations of current approaches?
   - Where does theory exceed or fall short of practice?
   - Which assumptions limit generalizability?

7. EMERGING DIRECTIONS AND FUTURE WORK
   - What papers explicitly identify future research directions?
   - Which preliminary or early-stage ideas show promise?
   - What interdisciplinary connections could advance the field?
   - What standardization efforts are underway?

DELIVERABLES FOR EACH AREA:
- 30-50 unique sources with full citations
- Structured technical summary (500+ words)
- Performance comparison table (if applicable)
- Methodology assessment with strengths/limitations
- Identified sub-areas ready for Stage 3 analysis

OVERALL DELIVERABLE:
- Comprehensive analysis spanning all 3 areas (2000+ words total)
- Cross-references between areas showing how they interconnect
- Preliminary gap analysis: Which topics need deeper investigation?
- List of 5-8 candidate systems/approaches for Stage 3 comparison

CITATION REQUIREMENTS: Full citations (APA format) for all referenced papers. 
After this analysis, you should be ready to identify specific frameworks/systems 
for detailed comparative analysis in Stage 3.
```

### Follow-Up Prompts

```
FOLLOW-UP 1 - Performance Validation:
"For the performance metrics you listed in [Area X], I want verification. 
Search for papers that compare these metrics directly or discuss reliability of 
these metrics. Are there controversies about how to properly measure [metric]? 
Cite specific papers discussing metric reliability."

FOLLOW-UP 2 - Methodology Deep-Dive:
"The research in [Area X] uses methodology [Y]. Find 5-10 papers exemplifying 
this methodology. What are its strengths? Its limitations? What are researchers 
saying about improving this methodology? Provide specific quotes from papers."

FOLLOW-UP 3 - Emerging Technologies:
"Which papers from 2024-2025 in [Area X] propose fundamentally new approaches? 
Find 10-15 papers representing preliminary or novel work. What makes these novel? 
What are researchers saying about their potential?"
```

---

## STAGE 3: COMPARATIVE ARCHITECTURE ANALYSIS (Copy-Paste Prompt)

### Primary Prompt

```
Create a detailed comparative analysis of the leading AI agent frameworks and 
AI OS architectures. This analysis will help practitioners select appropriate 
technology for specific use cases.

SYSTEMS TO COMPARE:
[Top 5-8 systems identified in Stages 1-2]

For EACH SYSTEM, extract and analyze:

1. ARCHITECTURE DESIGN (300+ words per system)
   - Core orchestration mechanism (how does it coordinate agents/components?)
   - Agent model (how are individual agents designed and reasoned?)
   - Communication approach (how do agents communicate?)
   - Memory/context management strategy
   - Data flow and control flow patterns
   - Stateful vs. stateless design choices

2. TECHNICAL IMPLEMENTATION
   - Primary technology stack (LLMs, frameworks, languages)
   - LLM compatibility and requirements
   - Reasoning mechanisms employed (ReAct, CoT, search, etc.)
   - Tool/API integration capabilities
   - Database and storage requirements
   - Deployment architecture (cloud, on-premise, hybrid, edge)

3. PERFORMANCE CHARACTERISTICS
   - Latency profiles (response time, throughput)
   - Resource requirements (compute, memory, storage)
   - Scalability limits (max agents, max concurrent tasks)
   - Cost model (infrastructure, API calls, licensing)
   - Real-world performance data if available

4. PRACTICAL CHARACTERISTICS
   - Learning curve and developer experience
   - Documentation quality and completeness
   - Community size and activity level
   - Open source vs. proprietary
   - Code availability and reproducibility
   - Production deployment maturity

5. COMPARATIVE STRENGTHS AND LIMITATIONS
   - What is each system optimized for?
   - Known limitations and constraints
   - Ideal use cases vs. poor fit scenarios
   - Comparison to competing systems

DELIVERABLES:

1. COMPREHENSIVE COMPARISON TABLES (8-10 dimensions minimum):
   - Create matrix comparing all systems across:
     * Architecture type
     * Multi-agent support capability
     * Memory sophistication
     * Tool integration breadth
     * Deployment flexibility
     * Performance characteristics
     * Enterprise readiness
     * Community maturity
     * Cost profile
     * Ease of use

2. ARCHITECTURAL DIAGRAMS
   - Describe in text the architectural diagrams for top 3 systems
   - Key components and their interactions
   - Data flow patterns

3. DECISION MATRIX
   - For different use cases, which system is recommended?
   - Use case 1 (e.g., "Customer service chatbots") → Best framework
   - Use case 2 (e.g., "Scientific research assistance") → Best framework
   - [5-10 realistic use cases]

4. TRADE-OFF ANALYSIS (500+ words)
   - Performance vs. Simplicity trade-offs
   - Flexibility vs. Ease-of-use trade-offs
   - Cost vs. Capability trade-offs
   - Maturity vs. Bleeding-edge features

5. ROADMAP PROJECTIONS (2-3 years forward)
   - For each system, project likely evolution
   - New capabilities being developed
   - Competitive dynamics in the space
   - Standardization trends (protocols, APIs)

RESEARCH REQUIREMENTS:
- Minimum 50-80 sources focused on implementation and engineering
- Include papers describing each system
- Include benchmark comparisons between systems
- Include practitioner experiences and lessons learned
- Include recent updates (2024-2025) on each system

CITATION STANDARDS:
Full APA citations for all referenced papers and sources.
```

### Follow-Up Prompts

```
FOLLOW-UP 1 - Performance Validation:
"For the performance comparisons you made between [System A] and [System B], 
find papers that directly compare these systems or run identical benchmarks on both. 
What do peer-reviewed comparisons show? Are there any published benchmark studies?"

FOLLOW-UP 2 - Production Deployment Patterns:
"Which organizations are deploying [System X] in production? Find case studies 
or technical blog posts describing: What scale are they operating at? What 
challenges did they encounter? What lessons did they learn? What recommendations 
do they offer others?"

FOLLOW-UP 3 - Technology Roadmap:
"For the leading systems, what are their announced development roadmaps for 
2025-2026? What new capabilities are being developed? Are any protocols or 
standards being adopted? Find official announcements and technical RFCs if available."
```

---

## STAGE 4: GAP ANALYSIS & RESEARCH FRONTIERS (Copy-Paste Prompt)

### Primary Prompt

```
Synthesize your comprehensive analysis from Stages 1-3 to identify critical 
research gaps, unsolved problems, and emerging research frontiers in AI OS 
and autonomous agents research.

TASK: Conduct a meta-analysis of the collected literature to identify:

1. TECHNICAL RESEARCH GAPS (500+ words)
   - Which architectural challenges remain largely unaddressed?
   - What performance bottlenecks persist across all current systems?
   - Which benchmark tasks consistently challenge all systems?
   - Where do theoretical capabilities exceed real-world performance?
   - Which scaling challenges are unsolved?
   - What safety/alignment problems are inadequately addressed?

2. METHODOLOGICAL GAPS AND LIMITATIONS
   - Which evaluation metrics are insufficient or misleading?
   - Are there fundamental disagreements about problem definitions?
   - Which experimental approaches limit generalizability?
   - What assumptions artificially limit applicability to domains?
   - Where is there insufficient standardization?
   - What reproducibility challenges exist?

3. APPLICATION DOMAIN GAPS
   - Which domains are well-studied? (finance, customer service, etc.)
   - Which domains are underexplored?
   - What domain-specific challenges are emerging?
   - Which application areas would benefit most from research?

4. STANDARDIZATION AND INTEROPERABILITY GAPS
   - What standardization efforts are lacking?
   - Which communication protocols need standardization?
   - Are there incompatibilities limiting system composition?
   - What standardization efforts are underway?

5. INTERDISCIPLINARY OPPORTUNITIES
   - Which distributed systems concepts could transfer?
   - What can AI OS design learn from traditional OS architecture?
   - How could cognitive science inform agent design?
   - What MARL insights apply to orchestration?
   - Which microservices patterns apply?

6. RESEARCH FRONTIERS AND EMERGING DIRECTIONS
   - What papers explicitly identify future research directions?
   - Which early-stage ideas show significant promise?
   - What emerging protocols or standards are being proposed?
   - Which problem formulations are new?

DELIVERABLES:

1. COMPREHENSIVE GAP ANALYSIS DOCUMENT (1500+ words)
   - Detailed description of each major gap
   - Evidence citations for each gap (2-5 papers per gap)
   - Why each gap matters (business/research impact)
   - Suggested research approaches to address gap

2. RESEARCH MATURITY HEAT MAP
   - Create matrix: Research topics vs. maturity level (nascent/emerging/mature)
   - Show which areas are well-studied vs. under-studied
   - Identify "white space" opportunities

3. PRIORITY RESEARCH QUESTIONS (8-12 questions)
   - Formulate specific, testable research questions
   - For each question:
     * Why is it important?
     * What evidence suggests it's a real gap? (cite papers)
     * What research approach would answer it?
     * Estimated resource requirements
     * Potential impact if solved
   - Rank by priority (based on field impact + feasibility)

4. CONTRADICTIONS AND DEBATES
   - What topics have researchers who disagree?
   - What are the competing viewpoints?
   - What evidence supports each viewpoint?
   - What would resolve these debates?

5. TIMELINE FOR ADDRESSING GAPS
   - Short-term gaps (solvable in 1-2 years)
   - Medium-term gaps (3-5 years)
   - Long-term challenges (5+ years)

RESEARCH REQUIREMENTS:
- 30-40 sources, concentrated on forward-looking papers
- Include problem statements and limitations discussions
- Include papers proposing novel approaches
- Include any research roadmaps from major labs

QUALITY REQUIREMENTS:
- Every claimed gap must be supported by 2+ independent sources
- Distinguish between gaps researchers identify vs. gaps you infer
- Rate confidence in each gap identification (high/medium/low)
```

### Follow-Up Prompts

```
FOLLOW-UP 1 - Gap Prioritization:
"Among the research gaps you identified, which 5 are most critical? For each, 
estimate: (1) How difficult to solve? (2) What would solving it enable? 
(3) Which research groups are already working on this? (4) What's the 
likelihood of progress in next 2 years?"

FOLLOW-UP 2 - Emerging Standards:
"You mentioned standardization gaps. What standardization efforts are currently 
underway? Find any working groups, RFCs, or proposed standards for: agent 
communication protocols, OS architectures, evaluation benchmarks, safety standards. 
What organizations are leading these efforts?"

FOLLOW-UP 3 - Future Predictions:
"Based on current trends and identified gaps, what are researchers predicting 
for the 2025-2026 research landscape? Find any position papers, opinion pieces, 
or forward-looking surveys. What are the top predictions for the field's evolution?"
```

---

## STAGE 5: HYPOTHESIS GENERATION (Copy-Paste Prompt)

### Primary Prompt

```
Based on comprehensive literature synthesis from Stages 1-4, generate specific, 
testable research hypotheses about critical questions in AI OS and autonomous 
agent research. These hypotheses should address identified research gaps and 
represent high-impact research directions.

TASK: Generate 8-12 specific research hypotheses. For EACH hypothesis:

1. HYPOTHESIS STATEMENT (precise, testable, operational definition)
   - Clearly state what would be true if hypothesis is correct
   - Make it falsifiable

2. SUPPORTING EVIDENCE FROM LITERATURE
   - What specific observations from literature support this hypothesis?
   - Cite 3-5 papers providing evidence
   - What do these papers conclude?

3. THEORETICAL BASIS
   - What theory or prior research suggests this hypothesis?
   - What are the underlying assumptions?
   - What analogous findings support this?

4. EXPERIMENTAL DESIGN (detailed)
   - How would you test this hypothesis?
   - What is the independent variable (what you manipulate)?
   - What is the dependent variable (what you measure)?
   - What controls or baselines are needed?
   - What is the study population/scope?

5. MEASUREMENT AND EVALUATION
   - How specifically would you measure the outcome?
   - What metrics or instruments would you use?
   - How would you ensure measurement validity?
   - What benchmarks or baselines apply?

6. POTENTIAL CONFOUNDING VARIABLES
   - What other factors might influence results?
   - How would you control for them?
   - What threatens internal validity?

7. EXTERNAL VALIDITY AND GENERALIZATION
   - To what populations/contexts would this apply?
   - What limits generalizability?
   - Where else should this be tested?

8. RESOURCE REQUIREMENTS AND TIMELINE
   - Estimated time to conduct study
   - Required computational resources
   - Required expertise and team size
   - Estimated budget

9. POTENTIAL IMPACT
   - If confirmed, what advances would this enable?
   - How would this change practice?
   - What other research would this enable?

10. RELATIONSHIP TO IDENTIFIED GAPS
    - Which research gap(s) does this address?
    - Why is answering this question important?

DELIVERABLES:

1. HYPOTHESIS VALIDATION MATRIX
   - Table with rows = hypotheses, columns = attributes
   - Columns: Hypothesis | Supporting evidence | Testability | Priority | 
             Estimated resources | Impact potential

2. PRIORITIZATION RANKING
   - Rank by: (1) likelihood of solving research gap, 
            (2) feasibility within 2-3 years,
            (3) potential field impact,
            (4) resource efficiency
   - Provide top 3 most promising hypotheses for immediate investigation

3. RESEARCH ROADMAP
   - Suggested sequence for investigating hypotheses
   - Dependencies (which should be tested first?)
   - Parallel vs. sequential investigation
   - Timeline for 2-3 year research program

4. IMPLEMENTATION GUIDE
   - For each top-3 hypothesis:
     * Detailed experimental protocol (could be given to researcher)
     * Code/tools/datasets needed
     * Expected results if hypothesis true vs. false
     * Interpretation guide

CITATION REQUIREMENTS:
- Minimum 40-60 sources, concentrated on specific research areas
- Heavy citation of papers proposing novel approaches
- Include any preliminary/pilot study results
- Include methodology papers relevant to testing these hypotheses
```

### Follow-Up Prompts

```
FOLLOW-UP 1 - Hypothesis Validation:
"For hypothesis [X], I want to find any existing preliminary studies or pilot 
work that has tested related questions. Are there papers that provide initial 
evidence for or against this hypothesis? What do early results suggest?"

FOLLOW-UP 2 - Methodological Feasibility:
"For hypothesis [X], what are the practical challenges in conducting the 
proposed experiment? What have researchers discovered about the difficulties 
in studying this question? Are there any published methodological critiques 
of approaches to testing this?"

FOLLOW-UP 3 - Timeline Estimation:
"Based on examples from the literature, how long did it take prior researchers 
to make progress on similar questions? What timeline should we estimate for 
testing this hypothesis? What are the critical path items?"
```

---

## Best Practices for Using These Prompts

### Tips for Maximum Effectiveness

1. **Run Deep Research for 3-5 minutes per query**: This gives the system time for reasoning
2. **Request source URLs explicitly**: Ask "Include full URLs for verification"
3. **Use numbered lists**: Makes parsing and verification easier
4. **Ask for confidence assessments**: "Rate your confidence in this finding (high/medium/low)"
5. **Request methodology discussion**: "Explain the research methods used in cited papers"
6. **Note contradictions**: "Highlight any contradictory findings or disagreements"
7. **Verify key claims**: "Cross-reference this finding with at least 2 independent sources"

### Quality Assurance During Research

- [ ] After each stage, validate 10% of sources by reading abstracts
- [ ] Track which researchers/institutions appear multiple times (indicates key players)
- [ ] Note any gaps between stages and conduct targeted follow-ups
- [ ] Document all decisions for methodology transparency
- [ ] Create master source list with metadata for final synthesis

### Organization System

**Recommended folder structure**:
```
literature_review_project/
├── stage_1_landscape/
│   ├── prompt_and_response.md
│   ├── extracted_sources.csv
│   └── follow_ups.md
├── stage_2_deep_dives/
│   ├── area_1_analysis.md
│   ├── area_2_analysis.md
│   └── area_3_analysis.md
├── stage_3_comparison/
│   ├── framework_comparison.md
│   ├── performance_tables.csv
│   └── architectural_diagrams.txt
├── stage_4_gaps/
│   ├── gap_analysis.md
│   ├── research_questions.md
│   └── maturity_heatmap.csv
├── stage_5_hypotheses/
│   ├── hypothesis_matrix.csv
│   └── research_roadmap.md
└── final_deliverables/
    ├── annotated_bibliography.md
    ├── synthesis_report.docx
    └── research_database.xlsx
```

---

## Critical Success Factors

1. **Patience with Deep Research**: First response may need follow-ups; iterate for quality
2. **Specific Research Questions**: Vague prompts yield vague results; be precise
3. **Source Verification**: Don't accept first results; verify and cross-check
4. **Citation Management**: Track all sources from start; don't lose track mid-review
5. **Document Everything**: Protocol transparency enables reproducibility
6. **Iterative Refinement**: Each stage builds on previous; adjust focus as patterns emerge

---

## Expected Outcomes by Stage

| Stage | Time | Source Count | Primary Output | Quality Gates |
|-------|------|--------------|-----------------|---------------|
| 1 | 3-5h | 50-80 | Research map | Coverage check |
| 2 | 4-6h | 90-150 | Technical analysis | Methodology review |
| 3 | 3-5h | 50-80 | Framework comparison | Accuracy validation |
| 4 | 3-4h | 30-40 | Gap analysis | Confidence assessment |
| 5 | 2-3h | 40-60 | Hypothesis matrix | Feasibility review |
| **TOTAL** | **15-23h** | **150-200** | **Complete review** | **Full validation** |

---

## Common Questions

**Q: Can I skip stages?**
A: Theoretically yes, but not recommended. Stages 1-2 build foundational knowledge; skipping risks missing important context.

**Q: How often should I do follow-ups?**
A: After each stage, 1-2 targeted follow-ups to fill gaps. More than 2-3 per stage suggests unclear initial prompt.

**Q: What if I find conflicting information?**
A: Document both viewpoints with citations. This is valuable; don't force false consensus.

**Q: How do I cite findings from Deep Research?**
A: Always cite the original papers, not Deep Research. Deep Research is the finding mechanism, not the source.

**Q: Can I reuse these prompts for other topics?**
A: Absolutely! The structure is generic; substitute your specific research domain.

---

**Document Version**: 1.0
**Created**: December 19, 2025
**For**: AI OS and Autonomous Agents Research Community

Copy these prompts into Perplexity Labs and begin your comprehensive literature review journey!
