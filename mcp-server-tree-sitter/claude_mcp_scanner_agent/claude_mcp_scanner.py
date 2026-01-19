#!/usr/bin/env python3
"""
Hybrid LLM Scanner: Claude + MCP Tree-sitter
Combines Claude's intelligence with direct MCP control
"""
import anthropic
import json
import os
import asyncio
from pathlib import Path
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ClaudeMCPScanner:
    """
    Hybrid scanner: Claude API decides what to search, MCP executes searches.
    This gives you Claude's intelligence + programmatic control.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.mcp_session = None
        self.mcp_stdio_context = None
    
    async def connect_mcp(self):
        """Connect to MCP tree-sitter server."""
        if self.mcp_session:
            return  # Already connected
        
        print("🔌 Connecting to MCP tree-sitter server...")
        
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_server_tree_sitter.server"],
            env=None
        )
        
        self.mcp_stdio_context = stdio_client(server_params)
        self.read, self.write = await self.mcp_stdio_context.__aenter__()
        
        self.mcp_session = ClientSession(self.read, self.write)
        await self.mcp_session.__aenter__()
        await self.mcp_session.initialize()
        
        print("✅ MCP server connected\n")
    
    async def disconnect_mcp(self):
        """Disconnect from MCP server."""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)
        if self.mcp_stdio_context:
            await self.mcp_stdio_context.__aexit__(None, None, None)
        self.mcp_session = None
        self.mcp_stdio_context = None
    
    async def call_mcp_tool(self, tool_name: str, arguments: dict) -> str:
        """Call an MCP tool and return text results."""
        result = await self.mcp_session.call_tool(tool_name, arguments=arguments)
        
        # Extract text content
        if result and hasattr(result, 'content'):
            parts = []
            for item in result.content:
                if hasattr(item, 'text'):
                    parts.append(item.text)
            return "\n".join(parts)
        return ""
    
    async def get_mcp_tools_for_claude(self):
        """Get MCP tools formatted for Claude's tool use API."""
        tools_result = await self.mcp_session.list_tools()
        
        claude_tools = []
        for tool in tools_result.tools:
            claude_tools.append({
                "name": tool.name,
                "description": tool.description or f"MCP tool: {tool.name}",
                "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            })
        
        return claude_tools
    
    async def scan_for_llm_usage_async(
        self, 
        project_path: str, 
        project_name: str,
        output_file: str = None
    ) -> Dict[str, Any]:
        """
        Scan a project for LLM usage using Claude API + MCP tree-sitter.
        
        Claude decides what to search for, we execute MCP tools on its behalf.
        """
        
        # Connect to MCP server
        await self.connect_mcp()
        
        # Register the project
        print(f"📁 Registering project: {project_name}")
        await self.call_mcp_tool("register_project_tool", {
            "path": project_path,
            "name": project_name
        })
        
        # Get MCP tools for Claude
        tools = await self.get_mcp_tools_for_claude()
        
        # Get file list first to provide context
        print(f"📂 Getting project file list...")
        files_result = await self.call_mcp_tool("list_files", {
            "project_name": project_name
        })
        
        file_count = len(files_result.split('\n')) if files_result else 0
        print(f"   Found {file_count} files")
        
        prompt = f"""
Analyze this codebase for LLM and AI API usage. Be EFFICIENT - use broad regex patterns to minimize tool calls.

**Project:** {project_name} (already registered)
**Files:** {file_count} files found

**Your Task:**

Use `find_text` tool with project_name="{project_name}" and broad regex patterns. Make just 2-3 searches total:

1. **SINGLE search for ALL AI models** using this regex:
   "(gpt-[0-9]|claude-[0-9]|gemini|dall-e|llama|mistral|deepseek|o[0-9]-)"
   
2. **SINGLE search for ALL API calls** using this regex:
   "(completions\\.create|messages\\.create|\\.completion\\(|anthropic\\.|openai\\.)"

3. Analyze ALL results and create the final JSON report immediately.

**IMPORTANT:** 
- Make BROAD searches (not one per model)
- Don't search multiple times for similar patterns
- After 2-3 searches, provide your final analysis
- Include everything in the final response

**Required JSON structure:**
```json
{{
  "project": {{
    "name": "{project_name}",
    "path": "{project_path}",
    "total_files_scanned": 0
  }},
  "llm_models": {{
    "total_references": 0,
    "by_provider": {{
      "openai": [],
      "anthropic": [],
      "google": [],
      "meta": [],
      "mistral": [],
      "other": []
    }},
    "files_with_models": []
  }},
  "api_calls": {{
    "total_calls": 0,
    "by_type": {{
      "completion": [],
      "async_completion": [],
      "streaming": [],
      "other": []
    }},
    "files_with_calls": []
  }},
  "summary": {{
    "unique_models_found": [],
    "unique_api_patterns": [],
    "most_used_model": "",
    "most_used_api": "",
    "recommendations": []
  }}
}}
```

**Important:** 
- Use the MCP find_text tool to search the codebase
- Provide specific regex patterns for better results
- After gathering all data, provide the final JSON analysis
"""
        
        print(f"🤖 Claude is analyzing {project_name}...")
        print(f"⏳ This may take a minute...\n")
        
        # Start conversation with Claude
        messages = [{"role": "user", "content": prompt}]
        max_iterations = 15  # Increased from 10
        iteration = 0
        tool_calls_made = 0
        
        try:
            while iteration < max_iterations:
                iteration += 1
                print(f"🔄 Iteration {iteration}/{max_iterations} (tool calls: {tool_calls_made})...")
                
                # Warn if approaching limit
                if iteration >= max_iterations - 2:
                    print(f"   ⚠️  Approaching iteration limit!")
                
                # Call Claude with tool use capability
                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
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
                    tool_results = []
                    
                    for content_block in response.content:
                        if content_block.type == "tool_use":
                            tool_name = content_block.name
                            tool_input = content_block.input
                            tool_calls_made += 1
                            
                            # Show which search pattern is being used
                            query_preview = ""
                            if 'query' in tool_input:
                                query_preview = f"'{tool_input['query']}'"
                                # query_preview = f" '{tool_input['query'][:50]}...'"
                            
                            # print(f"   🔧 Tool #{tool_calls_made}: {tool_name}{query_preview}")
                            print(f"MCP:Request:   🔧 Tool #{tool_calls_made}: {tool_name}{query_preview}")
                            
                            # Execute MCP tool
                            tool_result = await self.call_mcp_tool(tool_name, tool_input)
                            
                            # Truncate if too long
                            original_length = len(tool_result)
                            if len(tool_result) > 10000:
                                tool_result = tool_result[:10000] + f"\n... (truncated from {original_length} chars)"
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": content_block.id,
                                "content": tool_result
                            })
                            
                            matches = tool_result.count('\n')
                            print(f"MCP:Response:      ✅ Found ~{matches} matches ({original_length} chars)")
                    
                    # Add tool results to conversation
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                
                elif response.stop_reason == "end_turn":
                    # Claude is done
                    print(f"\n✅ Analysis complete!")
                    print(f"   📊 Used {iteration} iterations, {tool_calls_made} tool calls\n")
                    
                    # Extract final response
                    result_text = ""
                    for content_block in response.content:
                        if hasattr(content_block, 'text'):
                            result_text += content_block.text
                    
                    # Parse JSON from response
                    result_data = self._extract_json(result_text)
                    
                    # Save results
                    if output_file:
                        self._save_results(result_data, result_text, output_file)
                    
                    return {
                        "raw_response": result_text,
                        "parsed_data": result_data,
                        "usage": {
                            "input_tokens": response.usage.input_tokens,
                            "output_tokens": response.usage.output_tokens
                        },
                        "stats": {
                            "iterations": iteration,
                            "tool_calls": tool_calls_made
                        }
                    }
                
                else:
                    print(f"⚠️  Unexpected stop reason: {response.stop_reason}")
                    break
            
            # Max iterations reached - ask Claude for partial results
            print("\n⚠️  Max iterations reached, requesting partial results...")
            
            # Ask Claude to provide whatever analysis it has
            messages.append({
                "role": "user",
                "content": "Please provide your analysis based on the search results you've received so far, even if incomplete. Use the JSON format specified."
            })
            
            final_response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=messages
            )
            
            result_text = ""
            for content_block in final_response.content:
                if hasattr(content_block, 'text'):
                    result_text += content_block.text
            
            result_data = self._extract_json(result_text)
            
            if output_file:
                self._save_results(result_data, result_text, output_file)
            
            print("✅ Partial analysis complete")
            
            return {
                "raw_response": result_text,
                "parsed_data": result_data,
                "usage": {
                    "input_tokens": response.usage.input_tokens + final_response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens + final_response.usage.output_tokens
                },
                "warning": "Max iterations reached - results may be incomplete"
            }
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from Claude's response."""
        try:
            # Look for JSON code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                json_str = text[start:end].strip()
                return json.loads(json_str)
            
            # Try to parse the whole thing
            return json.loads(text)
        
        except json.JSONDecodeError:
            print("⚠️  Could not extract JSON, returning raw text")
            return {"raw_analysis": text}
    
    def _save_results(self, data: Dict, raw_text: str, output_file: str):
        """Save results to file."""
        output_path = Path(output_file)
        
        # Save structured data
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Also save raw text
        raw_path = output_path.with_suffix('.txt')
        with raw_path.open('w', encoding='utf-8') as f:
            f.write(raw_text)
        
        print(f"💾 Results saved to:")
        print(f"   - {output_path.absolute()}")
        print(f"   - {raw_path.absolute()}")
    
    def scan_for_llm_usage(self, project_path: str, project_name: str, output_file: str = None):
        """Synchronous wrapper for scan_for_llm_usage_async."""
        return asyncio.run(self.scan_for_llm_usage_async(project_path, project_name, output_file))
    
    async def scan_multiple_projects_async(
        self, 
        projects: List[Dict[str, str]],
        output_dir: str = "scan_results"
    ) -> List[Dict]:
        """Scan multiple projects asynchronously."""
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Connect to MCP once for all projects
        await self.connect_mcp()
        
        try:
            for i, project in enumerate(projects, 1):
                print(f"\n{'='*60}")
                print(f"Project {i}/{len(projects)}: {project['name']}")
                print(f"{'='*60}")
                
                output_file = output_path / f"{project['name']}_analysis.json"
                
                result = await self.scan_for_llm_usage_async(
                    project_path=project['path'],
                    project_name=project['name'],
                    output_file=str(output_file)
                )
                
                results.append({
                    "project": project['name'],
                    "result": result
                })
        
        finally:
            await self.disconnect_mcp()
        
        # Save combined summary
        summary_file = output_path / "all_projects_summary.json"
        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📊 Summary saved to: {summary_file.absolute()}")
        
        return results
    
    def scan_multiple_projects(self, projects: List[Dict[str, str]], output_dir: str = "scan_results"):
        """Synchronous wrapper for scan_multiple_projects_async."""
        return asyncio.run(self.scan_multiple_projects_async(projects, output_dir))


