import pytest
from test_generator.fuzzing_strategy import HappyPathStrategy

happy_path_strategy = HappyPathStrategy()

mock_expected_response = {"201": "Number created", "200": "Request is good"}


def test_max_and_min_bounds():
    """Prove that the happy path generates appropriate min and max items"""
    # Arrange
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

    # Act
    payload_array, _ = happy_path_strategy.generate_payload(
        mock_schema_array, mock_expected_response, "POST"
    )
    payload_integer, _ = happy_path_strategy.generate_payload(
        mock_schema_integer, mock_expected_response, "POST"
    )

    # Assert
    assert isinstance(payload_array, list)
    assert isinstance(payload_integer, int)
    assert len(payload_array) >= 1
    assert len(payload_array) <= 5
    assert payload_integer >= 4 and payload_integer <= 5


def test_negative_integer_math():
    # Arrange
    mock_schema_negative_integer = {
        "type": "integer",
        "minimum": -50,
        "maximum": -10,
    }

    # Act
    payload_negative, _ = happy_path_strategy.generate_payload(
        mock_schema_negative_integer, mock_expected_response, "POST"
    )

    # Assert
    assert isinstance(payload_negative, int)
    assert payload_negative >= -50 and payload_negative <= -10


def test_object_recursion():
    # Arrange
    mock_schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"},
            "clearance_level": {"type": "integer", "maximum": 5},
        },
    }

    # Act
    payload_object, _ = happy_path_strategy.generate_payload(
        mock_schema, mock_expected_response, "POST"
    )

    # Assert
    assert isinstance(payload_object, dict)
    assert "username" in payload_object
    assert isinstance(payload_object["clearance_level"], int)
    assert payload_object["clearance_level"] <= 5
