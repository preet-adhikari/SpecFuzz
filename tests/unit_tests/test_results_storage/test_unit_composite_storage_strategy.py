from unittest.mock import MagicMock

from execution_engine.execution_result import ExecutionResult
from test_results_storage.composite_storage_strategy.base import CompositeStorageStrategy
from validation_engine.validation_result import ValidationResult


class TestUnitCompositeStorageStrategy:
    def test_composite_storage_strategy_delegates_initialize_storage_to_all_strategies(self):
        # Arrange
        mock_strategy_1 = MagicMock()
        mock_strategy_2 = MagicMock()

        sut = CompositeStorageStrategy([mock_strategy_1, mock_strategy_2])
        metadata = {
            "test_run_id" : "run_composite_001",
            "target" : "sample_api"
        }

        # Act
        sut.initialize_storage(metadata)

        # Assert
        mock_strategy_1.initialize_storage.assert_called_once_with(metadata)
        mock_strategy_2.initialize_storage.assert_called_once_with(metadata)

    def test_composite_strategy_delegates_save_storage_to_all_strategies(self):
        # Arrange
        mock_strategy_1 = MagicMock()
        mock_strategy_1.save.return_value = True
        mock_strategy_2 = MagicMock()
        mock_strategy_2.save.return_value = True

        sut = CompositeStorageStrategy([mock_strategy_1, mock_strategy_2])
        fake_result = ValidationResult(
            validation_result_status=True,
            job={"test_case": "composite_path"},
            execution_result=ExecutionResult(
                is_success=True, response_time=0.1, status_code=200
            ),
            validation_context=[],
        )

        # Act
        is_saved = sut.save(fake_result)

        #Assert
        mock_strategy_1.save.assert_called_once_with(fake_result)
        mock_strategy_2.save.assert_called_once_with(fake_result)

        assert is_saved is True
