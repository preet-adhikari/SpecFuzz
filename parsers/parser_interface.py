from abc import ABC, abstractmethod
from parsers.parsed_endpoint_data import ParsedDataPackage

class BaseParserType(ABC):
    @abstractmethod
    def parse(self) -> ParsedDataPackage:
        pass

