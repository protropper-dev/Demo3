#!/usr/bin/env python3
"""
Script test backend2 để kiểm tra các chức năng cơ bản
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_imports():
    """Test import các module"""
    print("🔍 Testing imports...")
    
    try:
        import settings
        print("✅ settings imported successfully")
    except Exception as e:
        print(f"❌ Error importing settings: {e}")
        return False
    
    try:
        import config
        print("✅ config imported successfully")
    except Exception as e:
        print(f"❌ Error importing config: {e}")
        return False
    
    try:
        from models.chat import QueryRequest, ChatResponse
        print("✅ models imported successfully")
    except Exception as e:
        print(f"❌ Error importing models: {e}")
        return False
    
    return True

def test_config():
    """Test cấu hình"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import DeviceConfig, ModelConfig, ServerConfig, get_optimal_config
        
        # Test device config
        device_info = DeviceConfig.get_device_info()
        print(f"✅ Device: {device_info['device']}")
        print(f"✅ GPU Available: {device_info['gpu_available']}")
        
        # Test model config
        print(f"✅ Max Tokens: {ModelConfig.LLM_MAX_TOKENS}")
        print(f"✅ Temperature: {ModelConfig.LLM_TEMPERATURE}")
        
        # Test server config
        print(f"✅ Server: {ServerConfig.HOST}:{ServerConfig.PORT}")
        
        # Test optimal config
        optimal_config = get_optimal_config()
        print("✅ Optimal config generated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing config: {e}")
        return False

def test_settings():
    """Test settings"""
    print("\n⚙️ Testing settings...")
    
    try:
        import settings
        
        print(f"✅ ROOT_API: {settings.ROOT_API}")
        print(f"✅ ROOT_PROJECT: {settings.ROOT_PROJECT}")
        print(f"✅ FILE_FOLDER: {settings.FILE_FOLDER}")
        print(f"✅ EMBEDDING_FOLDER: {settings.EMBEDDING_FOLDER}")
        print(f"✅ LLM_MODEL_FOLDER: {settings.LLM_MODEL_FOLDER}")
        print(f"✅ MODEL: {settings.MODEL}")
        
        # Kiểm tra các thư mục quan trọng
        if settings.ROOT_PROJECT.exists():
            print("✅ ROOT_PROJECT exists")
        else:
            print("⚠️  ROOT_PROJECT does not exist")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing settings: {e}")
        return False

def test_routes():
    """Test routes"""
    print("\n🛣️ Testing routes...")
    
    try:
        from routes import chat, system, file, embedding
        print("✅ All routes imported successfully")
        
        # Test route attributes
        if hasattr(chat, 'router'):
            print("✅ Chat router exists")
        if hasattr(system, 'router'):
            print("✅ System router exists")
        if hasattr(file, 'router'):
            print("✅ File router exists")
        if hasattr(embedding, 'router'):
            print("✅ Embedding router exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing routes: {e}")
        return False

def test_utils():
    """Test utils"""
    print("\n🔧 Testing utils...")
    
    try:
        from utils import chat, embedding, file
        print("✅ All utils imported successfully")
        
        # Test utility functions
        if hasattr(chat, 'get_response'):
            print("✅ Chat get_response function exists")
        if hasattr(chat, 'get_response_stream'):
            print("✅ Chat get_response_stream function exists")
        if hasattr(embedding, 'embedding'):
            print("✅ Embedding function exists")
        if hasattr(file, 'save_uploaded_file'):
            print("✅ File save_uploaded_file function exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing utils: {e}")
        return False

def test_main_app():
    """Test main app"""
    print("\n🚀 Testing main app...")
    
    try:
        from main import app
        print("✅ Main app imported successfully")
        
        # Test app attributes
        if hasattr(app, 'routes'):
            print(f"✅ App has {len(app.routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing main app: {e}")
        return False

def main():
    """Chạy tất cả tests"""
    print("🧪 Backend2 Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Settings", test_settings),
        ("Routes", test_routes),
        ("Utils", test_utils),
        ("Main App", test_main_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend2 is ready to run.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
