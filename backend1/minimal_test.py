#!/usr/bin/env python3
"""
Minimal test để debug coroutine issue
"""

import sys
import os
import asyncio

# Add path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_minimal():
    """Minimal test"""
    try:
        from app.services.rag_service_unified import RAGServiceUnified
        
        print("Creating service...")
        service = RAGServiceUnified()
        
        print("Initializing...")
        await service.initialize()
        
        print("Testing query...")
        result = await service.query(
            question="Test question",
            top_k=1,
            use_enhancement=False  # Start with no enhancement
        )
        
        print(f"Result type: {type(result)}")
        print(f"Answer type: {type(result.get('answer', 'N/A'))}")
        print(f"Answer: {result.get('answer', 'N/A')[:100]}...")
        
        if 'coroutine' in str(type(result.get('answer', ''))):
            print("❌ Found coroutine in answer!")
        else:
            print("✅ No coroutine found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_minimal())
