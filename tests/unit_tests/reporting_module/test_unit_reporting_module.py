from unittest.mock import MagicMock

from reporting_module.base import ReportingModule
from test_results_storage.base import BaseStorageStrategy


class TestUnitReportingModule:
    def test_unit_reporting_module_generates_report_with_corresponding_validation_status(self):
        #TODO Improve this test
        # Arrange
        fake_storage_module = MagicMock()
        results_dictionary = {
            "metadata" : {
                "_id": "ObjectId1245",
                "test_run_id": "run_000",
                "timestamp": "2026-10-26T14:45:15.192754+00:00",
                "random_seed": 1793025915,
            },
            "results": [{
                    "_id": "ObjectId('1234567')",
                    "validation_result_status": "false",
                    "job": {
                        "test_case": {
                            "endpoint": "http://sampleapi.com/1234",
                            "method": "GET",
                            "payload": "null",
                            "expected_response": {},
                            "security": [{}],
                        },
                    },
                    "execution_result": {},
                    "validation_context": [
                        {
                            "field": "header.content-type",
                            "rule": "content_type_mismatch",
                            "message": "Content-Type mismatch: Expected [], got 'application/json'",
                        }
                    ],
                    "test_run_id": "run_000",
                },
                {
                    "_id": "ObjectId('1234567')",
                    "validation_result_status": "true",
                    "job": {
                        "test_case": {
                            "endpoint": "http://sampleapi.com/567",
                            "method": "GET",
                            "payload": "null",
                            "expected_response": {},
                            "security": [{}],
                        },
                    },
                    "execution_result": {},
                    "validation_context": [],
                    "test_run_id": "run_000",
                },
            ],
        }
        fake_storage_module.get_test_run_details.return_value = results_dictionary
        sut = ReportingModule(fake_storage_module)
        fake_test_run_id = "run_000"
        # Act
        report = sut.generate_report(fake_test_run_id)
        # call reporting module's method that generates report
        # Assert
        fake_storage_module.get_test_run_details.assert_called_once_with("run_000")
        assert all(report.get("is_success", {})) is True

        # assert that the generate report was called in reporting module
        # Assert validation status matches
        pass