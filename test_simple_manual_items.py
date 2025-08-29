#!/usr/bin/env python3
"""
Simple Test Script for Manual Item Addition (Simplified)
Only requires: Item Name + Quantity
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

def test_simple_manual_item(token):
    """Test adding a manual item with just name and quantity"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test data - SIMPLIFIED: Just name and quantity
    test_item = {
        "project_name": "Simple House Project",
        "item_name": "2x4 Studs",  # Just item name
        "quantity": 50,            # Just quantity
        "unit": "each",            # Optional, defaults to "each"
        "notes": "Added during estimation review"  # Optional
    }
    
    try:
        print("🔍 Testing simplified manual item addition...")
        print(f"   Item: {test_item['item_name']}")
        print(f"   Quantity: {test_item['quantity']} {test_item['unit']}")
        print(f"   Project: {test_item['project_name']}")
        
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
            print(f"   Category: {data.get('category')}")
            print(f"   Unit Price: ${data.get('estimated_unit_price', 'N/A')}")
            print(f"   Total Cost: ${data.get('estimated_cost', 'N/A')}")
            print(f"   Database Match: {data.get('database_match_found', False)}")
            print(f"   Estimation Method: {data.get('estimation_method', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to add manual item: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing manual item addition: {e}")
        return False

def test_multiple_simple_items(token):
    """Test adding multiple items with different names"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different item types
    test_items = [
        {
            "project_name": "Simple House Project",
            "item_name": "OSB Sheathing",
            "quantity": 20,
            "notes": "Wall sheathing"
        },
        {
            "project_name": "Simple House Project", 
            "item_name": "Roof Shingles",
            "quantity": 30,
            "unit": "sqft",
            "notes": "Roof covering"
        },
        {
            "project_name": "Simple House Project",
            "item_name": "Concrete Mix",
            "quantity": 10,
            "unit": "bags",
            "notes": "Foundation work"
        }
    ]
    
    print("\n🔍 Testing multiple simple items...")
    
    for i, item in enumerate(test_items, 1):
        print(f"\n   Item {i}: {item['item_name']} - {item['quantity']} {item.get('unit', 'each')}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/lumber/items/manual-add",
                headers=headers,
                json=item
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Added: ${data.get('estimated_cost', 'N/A')} | DB Match: {data.get('database_match_found', False)}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Simplified Manual Item Addition")
    print("=" * 60)
    print("📋 Requirements: Just Item Name + Quantity")
    print("🤖 Features: Automatic cost estimation + Database lookup")
    print("=" * 60)
    
    # Step 1: Get authentication token
    print("🔑 Getting authentication token...")
    token = get_auth_token()
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print(f"✅ Token obtained: {token[:20]}...")
    
    # Step 2: Test single item addition
    success1 = test_simple_manual_item(token)
    
    # Step 3: Test multiple items
    test_multiple_simple_items(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Simplified Manual Item Addition: {'✅ PASS' if success1 else '❌ FAIL'}")
    
    if success1:
        print("\n🎉 Simplified manual item addition is working!")
        print("   Estimators can now add items with just:")
        print("   - Item Name")
        print("   - Quantity")
        print("   - System automatically estimates costs! 🚀")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
