import csv
import json
import os
from typing import Any

from reporting_module.reporting_strategy.base import ReportingStrategy
from shared.dto_contracts import TestRunResults


class CSVReportingStrategy(ReportingStrategy):
    def __init__(self, reporting_folder: str = "csv_reports") -> None:
        self._reporting_directory = reporting_folder

    def generate_report(self, result: TestRunResults) -> Any:
        self._create_folder()
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
        with open(os.path.join(self._reporting_directory, f"{result.test_run_id}.csv"), "w") as report:
            writer = csv.DictWriter(report , fieldnames=csv_headers)
            writer.writeheader()
            for case in result.test_case_details:
                row_data = {
                    "test_run_id": result.test_run_id,
                    "timestamp": result.timestamp,
                    "endpoint": case.endpoint,
                    "method": case.method,
                    "attempts": case.attempts,
                    "response_status_code": case.response_status_code,
                    "response_time_taken": case.response_time_taken,
                    "validation_passed": case.validation_passed,
                    "expected_response_codes": json.dumps(case.expected_response_codes),
                    "request_headers": json.dumps(case.request_headers),
                    "payload": json.dumps(case.payload),
                    "response_header": json.dumps(case.response_header),
                    "response_body": case.response_body if case.response_body else "",
                    "validation_context": json.dumps(case.validation_context),
                }
                writer.writerow(row_data)

    def _create_folder(self) -> None:
        os.makedirs(self._reporting_directory, exist_ok=True)
