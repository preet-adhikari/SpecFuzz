import json
import pprint
import sys

from execution_engine.execution_result import ExecutionResult
from validation_engine.response_body_format_strategy.json_strategy import JSONStrategy
from validation_engine.validation_result import ValidationResult

class ValidationEngine:
    # def __init__(self, results_file):
    #     self._results_file = results_file

    # def __init__(self, test_case: dict, execution_engine_result : ExecutionResult) -> None:
    #     self._test_case = test_case
    #     self._execution_engine_result = execution_engine_result

    def validate(self, job: dict, execution_engine_result: ExecutionResult) -> ValidationResult:
        """ Validates data by comparing the expected response with the executed response"""


        pprint.pprint(job.get("test_case", {}).get("expected_response"))
        print("-----------------------")
        pprint.pprint(execution_engine_result)

        expected_response_body = job.get("test_case",{}).get("expected_response")
        for status_code in expected_response_body:
            if status_code == str(execution_engine_result.status_code):

                if expected_response_body.get(status_code) == {}:
                    validation_flag = True
                    break
                else:
                    # Compare content-type of the response
                    expected_content_types = expected_response_body.get(status_code).get("content", {})
                    actual_content_type = None
                    if execution_engine_result.response_header:
                        actual_content_type = execution_engine_result.response_header.get("content-type")
                    for expected_content_type in expected_content_types:
                        print(f"Expected_content_type : {expected_content_type}")
                        print(f"Actual_content_type : {actual_content_type}")
                        if expected_content_type == actual_content_type:
                            # TODO: Add more content types
                            if expected_content_type == "application/json":
                                if execution_engine_result.response_body:
                                    try:
                                        strategy = JSONStrategy()
                                        response_body_content_json = strategy.parse(execution_engine_result.response_body)
                                        validation_result_status, validation_context = strategy.validate(response_body_content_json, expected_content_types.get(expected_content_type))

                                        return ValidationResult(validation_result_status, validation_context, job, execution_engine_result)

                                    except json.JSONDecodeError:
                                        return ValidationResult(
                                            validation_result_status=False,
                                            validation_context="Failed to parse JSON: Response body is corrupted or invalid.",
                                            job=job,
                                            execution_result=execution_engine_result,
                                        )
                    # Content didn't match
                    return ValidationResult(
                        validation_result_status=False,
                        validation_context=f"Content-Type mismatch: Expected {list(expected_content_types.keys())}, got '{actual_content_type}'",
                        job=job,
                        execution_result=execution_engine_result,
                    )

        # API returned status code that wasn't in the expected status codes.
        return ValidationResult(
            validation_result_status=False,
            validation_context=f"Unexpected status code {execution_engine_result.status_code}. Expected one of: {list(expected_response_body.keys())}",
            job=job,
            execution_result=execution_engine_result,
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
