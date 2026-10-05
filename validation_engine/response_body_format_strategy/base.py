from abc import ABC, abstractmethod
from typing import Any, Optional


class ResponseBodyFormatStrategy(ABC):
    @abstractmethod
    def parse(self, response_body_content: bytes)-> Optional[Any] | None:
        """Parses the response content retreived by the Execution Engine according to the corresponding content-type"""
        pass

    @abstractmethod
    def validate(self, response_body_content: Any, expected_response_body: dict)-> Any:
        """Validate the content from the parse method with the expected_response from the specification"""
        pass

