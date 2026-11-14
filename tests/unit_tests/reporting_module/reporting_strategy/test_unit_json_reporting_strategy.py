from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import MagicMock, patch

from reporting_module.reporting_strategy.json_reporting_strategy import (
    JSONReportingStrategy,
)
from shared.dto_contracts import TestCaseDetail, TestRunResults


class TestUnitJSONReportingStrategy:
    @patch("os.makedirs")
    def test_unit_json_create_folder_creates_reporting_folder_if_doesnt_exist(
        self, makedirs
    ):
        # Arrange
        dummy_detail = TestCaseDetail(
            endpoint="/api/v1/auth",
            method="POST",
            attempts=1,
            response_status_code="401",
            response_time_taken=120.5,
            validation_passed=False,
        )

        test_results = TestRunResults(
            test_run_id="test-run-999",
            timestamp="2026-11-06T12:00:00Z",
            crash_count=0,
            total_endpoints=1,
            total_requests=1,
            passed_percentage=0.0,
            random_seed=42,
            test_case_details=[dummy_detail],
        )
        fake_path_to_folder = "reporting_folder_path"
        sut = JSONReportingStrategy(fake_path_to_folder)
        # Act
        sut.generate_report(test_results)
        # Assert
        makedirs.assert_called_once_with(fake_path_to_folder, exist_ok=True)


    def test_unit_json_generate_report_outputs_json_file(self):
        # Arrange
        dummy_detail = TestCaseDetail(
            endpoint="/api/v1/auth",
            method="POST",
            attempts=1,
            response_status_code="401",
            response_time_taken=120.5,
            validation_passed=False,
        )

        test_results = TestRunResults(
            test_run_id="test-run-999",
            timestamp="2026-11-06T12:00:00Z",
            crash_count=0,
            total_endpoints=1,
            total_requests=1,
            passed_percentage=0.0,
            random_seed=42,
            test_case_details=[dummy_detail],
        )
        fake_path_to_folder = "reporting_folder_path"
        dict_conversion = asdict(test_results)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / fake_path_to_folder
            sut = JSONReportingStrategy(str(target))
            expected_file = target / f"{test_results.test_run_id }.json"
            # Act
            sut.generate_report(test_results)

            # Assert
            assert target.is_dir()
            assert expected_file.is_file()
            with open(expected_file, "r") as file:
                saved_data = json.load(file)
                assert saved_data == dict_conversion

