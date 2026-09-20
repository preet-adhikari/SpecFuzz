from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


# We're creating a dataclass here so that if we have different kind of APIs to parse, we can make sure that it follows this standard.

# # 1. FLATTENED SERVER DATA
@dataclass
class ServerData:
    url: str
    description: Optional[str] = None


# # 2. FLATTENED SECURITY DATA
@dataclass
class ResolvedSecurity:
    """Represents a single lock and its mechanics."""

    scheme_name: str
    mechanics: Dict[str, Any]
    applied_scopes: List[str] = field(default_factory=list)


@dataclass
class SecurityRequirement:
    """
    Represents an AND relationship.
    If this contains multiple ResolvedSecurity items, ALL are required simultaneously.
    """

    schemes: List[ResolvedSecurity] = field(default_factory=list)


# # 3. THE ENDPOINT PACKAGE
@dataclass
class PathEndpointData:
    path: str
    method: str
    servers: List[ServerData] = field(default_factory=list)
    # The list below represents an OR relationship.
    # The Orchestrator only needs to satisfy ONE of these SecurityRequirements.
    security: List[SecurityRequirement] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)


# # 4. THE FINAL PAYLOAD TO THE ORCHESTRATOR
@dataclass
class ParsedDataPackage:
    # Security schemes is left empty and will be added in later versions to include token caching
    security_schemes: Dict[str, Any] = field(default_factory=dict)
    operations: List[PathEndpointData] = field(default_factory=list)
