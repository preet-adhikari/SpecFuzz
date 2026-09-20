from collections import deque
import os
import json
import requests

from execution_engine.execution_engine_request_data import ExecutionEngineRequestData
from execution_engine.execution_engine import ExecutionEngine

class TestOrchestrator:
    def __init__(self, blueprints: list) -> None:

        # Get the credentials from the .env file
        self.credentials = {
            "APIKEYAUTH": os.getenv("API_KEY", "spartan_123_default"),
            "OAUTH2": os.getenv("OAUTH_TOKEN", "Bearer temp_oauth_token"),
            "BASICAUTH": os.getenv("BASIC_AUTH", "Basic admin:password123"),
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
        self._create_job_queue(blueprints)

    def _create_job_queue(self, blueprints):
        """Wrapping test blueprints into jobs which are then added to the main queue"""

        for blueprint in blueprints:
            job = {
                "blueprint" : blueprint,
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
                # Job has to be marked as dead
                print(
                    f"💀 Job died after {self.max_retries} attempts: {current_job['blueprint']['endpoint']}"
                )
                current_job["status"] = "dead"
                self.dead_jobs.append(current_job)
                continue

            # 4. Token Injection
            self._attach_security_tokens(current_job)

            print(
                f"[{current_job['tries']}/{self.max_retries}] Executing {current_job['blueprint']['method']} {current_job['blueprint']['endpoint']}"
            )

            # 5. Execution: Map directly to the dedicated engine
            response_data = self._fire_execution_engine(current_job)

            # Routing the Response
            self._route_response(current_job, response_data)

    def _attach_security_tokens(self, job):
        """Attach security headers"""

        blueprint = job["blueprint"]
        security_instructions = blueprint.get("security", [])

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        for sec in security_instructions:
            if sec.get("in") == "header":
                # Convert scheme name to uppercase to match our RAM dictionary keys
                scheme = sec.get("scheme_name").upper()
                token = self.credentials.get(scheme, "UNKNOWN_TOKEN")
                headers[sec.get("key_name")] = token

        # Attach the finalized headers to the job state
        job["final_headers"] = headers

    def _fire_execution_engine(self, job):
        """Adapter that maps data and intercepts mocks before hitting the network."""
        blueprint = job["blueprint"]
        url = blueprint.get("endpoint")

        # 1. Intercept the Dry Run FIRST (Keeps the Execution Engine pure)
        if "midgard.com" in url or "alfheim-gateway" in url:
            return {"status_code": 200, "error": None}

        # 2. Map Orchestrator Dictionary -> ExecutionEngineRequestData
        request_payload = ExecutionEngineRequestData(
                method=blueprint.get("method").upper(),
                url=url,
                headers=job["final_headers"],
                payload=blueprint.get("payload")
            )

        # 3. Fire the real engine
        result = self.execution_engine.automate_http_request(request_payload)

        # 4. Map ExecutionResult back -> Orchestrator Dictionary
        # (This allows your existing _route_response logic to work without rewriting it)
        if result.is_success:
            return {"status_code": 200, "error": None} 
        else:
            return {"status_code": 502, "error": result.error_message}

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

            # Fail-safe: Save to disk immediately
            self._send_data_to_test_results_storage(job)

    def _send_data_to_test_results_storage(self, job):
        """Appends the result to a file so data survives a script crash."""
        # 'a' mode opens the file, appends the line, and closes it.
        # Using .jsonl (JSON Lines) is perfect for writing one JSON object per line incrementally.
        with open("test_results.jsonl", "a") as f:
            f.write(json.dumps(job) + "\n")
