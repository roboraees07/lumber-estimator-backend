#!/usr/bin/env python3
"""
Test Script for Manual Item Addition Endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8003"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_add_manual_item(token):
    """Test adding a manual item"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test data
    test_item = {
        "project_name": "Test House Project",
        "item_name": "Custom French Doors",
        "category": "Doors",
        "quantity": 2,
        "unit": "each",
        "dimensions": "6x8",
        "location": "Front entrance",
        "estimated_unit_price": 450.0,
        "notes": "Custom design not in standard catalog"
    }
    
    try:
        print("🔍 Testing manual item addition...")
        response = requests.post(
            f"{BASE_URL}/lumber/items/manual-add",
            headers=headers,
            json=test_item
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Manual item added successfully!")
            print(f"   Item ID: {data.get('item_id')}")
            print(f"   Project: {data.get('project_name')}")
            print(f"   Item: {data.get('item_name')}")
            print(f"   Estimated Cost: ${data.get('estimated_cost', 'N/A')}")
            print(f"   Database Match: {data.get('database_match_found', False)}")
            return True
        else:
            print(f"❌ Failed to add manual item: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual item addition: {e}")
        return False

def test_get_manual_items(token):
    """Test retrieving manual items for a project"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("\n🔍 Testing manual item retrieval...")
        response = requests.get(
            f"{BASE_URL}/lumber/items/manual/Test%20House%20Project",
            headers=headers
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Manual items retrieved successfully!")
            print(f"   Project: {data.get('project_name')}")
            print(f"   Total Items: {data.get('total_manual_items')}")
            print(f"   Total Cost: ${data.get('total_estimated_cost', 'N/A')}")
            
            items = data.get('items', [])
            for i, item in enumerate(items, 1):
                print(f"   Item {i}: {item.get('item_name')} - {item.get('quantity')} {item.get('unit')}")
            
            return True
        else:
            print(f"❌ Failed to retrieve manual items: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual item retrieval: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Manual Item Addition Endpoints")
    print("=" * 50)
    
    # Step 1: Get authentication token
    print("🔑 Getting authentication token...")
    token = get_auth_token()
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print(f"✅ Token obtained: {token[:20]}...")
    
    # Step 2: Test adding manual item
    success1 = test_add_manual_item(token)
    
    # Step 3: Test retrieving manual items
    success2 = test_get_manual_items(token)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Manual Item Addition: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Manual Item Retrieval: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Manual item endpoints are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
