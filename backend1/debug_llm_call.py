#!/usr/bin/env python3
"""
Debug script để kiểm tra cách gọi LLM service
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_llm_service():
    """Debug LLM service call"""
    try:
        from app.services.llm_service import LLMService
        import inspect
        
        print("🔍 Debugging LLM Service...")
        
        # Check method signature
        sig = inspect.signature(LLMService.generate_response)
        print(f"📝 Method signature: {sig}")
        
        # Print parameters
        for name, param in sig.parameters.items():
            print(f"  - {name}: {param}")
        
        # Test call without actual model loading
        print("\n🧪 Testing method call pattern...")
        
        # This is how we should call it
        test_call = """
        generation_config = {
            'temperature': 0.6,
            'max_new_tokens': 200,
            'top_p': 0.9
        }
        
        response = llm_service.generate_response(
            query="test",
            context_docs=None,
            max_new_tokens=200,
            generation_config=generation_config
        )
        """
        
        print("✅ Correct call pattern:")
        print(test_call)
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_rag_service():
    """Debug RAG service methods"""
    try:
        from app.services.rag_service_unified import RAGServiceUnified
        
        print("\n🔍 Debugging RAG Service...")
        
        # Check _generate_basic_llm_response method
        rag_service = RAGServiceUnified()
        
        # Check if method exists and is callable
        method = getattr(rag_service, '_generate_basic_llm_response', None)
        if method is None:
            print("❌ Method _generate_basic_llm_response not found")
            return False
        
        print("✅ Method _generate_basic_llm_response exists")
        
        # Check if method is async or not
        import asyncio
        if asyncio.iscoroutinefunction(method):
            print("📝 Method is async")
        else:
            print("📝 Method is sync")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debug function"""
    print("🔧 LLM Call Debug")
    print("=" * 40)
    
    debug_llm_service()
    debug_rag_service()
    
    print("\n" + "=" * 40)
    print("🏁 Debug completed!")

if __name__ == "__main__":
    main()
