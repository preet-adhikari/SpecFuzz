from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ExecutionResult:
    is_success: bool
    response_time: float

    # If request times out or fails, these will be empty (None)
    status_code: Optional[int] = None 
    response_header: Optional[Dict[str, str]] = None
    response_body: Optional[bytes] = None
    response_url: Optional[str] = None

    # If request fails
    error_message: Optional[str] = None
