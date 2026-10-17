from typing import Any, Dict, List

from validation_engine.api_spec_validator_strategy.base import APISpecValidatorStrategy


class OpenAPIV3xxValidatorStrategy(APISpecValidatorStrategy):

    def __init__(self) -> None:
        self._openapi_to_python_types = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }

    def validate(
        self, expected_response: Any, actual_response: Any
    ) -> tuple[bool, List[Dict[str, Any]]]:
        validation_context: list[dict[str, Any]] = []

        if isinstance(actual_response, dict):
            return self._validate_object(
                expected_response.get("schema", {}), actual_response, validation_context
            )

        return False, [
            {
                "field": "root",
                "rule": "invalid_payload",
                "message": "Expected JSON object",
            }
        ]

    def _validate_object(
        self,
        expected_response: dict,
        actual_response: dict,
        validation_context: list[dict[str, Any]],
        current_path: str = "",
    ):
        required_list = expected_response.get("required", [])

        for required_item in required_list:
            if required_item not in actual_response:
                validation_context.append(
                    {
                        "field": (
                            f"{current_path}.{required_item}"
                            if current_path
                            else required_item
                        ),
                        "rule": "required",
                        "message": "Missing required key",
                    }
                )


        expected_response_properties = expected_response.get("properties", {})

        for key, value in actual_response.items():
            if key in expected_response_properties:
                full_field_path = f"{current_path}.{key}" if current_path else key
                expected_type_string = expected_response_properties[key].get("type")

                if expected_type_string in self._openapi_to_python_types:
                    expected_python_type = self._openapi_to_python_types[expected_type_string]

                    actual_type_name = type(value).__name__

                    if not isinstance(value, expected_python_type):
                        validation_context.append(
                            {
                                "field": full_field_path,
                                "rule": "type",
                                "message": f"Expected {expected_type_string}, got {actual_type_name}",
                            }
                        )
                if expected_type_string == "array":
                    expected_item_type_string = (
                        expected_response_properties[key].get("items", {}).get("type")
                    )

                    if expected_item_type_string in self._openapi_to_python_types:
                        expected_item_python_type = self._openapi_to_python_types[
                            expected_item_type_string
                        ]

                        for index, item in enumerate(value):
                            if not isinstance(item, expected_item_python_type):
                                validation_context.append(
                                    {
                                        "field": f"{full_field_path}[{index}]",
                                        "rule": "item_type",
                                        "message": f"Mismatch in array, Expected {expected_item_type_string}, got {type(item).__name__}",
                                    }
                                )

                if expected_type_string == "object" and isinstance(value, dict):
                    new_path = key if current_path == "" else f"{current_path}.{key}"
                    self._validate_object(
                        expected_response=expected_response_properties[key],
                        actual_response=value,
                        validation_context=validation_context,
                        current_path=new_path,
                    )

        is_sucessful = len(validation_context) == 0
        return is_sucessful, validation_context
