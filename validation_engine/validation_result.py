from dataclasses import dataclass, field
from typing import Any, Dict, List

from execution_engine.execution_result import ExecutionResult


@dataclass
class ValidationResult:
    """
        Holds the context after validation of the API
    
        This is how validation_context is constructed:
        validation_context = [
                                {
                                    field: This will be the field that is causing the error in validation
                                    rule: This is the rule that is being invalidated
                                    message: This is the message containing why the rule was invalidated
                                }
                            ]
        """
    validation_result_status: bool
    job: dict
    execution_result: ExecutionResult
    validation_context: List[Dict[str,Any]] = field(default_factory = list)
    