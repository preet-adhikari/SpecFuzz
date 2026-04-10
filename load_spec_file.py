import yaml
import json
from typing import Any

def load_spec_file(file_path: str) -> dict[str, Any]:
    """
    A loader that handles both YAML and JSON.
    """
    with open(file_path, "r") as file:
        if file_path.endswith(".json"):
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format: {e}")

        elif file_path.endswith((".yaml", ".yml")):
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format: {e}")

        else:
            raise ValueError(
                "Unsupported file extension. Please use .yaml, .yml or .json file."
            )
