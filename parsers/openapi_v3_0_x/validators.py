import sys
import re

def check_and_validate_specification_version(spec_data: dict) -> bool:
    """
    A function that checks and validates the specification data
    """
    # Getting the version string. Will default to an empty string if there is no openapi key.

    spec_version = spec_data.get("openapi", "")
    if not spec_version:
        raise ValueError(
            "Invalid specification file. The openapi key is not present."
        )

    if "info" not in spec_data:
        raise ValueError("Invalid Spec: Missing required 'info' object.")

    if "paths" not in spec_data:
        raise ValueError(
            "Invalid Spec: Missing 'paths' object. There is nothing to test"
        )

    pattern = r"^3\.\d+\.\d+$"

    if not re.match(pattern, spec_version):
        raise ValueError(
            f"Unsupported OpenAPI version: '{spec_version}'. We only work with version 3.x.x"
        )

    return True

