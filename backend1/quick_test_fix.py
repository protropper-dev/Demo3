#!/usr/bin/env python3
"""
Quick test để kiểm tra các fix cho warning và validation issues
"""

import requests
import json
import time

def test_ddos_question():
    """Test câu hỏi DDoS với các fix mới"""
    
    print("🧪 Quick Test - DDoS Question with Fixes")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = "/api/v1/chat/send"
    
    test_data = {
        "message": "Tấn công DDoS là gì?",
        "top_k": 3
    }
    
    try:
        print("📝 Sending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json=test_data,
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
            
            # Show answer
            answer = result.get('ai_response', '')
            print(f"\n📄 Answer ({len(answer)} chars):")
            print("-" * 30)
            print(answer)
            
            # Check for issues
            if "Enhanced response too long, truncating" in str(result):
                print("❌ Still has truncation issue")
            else:
                print("✅ No truncation issue")
                
            if "Enhanced response missing key information" in str(result):
                print("❌ Still has missing key information issue")
            else:
                print("✅ No missing key information issue")
                
        else:
            print("❌ Error!")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ddos_question()
