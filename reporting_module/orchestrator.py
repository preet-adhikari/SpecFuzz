from typing import List
from reporting_module.reporting_strategy.base import ReportingStrategy
from shared.dto_contracts import TestRunResults


class ReportOrchestrator:
    def __init__(self, strategies: List[ReportingStrategy]) -> None:
        self._strategies = strategies

    def publish_all_reports(self, test_results: TestRunResults) -> None:
        for strategy in self._strategies:
            strategy.generate_report(test_results)
