from typing import Any

from reporting_module.reporting_strategy.base import ReportingStrategy
from shared.dto_contracts import TestRunResults


class PDFReportingStrategy(ReportingStrategy):
    
    def generate_report(self, result: TestRunResults) -> Any:
        pass