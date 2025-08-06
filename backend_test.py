import requests
import sys
import json
from datetime import datetime

class EmergencyAPITester:
    def __init__(self, base_url="https://88e7f437-5203-4592-a7bb-8f47c80bc208.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_help_request_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                        if response_data and len(response_data) > 0:
                            print(f"   First item keys: {list(response_data[0].keys())}")
                    else:
                        print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")

            return success, response.json() if response.text else {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout")
            return False, {}
        except requests.exceptions.ConnectionError:
            print(f"❌ Failed - Connection error")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_get_all_instructions(self):
        """Test getting all emergency instructions"""
        success, response = self.run_test(
            "Get All Emergency Instructions",
            "GET",
            "emergency-instructions",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} total instructions")
            # Check if we have instructions for all 3 emergency types
            types_found = set()
            for instruction in response:
                if 'type' in instruction:
                    types_found.add(instruction['type'])
            print(f"   Emergency types found: {types_found}")
            expected_types = {'choking', 'bleeding', 'allergic_reaction'}
            if types_found == expected_types:
                print(f"   ✅ All expected emergency types present")
            else:
                print(f"   ⚠️ Missing types: {expected_types - types_found}")
        return success

    def test_get_choking_instructions(self):
        """Test getting choking emergency instructions"""
        success, response = self.run_test(
            "Get Choking Instructions",
            "GET",
            "emergency-instructions/choking",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} choking instructions")
            for i, instruction in enumerate(response):
                if 'title' in instruction:
                    print(f"   {i+1}. {instruction['title']}")
        return success

    def test_get_bleeding_instructions(self):
        """Test getting bleeding emergency instructions"""
        success, response = self.run_test(
            "Get Bleeding Instructions",
            "GET",
            "emergency-instructions/bleeding",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} bleeding instructions")
            for i, instruction in enumerate(response):
                if 'title' in instruction:
                    print(f"   {i+1}. {instruction['title']}")
        return success

    def test_get_allergic_reaction_instructions(self):
        """Test getting allergic reaction emergency instructions"""
        success, response = self.run_test(
            "Get Allergic Reaction Instructions",
            "GET",
            "emergency-instructions/allergic_reaction",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} allergic reaction instructions")
            for i, instruction in enumerate(response):
                if 'title' in instruction:
                    print(f"   {i+1}. {instruction['title']}")
        return success

    def test_invalid_emergency_type(self):
        """Test getting instructions for invalid emergency type"""
        success, response = self.run_test(
            "Get Invalid Emergency Type",
            "GET",
            "emergency-instructions/invalid_type",
            404
        )
        return success

    def test_create_help_request(self):
        """Test creating a help request"""
        test_data = {
            "emergency_type": "choking",
            "location_description": "123 Test Street, Apartment 4B",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "contact_phone": "+1-555-0123",
            "additional_info": "Adult choking on food in restaurant"
        }
        
        success, response = self.run_test(
            "Create Help Request",
            "POST",
            "help-requests",
            200,
            data=test_data
        )
        
        if success and 'id' in response:
            self.created_help_request_id = response['id']
            print(f"   Created help request with ID: {self.created_help_request_id}")
            
            # Verify all fields are present
            expected_fields = ['id', 'emergency_type', 'location_description', 'status', 'created_at']
            for field in expected_fields:
                if field in response:
                    print(f"   ✅ {field}: {response[field]}")
                else:
                    print(f"   ❌ Missing field: {field}")
        
        return success

    def test_get_help_requests(self):
        """Test getting all help requests"""
        success, response = self.run_test(
            "Get All Help Requests",
            "GET",
            "help-requests",
            200
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} active help requests")
        return success

    def test_get_specific_help_request(self):
        """Test getting a specific help request"""
        if not self.created_help_request_id:
            print("⚠️ Skipping - No help request ID available")
            return True
            
        success, response = self.run_test(
            "Get Specific Help Request",
            "GET",
            f"help-requests/{self.created_help_request_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"   Retrieved help request: {response['id']}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Emergency type: {response.get('emergency_type', 'N/A')}")
        
        return success

    def test_update_help_request(self):
        """Test updating a help request status"""
        if not self.created_help_request_id:
            print("⚠️ Skipping - No help request ID available")
            return True
            
        update_data = {
            "status": "responded"
        }
        
        success, response = self.run_test(
            "Update Help Request Status",
            "PUT",
            f"help-requests/{self.created_help_request_id}",
            200,
            data=update_data
        )
        
        if success and 'status' in response:
            print(f"   Updated status to: {response['status']}")
        
        return success

    def test_invalid_help_request_id(self):
        """Test getting help request with invalid ID"""
        success, response = self.run_test(
            "Get Invalid Help Request ID",
            "GET",
            "help-requests/invalid-id-12345",
            404
        )
        return success

def main():
    print("🚨 Emergency First Aid Assistant - Backend API Testing")
    print("=" * 60)
    
    tester = EmergencyAPITester()
    
    # Test sequence
    tests = [
        ("API Root", tester.test_api_root),
        ("All Instructions", tester.test_get_all_instructions),
        ("Choking Instructions", tester.test_get_choking_instructions),
        ("Bleeding Instructions", tester.test_get_bleeding_instructions),
        ("Allergic Reaction Instructions", tester.test_get_allergic_reaction_instructions),
        ("Invalid Emergency Type", tester.test_invalid_emergency_type),
        ("Create Help Request", tester.test_create_help_request),
        ("Get All Help Requests", tester.test_get_help_requests),
        ("Get Specific Help Request", tester.test_get_specific_help_request),
        ("Update Help Request", tester.test_update_help_request),
        ("Invalid Help Request ID", tester.test_invalid_help_request_id),
    ]
    
    print(f"\nRunning {len(tests)} test categories...\n")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 BACKEND API TEST RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All backend API tests passed!")
        return 0
    else:
        print("⚠️ Some backend API tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())