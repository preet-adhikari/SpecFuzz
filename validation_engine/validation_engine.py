import json
import pprint
import sys

from execution_engine.execution_result import ExecutionResult

from validation_engine.media_type_parser_strategy.json_media_type_parser_strategy import (
    JSONMediaTypeParserStrategy,
)
from validation_engine.validation_result import ValidationResult
from validation_engine.validator_factory.base import ValidatorFactory


class ValidationEngine:
    def __init__(self):
        self._factory = ValidatorFactory()

    # def __init__(self, test_case: dict, execution_engine_result : ExecutionResult) -> None:
    #     self._test_case = test_case
    #     self._execution_engine_result = execution_engine_result

    def validate(
        self, job: dict, execution_engine_result: ExecutionResult
    ) -> ValidationResult:
        """Validates data by comparing the expected response with the executed response"""

        pprint.pprint(job.get("test_case", {}).get("expected_response"))
        print("-----------------------")
        pprint.pprint(execution_engine_result)

        expected_response_body = job.get("test_case", {}).get("expected_response")
        for status_code in expected_response_body:
            if status_code == str(execution_engine_result.status_code):

                if expected_response_body.get(status_code) == {}:
                    validation_flag = True
                    break
                else:
                    # Compare content-type of the response
                    expected_content_types = expected_response_body.get(
                        status_code
                    ).get("content", {})
                    actual_content_type = None
                    if execution_engine_result.response_header:
                        actual_content_type = (
                            execution_engine_result.response_header.get("content-type")
                        )
                    for expected_content_type in expected_content_types:
                        print(f"Expected_content_type : {expected_content_type}")
                        print(f"Actual_content_type : {actual_content_type}")
                        if expected_content_type == actual_content_type:
                            # TODO: Add more content types
                            if expected_content_type == "application/json":
                                if execution_engine_result.response_body:
                                    try:
                                        parser_strategy = JSONMediaTypeParserStrategy()
                                        actual_response_json = parser_strategy.parse(
                                            execution_engine_result.response_body
                                        )
                                        expected_response_json = (
                                            expected_content_types.get(
                                                expected_content_type
                                            )
                                        )
                                        spec_validator = self._factory.get_validator(
                                            "openapi_v3xx"
                                        )

                                        validation_result_status, validation_context = (
                                            spec_validator.validate(
                                                expected_response=expected_response_json,
                                                actual_response=actual_response_json,
                                            )
                                        )

                                        # validator_factory =

                                        return ValidationResult(
                                            validation_result_status,
                                            job,
                                            execution_engine_result,
                                            validation_context,
                                        )

                                    except json.JSONDecodeError:
                                        return ValidationResult(
                                            validation_result_status=False,
                                            job=job,
                                            execution_result=execution_engine_result,
                                            validation_context=[
                                                {
                                                    "field": "root",
                                                    "rule": "parse_error",
                                                    "message": "Failed to parse JSON: Response body is corrupted or invalid.",
                                                }
                                            ],
                                        )
                    # Content didn't match
                    return ValidationResult(
                        validation_result_status=False,
                        job=job,
                        execution_result=execution_engine_result,
                        validation_context=[
                            {
                                "field": "header.content-type",
                                "rule": "content_type_mismatch",
                                "message": f"Content-Type mismatch: Expected {list(expected_content_types.keys())}, got '{actual_content_type}'",
                            }
                        ],
                    )

        # API returned status code that wasn't in the expected status codes.
        return ValidationResult(
            validation_result_status=False,
            job=job,
            execution_result=execution_engine_result,
            validation_context=[
                {
                    "field": "header.status_code",
                    "rule": "status_code_mismatch",
                    "message": f"Unexpected status code {execution_engine_result.status_code}. Expected one of: {list(expected_response_body.keys())}",
                }
            ],
        )

    # Designing validation engine class

    # def generate_report(self):
    #     print("\n📊 Generating Test Report...")

    #     total_tests = 0
    #     passed = 0
    #     failed = 0

    #     try:
    #         with open(self._results_file, "r") as f:
    #             for line in f:
    #                 if not line.strip():
    #                     continue

    #                 total_tests += 1
    #                 job = json.loads(line)

    #                 endpoint = job["blueprint"]["endpoint"]
    #                 method = job["blueprint"]["method"]
    #                 actual_status = str(job["results"]["status_code"])
    #                 expected_responses = job["blueprint"].get("expected_response", {})

    #                 # Did the API return a status code we expected?
    #                 if actual_status in expected_responses or actual_status.startswith(
    #                     "2"
    #                 ):
    #                     passed += 1
    #                     print(
    #                         f"✅ PASS | {method} {endpoint} | Status: {actual_status}"
    #                     )
    #                 else:
    #                     failed += 1
    #                     print(
    #                         f"❌ FAIL | {method} {endpoint} | Expected: {list(expected_responses.keys())} | Got: {actual_status}"
    #                     )

    #     except FileNotFoundError:
    #         print(
    #             f"❌ Error: Could not find {self._results_file}. Did the Orchestrator run?"
    #         )
    #         return

    #     # Final summary
    #     print("\n=========================================")
    #     print("🏆 TEST RUN SUMMARY")
    #     print("=========================================")
    #     print(f"Total Tests Executed: {total_tests}")
    #     print(f"✅ Passed: {passed}")
    #     print(f"❌ Failed: {failed}")
    #     print("=========================================\n")
