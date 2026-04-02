from abc import ABC, abstractmethod
from typing import Any, Dict
import random
import string

class FuzzingStrategy(ABC):
    @abstractmethod
    def generate_payload(self, parsed_endpoint_data: dict) -> dict:
        """Every strategy must take the parsed spec and return a JSON payload"""
        pass


class HappyPathStrategy(FuzzingStrategy):
    """Generates 100% valid data based on the schema rules."""

    def generate_payload(self, schema: Dict[str, Any]) -> Any:
        if not schema:
            return None

        # 1. Short-circuits: If there's a hardcoded example or enum, use it safely!
        if "example" in schema:
            return schema["example"]
        if "enum" in schema:
            return random.choice(schema["enum"])

        schema_type = schema.get("type")

        # 2. RECURSION: Handling Objects
        if schema_type == "object":
            payload = {}
            properties = schema.get("properties", {})
            for key, prop_schema in properties.items():
                # The function calls itself to figure out what the property is!
                payload[key] = self.generate_payload(prop_schema)
            return payload

        # 3. RECURSION: Handling Arrays
        elif schema_type == "array":
            items_schema = schema.get("items", {})
            # Generate a list with 1 to 3 valid items by calling itself
            return [
                self.generate_payload(items_schema) for _ in range(random.randint(1, 3))
            ]

        # 4. Base Cases: Generating Primitives
        elif schema_type == "string":
            return "valid_" + "".join(random.choices(string.ascii_letters, k=6))
        elif schema_type in ["integer", "number"]:
            return random.randint(1, 100)
        elif schema_type == "boolean":
            return random.choice([True, False])

        return None


class MissingRequiredFieldsStrategy(FuzzingStrategy):
    """Purposefully deletes a required field to trigger a 400 Bad Request."""

    def __init__(self):
        self.base_generator = HappyPathStrategy()

    def generate_payload(self, schema: Dict[str, Any]) -> Any:
        # Build a perfectly valid payload first
        valid_payload = self.base_generator.generate_payload(schema)

        # If it's not an object or has no required fields, we can't break it this way
        if schema.get("type") != "object" or not schema.get("required"):
            return valid_payload

        # The Sabotage: Pick a random required field and delete it
        required_fields = schema.get("required", [])
        field_to_remove = random.choice(required_fields)

        if field_to_remove in valid_payload:
            del valid_payload[field_to_remove]

        return valid_payload


class TypeMismatchStrategy(FuzzingStrategy):
    """Purposefully swaps a data type (e.g., sends a dict instead of a string)."""

    def __init__(self):
        self.base_generator = HappyPathStrategy()

    def generate_payload(self, schema: Dict[str, Any]) -> Any:
        # 1. Build a perfectly valid payload first
        valid_payload = self.base_generator.generate_payload(schema)

        if schema.get("type") != "object" or not valid_payload:
            return valid_payload

        # 2. The Sabotage: Pick a random property that we just generated
        key_to_corrupt = random.choice(list(valid_payload.keys()))

        # 3. Replace the valid data with a wildly incorrect data type (an arbitrary dict)
        valid_payload[key_to_corrupt] = {
            "corrupted_type": "I should not be a dictionary"
        }

        return valid_payload
