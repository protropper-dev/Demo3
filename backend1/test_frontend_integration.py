#!/usr/bin/env python3
"""
Test script để kiểm tra frontend integration với pipeline RAG → LLM Enhancement
"""

import requests
import json
import time

def test_chat_endpoint_with_enhancement():
    """Test chat endpoint với LLM enhancement"""
    
    print("🧪 Testing Chat Endpoint with LLM Enhancement")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/chat/send"
    
    test_cases = [
        {
            "name": "Test Chat với LLM Enhancement (Luôn enabled)",
            "data": {
                "message": "An toàn thông tin là gì?",
                "top_k": 3
            }
        },
        {
            "name": "Test Chat với câu hỏi khác",
            "data": {
                "message": "ISO 27001 có những yêu cầu nào?",
                "top_k": 5
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 50)
        
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
                print(f"💬 Chat ID: {result.get('chat_id', 'N/A')}")
                print(f"📨 Message ID: {result.get('message_id', 'N/A')}")
                
                # Show answer preview
                answer = result.get('ai_response', '')
                print(f"📄 Answer preview: {answer[:100]}...")
                
                # Show original response if available
                if result.get('original_response'):
                    original = result.get('original_response', '')
                    print(f"📄 Original preview: {original[:100]}...")
                
                # Show sources
                sources = result.get('sources', [])
                if sources:
                    print(f"\n📚 Sources:")
                    for j, source in enumerate(sources[:3], 1):
                        print(f"  {j}. {source.get('display_name', 'Unknown')} (Score: {source.get('similarity_score', 0.0):.3f})")
                
            else:
                print("❌ Error!")
                print(f"📄 Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

def test_chat_history():
    """Test chat history endpoint"""
    
    print("\n🔍 Testing Chat History")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/v1/chat/history", timeout=10)
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat history retrieved!")
            print(f"📝 Total chats: {result.get('total', 0)}")
            print(f"📄 Chats in response: {len(result.get('chats', []))}")
        else:
            print("❌ Chat history failed!")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat history error: {e}")

def test_rag_endpoint_comparison():
    """So sánh kết quả giữa chat endpoint và rag endpoint"""
    
    print("\n🔍 Comparing Chat vs RAG Endpoints")
    print("-" * 40)
    
    question = "ISO 27001 có những yêu cầu nào?"
    
    # Test chat endpoint
    print("📝 Testing Chat Endpoint...")
    try:
        chat_response = requests.post(
            "http://localhost:8000/api/v1/chat/send",
            json={
                "message": question,
                "top_k": 3
            },
            timeout=30
        )
        
        if chat_response.status_code == 200:
            chat_result = chat_response.json()
            print(f"✅ Chat: {chat_result.get('method', 'unknown')}, enhancement: {chat_result.get('enhancement_applied', False)}")
        else:
            print(f"❌ Chat failed: {chat_response.status_code}")
    except Exception as e:
        print(f"❌ Chat error: {e}")
    
    # Test RAG endpoint
    print("📝 Testing RAG Endpoint...")
    try:
        rag_response = requests.post(
            "http://localhost:8000/api/v1/rag/query",
            json={
                "question": question,
                "top_k": 3,
                "use_enhancement": True
            },
            timeout=30
        )
        
        if rag_response.status_code == 200:
            rag_result = rag_response.json()
            print(f"✅ RAG: {rag_result.get('method', 'unknown')}, enhancement: {rag_result.get('enhancement_applied', False)}")
        else:
            print(f"❌ RAG failed: {rag_response.status_code}")
    except Exception as e:
        print(f"❌ RAG error: {e}")

def main():
    """Main test function"""
    print("🚀 Frontend Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Chat endpoint with enhancement
    test_chat_endpoint_with_enhancement()
    
    # Test 2: Chat history
    test_chat_history()
    
    # Test 3: Compare endpoints
    test_rag_endpoint_comparison()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
