from abc import ABC, abstractmethod
from typing import Any

from shared.dto_contracts import TestRunResults


class ReportingStrategy(ABC):
    @abstractmethod
    def generate_report(self, result : TestRunResults) -> Any:
        pass