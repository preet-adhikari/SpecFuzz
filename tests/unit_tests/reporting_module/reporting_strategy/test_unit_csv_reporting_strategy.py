import csv
from pathlib import Path
import tempfile

from reporting_module.reporting_strategy.csv_reporting_strategy import (
    CSVReportingStrategy,
)
from shared.dto_contracts import TestCaseDetail, TestRunResults


class TestUnitCSVReportingStrategy:
    def test_unit_csv_report_generates_csv_file_with_appropriate_data(self):
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

        csv_headers = [
            "test_run_id",
            "timestamp",
            "endpoint",
            "method",
            "attempts",
            "response_status_code",
            "response_time_taken",
            "validation_passed",
            "expected_response_codes",
            "request_headers",
            "payload",
            "response_header",
            "response_body",
            "validation_context",
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / fake_path_to_folder
            sut = CSVReportingStrategy(str(target))
            expected_file = target / f"{test_results.test_run_id}.csv"

            # Act
            sut.generate_report(test_results)
            # Assert
            assert target.is_dir()
            assert expected_file.is_file()
            with open(expected_file, "r") as file:
                reader = csv.DictReader(file)
                assert reader.fieldnames == csv_headers
                row = next(reader)
                assert row["endpoint"] == dummy_detail.endpoint
        pass
