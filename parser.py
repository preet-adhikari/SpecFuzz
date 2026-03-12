import os
import json
import re
import sys
from resolve_ref_openapi_spec import find_and_resolve_refs
from load_spec_file import load_spec_file


def check_and_validate_specification_version(spec_data: dict):
    """
    A function that checks and validates the specification data
    """
    # Getting the version string. Will default to an empty string if there is no openapi key.
    try:
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
    except AttributeError as e:
        print("Empty JSON or YAML file. Please input an OpenAPI spec file.")
        sys.exit(1)

    except ValueError as e:
        print(f"⛔️{e}")
        sys.exit(1)


def normalize_schema(processed_spec: dict):

    if not isinstance(processed_spec, (dict, list)):
        return processed_spec

    # First we identify nodes
    # List
    elif isinstance(processed_spec, list):
        for item in processed_spec:
            normalize_schema(item)

    # Dictionary
    if isinstance(processed_spec, dict):

        for key, value in processed_spec.items():
            processed_spec[key] = normalize_schema(value)  

        if "allOf" in processed_spec:
            inherited_properties = {}
            existing_required = processed_spec.get("required", [])
            target_normalized_required = set(existing_required)

            for sub_schema in processed_spec["allOf"]:
                if "properties" in sub_schema:
                    inherited_properties.update(sub_schema["properties"])
                if "required" in sub_schema:
                    target_normalized_required.update(sub_schema["required"])

            # Finally
            inherited_properties.update(processed_spec.get("properties",""))
            processed_spec["properties"] = inherited_properties
            processed_spec["required"] = sorted(list(target_normalized_required))
            processed_spec["type"] = "object"
            del processed_spec["allOf"]
    return processed_spec                   


def process_spec_file(file_path: str):
    spec_data = load_spec_file(file_path)
    if check_and_validate_specification_version(spec_data):
        find_and_resolve_refs(spec_data, spec_data, file_path)
        return spec_data


def parser_main(file_path: str):
    processed_spec = process_spec_file(file_path)
    processed_spec = normalize_schema(processed_spec)
    print(json.dumps(processed_spec, indent=4))
    # print(json.dumps(process_spec_file(file_path), indent=4))
