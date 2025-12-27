
import plotly.graph_objects as go
import pandas as pd
import json

# Load the data
data = {
    "frameworks": [
        {"name": "LangGraph", "learning_curve": 2, "multi_agent": 4, "enterprise": 4, "memory": 4, "deployment": 3, "community": 4, "documentation": 3, "production": 4},
        {"name": "AutoGen", "learning_curve": 3, "multi_agent": 3, "enterprise": 3, "memory": 3, "deployment": 2, "community": 3, "documentation": 2, "production": 2},
        {"name": "CrewAI", "learning_curve": 4, "multi_agent": 4, "enterprise": 3, "memory": 4, "deployment": 2, "community": 3, "documentation": 4, "production": 3},
        {"name": "Semantic Kernel", "learning_curve": 3, "multi_agent": 2, "enterprise": 5, "memory": 3, "deployment": 5, "community": 3, "documentation": 3, "production": 4},
        {"name": "Agno", "learning_curve": 3, "multi_agent": 4, "enterprise": 2, "memory": 3, "deployment": 4, "community": 2, "documentation": 3, "production": 2}
    ],
    "dimensions": [
        "Learning Curve",
        "Multi-Agent",
        "Enterprise",
        "Memory",
        "Deployment",
        "Community",
        "Docs",
        "Production"
    ]
}

# Create matrix for heatmap
framework_names = [f["name"] for f in data["frameworks"]]
dimensions = data["dimensions"]

# Build the values matrix
values = []
for framework in data["frameworks"]:
    row = [
        framework["learning_curve"],
        framework["multi_agent"],
        framework["enterprise"],
        framework["memory"],
        framework["deployment"],
        framework["community"],
        framework["documentation"],
        framework["production"]
    ]
    values.append(row)

# Create heatmap
fig = go.Figure(data=go.Heatmap(
    z=values,
    x=dimensions,
    y=framework_names,
    colorscale=[
        [0, '#DB4545'],      # Red for low values
        [0.5, '#D2BA4C'],    # Yellow for moderate values
        [1, '#2E8B57']       # Green for high values
    ],
    text=values,
    texttemplate='%{text}',
    textfont={"size": 16, "color": "white"},
    hovertemplate='<b>%{y}</b><br>%{x}: %{z}/5<extra></extra>',
    colorbar=dict(
        title="Score",
        tickvals=[1, 2, 3, 4, 5],
        ticktext=['1 (Low)', '2', '3', '4', '5 (High)']
    ),
    zmin=1,
    zmax=5
))

# Update layout
fig.update_layout(
    title={
        "text": "AI Agent Framework Comparison Across Dimensions (2024)<br><span style='font-size: 18px; font-weight: normal;'>LangGraph leads enterprise features, CrewAI excels in ease of use</span>"
    },
    xaxis_title="Capability Dimensions",
    yaxis_title="Framework"
)

# Save the chart
fig.write_image("ai_framework_comparison.png")
fig.write_image("ai_framework_comparison.svg", format="svg")
