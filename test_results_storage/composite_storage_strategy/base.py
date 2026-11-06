from typing import Any, List

from shared.dto_contracts import TestRunResults
from test_results_storage.base import BaseStorageStrategy
from validation_engine.validation_result import ValidationResult


class CompositeStorageStrategy(BaseStorageStrategy):
    def __init__(self, strategies: List[BaseStorageStrategy]) -> None:
        self._strategies = strategies

    def initialize_storage(self, test_run_metadata: dict) -> None:
        for strategy in self._strategies:
            strategy.initialize_storage(test_run_metadata)

    def save(self, validation_result: ValidationResult) -> bool:
        successes = []
        for strategy in self._strategies:
            is_success = strategy.save(validation_result)

            if not is_success:
                strategy_name = strategy.__class__.__name__
                print(f"[ERROR] {strategy_name} failed to save the result.")

            successes.append(is_success)

        return all(successes)

    def save_batch(self, results: List[ValidationResult]) -> bool:
        successes = []
        for strategy in self._strategies:
            is_success = strategy.save_batch(results)

            if not is_success:
                strategy_name = strategy.__class__.__name__
                print(f"[ERROR] {strategy_name} failed to save the results.")

            successes.append(is_success)

        return all(successes)

    def get_summary(self, test_run_metadata_id: str) -> Any:
        self._strategies[0].get_summary(test_run_metadata_id)

    def get_test_run_details(self, test_run_metadata_id: str) -> Any:
        return self._strategies[0].get_test_run_details(test_run_metadata_id)

