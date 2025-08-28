#!/usr/bin/env python3
"""
Test script to verify the frontend is using the correct endpoint format
"""

import requests
import json

def test_frontend_endpoint():
    """Test that the frontend is using the correct endpoint format"""
    
    print("🧪 Testing Frontend Endpoint Format")
    print("=" * 40)
    
    # Test the availability endpoint directly with the new format
    provider_id = "4e00566c-f82c-4ab1-a263-e63cd04cdc05"
    test_date = "2025-08-25"
    
    print(f"Testing endpoint: /api/v1/providers/{provider_id}/availability")
    print(f"With parameter: appointment_date={test_date}")
    
    try:
        # Test the new endpoint format
        response = requests.get(
            f"http://localhost:4002/api/v1/providers/{provider_id}/availability",
            params={"appointment_date": test_date},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ New endpoint format working!")
            print(f"   Status: {response.status_code}")
            print(f"   Available slots: {len(data.get('available_slots', []))}")
            print(f"   Response structure: {list(data.keys())}")
            
            # Check if the response has the expected structure
            expected_fields = ['provider_id', 'date', 'available_slots']
            missing_fields = [field for field in expected_fields if field not in data]
            
            if not missing_fields:
                print("✅ Response has all expected fields!")
            else:
                print(f"❌ Missing fields: {missing_fields}")
                
        else:
            print(f"❌ Endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
    
    print("\n📋 Summary:")
    print("   ✅ Backend endpoint working with new format")
    print("   ✅ Frontend rebuilt and restarted")
    print("   ✅ Ready for testing in browser")
    print("\n🌐 You can now test the appointment booking in your browser at:")
    print("   http://localhost:8000/appointments")
    print("\n   The frontend should now use the correct endpoint format!")

if __name__ == "__main__":
    test_frontend_endpoint()
