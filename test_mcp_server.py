#!/usr/bin/env python3
"""
MCP Server Test Script
Quick validation that the MCP server can be imported and basic functionality works.
"""

import sys
import traceback
from typing import Dict, Any

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("  ✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"  ❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("  ✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"  ❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print("  ✅ Pydantic imported successfully")
    except ImportError as e:
        print(f"  ❌ Pydantic import failed: {e}")
        return False
    
    try:
        from mcp_server import MCPServer
        print("  ✅ MCP Server imported successfully")
    except ImportError as e:
        print(f"  ❌ MCP Server import failed: {e}")
        return False
    
    return True

def test_mcp_server_creation():
    """Test that MCP server can be created."""
    print("\n🏗️  Testing MCP server creation...")
    
    try:
        from mcp_server import MCPServer
        server = MCPServer()
        print("  ✅ MCP Server created successfully")
        
        # Test that the server has required attributes
        if hasattr(server, 'app'):
            print("  ✅ FastAPI app found")
        else:
            print("  ❌ FastAPI app not found")
            return False
        
        if hasattr(server, 'tools'):
            print(f"  ✅ Tools defined: {len(server.tools)} tools")
        else:
            print("  ❌ Tools not defined")
            return False
        
        if hasattr(server, 'resources'):
            print(f"  ✅ Resources defined: {len(server.resources)} resources")
        else:
            print("  ❌ Resources not defined")
            return False
        
        if hasattr(server, 'prompts'):
            print(f"  ✅ Prompts defined: {len(server.prompts)} prompts")
        else:
            print("  ❌ Prompts not defined")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ MCP Server creation failed: {e}")
        traceback.print_exc()
        return False

def test_manifest_generation():
    """Test that manifest can be generated."""
    print("\n📄 Testing manifest generation...")
    
    try:
        from mcp_server import MCPServer
        server = MCPServer()
        manifest = server._generate_manifest()
        
        required_fields = ['name', 'version', 'description', 'capabilities', 'tools', 'resources', 'prompts']
        
        for field in required_fields:
            if field in manifest:
                print(f"  ✅ Manifest field '{field}' present")
            else:
                print(f"  ❌ Manifest field '{field}' missing")
                return False
        
        print(f"  ✅ Manifest generated with {len(manifest.get('tools', []))} tools")
        print(f"  ✅ Manifest generated with {len(manifest.get('resources', []))} resources")
        print(f"  ✅ Manifest generated with {len(manifest.get('prompts', []))} prompts")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Manifest generation failed: {e}")
        traceback.print_exc()
        return False

def test_optional_components():
    """Test optional RAG components."""
    print("\n🔧 Testing optional components...")
    
    try:
        from mcp_server import MCPServer, HAS_RAG_COMPONENTS
        
        if HAS_RAG_COMPONENTS:
            print("  ✅ RAG components available")
        else:
            print("  ⚠️  RAG components not available (this is OK for testing)")
        
        server = MCPServer()
        
        components = {
            'rag_pipeline': server.rag_pipeline,
            'document_processor': server.document_processor,
            'snowflake_client': server.snowflake_client,
            'mistral_client': server.mistral_client
        }
        
        for name, component in components.items():
            if component is not None:
                print(f"  ✅ {name} initialized")
            else:
                print(f"  ⚠️  {name} not initialized (may require configuration)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component testing failed: {e}")
        traceback.print_exc()
        return False

def test_client_imports():
    """Test that client example can be imported."""
    print("\n👥 Testing client imports...")
    
    try:
        import aiohttp
        print("  ✅ aiohttp imported successfully")
    except ImportError as e:
        print(f"  ❌ aiohttp import failed: {e}")
        return False
    
    try:
        from mcp_client_example import MCPClient
        print("  ✅ MCP Client imported successfully")
        return True
    except ImportError as e:
        print(f"  ❌ MCP Client import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 MCP Server Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("Server Creation", test_mcp_server_creation),
        ("Manifest Generation", test_manifest_generation),
        ("Optional Components", test_optional_components),
        ("Client Imports", test_client_imports),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🎯 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"  ✅ {test_name} PASSED")
            else:
                print(f"  ❌ {test_name} FAILED")
        except Exception as e:
            print(f"  ❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MCP server is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())