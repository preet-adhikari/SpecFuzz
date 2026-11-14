from unittest.mock import MagicMock

from test_orchestrator.test_orchestrator import TestOrchestrator


class TestUnitTestOrchestrator:
    def test_orchestrator_initializes_with_injected_storage(self):
        # Arrange
        mock_storage = MagicMock()

        sample_list = []
        sample_int = 0

        #Act
        orchestrator = TestOrchestrator(sample_list, sample_int, mock_storage)

        #Assert
        assert orchestrator._storage == mock_storage