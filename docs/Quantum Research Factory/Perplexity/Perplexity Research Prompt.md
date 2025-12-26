role: system
content: >
You are an academic AI research assistant. You conduct multi-step, source-based
research and write rigorous, well-structured reports suitable for
graduate-level work. Clearly separate source-backed claims from your own
integrative reasoning and avoid plagiarism.

---

role: user
content:
task_description: >
Generate an academic research report on the following AI topic:
[AI OS Layers].

research_objectives:
- Define and distinguish the key concepts and terminology relevant to the topic.
- Identify and summarize major theoretical frameworks, models, or approaches
in this AI area.
- Describe how these frameworks conceptualize the central phenomena or tasks
of interest.
- Review empirical methods and experimental designs commonly used to study
this AI topic.
- Explain current applications, systems, or use cases and how they implement
or operationalize the identified frameworks.
- Summarize known limitations, open challenges, and risks.
- Propose promising directions for future research and development.

topic_focus:
core_topic: "[AI OS Layers]"
related_terms:
Hardware layer (CPUs/GPUs, memory, storage, network)

Host OS / infrastructure layer (Linux, containers/VMs, orchestration)

AI runtime layer (model runtimes, inference engines, accelerators)

Agent kernel layer (agent scheduler, tool routing, memory, security controls)

Application layer (agents, workflows, plugins, UX/API surfaces)

Governance & observability layer (policies, monitoring, logging, audit, billing)


optional_domain_filters:
- "[AI Autonomous Agent Architecture]"
- "[AI Autonomous Agents]"

literature_scope:
include_types:
- peer-reviewed journal articles
- major conference papers
- scholarly books and chapters
- surveys, systematic reviews, and benchmarks
time_window_preference: >
Emphasize recent work (e.g., last 5–10 years) while including foundational
classic papers where necessary.
quality_criteria:
- clear conceptual or technical contribution to the AI topic
- empirical evaluation or well-argued theoretical analysis
- relevance to the specified core_topic and related_terms

methodological_emphasis:
spotlight_methods:
- "[METHOD_1 e.g., supervised learning experiments, simulations]"
- "[METHOD_2 e.g., user studies, A/B testing, benchmarks]"
- "[METHOD_3 e.g., interpretability analysis, causal evaluation]"
requested_analysis:
- describe each method or experimental paradigm
- explain strengths and weaknesses for studying this AI topic
- note typical datasets, metrics, and evaluation protocols

report_requirements:
target_audience: >
AI researchers, practitioners, and graduate students with general
technical background.
tone_style: formal academic, precise, analytic
length_guidance: "[E.g., approx. 4–6k words or within model limits]"
structure:
- "1. Introduction: problem statement, background, and main research questions."
- "2. Core concepts and terminology."
- "3. Major frameworks, models, or approaches."
- "4. Methods, datasets, and evaluation practices."
- "5. Current applications and systems."
- "6. Limitations, risks, and open challenges."
- "7. Future research directions."
- "8. Brief conclusion summarizing implications."
output_format:
citation_style: "author-year in-text, approximate APA if possible"
formatting: "use headings and bullets; tables only if clearly needed"
constraints: >
Do not reproduce copyrighted text; paraphrase and synthesize
source ideas.

reasoning_requirements:
depth: high
expectations:
- compare and contrast major approaches, noting overlaps and tensions
- make reasoning steps and assumptions explicit
- flag speculative or forward-looking claims as conjectural

customization_placeholders:
specific_use_case: "[OPTIONAL: narrow to a specific application, e.g., AI in healthcare diagnostics]"
population_or_context: "[OPTIONAL: user group, domain, or deployment context]"
max_token_or_length_budget: "[Set according to your API/model limits]"
