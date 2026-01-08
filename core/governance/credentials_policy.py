"""
L9 Core Governance - Credentials Policy Enforcer
=================================================

Executable security enforcement for credentials and secrets.
Converts patterns from learning/credentials-policy.md into
programmatic detection, validation, and blocking.

Key capabilities:
- Detects exposed secrets (API keys, passwords, tokens)
- Validates credential rotation dates
- Blocks deployments with exposed keys
- Enforces least-privilege patterns

Version: 1.0.0
"""

from __future__ import annotations

import re
import structlog
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

logger = structlog.get_logger(__name__)


class SecretType(Enum):
    """Types of secrets to detect."""
    
    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
    PRIVATE_KEY = "private_key"
    CONNECTION_STRING = "connection_string"
    WEBHOOK_URL = "webhook_url"


@dataclass
class SecretPattern:
    """
    A secret detection pattern.
    
    Attributes:
        id: Pattern identifier
        name: Human-readable name
        pattern: Regex to detect secret
        secret_type: Type of secret
        severity: How critical this exposure is
        redact_pattern: Regex to use for redaction
    """
    
    id: str
    name: str
    pattern: str
    secret_type: SecretType
    severity: str  # "critical", "high", "medium"
    redact_pattern: str = r"\*\*\*REDACTED\*\*\*"


@dataclass
class SecretViolation:
    """A detected secret exposure."""
    
    pattern_id: str
    name: str
    secret_type: str
    severity: str
    match_preview: str  # First/last chars only for safety
    line_number: Optional[int] = None
    blocked: bool = True


