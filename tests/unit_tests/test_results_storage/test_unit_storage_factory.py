from test_results_storage.composite_storage_strategy.base import CompositeStorageStrategy
from test_results_storage.file_storage_strategy import FileStorageStrategy
from test_results_storage.mongodb_storage_strategy import MongoDBStorageStrategy
from test_results_storage.storage_factory.base import StorageFactory


class TestUnitStorageFactory:
    def test_unit_storage_factory_returns_composite_strategy_for_all_storage_strategies(self):
        config = {
            "base_directory": "./sample-test-runs",
            "connection_url": "mongodb://localhost:27017/",
            "database_name": "test_db",
        }

        strategy = StorageFactory.get_storage("all", config)

        assert isinstance(strategy, CompositeStorageStrategy)

        # There are only two strategies present at the moment
        assert len(strategy._strategies) == 2

        file_strategy = strategy._strategies[1]
        mongodb_strategy = strategy._strategies[0]

        assert isinstance(file_strategy, FileStorageStrategy)
        assert file_strategy._base_directory == "./sample-test-runs"

        assert isinstance(mongodb_strategy, MongoDBStorageStrategy)
        assert mongodb_strategy.connection_url == "mongodb://localhost:27017/"
        assert mongodb_strategy.database_name == "test_db"
