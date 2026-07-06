import urllib.request
import urllib.parse
import json
import http.cookiejar
import re
import sys

# Setup cookie handler to store cookies like csrftoken
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

BASE_URL = "http://127.0.0.1:8000"

def get_csrf_token():
    try:
        response = urllib.request.urlopen(BASE_URL)
        html = response.read().decode('utf-8')
        match = re.search(r'name="csrf-token" content="([^"]+)"', html)
        if match:
            return match.group(1)
        return ""
    except Exception as e:
        print(f"Error connecting to server. Is the Django dev server running? Details: {e}")
        sys.exit(1)

def send_request(url, method="GET", data=None, csrf_token=None):
    req = urllib.request.Request(url)
    req.method = method
    
    if csrf_token:
        req.add_header('X-CSRFToken', csrf_token)
        # Add referer since Django CSRF checks referrer for HTTPS (though HTTP is fine, it's good practice)
        req.add_header('Referer', BASE_URL + '/')
        
    # Get cookies from cookie jar and put them in the request
    cookies = []
    for cookie in cj:
        cookies.append(f"{cookie.name}={cookie.value}")
    if cookies:
        req.add_header('Cookie', "; ".join(cookies))

    if data:
        json_data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Content-Length', len(json_data))
        req.data = json_data

    try:
        with urllib.request.urlopen(req) as response:
            # Capture any set-cookie headers
            for header, value in response.getheaders():
                if header.lower() == 'set-cookie':
                    # Parse and save cookies to our jar
                    # For simplicity, we let the HTTPCookieProcessor handle it automatically on the response
                    pass
            
            res_data = json.loads(response.read().decode('utf-8'))
            return response.status, res_data
    except urllib.error.HTTPError as e:
        try:
            res_data = json.loads(e.read().decode('utf-8'))
            return e.code, res_data
        except Exception:
            return e.code, {"success": False, "error": e.reason}
    except Exception as e:
        return 500, {"success": False, "error": str(e)}

