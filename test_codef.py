import requests
import json
import base64
import urllib.parse

def test_codef():
    # Sandbox Credentials
    client_id = "ef27cfaa-10c1-4470-adac-60ba476273f9"
    client_secret = "83160c33-9045-4915-86d8-809473cdf5c3"
    api_host = "https://oauth.codef.io"

    # Get Token
    token_url = f"{api_host}/oauth/token"
    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_auth}"
    }
    
    data = {
        "grant_type": "client_credentials",
        "scope": "read"
    }
    
    try:
        print("Requesting CODEF Access Token...")
        res = requests.post(token_url, headers=headers, data=data, timeout=10)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
        if res.status_code == 200:
            print("✅ CODEF Sandbox API Token Issuance SUCCESS!")
        else:
            print("❌ CODEF Sandbox API Token Issuance FAILED.")
    except Exception as e:
        print(f"❌ CODEF API Test Error: {e}")

if __name__ == "__main__":
    test_codef()
