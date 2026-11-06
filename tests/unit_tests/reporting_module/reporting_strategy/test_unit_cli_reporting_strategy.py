from unittest.mock import MagicMock

from reporting_module.reporting_strategy.cli_reporting_strategy import CLIReportingStrategy
from shared.dto_contracts import TestCaseDetail, TestRunResults


class TestUnitCLIReportingStrategy:
    def test_unit_cli_reporting_strategy_builds_tables_with_dto(self):
        #Arrange
        dummy_detail = TestCaseDetail(
            endpoint="/api/v1/auth",
            method="POST",
            attempts=1,
            response_status_code="401",
            response_time_taken=120.5,
            validation_passed=False
        )

        test_results = TestRunResults(
            test_run_id="test-run-999",
            timestamp="2026-11-06T12:00:00Z",
            crash_count=0,
            total_endpoints=1,
            total_requests=1,
            passed_percentage=0.0,
            random_seed=42,
            test_case_details=[dummy_detail]
        )
        console = MagicMock()

        sut = CLIReportingStrategy(console)

        #Act
        sut.generate_report(test_results)
        #Assert
        assert console.print.call_count == 2
        

        pass