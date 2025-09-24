#!/usr/bin/env python3
"""
Test script để validate RAG + LLM Enhancement pipeline
"""

import asyncio
import json
import time
from typing import Dict, Any

# Import các service cần thiết
from app.services.rag_service_unified import RAGServiceUnified
from app.core.config import settings

async def test_rag_llm_enhancement():
    """Test pipeline 2-stage RAG → LLM Enhancement"""
    
    print("🚀 Testing RAG + LLM Enhancement Pipeline")
    print("=" * 60)
    
    # Khởi tạo service
    rag_service = RAGServiceUnified()
    
    try:
        # Initialize service
        print("📝 Initializing RAG service...")
        await rag_service.initialize()
        print("✅ RAG service initialized successfully")
        
        # Test questions
        test_questions = [
            "An toàn thông tin là gì?",
            "ISO 27001 có những yêu cầu nào?",
            "Các biện pháp bảo mật cơ bản?",
            "Luật An toàn thông tin quy định gì?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Test {i}: {question}")
            print("-" * 50)
            
            # Test với enhancement enabled
            print("📝 Testing with LLM Enhancement...")
            start_time = time.time()
            
            result_enhanced = await rag_service.query(
                question=question,
                top_k=3,
                use_enhancement=True
            )
            
            enhanced_time = time.time() - start_time
            
            # Test với enhancement disabled
            print("📝 Testing without LLM Enhancement...")
            start_time = time.time()
            
            result_basic = await rag_service.query(
                question=question,
                top_k=3,
                use_enhancement=False
            )
            
            basic_time = time.time() - start_time
            
            # So sánh kết quả
            print(f"\n📊 Results Comparison:")
            print(f"Enhanced Response ({enhanced_time:.2f}s):")
            print(f"  - Method: {result_enhanced.get('method', 'unknown')}")
            print(f"  - Enhancement Applied: {result_enhanced.get('enhancement_applied', False)}")
            print(f"  - Confidence: {result_enhanced.get('confidence', 0.0):.3f}")
            print(f"  - Answer Length: {len(result_enhanced.get('answer', ''))}")
            print(f"  - Answer Preview: {result_enhanced.get('answer', '')[:100]}...")
            
            print(f"\nBasic Response ({basic_time:.2f}s):")
            print(f"  - Method: {result_basic.get('method', 'unknown')}")
            print(f"  - Enhancement Applied: {result_basic.get('enhancement_applied', False)}")
            print(f"  - Confidence: {result_basic.get('confidence', 0.0):.3f}")
            print(f"  - Answer Length: {len(result_basic.get('answer', ''))}")
            print(f"  - Answer Preview: {result_basic.get('answer', '')[:100]}...")
            
            # So sánh chất lượng
            enhanced_length = len(result_enhanced.get('answer', ''))
            basic_length = len(result_basic.get('answer', ''))
            enhanced_confidence = result_enhanced.get('confidence', 0.0)
            basic_confidence = result_basic.get('confidence', 0.0)
            
            print(f"\n📈 Quality Comparison:")
            print(f"  - Length Improvement: {enhanced_length - basic_length} chars")
            print(f"  - Confidence Improvement: {enhanced_confidence - basic_confidence:.3f}")
            print(f"  - Time Overhead: {enhanced_time - basic_time:.2f}s")
            
            if result_enhanced.get('enhancement_applied', False):
                print("✅ Enhancement successfully applied!")
            else:
                print("⚠️ Enhancement not applied (fallback to basic)")
            
            print("\n" + "=" * 60)
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🏁 Test completed!")

async def test_enhancement_quality():
    """Test chất lượng enhancement"""
    
    print("\n🔬 Testing Enhancement Quality")
    print("=" * 60)
    
    rag_service = RAGServiceUnified()
    
    try:
        await rag_service.initialize()
        
        # Test với câu hỏi cụ thể
        question = "An toàn thông tin là gì?"
        
        print(f"🔍 Question: {question}")
        
        # Test enhancement
        result = await rag_service.query(
            question=question,
            top_k=3,
            use_enhancement=True
        )
        
        print(f"\n📊 Enhancement Results:")
        print(f"  - Method: {result.get('method', 'unknown')}")
        print(f"  - Enhancement Applied: {result.get('enhancement_applied', False)}")
        print(f"  - Confidence: {result.get('confidence', 0.0):.3f}")
        print(f"  - Processing Time: {result.get('processing_time_ms', 0)}ms")
        print(f"  - Sources: {result.get('total_sources', 0)}")
        
        if result.get('original_response'):
            print(f"\n📝 Original Response:")
            print(f"  - Length: {len(result['original_response'])}")
            print(f"  - Content: {result['original_response'][:200]}...")
        
        print(f"\n📝 Enhanced Response:")
        print(f"  - Length: {len(result.get('answer', ''))}")
        print(f"  - Content: {result.get('answer', '')[:200]}...")
        
        # Kiểm tra sources
        sources = result.get('sources', [])
        if sources:
            print(f"\n📚 Sources Used:")
            for i, source in enumerate(sources[:3], 1):
                print(f"  {i}. {source.get('display_name', 'Unknown')} (Score: {source.get('similarity_score', 0.0):.3f})")
        
    except Exception as e:
        print(f"❌ Quality test failed: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🧪 RAG + LLM Enhancement Test Suite")
    print("=" * 60)
    
    # Test 1: Basic functionality
    await test_rag_llm_enhancement()
    
    # Test 2: Quality assessment
    await test_enhancement_quality()
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
