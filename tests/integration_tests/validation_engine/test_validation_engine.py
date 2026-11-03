from execution_engine.execution_result import ExecutionResult
from validation_engine.validation_engine import ValidationEngine


class TestValidationEngine:

    def test_validation_engine_should_pass_valid_json_payload(self):

        job = {
            "test_case": {
                "expected_response": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["user_id", "status"],
                                    "properties": {
                                        "user_id": {"type": "integer"},
                                        "status": {"type": "string"},
                                    },
                                }
                            }
                        }
                    }
                }
            }
        }

        fake_api_response = ExecutionResult(
            is_success=True,  # REQUIRED: Did the network call itself succeed?
            response_time=0.145,  # REQUIRED: Simulated ping in seconds
            status_code=200,  # OPTIONAL
            response_header={"content-type": "application/json"},  # OPTIONAL
            response_body=b'{"user_id": 1211, "status": "active"}',  # OPTIONAL: Notice the 'b' prefix for bytes!
        )
        sut = ValidationEngine()

        # Act
        result = sut.validate(job, fake_api_response)

        assert result.validation_result_status is True
        assert len(result.validation_context) == 0

        assert result.job == job
        assert result.execution_result == fake_api_response

    def test_validation_engine_should_fail_payload_that_doesnt_match_expected_response(
        self,
    ):
        # Arrange
        job = {
            "test_case": {
                "expected_response": {
                    "200": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["user_id", "status"],
                                    "properties": {
                                        "user_id": {"type": "integer"},
                                        "status": {"type": "string"},
                                    },
                                }
                            }
                        }
                    }
                }
            }
        }

        fake_api_response = ExecutionResult(
            is_success=True,
            response_time=0.224,
            status_code=500
        )

        sut = ValidationEngine()

        #Act
        result = sut.validate(job, fake_api_response)

        #Assert
        assert result.validation_result_status is False
        assert len(result.validation_context) == 1

        assert result.validation_context[0].get("rule") == "status_code_mismatch"
