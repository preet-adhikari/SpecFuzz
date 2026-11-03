import json
import os

from execution_engine.execution_result import ExecutionResult
from test_results_storage.file_storage_strategy import FileStorageStrategy
from validation_engine.validation_result import ValidationResult


class TestIntegrationFileStorageStrategy:
    def test_file_storage_strategy_should_save_test_results_to_disk(self, tmp_path):
        """Integration test between FileStorageStrategy and File System"""
        # Arrange
        
        fake_validation_result = ValidationResult(
            validation_result_status=True,
            job={"test_case": "happy_path"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )
        
        sut = FileStorageStrategy(tmp_path)
        test_run_metadata = {
            "test_run_id": "run_999",
            "target": "bifrost_api",
            "seed": 1234565,
        }
        expected_file_path = tmp_path / "run_run_999.jsonl"

        # Act
        sut.initialize_storage(test_run_metadata)
        save_status = sut.save(fake_validation_result)
        # Read file to see data was written
        with open(expected_file_path, "r") as f:
            lines = f.readlines()

        # Assert
        assert save_status is True
        assert os.path.exists(expected_file_path)

        assert len(lines) == 2
        saved_metadata = json.loads(lines[0])
        assert saved_metadata["test_run_id"] == "run_999"

        saved_result = json.loads(lines[1])
        assert saved_result["validation_result_status"] is True

    def test_file_storage_creates_unique_file_per_run(self, tmp_path):
        #Arrange
        sut = FileStorageStrategy(base_directory=str(tmp_path))

        test_run_metadata = {"test_run_id": "run_999", "target": "bifrost_api"}

        fake_result = ValidationResult(
            validation_result_status=True,
            job={"test_case": "happy_path"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )

        #Act
        sut.initialize_storage(test_run_metadata)
        is_saved = sut.save(fake_result)

        #Assert
        assert is_saved is True

        expected_file = tmp_path / "run_run_999.jsonl"

        # Prove file was actually created
        assert os.path.exists(expected_file)

        # Verify the contents
        with open(expected_file, "r") as f:
            lines = f.readlines()

        assert len(lines) == 2

        saved_metadata = json.loads(lines[0])
        assert saved_metadata["test_run_id"] == "run_999"

        saved_result = json.loads(lines[1])
        assert saved_result["validation_result_status"] is True
