from dataclasses import asdict
import json
import os
from typing import Any

from test_results_storage.base import BaseStorageStrategy
from validation_engine.validation_result import ValidationResult


class FileStorageStrategy(BaseStorageStrategy):
    def __init__(self, base_directory: str = "specfuzz_runs") -> None:
        self._base_directory = base_directory
        self.file_path = None

    def initialize_storage(self, test_run_metadata: dict) -> None:
        os.makedirs(self._base_directory, exist_ok=True)
        run_id = test_run_metadata["test_run_id"]
        self.file_path = os.path.join(self._base_directory, f"run_{run_id}.jsonl")
        self._test_run_metadata = test_run_metadata

        with open(self.file_path, "w") as f:
            f.write(json.dumps(test_run_metadata) + "\n")

    def save(self, validation_result: ValidationResult) -> bool:
        """Saves the single ValidationResult to the associated file"""
        if not self.file_path:
            return False
        try:
            with open(self.file_path, "a") as f:
                result_dict = asdict(validation_result)
                f.write(json.dumps(result_dict, default=str) + "\n")
                return True
        except Exception:
            return False

    def save_batch(self, results: list[ValidationResult]) -> bool:
        """Saves a list of ValidationResult to the associated file"""
        if not self.file_path:
            return False
        try:
            with open(self.file_path, "a") as f:
                lines = []
                for result in results:
                    lines.append(json.dumps(asdict(result), default=str) + "\n")
                f.writelines(lines)
                return True
        except Exception:
            return False

    def get_summary(self, test_run_metadata_id: str) -> dict:
        target_file = os.path.join(self._base_directory, f"run_{test_run_metadata_id}.jsonl")
        if not os.path.exists(target_file):
            return {"total": 0, "passed": 0, "failed": 0}

        summary = {"total": 0, "passed": 0, "failed": 0}
        try:
            with open(target_file, "r") as f:
                lines = f.readlines()
                if len(lines) <= 1:  # Means only metadata is present
                    return summary
                for line in lines[1:]:
                    result = json.loads(line)
                    summary["total"] += 1

                    if result.get("validation_result_status") is True:
                        summary["passed"] += 1
                    else:
                        summary["failed"] += 1
            return summary
        except Exception:
            return {"total": 0, "passed": 0, "failed": 0}

    def get_test_run_details(self, test_run_metadata_id: str) -> Any:
        pass
