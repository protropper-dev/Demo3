#!/usr/bin/env python3
"""
Simple debug script để tìm coroutine issue
"""

import inspect

def check_method_types():
    """Check if methods are async or sync"""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from app.services.rag_service_unified import RAGServiceUnified
        
        service = RAGServiceUnified()
        
        methods = [
            '_generate_rag_response',
            '_enhance_response_with_llm', 
            '_generate_basic_llm_response',
            '_call_llm_for_enhancement',
            '_generate_template_response',
            '_calculate_basic_confidence',
            '_validate_enhanced_response'
        ]
        
        print("🔍 Checking method types:")
        for method_name in methods:
            method = getattr(service, method_name, None)
            if method:
                is_async = inspect.iscoroutinefunction(method)
                print(f"  {method_name}: {'ASYNC' if is_async else 'SYNC'}")
                if is_async:
                    print(f"    ❌ Method {method_name} is async but should be sync!")
            else:
                print(f"  {method_name}: NOT FOUND")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_method_types()
