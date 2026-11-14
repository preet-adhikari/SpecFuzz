import copy
from typing import Any, List

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from shared.dto_contracts import TestCaseDetail, TestRunResults
from test_results_storage.base import BaseStorageStrategy
from validation_engine.validation_result import ValidationResult
from dataclasses import asdict


class MongoDBStorageStrategy(BaseStorageStrategy):
    def __init__(self, connection_url: str, database_name: str = "specfuzz_db") -> None:
        self.connection_url = connection_url
        self.database_name = database_name
        self.client = None
        self.db = None
        self.collection = None
        self.current_run_id = None
        self.metadata_collection = None

    def initialize_storage(self, test_run_metadata: dict) -> None:
        try:
            # Connect to the Docker Container
            self.client = MongoClient(self.connection_url)

            # Verify the connection works
            self.client.admin.command("ping")

            self.db = self.client[self.database_name]
            self.collection = self.db["validation_results"]

            self.current_run_id = test_run_metadata.get("test_run_id", "unknown_run")
            test_run_metadata_clone = copy.deepcopy(test_run_metadata)

            # Save metadata to a different collection for stats
            self.metadata_collection = self.db["test_runs"]
            self.metadata_collection.insert_one(test_run_metadata_clone)
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None

    def save(self, validation_result: ValidationResult) -> bool:
        """Insert a single test_document to MongoDB collection"""
        if self.client is None or self.collection is None:
            return False

        # Convert into dictionary
        document = asdict(validation_result)

        # Set the test_run_id as the current_run_id to query it
        document["test_run_id"] = self.current_run_id

        # Insert it into the database
        document_to_be_inserted = copy.deepcopy(document)

        try:
            self.collection.insert_one(document_to_be_inserted)
            return True
        except Exception as e:
            print(f"Failed to save document: {e}")
            return False

    def save_batch(self, results: List[ValidationResult]) -> bool:
        if self.client is None or self.collection is None:
            return False

        documents = []
        for result in results:
            doc = asdict(result)
            doc["test_run_id"] = self.current_run_id
            documents.append(doc)
        try:
            self.collection.insert_many(documents)
            return True
        except Exception as e:
            print(f"Failed to save batch : {e}")
            return False

    def get_summary(self, test_run_metadata_id: str) -> Any:
        if self.client is None or self.collection is None:
            return {"total": 0, "passed": 0, "failed": 0}

        try:
            total = self.collection.count_documents(
                {"test_run_id": test_run_metadata_id}
            )
            passed = self.collection.count_documents(
                {"test_run_id": test_run_metadata_id, "validation_result_status": True}
            )

            failed = self.collection.count_documents(
                {"test_run_id": test_run_metadata_id, "validation_result_status": False}
            )
            return {"total": total, "passed": passed, "failed": failed}
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return {"total": 0, "passed": 0, "failed": 0}

    def get_test_run_details(self, test_run_metadata_id: str) -> Any:
        if self.collection is None or self.metadata_collection is None:
            raise RuntimeError("Database collections are not initialized.")

        try:
            metadata = self.metadata_collection.find_one(
                {"test_run_id": test_run_metadata_id}
            )
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return None

        if metadata is None:
            raise ValueError(f"Test run {test_run_metadata_id} doesn't exist.")

        try:
            raw_data = self.collection.find({"test_run_id": test_run_metadata_id})
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return None
        if "_id" in metadata:
            metadata.pop("_id")
        result_dict = {"metadata": metadata, "results": []}
        for record in raw_data:
            if "_id" in record:
                record.pop("_id", None)
            execution_result = record.get("execution_result", {})
            if ("response_body" in execution_result) and isinstance(
                execution_result["response_body"], bytes
            ):
                execution_result["response_body"] = execution_result[
                    "response_body"
                ].decode("utf-8", errors="replace")
            result_dict["results"].append(record)

        result = self._map_to_dto(result_dict)
        return result

    def _map_to_dto(self, result_dict: dict) -> TestRunResults:
        test_case_detail_list = []
        
        total_endpoint_counter = 0
        total_crash_counter = 0
        total_request_counter = 0
        total_validation_passed = 0
        
        for record in result_dict.get("results", []):
            test_case = record.get("job", {}).get("test_case", {})
            execution_result = record.get("execution_result", {})
            
            total_endpoint_counter += 1
            attempts = record.get("job", {}).get("tries", 0)
            total_request_counter += attempts
            
            status_code = str(execution_result.get("status_code", ""))
            if status_code.startswith("5"):
                total_crash_counter += 1
                
            validation_passed = record.get("validation_result_status", False)
            if validation_passed:
                total_validation_passed += 1
                
            detail = TestCaseDetail(
                endpoint=test_case.get("endpoint", ""),
                method=test_case.get("method", ""),
                attempts=attempts,
                response_status_code=status_code,
                response_time_taken=execution_result.get("response_time", 0.0),
                validation_passed=validation_passed,
                request_headers=record.get("job", {}).get("final_headers", {}),
                payload=test_case.get("payload", {}),
                expected_response_codes=list(test_case.get("expected_response", {}).keys()),
                response_body=execution_result.get("response_body", ""),
                response_header=execution_result.get("response_header", {}),
                validation_context=record.get("validation_context", [])
            )
            
            test_case_detail_list.append(detail)

        passed_percentage = 0.0
        if total_endpoint_counter > 0:
            passed_percentage = (total_validation_passed / total_endpoint_counter) * 100

        metadata = result_dict.get("metadata", {})
        
        return TestRunResults(
            test_run_id=metadata.get("test_run_id", ""),
            timestamp=metadata.get("timestamp", ""),
            crash_count=total_crash_counter,
            total_endpoints=total_endpoint_counter,
            total_requests=total_request_counter,
            random_seed=metadata.get("random_seed", 0),
            test_case_details=test_case_detail_list,
            passed_percentage=passed_percentage
        )


