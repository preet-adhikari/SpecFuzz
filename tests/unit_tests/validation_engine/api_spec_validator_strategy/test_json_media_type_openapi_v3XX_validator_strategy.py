from validation_engine.api_spec_validator_strategy.openapiv3xx_validator_strategy import OpenAPIV3xxValidatorStrategy

class TestRequiredFieldValidation:

    def test_openapi_v3xx_validator_should_validate_successfully_when_matching_required_fields_are_present(self):
        # Arrange
        # This is a sample expected response in json that is of the OpenAPI v3xx spec
        # expected_response_json = {
        #     "schema": {
        #         "required": ["name", "strengths", "weaknesses", "weapons"],
        #         "properties": {
        #             "name": {"type": "string", "example": "Kratos"},
        #             "alignment": {"type": "string", "example": "Spartan"},
        #             "realm": {"type": "string", "example": "Midgard"},
        #             "catchphrase": {
        #                 "type": "string",
        #                 "example": "Death can have me when it earns me.",
        #             },
        #             "weapons": {
        #                 "type": "array",
        #                 "items": {"type": "string"},
        #                 "example": ["Leviathan Axe", "Blades of Chaos"],
        #             },
        #             "strengths": {
        #                 "type": "array",
        #                 "minItems": 1,
        #                 "maxItems": 10,
        #                 "items": {
        #                     "type": "object",
        #                     "required": ["attribute", "level"],
        #                     "properties": {
        #                         "attribute": {"type": "string"},
        #                         "level": {"type": "integer", "minimum": 1, "maximum": 10},
        #                     },
        #                 },
        #             },
        #             "weaknesses": {
        #                 "type": "array",
        #                 "items": {"type": "string", "maxLength": 100},
        #             },
        #         },
        #         "type": "object",
        #     }
        # }
        # API Spec JSON
        expected_response_json = {
            "schema": {
                "required": ["name"],
                "properties": {"name": {"type": "string", "example": "Kratos"}},
            }
        }
        # actual_response_json = {
        #     "catchphrase": "Death can have me when it earns me.",
        #     "id": 1,
        #     "alignment": "Spartan",
        #     "weapons": ["Leviathan Axe", "Blades of Chaos"],
        #     "weaknesses": ["valid_vVBKzL", "valid_dpNZzP"],
        #     "name": "Kratos",
        #     "realm": "Midgard",
        #     "strengths": [
        #         {"attribute": "valid_skFtcl", "level": 7},
        #         {"attribute": "valid_FoOwQi", "level": 4},
        #         {"attribute": "valid_KngowT", "level": 5},
        #         {"attribute": "valid_GcIpKP", "level": 10},
        #         {"attribute": "valid_dBziQK", "level": 7},
        #         {"attribute": "valid_VdQxeE", "level": 4},
        #     ],
        # }

        # Actual response from request JSON
        actual_response_json = {
            "name" : "Kratos"
        }

        sut = OpenAPIV3xxValidatorStrategy()

        # Act
        validation_result_status, validation_context = sut.validate(expected_response_json, actual_response_json)

        # Assert
        assert validation_result_status is True
        assert validation_context == []

    def test_openapi_v3xx_validator_should_fail_if_required_fields_are_not_present(self):
        # Arrange
        expected_response_json = {
                "schema": {
                    "required": ["name"],
                    "properties": {"name": {"type": "string", "example": "Kratos"}},
                }
            }

        actual_response_json = {
                "alignment" : "Spartan"
            }

        sut = OpenAPIV3xxValidatorStrategy()

        # Act
        validation_result_status, validation_context = sut.validate(expected_response_json, actual_response_json)

        # assert
        assert validation_result_status is False
        assert validation_context[0]["field"] == "name"
        assert validation_context[0]["rule"] == "required"

    def test_openapiv3xx_validator_should_show_all_the_required_fields_that_are_missing(self):
        # arrange
        # Arrange
        expected_response_json = {
                    "schema": {
                        "required": ["name", "strengths", "weaknesses", "weapons"],
                        "properties": {
                            "name": {"type": "string", "example": "Kratos"},
                            "alignment": {"type": "string", "example": "Spartan"},
                            "realm": {"type": "string", "example": "Midgard"},
                            "catchphrase": {
                                "type": "string",
                                "example": "Death can have me when it earns me.",
                            },
                            "weapons": {
                                "type": "array",
                                "items": {"type": "string"},
                                "example": ["Leviathan Axe", "Blades of Chaos"],
                            },
                            "strengths": {
                                "type": "array",
                                "minItems": 1,
                                "maxItems": 10,
                                "items": {
                                    "type": "object",
                                    "required": ["attribute", "level"],
                                    "properties": {
                                        "attribute": {"type": "string"},
                                        "level": {"type": "integer", "minimum": 1, "maximum": 10},
                                    },
                                },
                            },
                            "weaknesses": {
                                "type": "array",
                                "items": {"type": "string", "maxLength": 100},
                            },
                        },
                        "type": "object",
                    }
                }

        # 'strengths' and 'weaknesses' are missing
        actual_response_json = {
                    "catchphrase": "Death can have me when it earns me.",
                    "id": 1,
                    "alignment": "Spartan",
                    "weapons": ["Leviathan Axe", "Blades of Chaos"],
                    "name": "Kratos",
                    "realm": "Midgard",
                }

        sut = OpenAPIV3xxValidatorStrategy()

        # Act
        validation_result_status, validation_context = sut.validate(expected_response_json, actual_response_json)

        # Assert
        assert validation_result_status is False
        assert len(validation_context) == 2
        failed_fields = [ error["field"] for error in validation_context]
        failed_rules = [ error["rule"] for error in validation_context]

        assert "weaknesses" in failed_fields
        assert "strengths" in failed_fields
        assert failed_rules.count("required") == 2

