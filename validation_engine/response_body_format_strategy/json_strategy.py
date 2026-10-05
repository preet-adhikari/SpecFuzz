import json
import sys
from typing import Any, Optional

from validation_engine.response_body_format_strategy.base import ResponseBodyFormatStrategy


class JSONStrategy(ResponseBodyFormatStrategy):
    """Parses and handles the content-type that has application/json"""
    def parse(self, response_body_content: bytes) -> Any:
        return json.loads(response_body_content)

    def validate(self, response_body_content: dict, expected_response_body: dict) -> tuple[bool, str]:
        # Compare keys and types
        print("We are in JSON Strategy")
        expected_response_body_properties = expected_response_body.get("schema",{}).get("properties")
        required_list = expected_response_body.get("schema", {}).get("required", [])

        for required_item in required_list:
            if required_item not in response_body_content:
                return False, f"Missing required key, {required_item}"

        openapi_to_python_types = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        
        for key, value in response_body_content.items():
            if key in expected_response_body_properties:
                expected_type_string = expected_response_body_properties[key].get("type")

                if expected_type_string in openapi_to_python_types:
                    expected_python_type = openapi_to_python_types[expected_type_string]

                    if not isinstance(value, expected_python_type):
                        actual_type_name = type(value).__name__
                        return (
                            False,
                            f"Type mismatch for key '{key}': Expected {expected_type_string}, got {actual_type_name}",
                        )

        return True, "Valid JSON"    

        pass
