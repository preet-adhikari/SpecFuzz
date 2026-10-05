from dataclasses import dataclass

from execution_engine.execution_result import ExecutionResult


@dataclass
class ValidationResult:
    validation_result_status: bool
    validation_context: str
    job: dict
    execution_result: ExecutionResult