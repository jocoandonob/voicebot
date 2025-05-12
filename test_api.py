import requests
import json

base_url = "http://localhost:8000"

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw Response: {response.text}")
    print("-" * 50)

# Test track-visitor endpoint
print("Testing /api/voice/track-visitor endpoint:")
response = requests.post(f"{base_url}/api/voice/track-visitor")
print_response(response)

# Test stats endpoint
print("Testing /api/voice/stats endpoint:")
response = requests.get(f"{base_url}/api/voice/stats")
print_response(response)

# Test check-button-usage endpoint
print("Testing /api/voice/check-button-usage/record endpoint:")
response = requests.post(f"{base_url}/api/voice/check-button-usage/record")
print_response(response)

# Test increment-button-usage endpoint
print("Testing /api/voice/increment-button-usage/record endpoint:")
response = requests.post(f"{base_url}/api/voice/increment-button-usage/record")
print_response(response)