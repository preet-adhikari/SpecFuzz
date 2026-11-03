from pymongo import MongoClient

from execution_engine.execution_result import ExecutionResult
from test_results_storage.mongodb_storage_strategy import MongoDBStorageStrategy
from validation_engine.validation_result import ValidationResult


class TestIntegrationMongoDBStorageStrategy:
    def test_mongo_storage_saves_document_to_database(self):
        connection_string = "mongodb://admin:secretpassword@localhost:27017/"
        db_name = "specfuzz_test_db"

        sut = MongoDBStorageStrategy(
            connection_url=connection_string, database_name=db_name
        )
        test_run_metadata = {"test_run_id": "run_mongo_999", "target": "bifrost_api"}
        fake_result = ValidationResult(
            validation_result_status=True,
            job={"test_case": "happy_path_mongo"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )

        # Act
        sut.initialize_storage(test_run_metadata)
        is_saved = sut.save(fake_result)

        # Assert
        assert is_saved is True
        client = MongoClient(connection_string)
        db = client[db_name]
        collection = db["validation_results"]

        # Search the database for the document
        saved_doc = collection.find_one(
            {"test_run_id": "run_mongo_999", "job.test_case": "happy_path_mongo"}
        )

        #Teardown
        client.drop_database(db_name)
        client.close()

        #Assert
        assert saved_doc is not None
        assert saved_doc["validation_result_status"] is True