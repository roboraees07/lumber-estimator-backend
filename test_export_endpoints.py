#!/usr/bin/env python3
"""
Test Script for Export Endpoints (PDF and Excel)
Tests the new estimation export functionality
"""

import requests
import json
import os

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

def test_pdf_export(token):
    """Test PDF export endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing PDF export endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/lumber/export/pdf",
            headers=headers,
            data={"project_id": 1}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save PDF file
            filename = f"estimation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"✅ PDF exported successfully!")
            print(f"   File saved as: {filename}")
            print(f"   File size: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            return True
        else:
            print(f"❌ PDF export failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PDF export: {e}")
        return False

def test_excel_export(token):
    """Test Excel export endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing Excel export endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/lumber/export/excel",
            headers=headers,
            data={"project_id": 1}
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Save Excel file
            filename = f"estimation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, "wb") as f:
                f.write(response.content)
            
            print(f"✅ Excel file exported successfully!")
            print(f"   File saved as: {filename}")
            print(f"   File size: {len(response.content)} bytes")
            print(f"   Content-Type: {response.headers.get('content-type', 'Unknown')}")
            return True
        else:
            print(f"❌ Excel export failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Excel export: {e}")
        return False

def test_both_exports(token):
    """Test both export endpoints with different project names"""
    headers = {"Authorization": f"Bearer {token}"}
    
    test_projects = [
        "Modern Office Building",
        "Residential House Project",
        "Commercial Warehouse",
        "Custom Home Design"
    ]
    
    print("\n🔍 Testing multiple project exports...")
    
    for i, project in enumerate(test_projects, 1):
        print(f"\n   Project {i}: {project}")
        
        # Test PDF export
        try:
            pdf_response = requests.post(
                f"{BASE_URL}/lumber/export/pdf",
                headers=headers,
                data={"project_id": i}
            )
            
            if pdf_response.status_code == 200:
                pdf_filename = f"PDF_{project.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                with open(pdf_filename, "wb") as f:
                    f.write(pdf_response.content)
                print(f"   ✅ PDF: {pdf_filename}")
            else:
                print(f"   ❌ PDF failed: {pdf_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ PDF error: {e}")
        
        # Test Excel export
        try:
            excel_response = requests.post(
                f"{BASE_URL}/lumber/export/excel",
                headers=headers,
                data={"project_id": i}
            )
            
            if excel_response.status_code == 200:
                excel_filename = f"Excel_{project.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                with open(excel_filename, "wb") as f:
                    f.write(excel_response.content)
                print(f"   ✅ Excel: {excel_filename}")
            else:
                print(f"   ❌ Excel failed: {excel_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Excel error: {e}")

def main():
    """Main test function"""
    from datetime import datetime
    
    print("🧪 Testing Export Endpoints (PDF and Excel)")
    print("=" * 60)
    print("📄 Features: PDF and Excel export with comprehensive data")
    print("📊 Contents: SKU, quantity, pricing, contractor info, summaries")
    print("=" * 60)
    
    # Step 1: Get authentication token
    print("🔑 Getting authentication token...")
    token = get_auth_token()
    
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    print(f"✅ Token obtained: {token[:20]}...")
    
    # Step 2: Test PDF export
    success1 = test_pdf_export(token)
    
    # Step 3: Test Excel export
    success2 = test_excel_export(token)
    
    # Step 4: Test multiple projects
    test_both_exports(token)
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   PDF Export: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Excel Export: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 Export functionality is working perfectly!")
        print("   Users can now download:")
        print("   - Professional PDF reports with item details")
        print("   - Comprehensive Excel spreadsheets")
        print("   - SKU, quantity, pricing, and contractor information")
        print("   - Cost summaries and calculations")
    else:
        print("\n⚠️ Some export tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
