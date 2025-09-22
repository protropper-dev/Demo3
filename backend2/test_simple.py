#!/usr/bin/env python3
"""
Test đơn giản để kiểm tra backend2
"""

import sys
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_imports():
    """Test import cơ bản"""
    print("🔍 Testing basic imports...")
    
    try:
        import settings
        print("✅ Settings imported")
        
        import config
        print("✅ Config imported")
        
        from models.chat import QueryRequest
        print("✅ Models imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_routes_import():
    """Test import routes (không load models)"""
    print("\n🔍 Testing routes import...")
    
    try:
        # Import routes mà không trigger model loading
        import routes.chat
        import routes.system
        import routes.file
        import routes.embedding
        print("✅ All routes imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Routes import error: {e}")
        return False

def test_main_app():
    """Test main app (sẽ trigger model loading)"""
    print("\n🔍 Testing main app...")
    
    try:
        from main import app
        print("✅ Main app imported successfully")
        print(f"✅ App has {len(app.routes)} routes")
        
        return True
    except Exception as e:
        print(f"❌ Main app error: {e}")
        return False

def main():
    """Chạy test"""
    print("🧪 Backend2 Simple Test")
    print("=" * 40)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Routes Import", test_routes_import),
        ("Main App", test_main_app),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results:")
    print("-" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print("-" * 40)
    print(f"Total: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
