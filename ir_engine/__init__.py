"""
L9 IR Engine - Intent Representation Engine
============================================

Core module for extracting, validating, and transforming user intents
into structured intermediate representations for execution.

Components:
- ir_schema: Data models for IR nodes and graphs
- semantic_compiler: Natural language to IR conversion
- ir_validator: Schema validation and completeness checks
- ir_generator: IR output generation
- constraint_challenger: Detect/challenge false constraints
- simulation_router: Route IR to simulation engine
- ir_to_plan_adapter: Convert IR to executable plans
- deliberation_cell: 2-agent collaboration for IR refinement
"""

from ir_engine.ir_schema import (
    IntentNode,
    ConstraintNode,
    ActionNode,
    IRGraph,
    IRValidationResult,
    IRMetadata,
)
from ir_engine.semantic_compiler import SemanticCompiler
from ir_engine.ir_validator import IRValidator
from ir_engine.ir_generator import IRGenerator
from ir_engine.constraint_challenger import ConstraintChallenger
from ir_engine.simulation_router import SimulationRouter
from ir_engine.ir_to_plan_adapter import IRToPlanAdapter
from ir_engine.deliberation_cell import DeliberationCell

__all__ = [
    # Schema
    "IntentNode",
    "ConstraintNode",
    "ActionNode",
    "IRGraph",
    "IRValidationResult",
    "IRMetadata",
    # Components
    "SemanticCompiler",
    "IRValidator",
    "IRGenerator",
    "ConstraintChallenger",
    "SimulationRouter",
    "IRToPlanAdapter",
    "DeliberationCell",
]

