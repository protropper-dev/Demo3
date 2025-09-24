#!/usr/bin/env python3
"""
Debug script để tìm nguyên nhân coroutine issue
"""

import sys
import os
import asyncio
import inspect

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def debug_rag_service():
    """Debug RAG service step by step"""
    try:
        from app.services.rag_service_unified import RAGServiceUnified
        
        print("🔍 Debugging RAG Service...")
        
        # Create service
        rag_service = RAGServiceUnified()
        
        # Initialize
        await rag_service.initialize()
        print("✅ Service initialized")
        
        # Test simple question
        question = "An toàn thông tin là gì?"
        
        print(f"\n🧪 Testing question: {question}")
        
        # Step 1: Search relevant chunks
        print("📝 Step 1: Searching relevant chunks...")
        search_results = rag_service.search_relevant_chunks(
            question=question,
            top_k=3
        )
        print(f"✅ Found {len(search_results)} results")
        
        if not search_results:
            print("❌ No search results found")
            return
        
        # Step 2: Generate RAG response
        print("\n📝 Step 2: Generating RAG response...")
        rag_response = rag_service._generate_rag_response(question, search_results)
        
        # Check if rag_response is coroutine
        if inspect.iscoroutine(rag_response):
            print("❌ _generate_rag_response returned coroutine!")
            rag_response.close()  # Cleanup
            return
        else:
            print("✅ _generate_rag_response returned valid response")
            print(f"📄 Response type: {type(rag_response)}")
            print(f"📄 Raw response type: {type(rag_response.get('raw_response', 'N/A'))}")
        
        # Step 3: Test LLM Enhancement
        print("\n📝 Step 3: Testing LLM Enhancement...")
        if rag_service.llm_service:
            enhanced_response = rag_service._enhance_response_with_llm(rag_response, question)
            
            # Check if enhanced_response is coroutine
            if inspect.iscoroutine(enhanced_response):
                print("❌ _enhance_response_with_llm returned coroutine!")
                enhanced_response.close()  # Cleanup
                return
            else:
                print("✅ _enhance_response_with_llm returned valid response")
                print(f"📄 Enhanced response type: {type(enhanced_response)}")
                print(f"📄 Enhanced answer type: {type(enhanced_response.get('enhanced_response', 'N/A'))}")
        else:
            print("⚠️ LLM service not available")
        
        print("\n✅ All steps completed successfully!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

def debug_individual_methods():
    """Debug individual methods"""
    try:
        from app.services.rag_service_unified import RAGServiceUnified
        
        print("\n🔍 Debugging Individual Methods...")
        
        # Create service
        rag_service = RAGServiceUnified()
        
        # Check method signatures
        methods_to_check = [
            '_generate_rag_response',
            '_enhance_response_with_llm',
            '_generate_basic_llm_response',
            '_call_llm_for_enhancement',
            '_generate_template_response'
        ]
        
        for method_name in methods_to_check:
            method = getattr(rag_service, method_name, None)
            if method:
                if inspect.iscoroutinefunction(method):
                    print(f"❌ {method_name} is async (should be sync)")
                else:
                    print(f"✅ {method_name} is sync")
            else:
                print(f"❌ {method_name} not found")
        
    except Exception as e:
        print(f"❌ Method debug failed: {e}")

async def main():
    """Main debug function"""
    print("🐛 Coroutine Issue Debug")
    print("=" * 40)
    
    # Debug individual methods first
    debug_individual_methods()
    
    # Then debug full pipeline
    await debug_rag_service()
    
    print("\n🏁 Debug completed!")

if __name__ == "__main__":
    asyncio.run(main())