async def main():
    """
    Example usage of Claude + MCP Scanner.
    
    How this works:
    1. Connects to MCP tree-sitter server programmatically
    2. Registers your project with MCP
    3. Claude API decides what searches to perform
    4. We execute MCP find_text searches on Claude's behalf
    5. Claude analyzes results and generates structured JSON report
    
    This gives you Claude's intelligence + programmatic MCP control!
    """
    
    print("🚀 Claude + MCP Tree-sitter Scanner")
    print("="*60)
    print("This combines:")
    print("  ✅ Claude API for intelligent analysis")
    print("  ✅ MCP tree-sitter for code searching")
    print("  ✅ Programmatic control and automation")
    print("="*60 + "\n")
    
    # Initialize scanner
    scanner = ClaudeMCPScanner()
    
    # Define projects to scan
    projects = [
        {
            "name": "ai-ui",
            "path": "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/ai-ui"
        }
        # # Uncomment to scan OpenHands (will take longer and use more API tokens):
        # {
        #     "name": "openhands",
        #     "path": "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/OpenHands"
        # }
    ]
    
    # Scan all projects
    results = await scanner.scan_multiple_projects_async(
        projects=projects,
        output_dir="llm_scan_results"
    )
    
    print("\n✨ All done!")
    print(f"📁 Results saved to: llm_scan_results/")
    print(f"💰 Total API usage:")
    for r in results:
        if 'usage' in r.get('result', {}):
            usage = r['result']['usage']
            print(f"   {r['project']}: {usage['input_tokens']} in + {usage['output_tokens']} out tokens")


if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        print("\nGet your API key from: https://console.anthropic.com/")
        exit(1)
    
    asyncio.run(main())
