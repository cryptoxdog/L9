"""
L9 Core Security Module
========================

Provides security primitives including:
- Permission Graph (RBAC via Neo4j)
- Access control utilities

Version: 1.0.0
"""

from .permission_graph import (
    PermissionGraph,
    grant_role,
    revoke_role,
    grant_permission,
    can_access,
    get_user_permissions,
)

__all__ = [
    "PermissionGraph",
    "grant_role",
    "revoke_role",
    "grant_permission",
    "can_access",
    "get_user_permissions",
]