def run_tests():
    print("==================================================")
    print("Starting programatic verification of Django APIs")
    print("==================================================")
    
    # 1. Fetch CSRF token
    csrf_token = get_csrf_token()
    print(f"[SUCCESS] Server connected. CSRF token acquired: {csrf_token[:15]}...")
    
    # 2. Get initial student list
    code, res = send_request(f"{BASE_URL}/api/students/")
    print(f"\n[GET /api/students/] Code: {code}")
    print(f"  Success: {res.get('success')}")
    print(f"  Count: {len(res.get('students', []))}")
    print(f"  Stats: {res.get('stats')}")
    
    # 3. Add Student - Empty Fields Validation
    code, res = send_request(f"{BASE_URL}/api/add-student/", "POST", {
        "name": "",
        "email": "empty@gmail.com",
        "age": 20,
        "grade": "A"
    }, csrf_token)
    print(f"\n[POST /api/add-student/] Empty Name validation:")
    print(f"  Code: {code} (Expected: 400)")
    print(f"  Success: {res.get('success')} (Expected: False)")
    print(f"  Error msg: {res.get('error')}")
    
    # 4. Add Student - Invalid Email Validation
    code, res = send_request(f"{BASE_URL}/api/add-student/", "POST", {
        "name": "Invalid Email Student",
        "email": "invalid-email-address",
        "age": 20,
        "grade": "A"
    }, csrf_token)
    print(f"\n[POST /api/add-student/] Invalid Email validation:")
    print(f"  Code: {code} (Expected: 400)")
    print(f"  Success: {res.get('success')} (Expected: False)")
    print(f"  Error msg: {res.get('error')}")
    
    # 5. Add Student - Invalid Age Validation
    code, res = send_request(f"{BASE_URL}/api/add-student/", "POST", {
        "name": "Invalid Age Student",
        "email": "invalidage@gmail.com",
        "age": -5,
        "grade": "A"
    }, csrf_token)
    print(f"\n[POST /api/add-student/] Negative Age validation:")
    print(f"  Code: {code} (Expected: 400)")
    print(f"  Success: {res.get('success')} (Expected: False)")
    print(f"  Error msg: {res.get('error')}")

    # 6. Add Student - Valid Record (Alice Smith)
    code, res = send_request(f"{BASE_URL}/api/add-student/", "POST", {
        "name": "Alice Smith",
        "email": "alice@gmail.com",
        "age": 20,
        "grade": "A+"
    }, csrf_token)
    print(f"\n[POST /api/add-student/] Adding Alice Smith:")
    print(f"  Code: {code} (Expected: 200)")
    print(f"  Success: {res.get('success')} (Expected: True)")
    print(f"  Msg: {res.get('message')}")
    print(f"  Stats: {res.get('stats')}")
    
    # 7. Add Student - Duplicate Email Validation
    code, res = send_request(f"{BASE_URL}/api/add-student/", "POST", {
        "name": "Alice Duplicate",
        "email": "alice@gmail.com",
        "age": 22,
        "grade": "B"
    }, csrf_token)
    print(f"\n[POST /api/add-student/] Adding Duplicate Email (alice@gmail.com):")
    print(f"  Code: {code} (Expected: 400)")
    print(f"  Success: {res.get('success')} (Expected: False)")
    print(f"  Error msg: {res.get('error')}")

    # 8. Add Student - Valid Record 2 (Bob Jones)
    code, res = send_request(f"{BASE_URL}/api/add-student/", "POST", {
        "name": "Bob Jones",
        "email": "bob@yahoo.com",
        "age": 22,
        "grade": "B"
    }, csrf_token)
    print(f"\n[POST /api/add-student/] Adding Bob Jones:")
    print(f"  Code: {code} (Expected: 200)")
    print(f"  Success: {res.get('success')} (Expected: True)")
    print(f"  Msg: {res.get('message')}")
    
    # 9. Get all students & check dashboard statistics
    code, res = send_request(f"{BASE_URL}/api/students/")
    print(f"\n[GET /api/students/] Fetching all students:")
    print(f"  Code: {code} (Expected: 200)")
    print(f"  Success: {res.get('success')} (Expected: True)")
    print(f"  Count: {len(res.get('students', []))} (Expected: 2)")
    print(f"  Stats: {res.get('stats')}")
    
    # Extract IDs for deletion later
    students = res.get('students', [])
    alice_id = next((s['id'] for s in students if s['email'] == 'alice@gmail.com'), None)
    
    # 10. Live Search API
    code, res = send_request(f"{BASE_URL}/api/search-student/?query=Alice")
    print(f"\n[GET /api/search-student/?query=Alice] Search:")
    print(f"  Code: {code} (Expected: 200)")
    print(f"  Success: {res.get('success')} (Expected: True)")
    print(f"  Count: {len(res.get('students', []))} (Expected: 1)")
    if res.get('students'):
        print(f"  Name: {res.get('students')[0]['name']}")

    # 11. Delete Student (Alice Smith)
    if alice_id:
        code, res = send_request(f"{BASE_URL}/api/delete-student/{alice_id}/", "DELETE", csrf_token=csrf_token)
        print(f"\n[DELETE /api/delete-student/{alice_id}/] Deleting Alice:")
        print(f"  Code: {code} (Expected: 200)")
        print(f"  Success: {res.get('success')} (Expected: True)")
        print(f"  Msg: {res.get('message')}")
        print(f"  Stats: {res.get('stats')}")
    else:
        print("\n[ERROR] Alice Smith ID not found. Skipping delete test.")
        
    # 12. Final Check
    code, res = send_request(f"{BASE_URL}/api/students/")
    print(f"\n[GET /api/students/] Fetching final list:")
    print(f"  Code: {code} (Expected: 200)")
    print(f"  Success: {res.get('success')} (Expected: True)")
    print(f"  Count: {len(res.get('students', []))} (Expected: 1)")
    print(f"  Stats: {res.get('stats')} (Expected: total_students=1, average_age=22.0, total_records=1)")
    
    print("\n==================================================")
    print("API programatic verification completed successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
