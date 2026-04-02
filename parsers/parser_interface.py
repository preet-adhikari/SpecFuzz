from abc import ABC, abstractmethod
from parsers.parsed_endpoint_data import ParsedEndpointData

class BaseParserType(ABC):
    @abstractmethod
    def parse(self) -> ParsedEndpointData:
        pass

