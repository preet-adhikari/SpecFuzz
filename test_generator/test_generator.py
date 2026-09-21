import pprint
import sys

from parsers.parsed_endpoint_data import ParsedDataPackage
from test_generator.fuzzing_strategy import FuzzingStrategy
import random
import time

class TestGenerator:
    def __init__(self, strategy: FuzzingStrategy, seed: int | None = None):
        self._strategy = strategy

        # Storing seed so the user can see which random seed ran the fuzzing process
        if seed is None:
            seed = int(time.time())
        
        self._seed = seed
        # Setting the seed here
        random.seed(self._seed)


    def set_strategy(self, strategy: FuzzingStrategy):
        self._strategy = strategy

    def generate_test_cases(self, parsed_endpoint_data: ParsedDataPackage) -> list:
        # Main data where all of the tests reside
        blueprints = []

        for operation in parsed_endpoint_data.operations:

                raw_request_body = operation.request_body or {}

                

                request_body = raw_request_body.get("content",{}).get("application/json",{}).get("schema",{})
                if not request_body:
                    request_body = {}

                # Creating 5 test cases for now    
                for i in range(5):
                    path_params = self._strategy.generate_path_params(operation.parameters)
                    fuzzed_endpoint = operation.path.format(**path_params)
                    payload, expected_response = self._strategy.generate_payload(request_body,operation.response or {})
                # Attach security placeholders here
                    security_instructions = []

                    if operation.security:
                        primary_requirement = operation.security[0]
                        for scheme in primary_requirement.schemes:
                            mechanics = scheme.mechanics or {}
                            security_instructions.append({
                                "scheme_name": scheme.scheme_name,
                                "type": mechanics.get("type"),         
                                "in": mechanics.get("in", "header"),   
                                "key_name": mechanics.get("name", "Authorization"), 
                                "scopes": scheme.applied_scopes,
                                "inject_token": f"<INJECT_{scheme.scheme_name.upper()}_HERE>"
                            })

                    base_url = "http://localhost:8080" # Keeping this as default for now
                    # If the parser hands a list of servers, grab the first one
                    if isinstance(operation.servers, list):
                        base_url = operation.servers[0].url
                    # If the parser hands a single ServerData object directly
                    else:
                        base_url = operation.servers.url
                        
                    full_endpoint_url = f"{base_url}{fuzzed_endpoint}"
                    
                    # Final blueprint
                    blueprint = {
                        "endpoint": full_endpoint_url,
                        "method": operation.method,
                        "payload": payload,
                        "expected_response": expected_response,
                        "security" : security_instructions

                    }
                    blueprints.append(blueprint)

        return blueprints
