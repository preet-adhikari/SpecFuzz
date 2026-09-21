import requests
from execution_engine.execution_engine_request_data import ExecutionEngineRequestData

from requests.exceptions import Timeout, TooManyRedirects, RequestException
import time

from execution_engine.execution_result import ExecutionResult

class ExecutionEngine:
    # Initializing objects for the Execution Engine
    def __init__(self):
        self._session = requests.Session()
        self._timeout = (3, 7) # 3 seconds to connect, 7 seconds to read

    def automate_http_request(self, payload: ExecutionEngineRequestData):
        # To ensure isolation
        self._session.cookies.clear()
        start = time.perf_counter_ns()
        try:
            response = requests.request(
                method=payload.method,
                headers=payload.headers,
                url=payload.url,
                json=payload.payload,
                timeout=self._timeout
            )
            end = time.perf_counter_ns()
            elapsed_time_ms = (end - start) / 1_000_000
            return ExecutionResult(
                            is_success=response.ok,
                            status_code=response.status_code,  # <-- Added here
                            response_time=elapsed_time_ms,
                            response_header=dict(response.headers),
                            response_body=response.content
                        )

        except Timeout as e:
            end = time.perf_counter_ns()
            elapsed_ms = (end - start) / 1_000_000
            return ExecutionResult(
                is_success=False,
                status_code=None,  # No HTTP response received
                response_time=elapsed_ms,
                error_message=f"Timeout: {str(e)}",
            )

        except TooManyRedirects as e:
            end_time = time.perf_counter_ns()
            elapsed_ms = (end_time - start) / 1_000_000
            return ExecutionResult(
                is_success=False,
                status_code=None, 
                response_time=elapsed_ms,
                error_message=f"Too Many Redirects: {str(e)}",
            )

        except RequestException as e:
            end_time = time.perf_counter_ns()
            elapsed_ms = (end_time - start) / 1_000_000
            return ExecutionResult(
                is_success=False,
                status_code=None, 
                response_time=elapsed_ms,
                error_message=f"Connection Error: {str(e)}",
            )