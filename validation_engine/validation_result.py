from dataclasses import dataclass, field
from typing import Any, Dict, List

from execution_engine.execution_result import ExecutionResult


@dataclass
class ValidationResult:
    validation_result_status: bool
    job: dict
    execution_result: ExecutionResult
    validation_context: List[Dict[str,Any]] = field(default_factory = list)