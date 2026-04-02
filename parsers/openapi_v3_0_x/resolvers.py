import sys
import os
from functools import reduce
import copy
from load_spec_file import load_spec_file


def find_and_resolve_refs(
    current_node: dict, master_dict: dict, file_path, visted_nodes=None
):

    # To resolve cyclic reference
    if visted_nodes is None:
        visted_nodes = set()

    # If conditions to check the data types when we're looking for the $ref key inside the JSON dictionary
    if isinstance(current_node, dict):
        # print(json.dumps(current_node, indent=4))
        # sys.exit(1)
        if "$ref" in current_node:
            ref_path = current_node["$ref"]
            if ref_path in visted_nodes:
                return f"Current node: {current_node}"
            visted_nodes.add(ref_path)
            # We need to split the $ref paths based on the requirements from: https://spec.openapis.org/oas/v3.0.0.html#reference-object

            ref_file_path, _, ref_relative_path = ref_path.partition("#")

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
                    find_and_resolve_refs(
                        extracted_ref_relative_data,
                        master_dict,
                        file_path,
                        visted_nodes,
                    )
                    del current_node["$ref"]
                    visted_nodes.remove(ref_path)
                    current_node.update(extracted_ref_relative_data)
                pass
            else:
                # Now we look for the reference of the file
                original_file_path, _ = file_path.rsplit("/", maxsplit=1)
                if not os.path.exists(original_file_path + "/" + ref_file_path):
                    print(
                        f"⛔️Error: The file in your {ref_path} ---> '{original_file_path + '/' + ref_file_path}' was not found. Testing cannot continue..."
                    )
                    sys.exit(1)
                referenced_file_data = load_spec_file(
                    original_file_path + "/" + ref_file_path
                )

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
                    find_and_resolve_refs(
                        extracted_data, referenced_file_data, file_path, visted_nodes
                    )
                    del current_node["$ref"]
                    visted_nodes.remove(ref_path)
                    current_node.update(extracted_data)

        else:
            for key, value in current_node.items():
                find_and_resolve_refs(value, master_dict, file_path, visted_nodes)

    # If while looping, we get a list
    elif isinstance(current_node, list):
        for item in current_node:
            find_and_resolve_refs(item, master_dict, file_path, visted_nodes)

    # We don't do anything for strings, integers and other primitive data types
    else:
        pass
