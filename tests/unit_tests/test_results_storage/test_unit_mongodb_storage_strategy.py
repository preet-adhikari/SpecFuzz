from dataclasses import asdict
from unittest.mock import MagicMock, patch

import pytest

from execution_engine.execution_result import ExecutionResult
from test_results_storage.mongodb_storage_strategy import MongoDBStorageStrategy
from validation_engine.validation_result import ValidationResult


class TestUnitMongoDBStrategy:
    @patch("test_results_storage.mongodb_storage_strategy.MongoClient")
    def test_initialize_storage_connects_and_saves_metadata(self, mock_client_class):
        # Assert
        sut = MongoDBStorageStrategy("fake_url", "fake_db")
        metadata = {"test_run_id": "run_999", "target": "test_api"}

        # Act
        sut.initialize_storage(metadata)

        # Assert
        mock_client_class.assert_called_once_with("fake_url")
        mock_client_instance = mock_client_class()

        mock_client_instance.admin.command.assert_called_once_with("ping")
        mock_client_instance["fake_db"]["test_runs"].insert_one.assert_called_once_with(
            metadata
        )
        assert sut.current_run_id == "run_999"

    def test_mongodb_storage_strategy_saves_document(self):
        # Arrange
        sut = MongoDBStorageStrategy("fake_db", "fake_result")

        sut.client = MagicMock()
        sut.collection = MagicMock()
        sut.current_run_id = "run_999"
        fake_result = ValidationResult(
            validation_result_status=True,
            job={"test_case": "happy_path"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )
        expected_doc = asdict(fake_result)
        expected_doc["test_run_id"] = "run_999"

        # Act
        is_saved = sut.save(fake_result)

        # Arrange
        assert is_saved is True
        sut.collection.insert_one.assert_called_once_with(expected_doc)

    def test_mongodb_storage_strategy_saves_batch(self):
        # Arrange
        sut = MongoDBStorageStrategy("fake_url", "fake_db")
        sut.client = MagicMock()
        sut.collection = MagicMock()
        sut.current_run_id = "run_999"

        result_1 = ValidationResult(
            validation_result_status=True,
            job={"test_case": "1"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )
        result_2 = ValidationResult(
            validation_result_status=False,
            job={"test_case": "2"},
            execution_result=ExecutionResult(
                is_success=False, response_time=0.5, status_code=500
            ),
            validation_context=[],
        )
        batch = [result_1, result_2]

        expected_docs = [asdict(result_1), asdict(result_2)]
        for doc in expected_docs:
            doc["test_run_id"] = "run_999"

        # Act
        is_saved = sut.save_batch(batch)

        # Assert
        assert is_saved is True

        sut.collection.insert_many.assert_called_once_with(expected_docs)

    def test_unit_mongodb_storage_gets_summary(self):
        # Arrange
        sut = MongoDBStorageStrategy("fake_url", "fake_db")
        sut.client = MagicMock()
        sut.collection = MagicMock()

        # Side effect with a list returns next item each time the mock is called
        sut.collection.count_documents.side_effect = [10, 8, 2]

        # Act
        summary = sut.get_summary("run_999")

        # Assert
        assert summary["total"] == 10
        assert summary["passed"] == 8
        assert summary["failed"] == 2

        assert sut.collection.count_documents.call_count == 3

    def test_unit_mongodb_storage_strategy_gets_valid_individual_test_run_detail(self):
        # Arrange
        raw_json = [
            {
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
                "validation_result_status": "false",
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
                "validation_context": [
                    {
                        "field": "header.content-type",
                        "rule": "content_type_mismatch",
                        "message": "Content-Type mismatch: Expected [], got 'application/json'",
                    }
                ],
                "test_run_id": "run_000",
            },
        ]
        metadata_json = {
            "_id": "ObjectId1245",
            "test_run_id": "run_000",
            "timestamp": "2026-10-26T14:45:15.192754+00:00",
            "random_seed": 1793025915,
        }
        fake_test_run_id = "run_000"
        sut = MongoDBStorageStrategy("fake_url", "fake_db")
        sut.metadata_collection = MagicMock()
        sut.collection = MagicMock()
        sut.metadata_collection.find_one.return_value = metadata_json
        sut.collection.find.return_value = raw_json

        # Act
        result_dict = sut.get_test_run_details(fake_test_run_id)

        # Assert
        assert (
            result_dict.get("metadata", {}).get("test_run_id", {}) == fake_test_run_id
        )
        assert result_dict.get("results", [])[0].get("endpoint", "") == raw_json[0].get(
            "job", {}
        ).get("test_case", {}).get("endpoint", "")
        assert result_dict.get("results", [])[1].get("endpoint", "") == raw_json[1].get(
            "job", {}
        ).get("test_case", {}).get("endpoint", "")
        sut.metadata_collection.find_one.assert_called_once_with(
            {"test_run_id": fake_test_run_id}
        )
        sut.collection.find.assert_called_once_with({"test_run_id": fake_test_run_id})

    def test_unit_mongodb_storage_strategy_throws_valueError_if_test_id_doesnt_exist(
        self,
    ):
        # Arrange
        raw_json = {}
        fake_test_run_id = "run_000"
        sut = MongoDBStorageStrategy("fake_url", "fake_db")
        sut.metadata_collection = MagicMock()
        sut.metadata_collection.find_one.return_value = None

        # Act & Assert
        with pytest.raises(
            ValueError, match=f"Test run {fake_test_run_id} doesn't exist."
        ):
            sut.get_test_run_details(fake_test_run_id)

        pass
