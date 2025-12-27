
# Create the mermaid diagram for the 5-stage Deep Research workflow
diagram_code = """
flowchart TD
    A["<b>Stage 1: Landscape Mapping</b><br/>Duration: 3-5 hrs<br/>Objective: Establish boundaries, identify ecosystems<br/>Sources: 50-80<br/>Deliverable: Thematic map, institution list<br/>QA: Coverage & completeness check"]
    
    B{{"Quality Gate 1:<br/>Scope validated?"}}
    
    C["<b>Stage 2: Vertical Deep-Dives</b><br/>Duration: 4-6 hrs<br/>Objective: Analyze 3-5 themes with detail<br/>Sources: 90-150<br/>Deliverable: Comparison matrices, methodology inventory<br/>QA: Depth & rigor assessment"]
    
    D{{"Quality Gate 2:<br/>Analysis sufficient?"}}
    
    E["<b>Stage 3: Comparative Architecture Analysis</b><br/>Duration: 3-5 hrs<br/>Objective: Compare architectures & implementations<br/>Sources: 50-80<br/>Deliverable: Architecture diagrams, performance tables<br/>QA: Consistency validation"]
    
    F{{"Quality Gate 3:<br/>Patterns identified?"}}
    
    G["<b>Stage 4: Gap Identification & Research Frontiers</b><br/>Duration: 3-4 hrs<br/>Objective: Identify research gaps & frontiers<br/>Sources: 30-40<br/>Deliverable: Gap analysis report, hypothesis candidates<br/>QA: Novelty & relevance check"]
    
    H{{"Quality Gate 4:<br/>Gaps validated?"}}
    
    I["<b>Stage 5: Hypothesis Generation & Validation</b><br/>Duration: 2-3 hrs<br/>Objective: Generate testable hypotheses<br/>Sources: 40-60<br/>Deliverable: Validation matrix, research roadmap<br/>QA: Testability verification"]
    
    J["<b>Complete Literature Review</b><br/>Total Sources: 150-200<br/>Total Time: 15-23 hrs<br/>(vs 60-100 hrs traditional)"]
    
    A --> B
    B -->|Pass| C
    C --> D
    D -->|Pass| E
    E --> F
    F -->|Pass| G
    G --> H
    H -->|Pass| I
    I --> J
"""

# Use the provided helper function to create the diagram
create_mermaid_diagram(diagram_code, 'deep_research_workflow.png', 'deep_research_workflow.svg')
