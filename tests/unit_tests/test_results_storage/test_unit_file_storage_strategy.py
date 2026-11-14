from dataclasses import asdict
import json
import os
from unittest.mock import mock_open, patch

from execution_engine.execution_result import ExecutionResult
from test_results_storage.file_storage_strategy import FileStorageStrategy
from validation_engine.validation_result import ValidationResult


class TestUnitFileStorageStrategy:
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_initialize_storage_writes_metadata_to_file(self, mock_makedirs, mock_file):

        # Arrange
        fake_dir = "fake_directory"
        sut = FileStorageStrategy(base_directory=fake_dir)
        test_run_metadata = {"test_run_id": "run_999", "target": "bifrost_api"}
        expected_string = json.dumps(test_run_metadata) + "\n"
        expected_file_path = os.path.join(fake_dir, "run_run_999.jsonl")
        # Act
        sut.initialize_storage(test_run_metadata)

        # Assert
        mock_makedirs.assert_called_once_with(fake_dir, exist_ok=True)
        mock_file.assert_called_once_with(expected_file_path, "w")

        file_handle = mock_file()

        file_handle.write.assert_called_once_with(expected_string)

    @patch("builtins.open", new_callable=mock_open)
    def test_file_storage_strategy_saves_file(self, mock_file):
        # Arrange
        sut = FileStorageStrategy(base_directory="fake_directory")

        sut.file_path = "fake_directory/run_run_999.jsonl"

        fake_validation_result = ValidationResult(
            validation_result_status=True,
            job={"test_case": "happy_path"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )
        expected_dict = asdict(fake_validation_result)
        expected_string = json.dumps(expected_dict, default=str) + "\n"

        # Act
        is_saved = sut.save(fake_validation_result)
        # Assert
        assert is_saved is True
        mock_file.assert_called_once_with(sut.file_path, "a")

        file_handle = mock_file()
        file_handle.write.assert_called_once_with(expected_string)

    @patch("builtins.open", new_callable=mock_open)
    def test_file_storage_strategy_saves_batch(self, mock_file):
        # Assert
        sut = FileStorageStrategy(base_directory="fake_directory")
        sut.file_path = "fake_directory/run_999.jsonl"

        # Create two distinct test results to represent a batch
        result_1 = ValidationResult(
            validation_result_status=True,
            job={"test_case": "happy_path_1"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )
        result_2 = ValidationResult(
            validation_result_status=False,
            job={"test_case": "edge_case_2"},
            execution_result=ExecutionResult(
                is_success=False, response_time=0.5, status_code=500
            ),
            validation_context=[{
                                "field": "header.status_code",
                                "rule": "status_code_mismatch",
                                "message": f"Unexpected status code 500. Expected one of: [200, 404]"
                            }],
        )

        batch = [result_1, result_2]
        expected_lines = [
            json.dumps(asdict(result_1), default=str) + "\n",
            json.dumps(asdict(result_2), default=str) + "\n",
        ]

        # Act
        is_saved = sut.save_batch(batch)

        # Assert
        assert is_saved is True
        mock_file.assert_called_once_with(sut.file_path, "a")

        file_handle = mock_file()
        file_handle.writelines.assert_called_once_with(expected_lines)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    def test_file_storage_strategy_gets_summary(self, mock_exists, mock_file):
        # Arrange
        sut = FileStorageStrategy(base_directory="fake_directory")
        mock_exists.return_value = True
        fake_file_content = [
            '{"test_run_id": "run_999", "target": "bifrost_api"}\n',  # Line 1: Metadata
            '{"validation_result_status": true}\n',  # Line 2: Passed test
            '{"validation_result_status": false}\n',  # Line 3: Failed test
            '{"validation_result_status": true}\n',  # Line 4: Passed test
        ]
        mock_file.return_value.readlines.return_value = fake_file_content
        expected_filepath = "fake_directory/run_run_999.jsonl"
        # Act
        summary = sut.get_summary("run_999")
        #Assert
        mock_exists.assert_called_once_with(expected_filepath)
        mock_file.assert_called_once_with(expected_filepath, "r")
        assert summary["total"] == 3
        assert summary["passed"] == 2
        assert summary["failed"] == 1
