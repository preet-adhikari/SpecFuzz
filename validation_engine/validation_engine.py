import json

class ValidationEngine:
    def __init__(self, results_file):
        self._results_file = results_file

    def generate_report(self):
        print("\n📊 Generating Test Report...")

        total_tests = 0
        passed = 0
        failed = 0

        try:
            with open(self._results_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue

                    total_tests += 1
                    job = json.loads(line)

                    endpoint = job["blueprint"]["endpoint"]
                    method = job["blueprint"]["method"]
                    actual_status = str(job["results"]["status_code"])
                    expected_responses = job["blueprint"].get("expected_response", {})

                    # Did the API return a status code we expected?
                    if actual_status in expected_responses or actual_status.startswith(
                        "2"
                    ):
                        passed += 1
                        print(
                            f"✅ PASS | {method} {endpoint} | Status: {actual_status}"
                        )
                    else:
                        failed += 1
                        print(
                            f"❌ FAIL | {method} {endpoint} | Expected: {list(expected_responses.keys())} | Got: {actual_status}"
                        )

        except FileNotFoundError:
            print(
                f"❌ Error: Could not find {self._results_file}. Did the Orchestrator run?"
            )
            return

        # Final summary
        print("\n=========================================")
        print("🏆 TEST RUN SUMMARY")
        print("=========================================")
        print(f"Total Tests Executed: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print("=========================================\n")