# Test Types
class TestTypeValidation:
    def test_openapiv3xx_validator_should_be_successful_if_the_types_match(self):
        """The Validator should be successful if types match"""
        # Arrange
        expected_response_json = {
                "schema": {
                    "required": ["name"],
                    "properties": {"name": {"type": "string", "example": "Kratos"},
                        "weapons": {
                            "type": "array",
                            "items": {"type": "string"},
                            "example": ["Leviathan Axe", "Blades of Chaos"],
                        },},
                }
            }

        actual_response_json = {"name": "Kratos", "weapons": ["Leviathan Axe"]}

        sut = OpenAPIV3xxValidatorStrategy()

        # Act
        validation_result_status, validation_context = sut.validate(
            expected_response_json, actual_response_json
        )

        # assert
        assert validation_result_status is True
        assert validation_context == []


    def test_openapiv3xx_validator_should_fail_if_there_is_a_type_mismatch(self):
        """The Validator should fail if there is a type mismatch"""
        # Arrange
        expected_response_json = {
            "schema": {
                "required": ["name"],
                "properties": {"name": {"type": "string", "example": "Kratos"},
                    "weapons": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["Leviathan Axe", "Blades of Chaos"],
                    },},
            }
        }

        actual_response_json = {"name": "Kratos", "weapons": "Leviathan Axe"}

        sut = OpenAPIV3xxValidatorStrategy()

        # Act
        validation_result_status, validation_context = sut.validate(
            expected_response_json, actual_response_json
        )

        # assert
        assert validation_result_status is False

        failed_fields = [ error["field"] for error in validation_context]
        failed_rules = [ error["rule"] for error in validation_context]

        assert "weapons" in failed_fields
        assert "type" in failed_rules


    def test_openapiv3xx_validator_should_fail_if_items_inside_array_have_a_type_mismatch(self):

        # Arrange
        expected_response_json = {
            "schema": {
                "required": ["name"],
                "properties": {"name": {"type": "string", "example": "Kratos"},
                    "weapons": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["Leviathan Axe", "Blades of Chaos"],
                    },},
            }
        }

        actual_response_json = {"name": "Kratos", "weapons": ["Axe", 2345]}

        sut = OpenAPIV3xxValidatorStrategy()
        
        # Act
        validation_result_status, validation_context = sut.validate(
            expected_response_json, actual_response_json
        )

        # assert
        assert validation_result_status is False

        failed_fields = [ error["field"] for error in validation_context]
        failed_rules = [ error["rule"] for error in validation_context]

        assert "item_type" in failed_rules

    def test_openapi3xx_validator_should_pass_if_the_type_of_items_in_the_array_match(self):
        # Arrange
                expected_response_json = {
                    "schema": {
                        "required": ["name"],
                        "properties": {"name": {"type": "string", "example": "Kratos"},
                            "weapons": {
                                "type": "array",
                                "items": {"type": "string"},
                                "example": ["Leviathan Axe", "Blades of Chaos"],
                            },},
                    }
                }
        
                actual_response_json = {"name": "Kratos", "weapons": ["Axe", "Blades"]}
        
                sut = OpenAPIV3xxValidatorStrategy()
                
                # Act
                validation_result_status, validation_context = sut.validate(
                    expected_response_json, actual_response_json
                )
        
                # assert
                assert validation_result_status is True
                assert validation_context == []
