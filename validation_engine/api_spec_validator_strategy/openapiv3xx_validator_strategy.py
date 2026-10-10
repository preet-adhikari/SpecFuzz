from typing import Any, Dict, List

from validation_engine.api_spec_validator_strategy.base import APISpecValidatorStrategy


class OpenAPIV3xxValidatorStrategy(APISpecValidatorStrategy):
    def __init__(self) -> None:
        self._validation_context : list[dict[str, Any]]= [] 


    def validate(
        self, expected_response: Any, actual_response: Any
    ) -> tuple[bool, List[Dict[str , Any]]]:
        if isinstance(actual_response, dict):
            required_missing = False
            required_list = expected_response.get("schema", {}).get("required", [])

            for required_item in required_list:
                if required_item not in actual_response:
                    self._validation_context.append({
                        "field" : required_item,
                        "rule" : "required",
                        "message" : "Missing required key"
                    })
                    required_missing = True

            if required_missing:
                return False, self._validation_context

            openapi_to_python_types = {
                "string": str,
                "integer": int,
                "number": (int, float),
                "boolean": bool,
                "array": list,
                "object": dict,
            }

            expected_response_properties = expected_response.get("schema", {}).get(
                "properties"
            )

            type_mismatch = False
            for key, value in actual_response.items():
                if key in expected_response_properties:
                    expected_type_string = expected_response_properties[key].get("type")

                    if expected_type_string in openapi_to_python_types:
                        expected_python_type = openapi_to_python_types[
                            expected_type_string
                        ]

                        actual_type_name = type(value).__name__

                        if not isinstance(value, expected_python_type):
                            self._validation_context.append({
                                "field" : key,
                                "rule" : "type",
                                "message" : f"Expected {expected_type_string}, got {actual_type_name}"
                            })
                            type_mismatch = True

                    if expected_type_string == "array":
                        expected_item_type_string = expected_response_properties[key].get("items", {}).get("type")

                        if expected_item_type_string in openapi_to_python_types:
                            expected_item_python_type = openapi_to_python_types[expected_item_type_string]
                            

                            for index, item in enumerate(value):
                                if not isinstance(item, expected_item_python_type):
                                    self._validation_context.append({
                                                                    "field" : f"{key}[{index}]",
                                                                    "rule" : "item_type",
                                                                    "message" : f"Mismatch in array, Expected {expected_item_type_string}, got {type(item).__name__}"
                                                                })
                                    type_mismatch = True
                                    
            if type_mismatch:
                return False, self._validation_context

            return True, []
