#!/usr/bin/env python
"""
Backend API Test Script
Run this after starting Django server to verify all endpoints work
Usage: python test_api.py
"""

import requests
import json
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://localhost:8000/api"
AUTH_URL = "http://localhost:8000/api/auth"

# Test credentials (matching populate_data.py users)
STUDENT_EMAIL = "etudiant1@etu.academiya.ma"
STUDENT_PASSWORD = "etudiant123"
ADMIN_EMAIL = "admin@admin.ma"
ADMIN_PASSWORD = "admin"

def print_test(name):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"🧪 TEST: {name}")
    print(f"{'='*60}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message):
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")


class APITester:
    def __init__(self):
        self.student_token = None
        self.admin_token = None
        self.session = requests.Session()
    
    def test_student_login(self):
        print_test("Student Login")
        try:
            response = self.session.post(
                f"{AUTH_URL}/login/",
                json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.student_token = data['access']
                print_success(f"Login successful - Role: {data.get('role')}")
                print_info(f"Token: {self.student_token[:20]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_admin_login(self):
        print_test("Admin Login")
        try:
            response = self.session.post(
                f"{AUTH_URL}/login/",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data['access']
                print_success(f"Login successful - Role: {data.get('role')}")
                print_info(f"Token: {self.admin_token[:20]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_get_departements(self):
        print_test("GET Departements (Public)")
        try:
            response = self.session.get(f"{BASE_URL}/departements/")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} departements")
                if data:
                    print_info(f"First dept: {data[0].get('name')} ({data[0].get('code')})")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_get_filieres(self):
        print_test("GET Filieres (Public)")
        try:
            response = self.session.get(f"{BASE_URL}/filieres/")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} filieres")
                if data:
                    print_info(f"First filiere: {data[0].get('name')} - Capacity: {data[0].get('capacity')}")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_get_modules(self):
        print_test("GET Modules (Public)")
        try:
            response = self.session.get(f"{BASE_URL}/modules/")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} modules")
                if data:
                    print_info(f"First module: {data[0].get('name')}")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_student_create_inscription(self):
        print_test("Student Create Inscription")
        if not self.student_token:
            print_warning("No student token - skipping")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.post(
                f"{BASE_URL}/inscriptions/",
                headers=headers,
                json={
                    "filiere": 1,
                    "academic_year": "2025-2026"
                }
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                print_success(f"Inscription created - ID: {data.get('id')}")
                print_info(f"Status: {data.get('status')}")
                return True
            elif response.status_code == 400:
                # Expected if already exists
                error = response.json()
                print_warning(f"Validation error (expected): {error}")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_error(f"Response: {response.text}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_student_get_my_inscriptions(self):
        print_test("Student Get My Inscriptions")
        if not self.student_token:
            print_warning("No student token - skipping")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.student_token}"}
            response = self.session.get(
                f"{BASE_URL}/inscriptions/my_inscriptions/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} inscriptions")
                for insc in data:
                    print_info(f"  - {insc.get('filiere_details', {}).get('name')} ({insc.get('status')})")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_admin_get_pending_inscriptions(self):
        print_test("Admin Get Pending Inscriptions")
        if not self.admin_token:
            print_warning("No admin token - skipping")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.get(
                f"{BASE_URL}/inscriptions/pending/",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} pending inscriptions")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def test_cors(self):
        print_test("CORS Headers")
        try:
            response = self.session.options(
                f"{BASE_URL}/departements/",
                headers={"Origin": "http://localhost:5173"}
            )
            
            cors_header = response.headers.get('Access-Control-Allow-Origin')
            if cors_header:
                print_success(f"CORS enabled: {cors_header}")
                return True
            else:
                print_error("CORS headers not found")
                return False
        except Exception as e:
            print_error(f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"🚀 ACADEMIYA-HUB BACKEND API TESTS")
        print(f"{'='*60}{Style.RESET_ALL}")
        print_info(f"Base URL: {BASE_URL}")
        print_info(f"Make sure Django server is running on http://localhost:8000\n")
        
        results = []
        
        # Authentication Tests
        results.append(("Student Login", self.test_student_login()))
        results.append(("Admin Login", self.test_admin_login()))
        
        # Public Endpoints
        results.append(("GET Departements", self.test_get_departements()))
        results.append(("GET Filieres", self.test_get_filieres()))
        results.append(("GET Modules", self.test_get_modules()))
        
        # Student Endpoints
        results.append(("Create Inscription", self.test_student_create_inscription()))
        results.append(("Get My Inscriptions", self.test_student_get_my_inscriptions()))
        
        # Admin Endpoints
        results.append(("Get Pending Inscriptions", self.test_admin_get_pending_inscriptions()))
        
        # Infrastructure
        results.append(("CORS Configuration", self.test_cors()))
        
        # Summary
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = f"{Fore.GREEN}✅ PASS" if result else f"{Fore.RED}❌ FAIL"
            print(f"{status:<25} {test_name}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
        
        if passed == total:
            print(f"{Fore.GREEN}🎉 ALL TESTS PASSED! Backend is ready!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}⚠️  Some tests failed. Check errors above.{Style.RESET_ALL}")


if __name__ == "__main__":
    print(f"\n{Fore.YELLOW}⚠️  PREREQUISITES:{Style.RESET_ALL}")
    print("1. Django server must be running: python manage.py runserver")
    print("2. Database must be populated: python manage.py populate_data")
    print("3. Using credentials from populate_data.py")
    print(f"   - Student: {STUDENT_EMAIL} / {STUDENT_PASSWORD}")
    print(f"   - Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    
    input(f"\n{Fore.CYAN}Press ENTER to start tests...{Style.RESET_ALL}")
    
    tester = APITester()
    tester.run_all_tests()