import os
import yaml
import json
import re
import sys
from functools import reduce
import copy

def load_spec_file(file_path: str):
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

def check_and_validate_specification_version(spec_data: dict):
    """
    A function that checks and validates the specification data 
    """
    # Getting the version string. Will default to an empty string if there is no openapi key.
    try: 
        spec_version = spec_data.get("openapi", "")
        if not spec_version:
            raise ValueError("Invalid specification file. The openapi key is not present.")

        if "info" not in spec_data:
            raise ValueError("Invalid Spec: Missing required 'info' object.")

        if "paths" not in spec_data:
            raise ValueError("Invalid Spec: Missing 'paths' object. There is nothing to test")

        pattern = r"^3\.\d+\.\d+$"

        if not re.match(pattern, spec_version):
            raise ValueError(f"Unsupported OpenAPI version: '{spec_version}'. We only work with version 3.x.x")

        return True
    except AttributeError as e:
        print("Empty JSON or YAML file. Please input an OpenAPI spec file.")
        sys.exit(1)


    except ValueError as e:
        print(f"⛔️{e}")
        sys.exit(1)

def extract_ref_data_from_ref():
    pass


def find_and_resolve_refs(current_node: dict, master_dict: dict):
    # If conditions to check the data types when we're looking for the $ref key inside the JSON dictionary
    if isinstance(current_node, dict):
        if "$ref" in current_node:
            ref_path = current_node["$ref"]

            # We need to split the $ref paths based on the requirements from: https://spec.openapis.org/oas/v3.0.0.html#reference-object

            ref_file_path, separator, ref_relative_path = ref_path.partition("#")

            # Check if ref_file_path is empty to go for relative reference
            if not ref_file_path:
                # TODO: Only traverse inside the dictionary to look for content in the relative path
                if ref_relative_path:
                    keys_to_navigate = ref_relative_path.strip("/").split("/")

                    current_search_area = master_dict
                    for key in keys_to_navigate:
                        if key in current_search_area:
                            current_search_area = current_search_area[key]
                        else:
                            print(
                                f"⛔️Error: The path '{ref_relative_path}' is broken. Could not find '{key}'."
                            )
                            sys.exit(1)

                    # We're making a different instance here so that if two $ref keys with the same reference exist, they don't update each other in the same dictionary
                    extracted_ref_relative_data = copy.deepcopy(current_search_area) 

                    # Recursively clean the $refs if there are more in the referenced file
                    find_and_resolve_refs(extracted_ref_relative_data, master_dict)
                    del current_node["$ref"]
                    current_node.update(extracted_ref_relative_data)
                pass
            else:
                # Now we look for the reference of the file
                if not os.path.exists(ref_file_path):
                    print(f"⛔️Error: The file in your {ref_path} ---> '{ref_file_path}' was not found. Testing cannot continue...")
                    sys.exit(1)
                referenced_file_data = load_spec_file(ref_file_path)

                if referenced_file_data is not None:
                    # We take in the whole file
                    extracted_data = referenced_file_data

                    if ref_relative_path:
                        keys_to_navigate = ref_relative_path.strip("/").split("/")

                        for key in keys_to_navigate:
                            if key in extracted_data:
                                extracted_data = extracted_data[key]
                            else:
                                print(
                                    f"⛔️Error: The path '{ref_relative_path}' is broken. Could not find '{key}'."
                                )
                                sys.exit(1)

                    # Recursively clean the $refs if there are more in the referenced file
                    find_and_resolve_refs(extracted_data, referenced_file_data)
                    del current_node["$ref"]
                    current_node.update(extracted_data)

        else:
            for key, value in current_node.items():
                find_and_resolve_refs(value, master_dict)     

    # If while looping, we get a list
    elif isinstance(current_node, list):
        for item in current_node:
            find_and_resolve_refs(item, master_dict)

    # We don't do anything for strings, integers and other primitive data types
    else:
        pass

def process_spec_file(file_path: str):
    spec_data = load_spec_file(file_path)
    if check_and_validate_specification_version(spec_data):
        find_and_resolve_refs(spec_data, spec_data)
        print("******************EOP***********************")
        print(json.dumps(spec_data, indent=4))
        pass


def parser_main(file_path: str):
    processed_spec = process_spec_file(file_path)
    # print(json.dumps(process_spec_file(file_path), indent=4))
