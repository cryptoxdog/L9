"""
L9 World Model - Registry
=========================

Registry for entity types, relation schemas, and world model metadata.

Specification Sources:
- WorldModelOS.yaml → registry
- world_graph_schema.yaml → type_definitions
- reasoning kernel 01 (schema validation)

The registry provides:
- Entity type definitions
- Relation type definitions
- Schema validation rules
- Type inheritance hierarchy

Integration:
- WorldModelLoader: populates registry from specs
- WorldModelUpdater: validates against registry
- Reasoning Kernel 01: schema-aware reasoning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class EntityTypeSchema:
    """
    Schema definition for an entity type.
    
    Specification: world_graph_schema.yaml → entity_types
    """
    
    type_name: str
    description: str = ""
    attributes: dict[str, dict[str, Any]] = field(default_factory=dict)
    parent_type: Optional[str] = None
    constraints: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class RelationTypeSchema:
    """
    Schema definition for a relation type.
    
    Specification: world_graph_schema.yaml → relation_types
    """
    
    type_name: str
    description: str = ""
    source_types: list[str] = field(default_factory=list)
    target_types: list[str] = field(default_factory=list)
    attributes: dict[str, dict[str, Any]] = field(default_factory=dict)
    cardinality: str = "many_to_many"


class WorldModelRegistry:
    """
    Registry for World Model type definitions and schemas.
    
    Specification Sources:
    - WorldModelOS.yaml → registry
    - world_graph_schema.yaml → type_definitions
    - reasoning kernel 01 (schema validation)
    
    Tracks:
    - Entity type schemas
    - Relation type schemas
    - Type inheritance hierarchy
    - Validation constraints
    
    Operations:
    - Register entity/relation types
    - Validate instances against schemas
    - Resolve type inheritance
    - Query type metadata
    
    Integration:
    - WorldModelLoader: populates from YAML specs
    - WorldModelUpdater: validates updates
    - WorldModelState: type-checked entities/relations
    - Reasoning Kernel 01: schema-aware inference
    """
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._entity_types: dict[str, EntityTypeSchema] = {}
        self._relation_types: dict[str, RelationTypeSchema] = {}
        self._type_hierarchy: dict[str, list[str]] = {}  # type → [subtypes]
        self._created_at: datetime = datetime.utcnow()
    
    # =========================================================================
    # Entity Type Operations
    # =========================================================================
    
    def register_entity_type(self, schema: EntityTypeSchema) -> None:
        """
        Register an entity type schema.
        
        Args:
            schema: EntityTypeSchema to register
        """
        pass
    
    def get_entity_type(self, type_name: str) -> Optional[EntityTypeSchema]:
        """
        Get entity type schema by name.
        
        Args:
            type_name: Type name to look up
            
        Returns:
            EntityTypeSchema if found
        """
        pass
    
    def list_entity_types(self) -> list[str]:
        """
        List all registered entity type names.
        
        Returns:
            List of type names
        """
        pass
    
    def validate_entity(self, entity_type: str, attributes: dict[str, Any]) -> bool:
        """
        Validate entity attributes against schema.
        
        Specification: reasoning kernel 01 → schema_validation
        
        Args:
            entity_type: Type to validate against
            attributes: Entity attributes
            
        Returns:
            True if valid
        """
        pass
    
    # =========================================================================
    # Relation Type Operations
    # =========================================================================
    
    def register_relation_type(self, schema: RelationTypeSchema) -> None:
        """
        Register a relation type schema.
        
        Args:
            schema: RelationTypeSchema to register
        """
        pass
    
    def get_relation_type(self, type_name: str) -> Optional[RelationTypeSchema]:
        """
        Get relation type schema by name.
        
        Args:
            type_name: Type name to look up
            
        Returns:
            RelationTypeSchema if found
        """
        pass
    
    def list_relation_types(self) -> list[str]:
        """
        List all registered relation type names.
        
        Returns:
            List of type names
        """
        pass
    
    def validate_relation(
        self,
        relation_type: str,
        source_type: str,
        target_type: str,
        attributes: dict[str, Any],
    ) -> bool:
        """
        Validate relation against schema.
        
        Specification: reasoning kernel 01 → relation_validation
        
        Args:
            relation_type: Relation type
            source_type: Source entity type
            target_type: Target entity type
            attributes: Relation attributes
            
        Returns:
            True if valid
        """
        pass
    
    # =========================================================================
    # Type Hierarchy
    # =========================================================================
    
    def get_subtypes(self, type_name: str) -> list[str]:
        """
        Get all subtypes of an entity type.
        
        Args:
            type_name: Parent type
            
        Returns:
            List of subtype names
        """
        pass
    
    def get_supertypes(self, type_name: str) -> list[str]:
        """
        Get all supertypes (ancestors) of an entity type.
        
        Args:
            type_name: Child type
            
        Returns:
            List of supertype names (nearest first)
        """
        pass
    
    def is_subtype(self, child_type: str, parent_type: str) -> bool:
        """
        Check if one type is a subtype of another.
        
        Args:
            child_type: Potential subtype
            parent_type: Potential supertype
            
        Returns:
            True if child_type inherits from parent_type
        """
        pass
    
    # =========================================================================
    # Serialization
    # =========================================================================
    
    def to_dict(self) -> dict[str, Any]:
        """
        Serialize registry to dictionary.
        
        Returns:
            Dict representation
        """
        pass
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldModelRegistry:
        """
        Deserialize registry from dictionary.
        
        Args:
            data: Dict representation
            
        Returns:
            WorldModelRegistry instance
        """
        pass
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def entity_type_count(self) -> int:
        """Number of registered entity types."""
        return len(self._entity_types)
    
    @property
    def relation_type_count(self) -> int:
        """Number of registered relation types."""
        return len(self._relation_types)

