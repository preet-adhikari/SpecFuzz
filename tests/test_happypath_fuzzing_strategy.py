# Test for fuzzing strategy

import pytest
from test_generator.fuzzing_strategy import HappyPathStrategy

happy_path_strategy = HappyPathStrategy()


mock_expected_response = {
        "201" : "Number created",
        "200" : "Request is good"
    }



def test_max_and_min_bounds():
    """Prove that the happy path generates appropriate min and max items"""
    mock_schema_array = {
        "type": "array",
        "minItems": 1,
        "maxItems": 5,
        "items": {"type": "string"},
    }

    mock_schema_integer = {
        "type": "integer",
        "minimum": 4,
        "maximum": 5,
    }

    result_array = happy_path_strategy.generate_payload(mock_schema_array, mock_expected_response)
    result_integer = happy_path_strategy.generate_payload(mock_schema_integer, mock_expected_response)
    print(result_array)
    assert isinstance(result_array, list)
    assert isinstance(result_integer, int)
    assert len(result_array) >= 1
    assert len(result_array) <= 5
    assert result_integer >= 4 and result_integer <= 5


def test_negative_integer_math():

    mock_schema_negative_integer = {
        "type": "integer",
        "minimum": -50,
        "maximum": -10,
    }

    result_negative = happy_path_strategy.generate_payload(mock_schema_negative_integer, mock_expected_response)

    assert isinstance(result_negative, int)
    assert result_negative >= -50 and result_negative <= -10


def test_object_recursion():
    mock_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "clearance_level": {"type": "integer", "maximum": 5},
        },
    }

    result = happy_path_strategy.generate_payload(mock_schema, mock_expected_response)

    assert isinstance(result, dict)
    assert "username" in result
    assert isinstance(result["clearance_level"], int)
    assert result["clearance_level"] <= 5
