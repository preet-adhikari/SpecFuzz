from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import random
import string
import sys
import json
from dataclasses import asdict


class FuzzingStrategy(ABC):
    @abstractmethod
    def generate_payload(
        self, schema: dict, expected_response: dict, http_method: str
    ) -> dict:
        """Every strategy must take the parsed spec and return a JSON payload"""
        pass

    @abstractmethod
    def generate_path_params(self, parameters: list) -> dict:
        pass


class HappyPathStrategy(FuzzingStrategy):
    """Generates 100% valid data based on the schema rules."""

    def generate_payload(
        self, schema: Dict[str, Any], expected_response: dict, http_method: str
    ) -> Any:
        """Process and combine the built payload with the expected response body"""

        expected_response = self._extract_response_codes_from_response(
            expected_response, http_method
        )

        payload = self._build_happypath_data(schema)

        return payload, expected_response

    def _build_happypath_data(self, schema: Dict[str, Any]):
        """Building the HappyPathStrategy Data"""
        if not schema:
            return None
        # For Enums
        if "example" in schema:
            return schema["example"]
        if "enum" in schema:
            return random.choice(schema["enum"])

        schema_type = schema.get("type")

        # Handling objects with recursion
        if schema_type == "object":
            payload = {}
            properties = schema.get("properties", {})
            for key, prop_schema in properties.items():
                # The function calls itself to figure out what the property is!
                payload[key] = self._build_happypath_data(prop_schema)
            return payload

        # Handling arrays with recursion
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            # Do this only when minItems and maxItems aren't set
            # Generate a list with 1 to 3 valid items by calling itself
            raw_max = schema.get("maxItems")
            raw_min = schema.get("minItems")

            generate_range = self._calculate_min_max_bounds(raw_max, raw_min)
            return [
                self._build_happypath_data(items_schema)
                for _ in range(int(generate_range))
            ]

        # Generating primitive data types
        elif schema_type == "string":
            return "valid_" + "".join(random.choices(string.ascii_letters, k=6))
        elif schema_type in ["integer", "number"]:
            if schema_type == "number":
                is_float = True
            else:
                is_float = False
            # Check for maximum and minimum if they exist for numbers and integers
            return self._calculate_min_max_bounds(
                schema.get("maximum"), schema.get("minimum"), is_float
            )
        elif schema_type == "boolean":
            return random.choice([True, False])

        return None

    def generate_path_params(self, parameters: list) -> dict:
        """Takes the parameters list and returns a dictionary of fuzzed values."""
        path_params = {}
        if not parameters:
            return path_params

        for param in parameters:
            param_name = param.get("name")
            param_schema = param.get("schema", {})

            # Only fuzz parameters that are actually in the path(url)
            if param.get("in") == "path" and param_name and param_schema:

                fuzzed_value = self._build_happypath_data(param_schema)
                path_params[param_name] = fuzzed_value

        return path_params

    @staticmethod
    def _extract_response_codes_from_response(
        expected_response: dict, http_method: str
    ) -> dict:
        """Establishes 2XX response codes from the response_body in the specification according to the HTTP methods"""

        if expected_response:
            for code in expected_response:
                if str(code).startswith("2"):
                    return expected_response

        # Check for the HTTP method
        fallback_response = {}
        if http_method == "POST":
            fallback_response = {"201": {}}
        elif http_method == "DELETE":
            fallback_response = {"204": {}}
        else:  # GET, PUT, PATCH
            fallback_response = {"200": {}}

        if not expected_response:
            return fallback_response

        return expected_response | fallback_response

    @staticmethod
    def _calculate_min_max_bounds(max, min, is_float=False) -> float | int:
        """Returns integer or float based on requirement"""

        if is_float:
            if max is not None and min is not None:
                return round(random.uniform(min, max), 2)
            elif max is not None:
                return round(random.uniform(max - 5.0, max), 2)
            elif min is not None:
                return round(random.uniform(min, min + 5.0), 2)
            else:
                return round(random.uniform(1.0, 5.0), 2)

        else:
            if max is not None and min is not None:
                return random.randint(int(min), int(max))
            elif max is not None:
                return random.randint(int(max) - 5, int(max))
            elif min is not None:
                return random.randint(int(min), int(min) + 5)
            else:
                return random.randint(1, 5)


class MissingRequiredFieldsStrategy(FuzzingStrategy):
    """Purposefully deletes a required field to trigger a 400 Bad Request."""

    def __init__(self):
        self.base_generator = HappyPathStrategy()

    def generate_payload(
        self, schema: Dict[str, Any], expected_response: dict, http_method: str
    ) -> Any:
        # Build a perfectly valid payload first
        valid_payload = self.base_generator.generate_payload(
            schema, expected_response, http_method
        )

        # If it's not an object or has no required fields, we can't break it this way
        if schema.get("type") != "object" or not schema.get("required"):
            return valid_payload

        # The Sabotage: Pick a random required field and delete it
        required_fields = schema.get("required", [])
        field_to_remove = random.choice(required_fields)

        if field_to_remove in valid_payload:
            del valid_payload[field_to_remove]

        return valid_payload

    def generate_path_params(self, parameters: list) -> dict:
        pass


class TypeMismatchStrategy(FuzzingStrategy):
    """Purposefully swaps a data type (e.g., sends a dict instead of a string)."""

    def __init__(self):
        self.base_generator = HappyPathStrategy()

    def generate_payload(
        self, schema: Dict[str, Any], expected_response, http_method: str
    ) -> Any:
        # Build a perfectly valid payload first
        valid_payload = self.base_generator.generate_payload(
            schema, expected_response, http_method
        )

        if schema.get("type") != "object" or not valid_payload:
            return valid_payload

        # The Sabotage: Pick a random property that we just generated
        key_to_corrupt = random.choice(list(valid_payload.keys()))

        # Replace the valid data with a wildly incorrect data type (an arbitrary dict)
        valid_payload[key_to_corrupt] = {
            "corrupted_type": "I should not be a dictionary"
        }

        return valid_payload

    def generate_path_params(self, parameters: list) -> dict:
        pass
