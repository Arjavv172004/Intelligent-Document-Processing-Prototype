#!/usr/bin/env python3
"""
Test script for the Innovo IDP application
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from app import app, DocumentProcessor
        print("✅ Main app imports successfully")
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False
    
    try:
        processor = DocumentProcessor()
        print("✅ DocumentProcessor created successfully")
    except Exception as e:
        print(f"❌ DocumentProcessor creation failed: {e}")
        return False
    
    return True

def test_document_processing():
    """Test document processing functionality"""
    print("\nTesting document processing...")
    
    try:
        from app import DocumentProcessor
        processor = DocumentProcessor()
        
        # Test mock OCR
        mock_text = processor.mock_ocr_extraction("test_invoice.png")
        print("✅ Mock OCR extraction works")
        
        # Test data extraction
        extracted_data = processor.extract_structured_data(mock_text)
        print("✅ Data extraction works")
        print(f"   Extracted document type: {extracted_data['document_type']}")
        print(f"   Extracted company: {extracted_data['company_name']}")
        print(f"   Extracted amount: {extracted_data['amount']}")
        
        return True
    except Exception as e:
        print(f"❌ Document processing test failed: {e}")
        return False

def test_flask_routes():
    """Test Flask routes"""
    print("\nTesting Flask routes...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main page loads successfully")
            else:
                print(f"❌ Main page failed: {response.status_code}")
                return False
            
            # Test dashboard
            response = client.get('/dashboard')
            if response.status_code == 200:
                print("✅ Dashboard loads successfully")
            else:
                print(f"❌ Dashboard failed: {response.status_code}")
                return False
            
            # Test analytics endpoint
            response = client.get('/analytics')
            if response.status_code == 200:
                print("✅ Analytics endpoint works")
            else:
                print(f"❌ Analytics endpoint failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Innovo IDP Application")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_document_processing,
        test_flask_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python app.py")
        print("\nThen visit: http://localhost:5001")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
