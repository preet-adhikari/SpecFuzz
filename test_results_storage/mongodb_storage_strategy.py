import copy
from typing import Any, List

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from test_results_storage.base import BaseStorageStrategy
from validation_engine.validation_result import ValidationResult
from dataclasses import asdict

class MongoDBStorageStrategy(BaseStorageStrategy):
    def __init__(self, connection_url:str, database_name:str = "specfuzz_db") -> None:
        self.connection_url = connection_url
        self.database_name = database_name
        self.client = None
        self.db = None
        self.collection = None
        self.current_run_id = None

    def initialize_storage(self, test_run_metadata: dict) -> None:
        try:
            # Connect to the Docker Container
            self.client = MongoClient(self.connection_url)

            # Verify the connection works
            self.client.admin.command('ping')

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
            total = self.collection.count_documents({"test_run_id": test_run_metadata_id})
            passed = self.collection.count_documents({
                "test_run_id": test_run_metadata_id, 
                "validation_result_status": True
            })

            failed = self.collection.count_documents({
                "test_run_id": test_run_metadata_id, 
                "validation_result_status": False
            })
            return {"total": total, "passed": passed, "failed": failed}
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return {"total": 0, "passed": 0, "failed": 0}

    def get_test_run_details(self, test_run_metadata_id: str) -> Any:
        #TODO defensive code here

        try:
            metadata = self.metadata_collection.find_one({"test_run_id": test_run_metadata_id})
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return None
        
        if metadata is None:
            raise ValueError(f"Test run {test_run_metadata_id} doesn't exist.")

        try:
            raw_data = self.collection.find({"test_run_id" : test_run_metadata_id})
        except Exception as e:
            print(f"Failed to get summary: {e}")
            return None

        result_dict = {"metadata" : metadata, "results" : []}
        return result_dict


        


