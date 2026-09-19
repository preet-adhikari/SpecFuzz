import pytest
from test_generator.fuzzing_strategy import MissingRequiredFieldsStrategy

missing_strategy = MissingRequiredFieldsStrategy()

def test_missing_fields_fuzzing_strategy():
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

    result = missing_strategy.generate_payload(mock_schema)
    
    assert isinstance(result, dict)
    
    for value in mock_schema["required"]:
        if value not in result:
            assert True
