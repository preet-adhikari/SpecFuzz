from dataclasses import dataclass
from typing import Optional, Any, Dict

@dataclass
class ExecutionResult:
    is_success: bool
    response_time: float

    # If request times out, these will be empty
    response_status: Optional[int] = None
    response_header: Optional[Dict[str, str]] = None
    response_body: Optional[bytes] = None
    response_url: Optional[str] = None 

    # If request fails
    error_message: Optional[str] = None

