#!/usr/bin/env python3
"""
Setup script to configure provider working hours for testing appointment availability
"""

import requests
import json
from datetime import time

def setup_provider_working_hours():
    """Set up working hours for provider ID 1"""
    
    # Use a real provider UUID from the database
    provider_id = "4e00566c-f82c-4ab1-a263-e63cd04cdc05"  # Dr. Sarah Wilson
    
    # Sample working hours (Monday to Friday, 9 AM to 6 PM)
    working_hours = [
        {
            "day_of_week": 0,  # Monday
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "is_available": True
        },
        {
            "day_of_week": 1,  # Tuesday
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "is_available": True
        },
        {
            "day_of_week": 2,  # Wednesday
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "is_available": True
        },
        {
            "day_of_week": 3,  # Thursday
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "is_available": True
        },
        {
            "day_of_week": 4,  # Friday
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "is_available": True
        },
        {
            "day_of_week": 5,  # Saturday
            "start_time": "10:00:00",
            "end_time": "14:00:00",
            "is_available": True
        },
        {
            "day_of_week": 6,  # Sunday
            "start_time": "10:00:00",
            "end_time": "14:00:00",
            "is_available": False  # Not available on Sundays
        }
    ]
    
    try:
        # Set working hours for provider
        response = requests.post(
            f"http://localhost:4002/api/v1/providers/{provider_id}/working-hours",
            json=working_hours,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Provider working hours set successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to set working hours: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error setting working hours: {e}")

def test_availability():
    """Test the availability endpoint"""
    
    # Use a real provider UUID from the database
    provider_id = "4e00566c-f82c-4ab1-a263-e63cd04cdc05"  # Dr. Sarah Wilson
    
    try:
        # Test availability for August 25th, 2025 (Monday)
        response = requests.get(
            f"http://localhost:4002/api/v1/providers/{provider_id}/availability",
            params={
                "appointment_date": "2025-08-25"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Availability test successful!")
            print(f"Provider ID: {data['provider_id']}")
            print(f"Date: {data['date']}")
            print(f"Day of week: {data['day_of_week']} (0=Monday)")
            print(f"Working hours: {data['working_hours']['start']} - {data['working_hours']['end']}")
            print(f"Total available slots: {data['total_slots']}")
            print(f"Booked appointments: {data['booked_appointments']}")
            print(f"First 5 slots: {data['available_slots'][:5]}")
        else:
            print(f"❌ Availability test failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing availability: {e}")

def setup_jennifer_williams_hours():
    """Set up working hours for Jennifer Williams (Pediatrics)"""
    
    # Jennifer Williams provider ID
    provider_id = "b47280cd-eb9f-4b97-a51f-4d14168cfbb1"
    
    # Working hours for Jennifer Williams (Pediatrics)
    working_hours = [
        {
            "day_of_week": 0,  # Monday
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_available": True
        },
        {
            "day_of_week": 1,  # Tuesday
            "start_time": "08:00:00",
            "end_time": "16:00:00",
            "is_available": True
        },
        {
            "day_of_week": 2,  # Wednesday
            "start_time": "08:00:00",
            "end_time": "16:00:00",
            "is_available": True
        },
        {
            "day_of_week": 3,  # Thursday
            "start_time": "08:00:00",
            "end_time": "16:00:00",
            "is_available": True
        },
        {
            "day_of_week": 4,  # Friday
            "start_time": "08:00:00",
            "end_time": "16:00:00",
            "is_available": True
        },
        {
            "day_of_week": 5,  # Saturday
            "start_time": "08:00:00",
            "end_time": "14:00:00",
            "is_available": True
        },
        {
            "day_of_week": 6,  # Sunday
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "is_available": False  # Not available on Sundays
        }
    ]
    
    try:
        # Set working hours for Jennifer Williams
        response = requests.post(
            f"http://localhost:4002/api/v1/providers/{provider_id}/working-hours",
            json=working_hours,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Jennifer Williams working hours set successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to set Jennifer Williams working hours: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error setting Jennifer Williams working hours: {e}")

def test_jennifer_availability():
    """Test Jennifer Williams availability"""
    
    provider_id = "b47280cd-eb9f-4b97-a51f-4d14168cfbb1"
    
    try:
        # Test availability for August 25th, 2025
        response = requests.get(
            f"http://localhost:4002/api/v1/providers/{provider_id}/availability",
            params={
                "appointment_date": "2025-08-25"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Jennifer Williams availability test successful!")
            print(f"Provider ID: {data['provider_id']}")
            print(f"Date: {data['date']}")
            print(f"Total available slots: {data['total_slots']}")
            print(f"First 5 slots: {data['available_slots'][:5]}")
        else:
            print(f"❌ Jennifer Williams availability test failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing Jennifer Williams availability: {e}")

if __name__ == "__main__":
    print("🚀 Setting up provider working hours...")
    setup_provider_working_hours()
    
    print("\n🔧 Setting up Jennifer Williams working hours...")
    setup_jennifer_williams_hours()
    
    print("\n🧪 Testing availability endpoints...")
    test_availability()
    test_jennifer_availability()