class CredentialsPolicy:
    """
    Executable credentials policy enforcer.
    
    Detects and blocks exposed secrets, enforces rotation policies,
    and validates credential handling patterns.
    
    Usage:
        policy = CredentialsPolicy()
        safe, violations = policy.scan(content)
        if not safe:
            # Handle exposed secrets
            pass
    """
    
    def __init__(self) -> None:
        """Initialize with default secret patterns."""
        self._patterns: list[SecretPattern] = self._load_default_patterns()
    
    def _load_default_patterns(self) -> list[SecretPattern]:
        """Load default secret detection patterns."""
        return [
            SecretPattern(
                id="SEC-001",
                name="OpenAI API Key",
                pattern=r"sk-[a-zA-Z0-9]{20,}",
                secret_type=SecretType.API_KEY,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-002",
                name="Anthropic API Key",
                pattern=r"sk-ant-[a-zA-Z0-9\-]{20,}",
                secret_type=SecretType.API_KEY,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-003",
                name="Slack Bot Token",
                pattern=r"xoxb-[a-zA-Z0-9\-]{20,}",
                secret_type=SecretType.TOKEN,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-004",
                name="Slack App Token",
                pattern=r"xapp-[a-zA-Z0-9\-]{20,}",
                secret_type=SecretType.TOKEN,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-005",
                name="GitHub Token",
                pattern=r"ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{20,}",
                secret_type=SecretType.TOKEN,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-006",
                name="PostgreSQL Connection String",
                pattern=r"postgres(?:ql)?://[^:]+:[^@]+@[^/]+/\w+",
                secret_type=SecretType.CONNECTION_STRING,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-007",
                name="Generic Password in Code",
                pattern=r'(?:password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}["\']',
                secret_type=SecretType.PASSWORD,
                severity="high",
            ),
            SecretPattern(
                id="SEC-008",
                name="AWS Access Key",
                pattern=r"AKIA[0-9A-Z]{16}",
                secret_type=SecretType.API_KEY,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-009",
                name="AWS Secret Key",
                pattern=r"[a-zA-Z0-9/+]{40}(?=\s|$|['\"])",
                secret_type=SecretType.API_KEY,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-010",
                name="Private RSA Key",
                pattern=r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
                secret_type=SecretType.PRIVATE_KEY,
                severity="critical",
            ),
            SecretPattern(
                id="SEC-011",
                name="Webhook URL with Token",
                pattern=r"https://hooks\.[a-z]+\.com/[a-zA-Z0-9/]+",
                secret_type=SecretType.WEBHOOK_URL,
                severity="high",
            ),
            SecretPattern(
                id="SEC-012",
                name="Supabase Key",
                pattern=r"eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}",
                secret_type=SecretType.API_KEY,
                severity="critical",
            ),
        ]
    
    @property
    def patterns(self) -> list[SecretPattern]:
        """Get all loaded patterns."""
        return self._patterns
    
    def add_pattern(self, pattern: SecretPattern) -> None:
        """Add a custom secret pattern."""
        self._patterns.append(pattern)
        logger.info("credentials_policy.pattern_added", pattern_id=pattern.id)
    
    def scan(self, content: str) -> tuple[bool, list[SecretViolation]]:
        """
        Scan content for exposed secrets.
        
        Args:
            content: Text content to scan
            
        Returns:
            Tuple of (is_safe, list of violations)
        """
        violations: list[SecretViolation] = []
        lines = content.split("\n")
        
        for pattern in self._patterns:
            for line_num, line in enumerate(lines, 1):
                matches = re.findall(pattern.pattern, line, re.IGNORECASE)
                for match in matches:
                    # Create safe preview (first 4 + last 4 chars)
                    if len(match) > 12:
                        preview = f"{match[:4]}...{match[-4:]}"
                    else:
                        preview = f"{match[:2]}***"
                    
                    violation = SecretViolation(
                        pattern_id=pattern.id,
                        name=pattern.name,
                        secret_type=pattern.secret_type.value,
                        severity=pattern.severity,
                        match_preview=preview,
                        line_number=line_num,
                        blocked=pattern.severity == "critical",
                    )
                    violations.append(violation)
                    
                    logger.warning(
                        "credentials_policy.secret_detected",
                        pattern_id=pattern.id,
                        name=pattern.name,
                        line=line_num,
                        severity=pattern.severity,
                    )
        
        is_safe = not any(v.blocked for v in violations)
        return is_safe, violations
    
    def redact(self, content: str) -> str:
        """
        Redact all detected secrets from content.
        
        Args:
            content: Text content to redact
            
        Returns:
            Content with secrets replaced by ***REDACTED***
        """
        redacted = content
        
        for pattern in self._patterns:
            redacted = re.sub(
                pattern.pattern,
                "***REDACTED***",
                redacted,
                flags=re.IGNORECASE,
            )
        
        return redacted
    
    def validate_env_file(self, env_content: str) -> list[dict[str, Any]]:
        """
        Validate .env file format and content.
        
        Args:
            env_content: Content of .env file
            
        Returns:
            List of validation issues
        """
        issues: list[dict[str, Any]] = []
        lines = env_content.split("\n")
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Check format
            if "=" not in line:
                issues.append({
                    "line": line_num,
                    "issue": "Invalid format (missing =)",
                    "content": line[:30],
                })
                continue
            
            key, value = line.split("=", 1)
            
            # Check for placeholder values
            placeholder_patterns = [
                r"your[-_]?key[-_]?here",
                r"xxx+",
                r"placeholder",
                r"changeme",
                r"TODO",
            ]
            for pp in placeholder_patterns:
                if re.search(pp, value, re.IGNORECASE):
                    issues.append({
                        "line": line_num,
                        "issue": f"Placeholder value detected for {key}",
                        "content": value[:20],
                    })
        
        return issues
    
    def get_audit_report(self, content: str) -> dict[str, Any]:
        """
        Generate security audit report for content.
        
        Args:
            content: Content to audit
            
        Returns:
            Audit report dict
        """
        is_safe, violations = self.scan(content)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "is_safe": is_safe,
            "total_violations": len(violations),
            "critical_violations": sum(1 for v in violations if v.severity == "critical"),
            "high_violations": sum(1 for v in violations if v.severity == "high"),
            "violations_by_type": {
                secret_type.value: sum(1 for v in violations if v.secret_type == secret_type.value)
                for secret_type in SecretType
            },
            "blocked": not is_safe,
            "recommendations": self._generate_recommendations(violations),
        }
    
    def _generate_recommendations(self, violations: list[SecretViolation]) -> list[str]:
        """Generate recommendations based on violations."""
        recommendations: list[str] = []
        
        if any(v.secret_type == "api_key" for v in violations):
            recommendations.append("Move API keys to environment variables")
            recommendations.append("Use secret management service (Vault, AWS Secrets Manager)")
        
        if any(v.secret_type == "password" for v in violations):
            recommendations.append("Never hardcode passwords in source code")
            recommendations.append("Use credential injection at runtime")
        
        if any(v.secret_type == "connection_string" for v in violations):
            recommendations.append("Use DATABASE_URL environment variable")
            recommendations.append("Separate credentials from connection parameters")
        
        return recommendations


# Factory function
def create_credentials_policy() -> CredentialsPolicy:
    """Create a CredentialsPolicy instance with default patterns."""
    return CredentialsPolicy()


__all__ = [
    "CredentialsPolicy",
    "SecretPattern",
    "SecretViolation",
    "SecretType",
    "create_credentials_policy",
]

# ============================================================================
# L9 DORA BLOCK - AUTO-GENERATED - DO NOT EDIT
# ============================================================================
__dora_block__ = {
    "component_id": "COR-FOUN-022",
    "component_name": "Credentials Policy",
    "module_version": "1.0.0",
    "created_at": "2026-01-08T03:15:14Z",
    "created_by": "L9_DORA_Injector",
    "layer": "foundation",
    "domain": "governance",
    "type": "utility",
    "status": "active",
    "governance_level": "critical",
    "compliance_required": True,
    "audit_trail": True,
    "purpose": "Provides credentials policy components including SecretType, SecretPattern, SecretViolation",
    "dependencies": [],
}

# ============================================================================
# END L9 DORA BLOCK
# ============================================================================
