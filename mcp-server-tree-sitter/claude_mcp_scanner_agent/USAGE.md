# Quick Start Guide

## Prerequisites

✅ Virtual environment created  
✅ Dependencies installed (`anthropic`, `mcp`, `mcp-server-tree-sitter`)  
⚠️ **Need:** Anthropic API key

## Step-by-Step Setup

### 1. Activate Virtual Environment

```bash
cd /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/mcp-server-tree-sitter/claude_mcp_scanner_agent
source venv/bin/activate
```

### 2. Get Anthropic API Key

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key (starts with `sk-ant-`)

### 3. Set API Key

**Option A: Environment Variable (recommended)**

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

**Option B: In ~/.zshrc or ~/.bashrc (persistent)**

```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.zshrc
source ~/.zshrc
```

**Option C: Verify it's set**

```bash
echo $ANTHROPIC_API_KEY
# Should print: sk-ant-api03-...
```

### 4. Run the Scanner

```bash
python claude_mcp_scanner.py
```

### 5. Expected Output

```
🚀 Claude + MCP Tree-sitter Scanner
============================================================
This combines:
  ✅ Claude API for intelligent analysis
  ✅ MCP tree-sitter for code searching
  ✅ Programmatic control and automation
============================================================

🔌 Connecting to MCP tree-sitter server...
✅ MCP server connected

============================================================
Project 1/1: ai-ui
============================================================
📁 Registering project: ai-ui
🤖 Claude is analyzing ai-ui...
⏳ This may take a minute...

🔄 Iteration 1...
   Stop reason: tool_use
   🔧 find_text
      ✅ 2847 chars returned
   🔧 find_text
      ✅ 1234 chars returned

🔄 Iteration 2...
   Stop reason: end_turn

✅ Analysis complete!

💾 Results saved to:
   - /path/to/llm_scan_results/ai-ui_analysis.json
   - /path/to/llm_scan_results/ai-ui_analysis.txt

✨ All done!
📁 Results saved to: llm_scan_results/
💰 Total API usage:
   ai-ui: 12543 in + 3421 out tokens
```

## What the Scanner Does

1. **Connects to MCP** - Starts local tree-sitter server
2. **Registers Project** - Indexes the ai-ui codebase
3. **Claude Searches** - Decides what patterns to look for
4. **Executes Searches** - Runs MCP `find_text` tool calls
5. **Analyzes Results** - Claude interprets findings
6. **Generates Report** - Creates structured JSON + readable text

## Output Files

### JSON File: `llm_scan_results/ai-ui_analysis.json`

Structured data with:
- All model references found
- API call locations
- File paths and line numbers
- Categorization by provider
- Summary and recommendations

### Text File: `llm_scan_results/ai-ui_analysis.txt`

Human-readable analysis with Claude's insights.

## Customization

### Scan Different Project

Edit `claude_mcp_scanner.py`:

```python
projects = [
    {
        "name": "my-project",
        "path": "/full/path/to/my-project"
    }
]
```

### Scan Multiple Projects

```python
projects = [
    {"name": "frontend", "path": "/path/to/frontend"},
    {"name": "backend", "path": "/path/to/backend"},
    {"name": "mobile", "path": "/path/to/mobile"}
]
```

### Change Search Patterns

Edit the prompt in `scan_for_llm_usage_async()` method around line 100.

## Cost Estimation

**For ai-ui project (small):**
- Input tokens: ~10K-15K
- Output tokens: ~2K-5K  
- Cost: ~$0.02-0.05 per scan

**For OpenHands project (large):**
- Input tokens: ~50K-100K
- Output tokens: ~10K-20K
- Cost: ~$0.15-0.30 per scan

## Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"

**Solution:**
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Error: "Failed to spawn process"

**Solution:**
```bash
pip install mcp-server-tree-sitter
```

### Error: "Max iterations reached"

**Causes:**
- Project is very large
- Too many files to search
- API token limits

**Solutions:**
- Scan smaller subdirectories
- Increase `max_iterations` to 15-20
- Use more specific project paths

### MCP Server Won't Start

**Check installation:**
```bash
python -m mcp_server_tree_sitter.server --version
```

**Reinstall if needed:**
```bash
pip uninstall mcp-server-tree-sitter
pip install mcp-server-tree-sitter
```

## Comparison with Other Tools

| Tool | Setup | Cost | Speed | AI Analysis |
|------|-------|------|-------|-------------|
| **This Scanner** | Medium | $0.02-0.30 | Medium | ✅ Full |
| **Claude Desktop + MCP** | Easy | Free | Fast | ✅ Interactive |
| **Tree-sitter CLI** | Hard | Free | Very Fast | ❌ None |
| **Semgrep** | Medium | Free | Fast | ❌ None |

## Next Steps

1. ✅ Run the scanner on ai-ui
2. 📊 Review the JSON output
3. 🔄 Try scanning your own project
4. 🎯 Customize search patterns for your needs
5. 🤖 Integrate into your CI/CD pipeline

## Support

For issues or questions:
- Check the main README.md
- Review MCP documentation: https://github.com/wrale/mcp-server-tree-sitter
- Check Claude API docs: https://docs.anthropic.com/

## Example Output

```json
{
  "project": {
    "name": "ai-ui",
    "path": "/path/to/ai-ui",
    "total_files_scanned": 5
  },
  "llm_models": {
    "total_references": 16,
    "by_provider": {
      "openai": ["gpt-4o", "gpt-4o-mini", "dall-e-3"],
      "anthropic": [],
      "google": [],
      "meta": [],
      "mistral": [],
      "other": []
    },
    "files_with_models": ["server.js", "script.js"]
  },
  "api_calls": {
    "total_calls": 2,
    "by_type": {
      "completion": ["chat.completions.create"],
      "streaming": ["images.generate"]
    },
    "files_with_calls": ["server.js"]
  },
  "summary": {
    "unique_models_found": ["gpt-4o", "gpt-4o-mini", "dall-e-3"],
    "most_used_model": "gpt-4o",
    "recommendations": [
      "Model names are well-organized with string concatenation",
      "Consider adding model version constants",
      "Good separation of model configuration"
    ]
  }
}
```
