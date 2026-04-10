from fuzzing_strategy import FuzzingStrategy


class TestCaseGenerator:
    def __init__(self, strategy: FuzzingStrategy):
        self._strategy = strategy
        pass

    def set_strategy(self, strategy: FuzzingStrategy):
        self._strategy = strategy

    def create_test_case(self, parsed_endpoint_data: dict) -> dict:
        return self._strategy.generate_payload(parsed_endpoint_data)
