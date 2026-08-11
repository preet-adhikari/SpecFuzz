from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


# We're creating a dataclass here so that if we have different kind of APIs to parse, we can make sure that it follows this standard.
@dataclass
class PathEndpointData:
    path: str
    method: str
    servers: List[Dict[str, Any]] = field(default_factory=list)
    security: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None

# Global Class
@dataclass
class ParsedEndpointData:
    servers: List[Dict[str, Any]] = field(default_factory = list)
    security: List[Dict[str, Any]] = field(default_factory = list)
    operations: List[PathEndpointData] = field(default_factory = list)

# Making some changes

# from dataclasses import dataclass, field
# from typing import List, Dict, Any, Optional


# # 1. FLATTENED SERVER DATA
# @dataclass
# class ServerData:
#     url: str
#     description: Optional[str] = None


# # 2. FLATTENED SECURITY DATA
# @dataclass
# class ResolvedSecurity:
#     """Represents a single lock and its mechanics."""

#     scheme_name: str
#     mechanics: Dict[str, Any]
#     scopes: List[str] = field(default_factory=list)


# @dataclass
# class SecurityRequirement:
#     """
#     Represents an AND relationship.
#     If this contains multiple ResolvedSecurity items, ALL are required simultaneously.
#     """

#     schemes: List[ResolvedSecurity] = field(default_factory=list)


# # 3. THE ENDPOINT PACKAGE
# @dataclass
# class PathEndpointData:
#     path: str
#     method: str
#     servers: List[ServerData] = field(default_factory=list)
#     # The list below represents an OR relationship.
#     # The Orchestrator only needs to satisfy ONE of these SecurityRequirements.
#     security: List[SecurityRequirement] = field(default_factory=list)
#     request_body: Optional[Dict[str, Any]] = None
#     response: Optional[Dict[str, Any]] = None


# # 4. THE FINAL PAYLOAD TO THE ORCHESTRATOR
# @dataclass
# class ParsedDataPackage:
#     # Notice: Global servers and global security are GONE!
#     # Everything is flattened into the operations.
#     # We only pass the global blueprints (The Armory) just in case the engine needs them.
#     security_schemes: Dict[str, Any] = field(default_factory=dict)
#     operations: List[PathEndpointData] = field(default_factory=list)
