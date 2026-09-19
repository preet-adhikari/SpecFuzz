import pytest
from test_generator.fuzzing_strategy import TypeMismatchStrategy


type_mismatch_strategy = TypeMismatchStrategy()

def test_type_mismatch_fuzzing_strategy():
    mock_schema = {
        "required": ["clearance_level", "username"],
        "properties": {
            "username": {"type": "string", "example": "jdoe"},
            "status": {
                "type": "boolean",
                "description": "CHILD DEFINITION: This is the boss. This should win!",
                "example": True,
            },
            "clearance_level": {"type": "integer", "minimum": 0, "maximum": 2},
            "managed_teams": {
                "type": "array",
                "description": "A list of teams this admin manages.",
                "minItems": 3,
                "maxItems": 6,
                "items": {"type": "string", "example": "Alpha Team"},
            },
        },
        "type": "object",
    }

    result = type_mismatch_strategy.generate_payload(mock_schema)
    corrupted_type_count = 0

    # Using corrupted count here to count the number of times this key appears. We need to make sure that typemismatch doesn't pass a clean object
    assert isinstance(result, dict)
    for value in result.values():
        if isinstance(value, dict) and value["corrupted_type"]:
            corrupted_type_count += 1
    assert corrupted_type_count == 1 
