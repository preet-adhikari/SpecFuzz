import pprint

from ..parsed_endpoint_data import (
    ServerData,
    ResolvedSecurity,
    SecurityRequirement,
    PathEndpointData,
    ParsedDataPackage,
)
import json
import sys
from dataclasses import asdict
from urllib.parse import urlsplit

# For regular expression
import re

def normalize_schema(processed_spec: dict) -> dict:

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
            inherited_properties.update(processed_spec.get("properties", ""))
            processed_spec["properties"] = inherited_properties
            processed_spec["required"] = sorted(list(target_normalized_required))
            processed_spec["type"] = "object"
            del processed_spec["allOf"]
    return processed_spec


# TODO move the parse_openapi_endpoints here
# TODO Handle the server items by adding them to a data variable
def handle_servers(server_items: dict):
    extracted_servers = []
    if "servers" in server_items:
        for server_item in server_items["servers"]:
            # Checking url presence and continuing early
            if "url" not in server_item or not server_item["url"]:
                print("[WARN] Server entry missing 'url' key or is empty. Skipping.")
                continue

            url_str = server_item["url"]
            if server_item.get("description"):
                url_description = server_item["description"]
            else:
                url_description = ""

            # Validation flag to check if the url is true or not
            is_valid_url = False

            try:
                if url_str.startswith("//"):
                    print(f"[WARN] Malformed URL: '{url_str}'. Skipping.")
                    continue

                # For Relative URL
                if url_str.startswith("/"):
                    print(f"[OK] Relative URL detected: '{url_str}'")
                    extracted_servers.append(
                        ServerData(url=url_str, description=url_description)
                    )
                    continue
                url_component = urlsplit(url_str)
                # For Absolute URL
                if url_component.scheme:
                    if not url_component.netloc:
                        print(
                            f"[WARN] Invalid Absolute URL (missing domain): '{url_str}'. Skipping."
                        )
                        continue
                    # Adding variable check here
                    # Checking server variables using regex
                    variable_search_pattern = r"\{([^}]+)\}"
                    server_variables = re.findall(variable_search_pattern, url_str)

                    if server_variables:
                        if server_item.get("variables"):
                            for server_variable in server_variables:

                                if server_item["variables"].get(server_variable):
                                    variable_data = server_item["variables"].get(
                                        server_variable
                                    )
                                    if variable_data.get("default"):
                                        url_str = re.sub(
                                            "{" + server_variable + "}",
                                            variable_data.get("default"),
                                            url_str,
                                        )
                                        is_valid_url = True

                                    elif variable_data.get("enum"):
                                        url_str = re.sub(
                                            "{" + server_variable + "}",
                                            variable_data.get("enum")[0],
                                            url_str,
                                        )
                                        is_valid_url = True

                                    else:
                                        is_valid_url = False
                                        print(
                                            f"[WARN] Malformed URL because both default and enum are missing for the variable. {url_str}"
                                        )
                                        # Using break here because the URL is already malformed
                                        break
                                else:
                                    print(
                                        f"[WARN] Malformed URL because the variable in the url is missing it's data. Skipping. {url_str}"
                                    )
                                    is_valid_url = False
                                    # Using break here because the URL is already malformed
                                    break
                        else:
                            if is_valid_url == False:
                                print(
                                    f"[WARN] Malformed URL because the expected variable in the URL is missing due to an unexisting variables block. {url_str}"
                                )

                    # Case where server variables don't exist but the URL is a standard static URL
                    else:
                        print(f"Server variables : {server_variables}")
                        print(f"[OK] Absolute URL detected: '{url_str}'")
                        extracted_servers.append(
                            ServerData(url=url_str, description=url_description)
                        )
                        continue

                    # Check if URL is valid or not
                    if is_valid_url == False:
                        # print(f"[WARN] Malformed URL. {url_str}")
                        continue

                    print(f"Server variables : {server_variables}")
                    print(f"[OK] Absolute URL detected: '{url_str}'")
                    extracted_servers.append(
                        ServerData(url=url_str, description=url_description)
                    )
                    continue

                # Missing Protocol
                if "." in url_component.path.split("/")[0]:
                    print(
                        f"[WARN] Missing protocol scheme on domain: '{url_str}'. Skipping."
                    )
                    continue

                # Catch any remaining issues
                print(f"[WARN] Invalid URL format: '{url_str}'. Skipping.")

            except ValueError as e:
                print(f"[ERROR] URL parsing crashed on '{url_str}': {e}. Skipping.")
                continue

    return extracted_servers


def handle_security(security_items: dict, securitySchemes=None):
    """
    Handles the security portion of the OpenAPI document. It extracts the necessary schemes, mechanics and scopes. Here, mechanics are the securityScheme contents like "type" and "scheme".
    """
    # print(json.dumps(security_items, indent=4))
    # sys.exit(1)
    # This only executes if we're looking at security globally
    if securitySchemes is None:
        try:
            if security_items["components"].get("securitySchemes"):
                securitySchemes = security_items["components"].get("securitySchemes")
                pass
            # securitySchemes doesn't exist
            else:
                print("There are no security schemes for the global security.")
                return
        except KeyError:
            print("The 'components' section is missing from the OpenAPI spec.")
            return
        pass

    
    extracted_resolved_security_schemes = []
    # Global security check over the OpenAPI spec

    if "security" in security_items:
        if not (security_items["security"] == []):
            for security_item in security_items["security"]:
                # if there are more keys, it means there is an AND relationship in the securities
                if len(security_item) > 1:
                    security_requirement_list = SecurityRequirement()
                    for security_scheme_name in security_item:

                        security_requirement_list.schemes.append(
                            ResolvedSecurity(
                                scheme_name=security_scheme_name,
                                mechanics=securitySchemes.get(security_scheme_name),
                                applied_scopes=(
                                    security_item.get(security_scheme_name)
                                    if security_item.get(security_scheme_name)
                                    else []
                                ),
                            )
                        )
                    extracted_resolved_security_schemes.append(
                        security_requirement_list
                    )
                    continue
                else:
                    # Check if the scheme actually exists in securitySchemes
                    # for security_scheme_name in security_item:
                    #     if securitySchemes.get(security_scheme_name):
                    #         extracted_resolved_security_schemes.append(
                    #             ResolvedSecurity(
                    #                 scheme_name=security_scheme_name,
                    #                 mechanics=securitySchemes.get(security_scheme_name),
                    #                 applied_scopes=(
                    #                     security_item.get(security_scheme_name)
                    #                     if security_item.get(security_scheme_name)
                    #                     else []
                    #                 ),
                    #             )
                    #         )
                    # pass
                    for security_scheme_name in security_item:
                        if securitySchemes.get(security_scheme_name):
                            single_requirement = SecurityRequirement()
                            single_requirement.schemes.append(
                                ResolvedSecurity(
                                    scheme_name=security_scheme_name,
                                    mechanics=securitySchemes.get(security_scheme_name),
                                    applied_scopes=(
                                        security_item.get(security_scheme_name)
                                        if security_item.get(security_scheme_name)
                                        else []
                                    ),
                                )
                            )
                            extracted_resolved_security_schemes.append(single_requirement)
    return extracted_resolved_security_schemes
