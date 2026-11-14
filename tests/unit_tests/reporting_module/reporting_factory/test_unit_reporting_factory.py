from unittest.mock import MagicMock

import pytest

from reporting_module.reporting_factory.base import ReportingFactory
from reporting_module.reporting_strategy.cli_reporting_strategy import CLIReportingStrategy


class TestUnitReportingFactory:
    def test_unit_reporting_factory_calls_the_appropriate_strategy(self):
        #Arrange
        sut = ReportingFactory("cli")

        #Act
        strategy = sut.choose_reporting_strategy()

        #Assert
        assert isinstance(strategy, CLIReportingStrategy)

    def test_unit_reporting_factory_raises_valuerror_if_strategy_is_inappropriate(self):
        #Arrange
        sut = ReportingFactory("apple")
        #Act
        
        with pytest.raises(ValueError, match="Inappropriate reporting strategy"):
            sut.choose_reporting_strategy()
        