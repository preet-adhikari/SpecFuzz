from reporting_module.reporting_strategy.cli_reporting_strategy import (
    CLIReportingStrategy,
)
from reporting_module.reporting_strategy.pdf_reporting_strategy import (
    PDFReportingStrategy,
)


class ReportingFactory:
    def __init__(self, reporting_factory: str) -> None:
        self._reporting_factory = reporting_factory

    def choose_reporting_strategy(self):
        if self._reporting_factory == "cli":
            return CLIReportingStrategy()
        elif self._reporting_factory == "pdf":
            return PDFReportingStrategy()
        else:
            raise ValueError("Inappropriate reporting strategy")
