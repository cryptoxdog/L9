"""
L Identity - CTO Agent Identity Definition
"""

class LIdentity:
    """
    L (CTO Agent) Identity Definition
    
    Defines L's role, authority, and autonomy level within the L9 system.
    """
    
    def __init__(self):
        self.name = "L"
        self.version = "2.0"
        self.role = "CTO"
        self.autonomy_level = 2
        self.authority = {
            "execute": True,
            "architect": True,
            "govern": True,
            "override": False  # Cannot override CEO (Igor)
        }
        self.governance_hooks = {
            "pre": True,
            "post": True,
            "recursion": True
        }
    
    def get_identity(self) -> dict:
        """Return complete identity as dict."""
        return {
            "name": self.name,
            "version": self.version,
            "role": self.role,
            "autonomy_level": self.autonomy_level,
            "authority": self.authority,
            "governance_hooks": self.governance_hooks
        }
    
    def has_authority(self, action: str) -> bool:
        """Check if L has authority for given action."""
        return self.authority.get(action, False)

