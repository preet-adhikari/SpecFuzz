from __future__ import annotations
from parsers.parser_interface import BaseParserType
from parsers.openapi_parser import OpenAPIParser

class SpecFactory:
    # This is the method where we do a simple peek into the file to determine if it needs an OpenAPI parser or something else.  
    # Using staticmethod here because it is logically related to SpecFactory but it doesn't need the class object.
    # This peek is simple and not too deep.
    @staticmethod
    def peek_parser_type(file_path: str) -> BaseParserType:
        with open(file_path, "r") as file:
            # Goes through the file object, reads the first line
            first_line = file.readline().strip()
            if "openapi" in first_line:
                return OpenAPIParser(file_path)
            else:
                raise ValueError("Unknown Format.")