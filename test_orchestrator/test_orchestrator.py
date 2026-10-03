from collections import deque
import os
import json
import requests
import base64

from execution_engine.execution_engine_request_data import ExecutionEngineRequestData
from execution_engine.execution_engine import ExecutionEngine
from execution_engine.execution_result import ExecutionResult
from validation_engine.validation_engine import ValidationEngine

class TestOrchestrator:
    def __init__(self, test_suite: list) -> None:

        # Get the credentials from the .env file
        self.credentials = {
            "APIKEYAUTH": os.getenv("API_KEY", "spartan_123_default"),
            "OAUTH2": os.getenv("OAUTH_TOKEN", "Bearer temp_oauth_token"),
            # "BASICAUTH": os.getenv("BASIC_AUTH", "Basic admin:password123"),
            "BASICAUTH": os.getenv("BASIC_AUTH", "kratos:sparta123"),
        }
        # Create the queue
        self.pending_queue = deque()
        self.dead_jobs = []
        self.completed_jobs = []

        # Setting max retries to 3 for now
        self.max_retries = 3

        # Instantiate the external engine
        self.execution_engine = ExecutionEngine()

        # Initialize queue
        self._create_job_queue(test_suite)

    def _create_job_queue(self, test_suite):
        """Wrapping test cases into jobs which are then added to the main queue"""

        for test_case in test_suite:
            job = {
                "test_case" : test_case,
                "result" : None,
                "tries" : 0,
                "status" : "pending"
            }
            self.pending_queue.append(job)

    def execute_tests(self):
        """Main function to execute the tests"""

        print(f"🚀 [START] Starting execution of {len(self.pending_queue)} tests...")

        while self.pending_queue:

            current_job = self.pending_queue.popleft()

            current_job["status"] = "active"
            current_job["tries"] += 1

            # Check if job has crossed max retries
            if current_job["tries"] > self.max_retries:
                print(
                    f"💀 Job died after {self.max_retries} attempts: {current_job['test_case']['endpoint']}"
                )
                current_job["status"] = "dead"

                # Attaching mock result
                current_job["results"] = {
                    "status_code": 502,
                    "error": "Max retries exceeded",
                }

                self.completed_jobs.append(current_job)
                self.dead_jobs.append(current_job)

                # Save the dead job to the JSONL file so the reporter sees it
                self._send_data_to_test_results_storage(current_job)
                continue

            # Token Injection
            self._attach_security_tokens(current_job)

            print(
                f"[{current_job['tries']}/{self.max_retries}] Executing {current_job['test_case']['method']} {current_job['test_case']['endpoint']}"
            )

            # Execution
            response_data = self._fire_execution_engine(current_job)

            # TODO : Data to the validation engine should be sent from here
            validation_engine = ValidationEngine()
            validation_engine.validate(current_job, response_data)

            # Routing the Response
            self._route_response(current_job, response_data)

    def _attach_security_tokens(self, job):
        """Attach security headers"""

        test_case = job["test_case"]
        security_instructions = test_case.get("security", [])

        # For testing purposes
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        for sec in security_instructions:
            if sec.get("in") == "header":
                # Convert scheme name to uppercase to match our RAM dictionary keys
                scheme = sec.get("scheme_name").upper()
                token = self.credentials.get(scheme, "UNKNOWN_TOKEN")
                if scheme == "BASICAUTH":
                    encoded_token = base64.b64encode(token.encode('utf-8')).decode('utf-8')
                    headers[sec.get("key_name")] = f"Basic {encoded_token}"    
                else:
                    headers[sec.get("key_name")] = token

        # Attach the finalized headers to the job state
        job["final_headers"] = headers

    def _fire_execution_engine(self, job):
        """Adapter that maps data and intercepts mocks before hitting the network."""
        test_case = job["test_case"]
        url = test_case.get("endpoint")

        # # Intercept URL to force a 502 Bad Gateway
        # if "helheim" in url:
        #     return {"status_code": 502, "error": "Mock Network Failure"}

        # # For Dry run
        # if "midgard.com" in url or "alfheim-gateway" in url:
        #     return {"status_code": 200, "error": None}

        # Map Orchestrator Dictionary -> ExecutionEngineRequestData
        request_payload = ExecutionEngineRequestData(
                method=test_case.get("method").upper(),
                url=url,
                headers=job["final_headers"],
                payload=test_case.get("payload")
            )


        # Fire the real engine
        result = self.execution_engine.automate_http_request(request_payload)

        # if result.is_success:
        #     return {"status_code": 200, "error": None}
        # else:
        #     return {"status_code": 502, "error": result.error_message}
        return result
        # return {
        #     "status_code" : result.status_code,
        #     "error" : result.error_message
        # }

    #TODO: Check if additional logic is required for more cases of network errors
    def _route_response(self, job, response_data):
        """Routes the job based on network success or failure."""
        if response_data["error"] or response_data["status_code"] in [502, 503, 504]:
            print("⚠️ Network error, pushing back to queue...")
            job["status"] = "pending"
            self.pending_queue.append(job)
        else:
            job["status"] = "completed"
            job["results"] = response_data
            self.completed_jobs.append(job)

            # Fail-safe: Save to disk
            self._send_data_to_test_results_storage(job)

    def _send_data_to_test_results_storage(self, job):
        """Appends the result to a file so data survives a script crash."""
        # 'a' mode opens the file, appends the line, and closes it.
        # Using .jsonl (JSON Lines) is perfect for writing one JSON object per line incrementally.
        with open("test_results.jsonl", "a") as f:
            f.write(json.dumps(job) + "\n")
