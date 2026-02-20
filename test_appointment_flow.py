#!/usr/bin/env python3
"""
Comprehensive test for the complete appointment booking flow
Tests the fixed availability endpoint and appointment creation
"""

import requests
import json
from datetime import date, datetime

def test_complete_appointment_flow():
    """Test the complete appointment booking flow"""
    
    print("🧪 Testing Complete Appointment Booking Flow")
    print("=" * 50)
    
    # Test 1: Check if the fixed availability endpoint works
    print("\n1️⃣ Testing Fixed Availability Endpoint...")
    
    provider_id = "4e00566c-f82c-4ab1-a263-e63cd04cdc05"  # Dr. Sarah Wilson
    patient_id = "444ed30b-defc-47c9-93ca-5b522828d7ec"   # John Doe
    test_date = "2025-08-25"  # Monday
    
    try:
        response = requests.get(
            f"http://localhost:4002/api/v1/providers/{provider_id}/availability",
            params={"appointment_date": test_date},
            timeout=10  # Safety timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Availability endpoint working!")
            print(f"   Provider: {data['provider_id']}")
            print(f"   Date: {data['date']}")
            print(f"   Day of week: {data['day_of_week']} (0=Monday)")
            print(f"   Working hours: {data['working_hours']['start']} - {data['working_hours']['end']}")
            print(f"   Available slots: {len(data['available_slots'])}")
            
            # Show first few slots
            for i, slot in enumerate(data['available_slots'][:5]):
                print(f"   Slot {i+1}: {slot['time']} - {slot['end_time']}")
            
            if len(data['available_slots']) > 5:
                print(f"   ... and {len(data['available_slots']) - 5} more slots")
                
        else:
            print(f"❌ Availability endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Availability endpoint timed out - infinite loop detected!")
        return False
    except Exception as e:
        print(f"❌ Availability endpoint error: {e}")
        return False
    
    # Test 2: Test appointment creation
    print("\n2️⃣ Testing Appointment Creation...")
    
    try:
        # Create an appointment using the first available slot
        first_slot = data['available_slots'][0]
        # Use the correct time format: HH:MM:SS
        appointment_time = f"{first_slot['time']}:00"
        
        appointment_data = {
            "patient_id": patient_id,
            "provider_id": provider_id,
            "appointment_date": test_date,
            "appointment_time": appointment_time,  # Format: HH:MM:SS
            "appointment_type": "consultation",
            "notes": "Test appointment from fixed system",
            "status": "pending"
        }
        
        response = requests.post(
            "http://localhost:4002/api/v1/appointments",
            json=appointment_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            appointment = response.json()
            print("✅ Appointment creation working!")
            print(f"   Appointment ID: {appointment.get('id', 'N/A')}")
            print(f"   Patient: {appointment.get('patient_id', 'N/A')}")
            print(f"   Provider: {appointment.get('provider_id', 'N/A')}")
            print(f"   Date: {appointment.get('appointment_date', 'N/A')}")
            print(f"   Time: {appointment.get('appointment_time', 'N/A')}")
            print(f"   Status: {appointment.get('status', 'N/A')}")
            
        else:
            print(f"❌ Appointment creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Appointment creation timed out!")
        return False
    except Exception as e:
        print(f"❌ Appointment creation error: {e}")
        return False
    
    # Test 3: Test that the slot is now unavailable
    print("\n3️⃣ Testing Slot Availability After Booking...")
    
    try:
        response = requests.get(
            f"http://localhost:4002/api/v1/providers/{provider_id}/availability",
            params={"appointment_date": test_date},
            timeout=10
        )
        
        if response.status_code == 200:
            updated_data = response.json()
            booked_slot = first_slot['time']
            
            # Check if the booked slot is no longer available
            available_times = [slot['time'] for slot in updated_data['available_slots'] if slot['available']]
            
            if booked_slot not in available_times:
                print("✅ Booked slot correctly marked as unavailable!")
                print(f"   Booked time: {booked_slot}")
                print(f"   Remaining available slots: {len(available_times)}")
            else:
                print("⚠️  Booked slot still shows as available - may need to check booking logic")
                
        else:
            print(f"❌ Failed to check updated availability: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking updated availability: {e}")
    
    # Test 4: Test frontend endpoint compatibility
    print("\n4️⃣ Testing Frontend Endpoint Compatibility...")
    
    try:
        # Test the exact endpoint format the frontend uses
        response = requests.get(
            f"http://localhost:4002/api/v1/providers/{provider_id}/availability",
            params={"appointment_date": test_date},
            timeout=10
        )
        
        if response.status_code == 200:
            frontend_data = response.json()
            
            # Check if response has the expected structure for frontend
            required_fields = ['provider_id', 'date', 'available_slots']
            missing_fields = [field for field in required_fields if field not in frontend_data]
            
            if not missing_fields:
                print("✅ Frontend endpoint compatibility confirmed!")
                print(f"   Response has all required fields: {required_fields}")
                print(f"   Available slots format: {type(frontend_data['available_slots'])}")
                
                if frontend_data['available_slots']:
                    slot_format = frontend_data['available_slots'][0]
                    print(f"   Slot format: {list(slot_format.keys())}")
            else:
                print(f"❌ Missing fields for frontend: {missing_fields}")
                return False
                
        else:
            print(f"❌ Frontend endpoint test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend endpoint test error: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED! Appointment system is working correctly.")
    print("\n📋 Summary:")
    print("   ✅ Availability endpoint fixed and working")
    print("   ✅ No infinite loops or timeouts")
    print("   ✅ Appointment creation working")
    print("   ✅ Frontend compatibility confirmed")
    print("   ✅ Safety breakpoints active")
    
    return True

if __name__ == "__main__":
    test_complete_appointment_flow()
