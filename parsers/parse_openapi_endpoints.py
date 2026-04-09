from .parsed_endpoint_data import ParsedEndpointData, PathEndpointData
import json
from dataclasses import asdict

def parse_openapi_endpoints(processed_spec: dict):
    parsed_endpoint_data = ParsedEndpointData()

    # Insert servers and security
    if "servers" in processed_spec:
        parsed_endpoint_data.servers = processed_spec["servers"]
    if "security" in processed_spec:
        parsed_endpoint_data.security = processed_spec["security"]

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
                    request_body=operation_details.get("requestBody"),
                    response=operation_details.get("responses")
                )

                parsed_endpoint_data.operations.append(operation)

    # print(json.dumps(asdict(parsed_endpoint_data), indent=4))
    # print(parsed_endpoint_data)
    return parsed_endpoint_data
