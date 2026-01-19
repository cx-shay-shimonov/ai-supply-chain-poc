# Claude + MCP Scanner Agent

A hybrid AI scanner that combines **Claude API's intelligence** with **MCP tree-sitter's code analysis** for programmatic LLM usage detection.

## 🎯 What This Does

This scanner gives you the best of both worlds:

1. **Claude's Intelligence** - Decides what patterns to search for, interprets results, provides insights
2. **MCP's Precision** - Fast tree-sitter AST parsing with regex-based code search
3. **Programmatic Control** - Run automated scans, batch process projects, integrate into CI/CD

## 🔄 How It Works

```
┌─────────────────┐
│   Your Script   │
└────────┬────────┘
         │
         ├──► Connect to MCP tree-sitter server
         │
         ├──► Register project(s)
         │
         ├──► Ask Claude: "Find all LLM usage"
         │
         ├──► Claude decides: "Search for gpt-4, claude-*, etc."
         │
         ├──► Execute MCP find_text searches
         │
         ├──► Claude analyzes results
         │
         └──► Return structured JSON report
```

## 📦 Installation

```bash
# 1. Create virtual environment
cd mcp-server-tree-sitter/claude_mcp_scanner_agent
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
pip list | grep -E "anthropic|mcp"
```

## 🔑 Setup API Key

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Or add to your ~/.bashrc or ~/.zshrc:
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc

# Get your API key from:
# https://console.anthropic.com/
```

## 🚀 Usage

### Quick Start

```bash
# Make sure MCP server is installed
pip list | grep mcp-server-tree-sitter

# Run the scanner
python claude_mcp_scanner.py
```

### Programmatic Usage

```python
from claude_mcp_scanner import ClaudeMCPScanner
import asyncio

async def scan_my_project():
    scanner = ClaudeMCPScanner()
    
    result = await scanner.scan_for_llm_usage_async(
        project_path="/path/to/your/project",
        project_name="my-project",
        output_file="results/my_project_analysis.json"
    )
    
    print(result['parsed_data'])

asyncio.run(scan_my_project())
```

### Scan Multiple Projects

```python
scanner = ClaudeMCPScanner()

projects = [
    {"name": "frontend", "path": "/path/to/frontend"},
    {"name": "backend", "path": "/path/to/backend"}
]

results = scanner.scan_multiple_projects(
    projects=projects,
    output_dir="scan_results"
)
```

## 📊 Output Format

The scanner generates:

1. **JSON file** - Structured data with all findings
2. **TXT file** - Claude's full analysis in readable format

### Example JSON Structure

```json
{
  "project": {
    "name": "ai-ui",
    "path": "/path/to/project",
    "total_files_scanned": 5
  },
  "llm_models": {
    "total_references": 12,
    "by_provider": {
      "openai": ["gpt-4o", "gpt-4o-mini", "dall-e-3"],
      "anthropic": ["claude-3-sonnet"]
    },
    "files_with_models": ["server.js", "config.js"]
  },
  "api_calls": {
    "total_calls": 3,
    "by_type": {
      "completion": ["chat.completions.create"],
      "streaming": ["images.generate"]
    }
  },
  "summary": {
    "unique_models_found": ["gpt-4o", "gpt-4o-mini", "dall-e-3"],
    "most_used_model": "gpt-4o",
    "recommendations": [
      "Consider consolidating model versions",
      "Add model name constants"
    ]
  }
}
```

## 💰 Cost Estimation

- **Claude API**: ~$0.01-0.05 per project scan (depends on codebase size)
- **MCP Server**: Free (runs locally)

Typical token usage:
- Small project (< 100 files): ~5K-10K tokens
- Medium project (< 1K files): ~20K-50K tokens  
- Large project (> 1K files): ~50K-200K tokens

## 🆚 Comparison

| Feature | This Scanner | Claude Desktop + MCP | Pure MCP | Pure Tree-sitter |
|---------|--------------|---------------------|----------|------------------|
| AI Analysis | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Programmatic | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| Interactive | ❌ No | ✅ Yes | ❌ No | ❌ No |
| Cost | 💰 API usage | 🆓 Free | 🆓 Free | 🆓 Free |
| Batch Processing | ✅ Yes | ❌ No | ⚠️ Manual | ✅ Yes |
| Structured Output | ✅ JSON | ⚠️ Chat | ✅ JSON | ✅ JSON |

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### "ModuleNotFoundError: No module named 'mcp'"

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Failed to spawn process"

Make sure `mcp-server-tree-sitter` is installed globally or in your environment:

```bash
pip install mcp-server-tree-sitter
```

### "Max iterations reached"

The codebase might be too large. Try:
- Scan smaller sub-projects
- Increase `max_iterations` in code
- Use more specific queries

## 📖 Examples

### Example 1: Single Project Scan

```bash
python claude_mcp_scanner.py
# Scans ai-ui project by default
# Results in: llm_scan_results/ai-ui_analysis.json
```

### Example 2: Custom Project

Edit `main()` function:

```python
projects = [
    {
        "name": "my-app",
        "path": "/Users/me/projects/my-app"
    }
]
```

### Example 3: CI/CD Integration

```bash
#!/bin/bash
# ci-scan.sh

source venv/bin/activate
python claude_mcp_scanner.py

# Check if results contain critical findings
if grep -q "gpt-4" llm_scan_results/ai-ui_analysis.json; then
    echo "⚠️  GPT-4 usage detected"
    exit 1
fi
```

## 🤝 Contributing

This scanner is part of the AI Supply Chain POC project. To modify:

1. **Change search patterns** - Update the prompt in `scan_for_llm_usage_async()`
2. **Add new model types** - Extend the model lists in the prompt
3. **Custom output format** - Modify `_extract_json()` and `_save_results()`

## 📚 Related Tools

- **Pure Tree-sitter Scanner** - `../tree-sitter/scanner.py` (faster, no API costs)
- **Manual MCP Analysis** - `../llm_analyzer.py` (direct MCP access)
- **Claude Desktop** - Interactive MCP usage (no programming)

## 📄 License

Same as parent project.
