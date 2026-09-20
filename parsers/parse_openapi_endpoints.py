# from .parsed_endpoint_data import ParsedEndpointData, PathEndpointData, ServerData
from parsers.openapi_v3_0_x.normalizers import handle_servers, handle_security
from .parsed_endpoint_data import (
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


def parse_openapi_endpoints(processed_spec: dict):
    parsed_endpoint_data = ParsedDataPackage()
    # print(json.dumps(processed_spec, indent=4))
    # sys.exit(1)

    # Parsing global servers
    global_servers = []
    if "servers" in processed_spec:
        pass
        # TODO add data variables to save the servers
        global_servers = handle_servers(processed_spec)
        if global_servers:
            global_servers = global_servers[0]

    # Parsing global security
    global_security = []
    if "security" in processed_spec:
        global_security = handle_security(processed_spec)
        # print(json.dumps(global_security, indent=4))
        # print(global_security)
        # json_string = json.dumps(
        #     global_security, default=lambda o: o.__dict__, indent=4
        # )
        # print(json_string)
        # sys.exit(1)
        pass

    # Process path and insert it
    if "paths" in processed_spec:
        # print(json.dumps(processed_spec["paths"], indent=4))

        for route_path, path_items in processed_spec["paths"].items():
            path_servers = []
            path_servers = handle_servers(path_items)
            route_path_server = None
            route_path_security = None

            if path_servers:
                # Selecting the first available server for now
                route_path_server = path_servers[0]

            for path_method, operation_details in path_items.items():

                valid_methods = ["get", "post", "put", "patch", "delete"]
                if path_method.lower() not in valid_methods:
                    continue

                override_global_security = False
                # Checking for servers again at the path method level
                operation_detail_path_servers = None
                operation_detail_path_servers = handle_servers(operation_details)
                if operation_detail_path_servers:
                    route_path_server = operation_detail_path_servers[0]

                operation_detail_path_security = None
                if operation_details.get("security") == []:
                    override_global_security = True
                operation_detail_path_security = handle_security(
                    operation_details,
                    processed_spec.get("components", {}).get("securitySchemes",{}),
                )
                

                operation = PathEndpointData(
                    path=route_path,
                    method=path_method.upper(),
                    servers=route_path_server if route_path_server else global_servers,
                    security=[] if override_global_security else (operation_detail_path_security if operation_detail_path_security else global_security),
                    request_body=operation_details.get("requestBody", {}),
                    response=operation_details.get("responses", {}),
                    parameters=operation_details.get("parameters", [])
                )

                parsed_endpoint_data.operations.append(operation)

    return parsed_endpoint_data
