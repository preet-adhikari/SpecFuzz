from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


# We're creating a dataclass here so that if we have different kind of APIs to parse, we can make sure that it follows this standard.
@dataclass
class PathEndpointData:
    path: str
    method: str
    request_body: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None

# Global Class
@dataclass
class ParsedEndpointData:
    servers: List[Dict[str, Any]] = field(default_factory = list)
    security: List[Dict[str, Any]] = field(default_factory = list)
    operations: List[PathEndpointData] = field(default_factory = list)