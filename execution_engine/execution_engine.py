from execution_engine_request_data import ExecutionEngineRequestData
import requests
from execution_result import ExecutionResult
from requests.exceptions import Timeout, TooManyRedirects, RequestException
import time

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
                    is_success = response.ok,
                    response_time = elapsed_time_ms,
                    response_header = dict(response.headers),
                    response_body = response.text 
                )

        except Timeout as e:
            end = time.perf_counter_ns()
            elapsed_ms = (end - start) / 1_000_000
            return ExecutionResult(
                is_success=False,
                response_time = elapsed_ms,
                error_message=f"Timeout: {str(e)}",
            )

        except TooManyRedirects:
            end_time = time.perf_counter_ns()
            elapsed_ms = (end - start) / 1_000_000
            return ExecutionResult(
                is_success=False,
                response_time = elapsed_ms,
                error_message=f"Too Many Redirects: {str(e)}",
            )

        except RequestException:
            end_time = time.perf_counter_ns()
            elapsed_ms = (end - start) / 1_000_000
            return ExecutionResult(
                is_success=False,
                response_time =elapsed_ms,
                error_message=f"Connection Error: {str(e)}",
            )
