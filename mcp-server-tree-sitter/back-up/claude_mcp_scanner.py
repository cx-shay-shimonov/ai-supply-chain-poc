#!/usr/bin/env python3
"""
Hybrid LLM Scanner: Claude + MCP Tree-sitter
Combines Claude's intelligence with direct MCP control
"""
import anthropic
import json
import os
from pathlib import Path
from typing import Dict, List, Any


class ClaudeMCPScanner:
    """
    Simple scanner that uses Claude with MCP tools.
    Claude does the thinking, MCP does the searching.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def scan_for_llm_usage(
        self, 
        project_path: str, 
        project_name: str,
        output_file: str = None
    ) -> Dict[str, Any]:
        """
        Scan a project for LLM usage using Claude + MCP.
        
        Claude will automatically use the tree-sitter MCP server
        if it's configured in your Claude Desktop app.
        """
        
        prompt = f"""
Please analyze the codebase for LLM and AI API usage. Here's what I need:

**Project Details:**
- Path: {project_path}
- Name: {project_name}

**Tasks:**

1. **Register the project** using the tree-sitter MCP server

2. **Find all LLM model names** including:
   - OpenAI models: gpt-4, gpt-3.5, gpt-4o, o1, o3, dall-e
   - Anthropic models: claude, sonnet, opus, haiku
   - Google models: gemini, palm
   - Meta models: llama
   - Mistral models: mistral
   - Any other AI models

3. **Find all AI API calls** including:
   - openai.chat.completions
   - anthropic.messages
   - litellm.completion
   - .completion()
   - .acompletion()
   - .create_message()
   - Any async variants

4. **Categorize findings** by:
   - Literal string assignments (e.g., model = "gpt-4")
   - Variable assignments
   - Function/method calls
   - Configuration files

5. **Return results in this JSON structure:**
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
- Use tree-sitter MCP tools for searching
- Include file paths, line numbers, and code context
- Be thorough but concise
- Group similar findings
"""
        
        print(f"🤖 Asking Claude to analyze {project_name}...")
        print(f"📁 Project path: {project_path}")
        print(f"⏳ This may take a minute...\n")
        
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract the response
            result_text = response.content[0].text
            
            print("✅ Analysis complete!\n")
            
            # Try to parse JSON from response
            result_data = self._extract_json(result_text)
            
            # Save results if output file specified
            if output_file:
                self._save_results(result_data, result_text, output_file)
            
            return {
                "raw_response": result_text,
                "parsed_data": result_data,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
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
    
    def scan_multiple_projects(
        self, 
        projects: List[Dict[str, str]],
        output_dir: str = "scan_results"
    ) -> List[Dict]:
        """Scan multiple projects."""
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        for i, project in enumerate(projects, 1):
            print(f"\n{'='*60}")
            print(f"Project {i}/{len(projects)}: {project['name']}")
            print(f"{'='*60}")
            
            output_file = output_path / f"{project['name']}_analysis.json"
            
            result = self.scan_for_llm_usage(
                project_path=project['path'],
                project_name=project['name'],
                output_file=str(output_file)
            )
            
            results.append({
                "project": project['name'],
                "result": result
            })
        
        # Save combined summary
        summary_file = output_path / "all_projects_summary.json"
        with summary_file.open('w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 Summary saved to: {summary_file.absolute()}")
        
        return results


def main():
    """Example usage."""
    
    # Initialize scanner
    scanner = ClaudeMCPScanner()
    
    # Define projects to scan
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
    
    # Scan all projects
    results = scanner.scan_multiple_projects(
        projects=projects,
        output_dir="llm_scan_results"
    )
    
    print("\n✨ All done!")
    print(f"📁 Results in: llm_scan_results/")


if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export ANTHROPIC_API_KEY='your-api-key'")
        exit(1)
    
    main()
