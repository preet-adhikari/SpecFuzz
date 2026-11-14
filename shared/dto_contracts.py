from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TestCaseDetail:
    endpoint: str
    method: str
    attempts: int
    response_status_code: str
    response_time_taken: float
    validation_passed: bool

    request_headers: Dict[str, Any] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    expected_response_codes: List[str] = field(default_factory=list)

    response_body: Optional[str] = None
    response_header: Dict[str, Any] = field(default_factory=dict)
    validation_context: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TestRunResults:
    test_run_id: str
    timestamp: str
    crash_count: int
    total_endpoints: int
    total_requests: int
    passed_percentage: float
    random_seed: int
    test_case_details: list[TestCaseDetail]
