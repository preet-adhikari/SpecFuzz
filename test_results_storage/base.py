
from abc import ABC, abstractmethod
from typing import Any, List

from validation_engine.validation_result import ValidationResult


class BaseStorageStrategy(ABC):
    @abstractmethod
    def initialize_storage(self, test_run_metadata: dict) -> None:
        """Sets up destination using the details of the current test run"""
        pass

    @abstractmethod
    def save(self, validation_result : ValidationResult) -> bool:
        """Saves the individual test case data"""
        pass

    @abstractmethod
    def save_batch(self, results: List[ValidationResult]) -> bool:
        """Stores test case data in batches"""
        pass

    @abstractmethod
    def get_summary(self, test_run_metadata_id: str) -> Any:
        pass

    @abstractmethod
    def get_test_run_details(self, test_run_metadata_id: str) -> Any:
        pass