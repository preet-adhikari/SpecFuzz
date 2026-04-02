from parsers.parser_interface import BaseParserType
from load_spec_file import load_spec_file
from parsers.openapi_v3_0_x.validators import check_and_validate_specification_version
from parsers.openapi_v3_0_x.resolvers import find_and_resolve_refs
from parsers.openapi_v3_0_x.normalizers import normalize_schema
from parsers.parse_openapi_endpoints import parse_openapi_endpoints

class OpenAPIParser(BaseParserType):
    def parse(self, file_path: str):
        raw_dict = load_spec_file(file_path)
        if check_and_validate_specification_version(raw_dict):
            find_and_resolve_refs(raw_dict, raw_dict, file_path)
            processed_spec = normalize_schema(raw_dict)
            parsed_endpoint_data = parse_openapi_endpoints(processed_spec)
            return parsed_endpoint_data
