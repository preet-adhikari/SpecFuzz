from .parsed_endpoint_data import ParsedEndpointData, PathEndpointData
# from .parsed_endpoint_data import ServerData, ResolvedSecurity, SecurityRequirement, PathEndpointData, ParsedDataPackage
import json
import sys
from dataclasses import asdict
from urllib.parse import urlsplit
# For regular expression
import re

# TODO Handle the server items by adding them to a data variable
def handle_servers(server_items: dict):
    if "servers" in server_items:
        for server_item in server_items["servers"]:
            # Checking url presence and continuing early
            if "url" not in server_item or not server_item["url"]:
                print("[WARN] Server entry missing 'url' key or is empty. Skipping.")
                continue

            url_str = server_item["url"]

            # Validation flag to check if the url is true or not
            is_valid_url = False

            try:
                url_component = urlsplit(url_str)
                # For Absolute URL
                if url_component.scheme:
                    if not url_component.netloc:
                        print(f"[WARN] Invalid Absolute URL (missing domain): '{url_str}'. Skipping.")
                        continue
                    # Adding variable check here
                    # Checking server variables using regex
                    variable_search_pattern = r'\{([^}]+)\}'
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
                                        print(f"[WARN] Malformed URL because both default and enum are missing for the variable. {url_str}")
                                        # Using break here because the URL is already malformed
                                        break
                                else:
                                    print(f"[WARN] Malformed URL because the variable in the url is missing it's data. Skipping. {url_str}")
                                    is_valid_url = False
                                    # Using break here because the URL is already malformed
                                    break
                        else:
                            if is_valid_url == False:
                                print(f"[WARN] Malformed URL because the expected variable in the URL is missing due to an unexisting variables block. {url_str}")

                    # Case where server variables don't exist but the URL is a standard static URL
                    else:
                        print(f"Server variables : {server_variables}")
                        print(f"[OK] Absolute URL detected: '{url_str}'")
                        continue

                    # Check if URL is valid or not
                    if is_valid_url == False:
                        # print(f"[WARN] Malformed URL. {url_str}")
                        continue

                    print(f"Server variables : {server_variables}")
                    print(f"[OK] Absolute URL detected: '{url_str}'")
                    continue

                # Handling URLs with double slash
                if url_component.path.startswith("//"):
                    print(f"[WARN] Malformed URL: '{url_str}'. Skipping.")
                    continue

                # For Relative URL
                if url_component.path.startswith("/"):
                    print(f"[OK] Relative URL detected: '{url_str}'")
                    continue

                # Missing Protocol
                if "." in url_component.path.split("/")[0]:
                    print(f"[WARN] Missing protocol scheme on domain: '{url_str}'. Skipping.")
                    continue

                # Catch any remaining issues
                print(f"[WARN] Invalid URL format: '{url_str}'. Skipping.")   

            except ValueError as e:
                print(f"[ERROR] URL parsing crashed on '{url_str}': {e}. Skipping.")
                continue
    pass

def parse_openapi_endpoints(processed_spec: dict):
    parsed_endpoint_data = ParsedEndpointData()
    # parsed_endpoint_data = ParsedDataPackage()
    # print(json.dumps(processed_spec, indent=4))
    # sys.exit(1)

    # # Insert servers and security
    # if "servers" in processed_spec:
    #     parsed_endpoint_data.servers = processed_spec["servers"]
    # if "security" in processed_spec:
    #     parsed_endpoint_data.security = processed_spec["security"]

    # Parsing global servers
    if "servers" in processed_spec:
        # TODO add data variables to save the servers
        handle_servers(processed_spec)
        sys.exit(1)    

    # Process path and insert it
    if "paths" in processed_spec:
        # print(json.dumps(processed_spec["paths"], indent=4))

        for route_path, path_items in processed_spec["paths"].items():

            for http_method, operation_details in path_items.items():

                valid_methods = ["get", "post", "put", "patch", "delete"]
                if http_method.lower() not in valid_methods:
                    continue

                operation = PathEndpointData(
                    path=route_path,
                    method=http_method.upper(),
                    servers=operation_details.get("servers") if operation_details.get("servers") else processed_spec["servers"],
                    security=operation_details.get("security") if operation_details.get("security") else processed_spec["security"],
                    request_body=operation_details.get("requestBody"),
                    response=operation_details.get("responses")
                )

                parsed_endpoint_data.operations.append(operation)

    # print(json.dumps(asdict(parsed_endpoint_data), indent=4))
    # print(parsed_endpoint_data)
    return parsed_endpoint_data
