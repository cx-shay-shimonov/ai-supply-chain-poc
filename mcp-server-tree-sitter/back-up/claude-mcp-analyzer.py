#!/usr/bin/env python3
"""
Claude + MCP Tree-sitter Analyzer

This script demonstrates programmatic usage of Claude API with MCP tree-sitter
to get AI-powered code analysis insights, similar to Claude Desktop's MCP integration.
"""

import json
import sys
import os
from pathlib import Path
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ClaudeMCPAnalyzer:
    """Combines Claude API with MCP tree-sitter for AI-powered code analysis."""
    
    def __init__(self, api_key: str = None):
        """Initialize with Anthropic API key."""
        self.anthropic = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.session: ClientSession | None = None
        self.mcp_tools_cache = None
    
    async def connect_to_mcp(self):
        """Connect to the MCP tree-sitter server."""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_server_tree_sitter.server"],
            env=None
        )
        
        self.stdio_context = stdio_client(server_params)
        self.read, self.write = await self.stdio_context.__aenter__()
        
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        print("✅ Connected to MCP tree-sitter server")
    
    async def get_mcp_tools(self):
        """Get available MCP tools and convert them to Claude tool format."""
        if self.mcp_tools_cache:
            return self.mcp_tools_cache
        
        # Get tools from MCP server
        tools_result = await self.session.list_tools()
        
        # Convert MCP tools to Claude's tool format
        claude_tools = []
        for tool in tools_result.tools:
            claude_tool = {
                "name": tool.name,
                "description": tool.description or f"MCP tool: {tool.name}",
                "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            claude_tools.append(claude_tool)
        
        self.mcp_tools_cache = claude_tools
        return claude_tools
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict):
        """Call an MCP tool and return results."""
        result = await self.session.call_tool(tool_name, arguments=arguments)
        
        # Extract text content from MCP result
        if result and hasattr(result, 'content'):
            content_parts = []
            for item in result.content:
                if hasattr(item, 'text'):
                    content_parts.append(item.text)
            return "\n".join(content_parts)
        return ""
    
    async def analyze_with_claude(self, project_name: str, project_path: str, query: str):
        """
        Use Claude to analyze a codebase via MCP tools.
        
        Claude decides which tools to call based on the query.
        """
        print(f"\n🤖 Analyzing {project_name} with Claude...")
        print(f"📝 Query: {query}\n")
        
        # Get available MCP tools
        tools = await self.get_mcp_tools()
        
        # Register the project first
        print(f"📁 Registering project: {project_name}")
        await self.call_mcp_tool("register_project_tool", {
            "path": project_path,
            "name": project_name
        })
        
        # Prepare initial message with context
        messages = [{
            "role": "user",
            "content": f"""I need you to analyze the codebase at: {project_path}

Project name: {project_name}

Please help me with this query: {query}

Use the available MCP tools to search the codebase and provide insights. 
Start by using find_text to search for relevant patterns, then analyze the results."""
        }]
        
        # Start conversation with Claude
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}...")
            
            # Call Claude with tool use capability
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                tools=tools,
                messages=messages
            )
            
            print(f"   Stop reason: {response.stop_reason}")
            
            # Add Claude's response to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Execute all tool calls
                tool_results = []
                
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        
                        print(f"   🔧 Calling tool: {tool_name}")
                        print(f"      Arguments: {json.dumps(tool_input, indent=2)}")
                        
                        # Call the MCP tool
                        tool_result = await self.call_mcp_tool(tool_name, tool_input)
                        
                        # Truncate large results
                        if len(tool_result) > 5000:
                            tool_result = tool_result[:5000] + f"\n\n... (truncated, {len(tool_result)} total chars)"
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": content_block.id,
                            "content": tool_result
                        })
                        
                        print(f"      ✅ Result length: {len(tool_result)} chars")
                
                # Add tool results to conversation
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
            elif response.stop_reason == "end_turn":
                # Claude is done - extract final response
                print("\n✅ Analysis complete!\n")
                
                final_response = ""
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        final_response += content_block.text
                
                return final_response
            
            else:
                # Unexpected stop reason
                print(f"⚠️  Unexpected stop reason: {response.stop_reason}")
                break
        
        print("\n⚠️  Max iterations reached")
        return "Analysis incomplete - max iterations reached"
    
    async def cleanup(self):
        """Cleanup MCP connection."""
        if hasattr(self, 'session') and self.session:
            await self.session.__aexit__(None, None, None)
        if hasattr(self, 'stdio_context'):
            await self.stdio_context.__aexit__(None, None, None)


async def main():
    """Main entry point."""
    
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        print("   export ANTHROPIC_API_KEY=your_api_key_here")
        sys.exit(1)
    
    # Configuration
    project_name = "ai-ui"
    project_path = "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/ai-ui"
    
    # Query to analyze
    query = """Find all usages of AI models (GPT, Claude, DALL-E, etc.) in this codebase. 
For each finding:
1. List the model name
2. Show the file and line number
3. Explain how it's being used
4. Identify if it's in active code or comments

Then provide a summary of:
- Total unique AI models found
- Which files use AI APIs
- Any potential issues or recommendations"""
    
    # Allow custom query from command line
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    
    analyzer = ClaudeMCPAnalyzer()
    
    try:
        # Connect to MCP
        await analyzer.connect_to_mcp()
        
        # Analyze with Claude
        result = await analyzer.analyze_with_claude(
            project_name=project_name,
            project_path=project_path,
            query=query
        )
        
        # Print results
        print("="*80)
        print("📊 CLAUDE'S ANALYSIS:")
        print("="*80)
        print(result)
        print("="*80)
        
        # Save to file
        output_file = "claude_mcp_analysis.txt"
        with open(output_file, 'w') as f:
            f.write(result)
        print(f"\n💾 Analysis saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await analyzer.cleanup()


if __name__ == "__main__":
    import asyncio
    
    print("🚀 Claude + MCP Tree-sitter Analyzer")
    print("="*80)
    
    asyncio.run(main())
