
from abc import ABC, abstractmethod
from typing import Any


class APISpecValidatorStrategy(ABC):
    @abstractmethod
    def validate(self, expected_response: Any, actual_response: Any)-> tuple[bool, list[dict[str, Any]]]:
        pass