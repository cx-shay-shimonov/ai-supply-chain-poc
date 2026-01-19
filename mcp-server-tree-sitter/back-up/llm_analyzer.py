#!/usr/bin/env python3
"""
LLM Model Usage Analyzer using MCP Tree-sitter Server

This script analyzes a codebase to find all usages of LLM model names,
including literal assignments, variables, and function calls.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class LLMModelAnalyzer:
    """Analyzes codebases for LLM model usage patterns."""
    
    def __init__(self):
        self.session: ClientSession | None = None
        self.results: Dict[str, Any] = {
            "projects": [],
            "model_names_found": [],
            "api_calls_found": [],
            "summary": {}
        }
    
    async def connect_to_server(self):
        """Connect to the MCP tree-sitter server."""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_server_tree_sitter.server"],
            env=None
        )
        
        # Use stdio_client as async context manager
        self.stdio_context = stdio_client(server_params)
        self.read, self.write = await self.stdio_context.__aenter__()
        
        self.session = ClientSession(self.read, self.write)
        await self.session.__aenter__()
        await self.session.initialize()
        
        print("✅ Connected to MCP tree-sitter server")
    
    async def register_project(self, project_path: str, project_name: str) -> bool:
        """Register a project with the tree-sitter server."""
        try:
            result = await self.session.call_tool(
                "register_project_tool",
                arguments={
                    "path": project_path,
                    "name": project_name,
                    "description": f"Project analysis: {project_name}"
                }
            )
            
            print(f"✅ Registered project: {project_name}")
            # Convert result to dict if it's a CallToolResult
            result_dict = {"content": []} 
            if hasattr(result, 'content'):
                result_dict["content"] = [
                    {"text": item.text if hasattr(item, 'text') else str(item)}
                    for item in result.content
                ]
            
            self.results["projects"].append({
                "name": project_name,
                "path": project_path,
                "registration_result": result_dict
            })
            return True
            
        except Exception as e:
            print(f"❌ Failed to register project {project_name}: {e}")
            return False
    
    async def find_llm_model_names(self, project_name: str) -> List[Dict]:
        """
        Find all LLM model names in the project.
        Searches for common model name patterns.
        """
        print(f"\n🔍 Searching for LLM model names in {project_name}...")
        
        # Pattern for common LLM model names
        model_patterns = [
            r"gpt-4|gpt-3\.5|gpt-5",
            r"claude|sonnet|opus|haiku",
            r"gemini|palm",
            r"llama|mistral",
            r"o1-preview|o1-mini|o3-mini|o4-mini",
            r"dall-e"
        ]
        
        all_matches = []
        
        for pattern in model_patterns:
            try:
                result = await self.session.call_tool(
                    "find_text",
                    arguments={
                        "project": project_name,
                        "pattern": pattern,
                        "use_regex": True,
                        "case_sensitive": False,
                        "max_results": 200,
                        "context_lines": 2
                    }
                )
                
                if result and hasattr(result, 'content'):
                    for content_item in result.content:
                        if hasattr(content_item, 'text') and content_item.text:
                            try:
                                matches = json.loads(content_item.text)
                                if isinstance(matches, list):
                                    all_matches.extend(matches)
                                elif isinstance(matches, dict):
                                    all_matches.append(matches)
                            except json.JSONDecodeError:
                                # If not JSON, treat as plain text match
                                all_matches.append({
                                    "pattern": pattern,
                                    "text": content_item.text
                                })
                
            except Exception as e:
                print(f"⚠️  Error searching pattern {pattern}: {e}")
        
        self.results["model_names_found"] = all_matches
        print(f"  Found {len(all_matches)} model name references")
        return all_matches
    
    async def find_api_calls(self, project_name: str) -> List[Dict]:
        """
        Find all AI API function calls in the project.
        Searches for common API patterns.
        """
        print(f"\n🔍 Searching for API calls in {project_name}...")
        
        # Patterns for API calls
        api_patterns = [
            r"openai\.chat\.completions",
            r"anthropic\.messages",
            r"litellm\.completion",
            r"\.completion\(",
            r"\.async_completion\(",
            r"create_message",
            r"acompletion\("
        ]
        
        all_calls = []
        
        for pattern in api_patterns:
            try:
                result = await self.session.call_tool(
                    "find_text",
                    arguments={
                        "project": project_name,
                        "pattern": pattern,
                        "use_regex": True,
                        "case_sensitive": True,
                        "file_pattern": "**/*.py",  # Focus on Python files
                        "max_results": 100,
                        "context_lines": 3
                    }
                )
                
                if result and hasattr(result, 'content'):
                    for content_item in result.content:
                        if hasattr(content_item, 'text') and content_item.text:
                            try:
                                matches = json.loads(content_item.text)
                                if isinstance(matches, list):
                                    all_calls.extend(matches)
                                elif isinstance(matches, dict):
                                    all_calls.append(matches)
                            except json.JSONDecodeError:
                                # If not JSON, treat as plain text match
                                all_calls.append({
                                    "pattern": pattern,
                                    "text": content_item.text
                                })
                
            except Exception as e:
                print(f"⚠️  Error searching API pattern {pattern}: {e}")
        
        self.results["api_calls_found"] = all_calls
        print(f"  Found {len(all_calls)} API call references")
        return all_calls
    
    async def analyze_specific_files(self, project_name: str, file_patterns: List[str]) -> Dict:
        """Analyze specific files for detailed insights."""
        print(f"\n🔍 Analyzing specific files in {project_name}...")
        
        file_analyses = {}
        
        for pattern in file_patterns:
            try:
                # List files matching pattern
                files_result = await self.session.call_tool(
                    "tree_sitter:list_files",
                    arguments={
                        "project": project_name,
                        "pattern": pattern,
                        "max_depth": 10
                    }
                )
                
                if files_result and hasattr(files_result, 'content'):
                    for content_item in files_result.content:
                        if hasattr(content_item, 'text'):
                            files = json.loads(content_item.text)
                            
                            # Analyze first few files
                            for file_path in files[:5]:  # Limit to 5 files per pattern
                                try:
                                    # Get symbols from file
                                    symbols_result = await self.session.call_tool(
                                        "tree_sitter:get_symbols",
                                        arguments={
                                            "project": project_name,
                                            "file_path": file_path,
                                            "symbol_types": ["functions", "classes", "variables"]
                                        }
                                    )
                                    
                                    if symbols_result:
                                        file_analyses[file_path] = {
                                            "symbols": symbols_result
                                        }
                                        
                                except Exception as e:
                                    print(f"  ⚠️  Error analyzing {file_path}: {e}")
            
            except Exception as e:
                print(f"⚠️  Error listing files for {pattern}: {e}")
        
        return file_analyses
    
    def generate_summary(self):
        """Generate a summary of findings."""
        model_names = self.results["model_names_found"]
        api_calls = self.results["api_calls_found"]
        
        # Count unique files
        unique_files_models = set(m.get("file", "") for m in model_names)
        unique_files_apis = set(c.get("file", "") for c in api_calls)
        
        # Extract unique model names (simplified)
        unique_models = set()
        for match in model_names:
            text = match.get("text", "")
            # Extract model name patterns
            if "gpt-" in text.lower():
                unique_models.add("GPT models")
            if "claude" in text.lower():
                unique_models.add("Claude models")
            if "gemini" in text.lower():
                unique_models.add("Gemini models")
            if "llama" in text.lower():
                unique_models.add("Llama models")
            if "mistral" in text.lower():
                unique_models.add("Mistral models")
        
        self.results["summary"] = {
            "total_model_references": len(model_names),
            "total_api_calls": len(api_calls),
            "unique_files_with_models": len(unique_files_models),
            "unique_files_with_api_calls": len(unique_files_apis),
            "model_families_found": list(unique_models),
            "projects_analyzed": len(self.results["projects"])
        }
        
        print("\n" + "="*60)
        print("📊 ANALYSIS SUMMARY")
        print("="*60)
        for key, value in self.results["summary"].items():
            print(f"{key:.<40} {value}")
        print("="*60)
    
    def save_results(self, output_file: str = "llm_analysis_results.json"):
        """Save results to JSON file."""
        output_path = Path(output_file)
        
        with output_path.open('w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_path.absolute()}")
    
    async def run_analysis(self, projects: List[Dict[str, str]], output_file: str = None):
        """
        Run complete analysis on multiple projects.
        
        Args:
            projects: List of dicts with 'name' and 'path' keys
            output_file: Optional output file path
        """
        try:
            await self.connect_to_server()
            
            # Register all projects
            for project in projects:
                await self.register_project(
                    project_path=project["path"],
                    project_name=project["name"]
                )
            
            # Analyze each project
            for project in projects:
                project_name = project["name"]
                
                # Find model names
                await self.find_llm_model_names(project_name)
                
                # Find API calls
                await self.find_api_calls(project_name)
            
            # Generate summary
            self.generate_summary()
            
            # Save results
            if output_file:
                self.save_results(output_file)
            else:
                self.save_results()
            
            print("\n✅ Analysis complete!")
            
        except Exception as e:
            print(f"\n❌ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if hasattr(self, 'session') and self.session:
                await self.session.__aexit__(None, None, None)
            if hasattr(self, 'stdio_context'):
                await self.stdio_context.__aexit__(None, None, None)


async def main():
    """Main entry point."""
    
    # Define projects to analyze
    projects = [
        {
            "name": "ai-ui",
            "path": "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/ai-ui"
        },
        {
            "name": "openhands",
            "path": "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/projects-samples/OpenHands"
        }
    ]
    
    # You can also accept command line arguments
    if len(sys.argv) > 1:
        # Parse command line arguments
        # Format: script.py project_name=/path/to/project [project_name2=/path/to/project2 ...]
        projects = []
        for arg in sys.argv[1:]:
            if '=' in arg:
                name, path = arg.split('=', 1)
                projects.append({"name": name, "path": path})
    
    # Run analysis
    analyzer = LLMModelAnalyzer()
    await analyzer.run_analysis(
        projects=projects,
        output_file="llm_model_analysis.json"
    )


if __name__ == "__main__":
    import asyncio
    
    print("🚀 LLM Model Usage Analyzer")
    print("="*60)
    
    asyncio.run(main())