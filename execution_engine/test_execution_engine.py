from execution_engine.execution_engine import ExecutionEngine
from execution_engine.execution_engine_request_data import ExecutionEngineRequestData




# test_data = ExecutionEngineRequestData(
#     method="POST",
#     url="https://httpbin.org/post",
#     headers={
#         "Content-Type": "application/json",
#         "Authorization": "Bearer Fake-VIP-Wristband-123",
#         "X-Test-Header": "Fuzzing-Test",
#     },
#     payload={"username": "admin", "fuzz_attack": "' OR 1=1 --", "age": -999},
# )

# # 1. Triggering a Timeout
# test_data = ExecutionEngineRequestData(
#     method="GET",
#     url="https://httpbin.org/delay/10",  # Tells the server to wait 10 seconds
#     headers={"X-Test-Header": "Testing-Timeout"},
#     payload=None,
# )

# 2. Triggering Redirect error

# test_data = ExecutionEngineRequestData(
#     method="GET",
#     url="https://httpbin.org/redirect/300", # Redirects 300 times
#     # url="https://httpbiiiiiin.org",
#     headers={"X-Test-Header": "Testing redirect"},
#     payload=None,
# )

# Testing if the API key security for basic authentication works
test_data = ExecutionEngineRequestData(
    method="GET",
    url="https://httpbin.org/basic-auth/kratos/atreus",
    headers={
        "Accept": "application/json",
        # Notice the word 'Basic' followed by a space and the scrambled string
        "Authorization": "Basic a3JhdG9zOmF0cmV1cw==",
        "X-Test-Header": "Fuzzing-Test",
    },
    # Note: GET requests typically do not have a payload/body
    payload=None,
)

engine = ExecutionEngine()

print("Sending an automatic request to httpbin.org...")

receipt = engine.automate_http_request(test_data)

print("\n--- EXECUTION RECEIPT ---")
print(f"Success: {receipt.is_success}")
print(f"Time Taken: {receipt.response_time} ms")
print(f"Status Code: {receipt.status_code}")

if receipt.error_message:
    print(f"Error: {receipt.error_message}")

print("\n--- RAW BODY RETURNED FROM SERVER ---")
print(receipt.response_body)
