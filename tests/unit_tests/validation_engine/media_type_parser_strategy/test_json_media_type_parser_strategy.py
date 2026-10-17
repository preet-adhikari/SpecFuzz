import json

import pytest

from validation_engine.media_type_parser_strategy.json_media_type_parser_strategy import JSONMediaTypeParserStrategy


def test_json_media_type_parser_strategy_should_return_dict_when_given_valid_bytes():
    """
    Let's write a unit test.

    Unit Test 1: JSONMediaTypeParserStrategy should take in bytes as payload and parse it into a dictionary
            fake_response_in_bytes = mock data in bytes format
            sut is JSONMediaTypeParserStrategy returning dictionary in Python
            Assert that sut.parse returns type as dictionary
            Assert that the returned value is the exact same as the inputted bytes
    """
    # Arrange
    expected_dict = {"weapon": "Draupnir Spear"}
    fake_response_in_bytes = json.dumps(expected_dict).encode("utf-8")
    sut = JSONMediaTypeParserStrategy()

    # Act
    parsed_dict = sut.parse(fake_response_in_bytes)

    # Assert
    assert isinstance(parsed_dict, dict)
    assert parsed_dict == expected_dict

def test_json_media_type_parser_strategy_should_raise_json_decode_error_when_given_corrputed_bytes():
    #Arrange
    corrupted_bytes = b'{"weapon" : "Blades of Chaos"'
    sut = JSONMediaTypeParserStrategy()
    
    #Act
    #Assert
    with pytest.raises(json.JSONDecodeError):
        sut.parse(corrupted_bytes)

    