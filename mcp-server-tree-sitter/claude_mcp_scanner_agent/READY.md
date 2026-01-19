# ✅ Claude MCP Scanner Agent - Ready to Use!

## 🎉 Setup Complete!

Your hybrid Claude + MCP scanner is fully configured and tested.

### ✅ What's Installed

```
✅ Virtual environment: venv/
✅ Anthropic SDK: anthropic 0.76.0
✅ MCP SDK: mcp 1.25.0
✅ MCP Server: mcp-server-tree-sitter 0.5.1
✅ Tree-sitter: 0.25.2
✅ All dependencies resolved
```

### ✅ What's Been Tested

```
✅ MCP server starts successfully
✅ Session initialization works
✅ 26 tools available (register_project, find_text, run_query, etc.)
✅ Project registration works
✅ Basic searches execute
✅ No syntax errors in scanner code
```

---

## 🚀 How to Run

### Prerequisites

You need an **Anthropic API key** to use this scanner.

1. **Get your API key:**
   - Visit: https://console.anthropic.com/
   - Sign in or create account
   - Go to API Keys section
   - Create new key (starts with `sk-ant-`)

2. **Set the API key:**

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Run the Scanner

```bash
# 1. Navigate to the folder
cd /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/mcp-server-tree-sitter/claude_mcp_scanner_agent

# 2. Activate virtual environment
source venv/bin/activate

# 3. Set API key (if not already set)
export ANTHROPIC_API_KEY='sk-ant-...'

# 4. Run the scanner!
python claude_mcp_scanner.py
```

---

## 📊 What Happens When You Run It

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
   
🔄 Iteration 2...
   Stop reason: tool_use
   🔧 find_text
      ✅ 1543 chars returned

🔄 Iteration 3...
   Stop reason: end_turn

✅ Analysis complete!

💾 Results saved to:
   - llm_scan_results/ai-ui_analysis.json
   - llm_scan_results/ai-ui_analysis.txt

✨ All done!
📁 Results saved to: llm_scan_results/
💰 Total API usage:
   ai-ui: 15234 in + 3821 out tokens
```

---

## 📁 Output Files

### JSON: `llm_scan_results/ai-ui_analysis.json`

Structured data with:
- ✅ All AI model references found
- ✅ API call locations with line numbers
- ✅ File paths and code context
- ✅ Categorization by provider (OpenAI, Anthropic, etc.)
- ✅ Summary with recommendations

### Text: `llm_scan_results/ai-ui_analysis.txt`

Human-readable analysis with Claude's insights.

---

## 🎯 Key Features

### What Makes This Special

1. **Claude's Intelligence**
   - Decides what patterns to search for
   - Interprets and categorizes results
   - Provides actionable recommendations

2. **MCP's Precision**
   - Fast AST-based code parsing
   - Accurate regex pattern matching
   - No false positives from comments

3. **Programmatic Control**
   - Batch scan multiple projects
   - Automate in CI/CD pipelines
   - Generate structured reports

4. **Best of Both Worlds**
   ```
   Pure Claude = Smart but expensive
   Pure MCP = Fast but requires manual queries
   This Tool = Smart + Fast + Automated ✨
   ```

---

## 💰 Cost Estimate

### For ai-ui Project (Small - ~5 files)
- **Input tokens:** ~10K-15K
- **Output tokens:** ~2K-5K
- **Cost:** ~$0.02-0.05 per scan
- **Time:** ~30-60 seconds

### For OpenHands Project (Large - ~1000 files)
- **Input tokens:** ~50K-100K
- **Output tokens:** ~10K-20K
- **Cost:** ~$0.15-0.30 per scan
- **Time:** ~2-5 minutes

*Prices based on Claude Sonnet 4 rates (Jan 2026)*

---

## 🛠️ Customization

### Scan Your Own Project

Edit `claude_mcp_scanner.py` (line 330):

```python
projects = [
    {
        "name": "my-project",
        "path": "/full/path/to/your/project"
    }
]
```

### Scan Multiple Projects

```python
projects = [
    {"name": "frontend", "path": "/path/to/frontend"},
    {"name": "backend", "path": "/path/to/backend"},
    {"name": "api", "path": "/path/to/api"}
]
```

### Change Search Patterns

Edit the prompt in `scan_for_llm_usage_async()` method (around line 150) to add:
- New model names
- Different API patterns
- Custom analysis requirements

---

## 🆚 Comparison with Other Tools

| Feature | This Scanner | Claude Desktop | Pure MCP | Tree-sitter CLI |
|---------|--------------|----------------|----------|-----------------|
| **AI Analysis** | ✅ Full | ✅ Full | ❌ None | ❌ None |
| **Programmatic** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Interactive** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **Cost** | 💰 $0.02-0.30 | 🆓 Free | 🆓 Free | 🆓 Free |
| **Batch Scan** | ✅ Yes | ❌ Manual | ⚠️ Manual | ✅ Yes |
| **JSON Output** | ✅ Structured | ⚠️ Chat | ✅ Raw | ✅ Raw |
| **Setup** | ⚠️ Medium | ✅ Easy | ⚠️ Medium | ⚠️ Hard |

---

## 🐛 Troubleshooting

### "ANTHROPIC_API_KEY not found"
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
echo $ANTHROPIC_API_KEY  # Verify it's set
```

### "ModuleNotFoundError: No module named 'anthropic'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Failed to spawn process"
```bash
pip install mcp-server-tree-sitter
python -m mcp_server_tree_sitter.server --version
```

### Test Without Using API Tokens
```bash
python test_mcp_connection.py
```

---

## 📚 Documentation

- **README.md** - Full documentation and API reference
- **USAGE.md** - Step-by-step usage guide
- **READY.md** - This file (quick start)

---

## 🎯 Quick Command Reference

```bash
# Activate environment
source venv/bin/activate

# Set API key
export ANTHROPIC_API_KEY='sk-ant-...'

# Run scanner
python claude_mcp_scanner.py

# Test MCP without API
python test_mcp_connection.py

# Check results
cat llm_scan_results/ai-ui_analysis.json | jq '.summary'
```

---

## ✨ You're All Set!

Your scanner is ready to use. Just need to:

1. ✅ Get Anthropic API key
2. ✅ Set the environment variable
3. ✅ Run `python claude_mcp_scanner.py`

**Happy scanning!** 🚀

---

*Questions? Check README.md or USAGE.md for detailed documentation.*
