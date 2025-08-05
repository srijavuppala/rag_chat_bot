#!/usr/bin/env python3
"""
MCP Client Example
Demonstrates how to interact with the RAG Chatbot MCP Server
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import argparse
import sys

@dataclass
class MCPClient:
    """Client for interacting with the MCP server."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_manifest(self) -> Dict[str, Any]:
        """Get the MCP server manifest."""
        async with self.session.get(f"{self.server_url}/.well-known/mcp/manifest.json") as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise Exception(f"Failed to get manifest: {resp.status}")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools."""
        async with self.session.get(f"{self.server_url}/mcp/tools/list") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("tools", [])
            else:
                raise Exception(f"Failed to list tools: {resp.status}")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a specific tool."""
        if arguments is None:
            arguments = {}
        
        payload = {
            "name": name,
            "arguments": arguments
        }
        
        async with self.session.post(
            f"{self.server_url}/mcp/tools/call",
            json=payload
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_text = await resp.text()
                raise Exception(f"Failed to call tool {name}: {resp.status} - {error_text}")
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List all available resources."""
        async with self.session.get(f"{self.server_url}/mcp/resources/list") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("resources", [])
            else:
                raise Exception(f"Failed to list resources: {resp.status}")
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a specific resource."""
        payload = {"uri": uri}
        
        async with self.session.post(
            f"{self.server_url}/mcp/resources/read",
            json=payload
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_text = await resp.text()
                raise Exception(f"Failed to read resource {uri}: {resp.status} - {error_text}")
    
    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts."""
        async with self.session.get(f"{self.server_url}/mcp/prompts/list") as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("prompts", [])
            else:
                raise Exception(f"Failed to list prompts: {resp.status}")
    
    async def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a specific prompt with arguments."""
        if arguments is None:
            arguments = {}
        
        payload = {
            "name": name,
            "arguments": arguments
        }
        
        async with self.session.post(
            f"{self.server_url}/mcp/prompts/get",
            json=payload
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_text = await resp.text()
                raise Exception(f"Failed to get prompt {name}: {resp.status} - {error_text}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        async with self.session.get(f"{self.server_url}/health") as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise Exception(f"Health check failed: {resp.status}")

async def demo_mcp_capabilities():
    """Demonstrate MCP server capabilities."""
    
    print("🤖 MCP Client Demo - RAG Chatbot Server")
    print("=" * 50)
    
    async with MCPClient() as client:
        try:
            # Health check
            print("\n1. Health Check")
            print("-" * 20)
            health = await client.health_check()
            print(f"Server Status: {health.get('status', 'unknown')}")
            print(f"Timestamp: {health.get('timestamp', 'unknown')}")
            
            components = health.get('components', {})
            for component, available in components.items():
                status = "✅ Available" if available else "❌ Unavailable"
                print(f"  {component}: {status}")
            
            # Get manifest
            print("\n2. Server Manifest")
            print("-" * 20)
            manifest = await client.get_manifest()
            print(f"Server Name: {manifest.get('name', 'Unknown')}")
            print(f"Version: {manifest.get('version', 'Unknown')}")
            print(f"Description: {manifest.get('description', 'No description')}")
            
            # List tools
            print("\n3. Available Tools")
            print("-" * 20)
            tools = await client.list_tools()
            for i, tool in enumerate(tools, 1):
                print(f"  {i}. {tool['name']}: {tool['description']}")
            
            # List resources
            print("\n4. Available Resources")
            print("-" * 25)
            resources = await client.list_resources()
            for i, resource in enumerate(resources, 1):
                print(f"  {i}. {resource['name']} ({resource['uri']})")
                print(f"     Description: {resource.get('description', 'No description')}")
            
            # List prompts
            print("\n5. Available Prompts")
            print("-" * 23)
            prompts = await client.list_prompts()
            for i, prompt in enumerate(prompts, 1):
                print(f"  {i}. {prompt['name']}: {prompt['description']}")
            
            # Demonstrate tool calls
            print("\n6. Tool Demonstrations")
            print("-" * 25)
            
            # System status
            print("\n6.1 System Status Tool")
            try:
                status_result = await client.call_tool("get_system_status")
                if not status_result.get('isError', False):
                    content = status_result.get('content', [])
                    if content and content[0].get('type') == 'text':
                        status_data = json.loads(content[0]['text'])
                        print(f"✅ System status retrieved successfully")
                        print(f"   Components checked: {len(status_data.get('components', {}))}")
                else:
                    print(f"❌ Error: {status_result.get('content', [{}])[0].get('text', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Failed to get system status: {e}")
            
            # Document stats (if available)
            print("\n6.2 Document Statistics Tool")
            try:
                stats_result = await client.call_tool("get_document_stats", {"include_details": False})
                if not stats_result.get('isError', False):
                    print("✅ Document statistics retrieved successfully")
                else:
                    print(f"❌ Error: {stats_result.get('content', [{}])[0].get('text', 'Unknown error')}")
            except Exception as e:
                print(f"❌ Failed to get document stats: {e}")
            
            # Demonstrate resource access
            print("\n7. Resource Access Demonstrations")
            print("-" * 35)
            
            # System config resource
            print("\n7.1 System Configuration Resource")
            try:
                config_result = await client.read_resource("rag://system/config")
                contents = config_result.get('contents', [])
                if contents and contents[0].get('type') == 'text':
                    config_data = json.loads(contents[0]['text'])
                    print("✅ System configuration retrieved successfully")
                    print(f"   App Title: {config_data.get('app_title', 'Unknown')}")
                    print(f"   Chunk Size: {config_data.get('chunk_size', 'Unknown')}")
            except Exception as e:
                print(f"❌ Failed to read system config: {e}")
            
            # Demonstrate prompt usage
            print("\n8. Prompt Demonstrations")
            print("-" * 26)
            
            # Document summary prompt
            print("\n8.1 Document Summary Prompt")
            try:
                sample_content = "This is a sample document about machine learning. It covers various algorithms and techniques used in AI development."
                prompt_result = await client.get_prompt("document_summary", {
                    "document_content": sample_content,
                    "max_length": "brief"
                })
                
                print("✅ Document summary prompt generated successfully")
                messages = prompt_result.get('messages', [])
                if messages:
                    print(f"   Prompt length: {len(messages[0].get('content', ''))} characters")
            except Exception as e:
                print(f"❌ Failed to get document summary prompt: {e}")
            
            # Question answering prompt
            print("\n8.2 Question Answering Prompt")
            try:
                prompt_result = await client.get_prompt("question_answering", {
                    "question": "What is machine learning?",
                    "context": "Machine learning is a subset of artificial intelligence that focuses on algorithms."
                })
                
                print("✅ Question answering prompt generated successfully")
                messages = prompt_result.get('messages', [])
                if messages:
                    print(f"   Prompt length: {len(messages[0].get('content', ''))} characters")
            except Exception as e:
                print(f"❌ Failed to get question answering prompt: {e}")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            sys.exit(1)
    
    print("\n🎉 MCP Client Demo completed successfully!")
    print("=" * 50)

async def interactive_mode():
    """Interactive mode for exploring MCP server."""
    
    print("🔧 MCP Interactive Mode")
    print("Type 'help' for available commands, 'exit' to quit")
    print("=" * 50)
    
    async with MCPClient() as client:
        while True:
            try:
                command = input("\nmcp> ").strip().lower()
                
                if command == "exit":
                    break
                elif command == "help":
                    print("\nAvailable commands:")
                    print("  help           - Show this help message")
                    print("  health         - Check server health")
                    print("  manifest       - Show server manifest")
                    print("  tools          - List available tools")
                    print("  resources      - List available resources")
                    print("  prompts        - List available prompts")
                    print("  call <tool>    - Call a tool (you'll be prompted for arguments)")
                    print("  read <uri>     - Read a resource")
                    print("  prompt <name>  - Get a prompt (you'll be prompted for arguments)")
                    print("  exit           - Exit interactive mode")
                
                elif command == "health":
                    health = await client.health_check()
                    print(json.dumps(health, indent=2))
                
                elif command == "manifest":
                    manifest = await client.get_manifest()
                    print(json.dumps(manifest, indent=2))
                
                elif command == "tools":
                    tools = await client.list_tools()
                    for i, tool in enumerate(tools, 1):
                        print(f"{i}. {tool['name']}: {tool['description']}")
                
                elif command == "resources":
                    resources = await client.list_resources()
                    for i, resource in enumerate(resources, 1):
                        print(f"{i}. {resource['name']} ({resource['uri']})")
                
                elif command == "prompts":
                    prompts = await client.list_prompts()
                    for i, prompt in enumerate(prompts, 1):
                        print(f"{i}. {prompt['name']}: {prompt['description']}")
                
                elif command.startswith("call "):
                    tool_name = command[5:].strip()
                    if tool_name:
                        print(f"Calling tool: {tool_name}")
                        args_input = input("Arguments (JSON format, or empty for {}): ").strip()
                        
                        try:
                            args = json.loads(args_input) if args_input else {}
                            result = await client.call_tool(tool_name, args)
                            print(json.dumps(result, indent=2))
                        except json.JSONDecodeError:
                            print("❌ Invalid JSON format for arguments")
                        except Exception as e:
                            print(f"❌ Error calling tool: {e}")
                    else:
                        print("❌ Please specify a tool name")
                
                elif command.startswith("read "):
                    uri = command[5:].strip()
                    if uri:
                        try:
                            result = await client.read_resource(uri)
                            print(json.dumps(result, indent=2))
                        except Exception as e:
                            print(f"❌ Error reading resource: {e}")
                    else:
                        print("❌ Please specify a resource URI")
                
                elif command.startswith("prompt "):
                    prompt_name = command[7:].strip()
                    if prompt_name:
                        print(f"Getting prompt: {prompt_name}")
                        args_input = input("Arguments (JSON format, or empty for {}): ").strip()
                        
                        try:
                            args = json.loads(args_input) if args_input else {}
                            result = await client.get_prompt(prompt_name, args)
                            print(json.dumps(result, indent=2))
                        except json.JSONDecodeError:
                            print("❌ Invalid JSON format for arguments")
                        except Exception as e:
                            print(f"❌ Error getting prompt: {e}")
                    else:
                        print("❌ Please specify a prompt name")
                
                elif command:
                    print(f"❌ Unknown command: {command}. Type 'help' for available commands.")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="MCP Client for RAG Chatbot Server")
    parser.add_argument("--server", default="http://localhost:8000", 
                       help="MCP server URL (default: http://localhost:8000)")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Update client server URL if specified
    MCPClient.__init__.__defaults__ = (args.server,)
    
    if args.interactive:
        await interactive_mode()
    else:
        await demo_mcp_capabilities()

if __name__ == "__main__":
    asyncio.run(main())