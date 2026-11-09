from dataclasses import asdict
import json
import os
from typing import Any

from reporting_module.reporting_strategy.base import ReportingStrategy
from shared.dto_contracts import TestRunResults


class JSONReportingStrategy(ReportingStrategy):
    def __init__(self, reporting_directory: str = "json_reports") -> None:
        self._reporting_directory = reporting_directory

    def generate_report(self, result: TestRunResults) -> Any:
        self._create_folder()
        dict_result = asdict(result)
        with open(
            os.path.join(self._reporting_directory, f"{result.test_run_id}.json"), "w"
        ) as report:
            json.dump(dict_result, report)

    def _create_folder(self) -> None:
        os.makedirs(self._reporting_directory, exist_ok=True)
