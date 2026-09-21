from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class ExecutionEngineRequestData:
    method: str
    url: str
    payload: Optional[Dict[str, Any]] = None

    # I'm keeping the dictionary value to string because I don't want "Any" type into the header
    headers: Optional[Dict[str, str]] = None

    