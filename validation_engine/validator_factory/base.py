

from abc import ABC

from validation_engine.api_spec_validator_strategy.base import APISpecValidatorStrategy
from validation_engine.api_spec_validator_strategy.openapiv3xx_validator_strategy import OpenAPIV3xxValidatorStrategy


class ValidatorFactory(ABC):
    def __init__(self) -> None:
        self._registry = {
            "openapi_v3xx" : OpenAPIV3xxValidatorStrategy()
        }

    def get_validator(self, spec_name: str) -> APISpecValidatorStrategy:
        validator = self._registry.get(spec_name)

        if not validator:
            raise ValueError(f"Validator not available for given spec name '{spec_name}'")

        return validator
