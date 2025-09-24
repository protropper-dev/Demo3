#!/usr/bin/env python3
"""
Test script để kiểm tra API endpoint sau khi sửa lỗi async
"""

import requests
import json
import time

def test_api_endpoint():
    """Test API endpoint"""
    
    print("🧪 Testing API Endpoint: /api/v1/rag/query")
    print("=" * 50)
    
    # Test data
    test_cases = [
        {
            "name": "Test với LLM Enhancement",
            "data": {
                "question": "An toàn thông tin là gì?",
                "top_k": 3,
                "use_enhancement": True
            }
        },
        {
            "name": "Test không có LLM Enhancement", 
            "data": {
                "question": "An toàn thông tin là gì?",
                "top_k": 3,
                "use_enhancement": False
            }
        }
    ]
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/rag/query"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 30)
        
        try:
            # Make request
            start_time = time.time()
            response = requests.post(
                f"{base_url}{endpoint}",
                json=test_case['data'],
                timeout=30
            )
            end_time = time.time()
            
            print(f"⏱️  Response time: {end_time - start_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"📝 Method: {result.get('method', 'unknown')}")
                print(f"🚀 Enhancement applied: {result.get('enhancement_applied', False)}")
                print(f"📊 Confidence: {result.get('confidence', 0.0):.3f}")
                print(f"⏱️  Processing time: {result.get('processing_time_ms', 0)}ms")
                print(f"📚 Sources: {result.get('total_sources', 0)}")
                
                # Show answer preview
                answer = result.get('answer', '')
                print(f"📄 Answer preview: {answer[:100]}...")
                
                # Show original response if available
                if result.get('original_response'):
                    original = result.get('original_response', '')
                    print(f"📄 Original preview: {original[:100]}...")
                
            else:
                print("❌ Error!")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

def test_health_endpoint():
    """Test health endpoint"""
    
    print("\n🔍 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/rag/health", timeout=10)
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed!")
            print(f"📝 Status: {result.get('status', 'unknown')}")
            print(f"🔧 Service: {result.get('service_name', 'unknown')}")
        else:
            print("❌ Health check failed!")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")

def main():
    """Main test function"""
    print("🚀 API Endpoint Test Suite")
    print("=" * 50)
    
    # Test health first
    test_health_endpoint()
    
    # Test main endpoint
    test_api_endpoint()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
