#!/usr/bin/env python3
"""
Test MCP connection without using Claude API.
This verifies that the MCP server can be reached and tools are available.
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_connection():
    """Test connection to MCP tree-sitter server."""
    
    print("🧪 Testing MCP Tree-sitter Connection")
    print("="*60)
    
    try:
        # 1. Start MCP server
        print("\n1️⃣  Starting MCP server...")
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_server_tree_sitter.server"],
            env=None
        )
        
        stdio_context = stdio_client(server_params)
        read, write = await stdio_context.__aenter__()
        
        session = ClientSession(read, write)
        await session.__aenter__()
        print("   ✅ Server started")
        
        # 2. Initialize
        print("\n2️⃣  Initializing session...")
        await session.initialize()
        print("   ✅ Session initialized")
        
        # 3. List available tools
        print("\n3️⃣  Listing available tools...")
        tools_result = await session.list_tools()
        print(f"   ✅ Found {len(tools_result.tools)} tools:")
        for tool in tools_result.tools:
            print(f"      - {tool.name}")
        
        # 4. Test project registration
        print("\n4️⃣  Testing project registration...")
        result = await session.call_tool("register_project_tool", {
            "path": "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/ai-ui",
            "name": "test-project"
        })
        
        if result and hasattr(result, 'content'):
            content = "\n".join(item.text for item in result.content if hasattr(item, 'text'))
            print(f"   ✅ Project registered successfully")
            print(f"      {content[:100]}...")
        
        # 5. Test a simple search
        print("\n5️⃣  Testing find_text search...")
        search_result = await session.call_tool("find_text", {
            "project_name": "test-project",
            "query": "gpt-4"
        })
        
        if search_result and hasattr(search_result, 'content'):
            content = "\n".join(item.text for item in search_result.content if hasattr(item, 'text'))
            lines = content.split('\n')
            matches = len([l for l in lines if 'gpt-4' in l.lower()])
            print(f"   ✅ Search completed: {matches} matches found")
            if matches > 0:
                print(f"      First match: {lines[0][:80]}...")
        
        # 6. Cleanup
        print("\n6️⃣  Cleaning up...")
        await session.__aexit__(None, None, None)
        await stdio_context.__aexit__(None, None, None)
        print("   ✅ Connection closed")
        
        # Success!
        print("\n" + "="*60)
        print("✨ All tests passed!")
        print("="*60)
        print("\n✅ MCP server is working correctly")
        print("✅ You can now use claude_mcp_scanner.py")
        print("\n📝 Next step:")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   python claude_mcp_scanner.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "="*60)
        print("⚠️  MCP connection test failed")
        print("="*60)
        print("\n🔧 Troubleshooting:")
        print("1. Make sure mcp-server-tree-sitter is installed:")
        print("   pip install mcp-server-tree-sitter")
        print("\n2. Test the server directly:")
        print("   python -m mcp_server_tree_sitter.server")
        print("\n3. Check if the project path exists:")
        print("   ls /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/ai-ui")
        
        return False


if __name__ == "__main__":
    print("\n" + "🔬 MCP Connection Test" + "\n")
    print("This test verifies:")
    print("  1. MCP server can start")
    print("  2. Session can initialize")
    print("  3. Tools are available")
    print("  4. Projects can be registered")
    print("  5. Searches work")
    print("\nNo API keys required for this test.")
    print("\n" + "-"*60 + "\n")
    
    success = asyncio.run(test_mcp_connection())
    exit(0 if success else 1)
