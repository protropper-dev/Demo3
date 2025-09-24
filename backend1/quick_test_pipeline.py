#!/usr/bin/env python3
"""
Quick test script để kiểm tra pipeline đã sửa lỗi chưa
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_import():
    """Test basic import"""
    try:
        from app.services.rag_service_unified import RAGServiceUnified
        from app.services.llm_service import LLMService
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_method_signatures():
    """Test method signatures"""
    try:
        from app.services.rag_service_unified import RAGServiceUnified
        
        # Create instance
        rag_service = RAGServiceUnified()
        
        # Check if methods exist
        assert hasattr(rag_service, '_generate_rag_response')
        assert hasattr(rag_service, '_enhance_response_with_llm') 
        assert hasattr(rag_service, '_call_llm_for_enhancement')
        assert hasattr(rag_service, '_generate_basic_llm_response')
        
        print("✅ All methods exist")
        return True
    except Exception as e:
        print(f"❌ Method check failed: {e}")
        return False

def test_llm_service():
    """Test LLM service method signature"""
    try:
        from app.services.llm_service import LLMService
        import inspect
        
        # Check generate_response method signature
        sig = inspect.signature(LLMService.generate_response)
        params = list(sig.parameters.keys())
        
        print(f"📝 LLMService.generate_response params: {params}")
        
        # Should have: self, query, context_docs, max_new_tokens, generation_config
        expected_params = ['self', 'query', 'context_docs', 'max_new_tokens', 'generation_config']
        for param in expected_params:
            if param not in params:
                print(f"❌ Missing parameter: {param}")
                return False
        
        print("✅ LLM service signature correct")
        return True
    except Exception as e:
        print(f"❌ LLM service check failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Quick Pipeline Test")
    print("=" * 40)
    
    tests = [
        test_basic_import,
        test_method_signatures, 
        test_llm_service
    ]
    
    all_passed = True
    for test in tests:
        print(f"\n🔍 Running {test.__name__}...")
        if not test():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
