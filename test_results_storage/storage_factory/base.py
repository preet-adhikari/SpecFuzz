

from test_results_storage.base import BaseStorageStrategy
from test_results_storage.composite_storage_strategy.base import CompositeStorageStrategy
from test_results_storage.file_storage_strategy import FileStorageStrategy
from test_results_storage.mongodb_storage_strategy import MongoDBStorageStrategy


class StorageFactory:

    @staticmethod
    def get_storage(storage_type: str, config: dict) -> BaseStorageStrategy:
        """
        Builds and returns the appropriate storage strategy based on the requested type.
        """
        if storage_type == "file":
            base_dir = config.get("base_directory", "./specfuzz_runs")
            return FileStorageStrategy(base_directory=base_dir)

        elif storage_type == "mongo":
            return MongoDBStorageStrategy(
                connection_url=config["connection_url"],
                database_name=config["database_name"],
            )

        elif storage_type == "all":
            base_dir = config.get("base_directory", "./specfuzz_runs")
            file_strategy = FileStorageStrategy(base_directory=base_dir)

            mongo_strategy = MongoDBStorageStrategy(
                connection_url=config["connection_url"],
                database_name=config["database_name"],
            )

            return CompositeStorageStrategy([mongo_strategy, file_strategy])

        else:
            # The immediate crash if the CLI receives an invalid command
            raise ValueError(f"Unsupported storage type: {storage_type}")
