from abc import ABC, abstractmethod

class FuzzingStrategy(ABC):
    @abstractmethod
    def generate_payload(self, parsed_endpoint_data: dict) -> dict:
        """Every strategy must take the parsed spec and return a JSON payload"""
        pass


class HappyPathStrategy(FuzzingStrategy):
    def generate_payload(self, parsed_endpoint_data: dict) -> dict:
        # Implement logic for happy paths
        # return super().generate_payload(parsed_endpoint_data)
        pass

class MissingRequiredFieldsStrategy(FuzzingStrategy):
    def generate_payload(self, parsed_endpoint_data: dict) -> dict:
        # return super().generate_payload(parsed_endpoint_data)
        pass

class TypeMismatchStrategy(FuzzingStrategy):
    def generate_payload(self, parsed_endpoint_data: dict) -> dict:
        # return super().generate_payload(parsed_endpoint_data)
        pass

