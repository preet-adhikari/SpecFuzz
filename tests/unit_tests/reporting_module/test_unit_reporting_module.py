from unittest.mock import MagicMock, patch

from reporting_module.base import ReportingModule
from test_results_storage.base import BaseStorageStrategy


class TestUnitReportingModule:
    def test_unit_reporting_module_generates_report_with_corresponding_validation_status(self):
        # Arrange
        fake_storage_module = MagicMock()
        results_dictionary = {
            "test_run_id": "run_000",
            "results": [
                {"endpoint": "/login", "passed": True},
                {"endpoint": "/users", "passed": True},
            ],
        }
        fake_storage_module.get_test_run_details.return_value = results_dictionary
        sut = ReportingModule(fake_storage_module)
        # Act
        report = sut.generate_report(results_dictionary["test_run_id"])
        # call reporting module's method that generates report
        # Assert
        fake_storage_module.get_test_run_details.assert_called_once_with("run_000")
        assert all(report.get("is_success", {})) is True
        # assert that the generate report was called in reporting module
        # Assert validation status matches
        pass
