import pytest

from validation_engine.api_spec_validator_strategy.openapiv3xx_validator_strategy import OpenAPIV3xxValidatorStrategy
from validation_engine.validator_factory.base import ValidatorFactory


class TestValidatorFactory:
    def test_validator_factory_should_return_openapiv3xx_strategy(self):
        #Arrange
        factory = ValidatorFactory()

        #Act
        sut = factory.get_validator("openapi_v3xx")

        #assert
        assert isinstance(sut, OpenAPIV3xxValidatorStrategy)


    def test_validator_factory_should_raise_value_error_if_validator_not_present(self):
        #Arrange
        sut = ValidatorFactory()
        invalid_validator = "sample"

        #Act
        with pytest.raises(ValueError) as exception:
            sut.get_validator(invalid_validator)

        #Assert
        expected_error_message = "Validator not available for given spec name 'sample'"
        assert str(exception.value) == expected_error_message
            