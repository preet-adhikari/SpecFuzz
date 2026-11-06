from typing import Any

from reporting_module.reporting_strategy.base import ReportingStrategy
from shared.dto_contracts import TestRunResults
from rich.console import Console
from rich.table import Table


class CLIReportingStrategy(ReportingStrategy):
    def __init__(self, console: Console | None = None) -> None:
        self._console = console if console else Console()

    def generate_report(self, result: TestRunResults) -> Any:
        summary, details = self._build_data(result)
        self._console.print(details)
        self._console.print(summary)
        pass

    def _build_data(self, result: TestRunResults) -> Any:
        summary_table = Table(title="Test Run Results Overview", title_justify="center")
        summary_table.add_column("Metric", style="cyan", no_wrap=True)
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Test Run ID", str(result.test_run_id))
        summary_table.add_row("Timestamp", str(result.timestamp))
        summary_table.add_row("Total Endpoints", str(result.total_endpoints))
        summary_table.add_row("Total Requests", str(result.total_requests))
        summary_table.add_row("Crash Count", str(result.crash_count))
        summary_table.add_row("Percentage Passed", f"{result.passed_percentage}%")
        summary_table.add_row("Random Seed", str(result.random_seed))

        details_table = Table(title="Details for the Test Cases")
        details_table.add_column("Endpoint")
        details_table.add_column("Method")
        details_table.add_column("Passed Status")
        details_table.add_column("Validation Result Context")
        details_table.add_column("Response Status Code")
        details_table.add_column("Response Time Taken(ms)")
        details_table.add_column("Request Headers")
        details_table.add_column("Request Payload")
        details_table.add_column("Expected Response Codes")
        details_table.add_column("Response Body")
        details_table.add_column("Response Header")

        for record in result.test_case_details:
            req_payload = (
                str(record.payload)[:30] + "..."
                if record.payload
                else "None"
            )
            res_body = (
                str(record.response_body)[:30] + "..."
                if record.response_body
                else "None"
            )

            passed_status = "Pass" if record.validation_passed else "Fail"

            details_table.add_row(
                str(record.endpoint),
                str(record.method),
                passed_status,
                str(record.validation_context),
                str(record.response_status_code),
                f"{record.response_time_taken}ms",
                str(record.request_headers)[:20] + "...", 
                req_payload,  
                str(record.expected_response_codes),
                res_body, 
                str(record.response_header)[:20] + "...",
            )

        return summary_table, details_table

        pass
