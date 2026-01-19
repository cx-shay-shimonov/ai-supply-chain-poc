# ❓ Frequently Asked Questions

## Your Questions Answered

### Q1: "Why are iterations important?"

**Answer:**

Iterations are needed because **Claude API cannot directly access your MCP server**.

```
Claude Desktop (free):          Claude API (this tool):
┌────────────┐                  ┌────────────┐
│   Claude   │──┐               │   Claude   │
│  Desktop   │  │               │    API     │
└────────────┘  │               └─────┬──────┘
                │                     │
         ┌──────┴──────┐             │ ❌ No direct access
         │             │             │
         ▼             ▼             ▼
    ┌───────┐     ┌───────┐     ┌───────┐
    │  MCP  │     │ Your  │     │  MCP  │
    │Server │     │ Files │     │Server │
    └───────┘     └───────┘     └───────┘
                                     ▲
                                     │
                              ┌──────┴──────┐
                              │   Your      │
                              │   Script    │
                              └─────────────┘
                              (acts as bridge)
```

**Claude Desktop:** Has built-in MCP integration  
**Claude API:** Has NO MCP access - we must bridge it

**Each iteration:**
1. Claude API → "I want to call tool X"
2. We → Execute MCP tool X
3. We → Send results back to Claude
4. Claude API → Analyzes, may request more tools
5. Repeat until Claude is satisfied

---

### Q2: "Can't you just send the project and prompt?"

**Answer: No**, because:

1. **Claude API has no access to:**
   - Your filesystem
   - Your MCP server
   - Any local resources

2. **Claude API can only:**
   - Request tools to be called
   - Receive results you send back
   - Analyze those results
   - Request more tools if needed

3. **We must act as the bridge:**
   ```python
   # This DOESN'T work:
   claude_api.analyze("/path/to/project")  # ❌
   
   # This DOES work:
   # Step 1: Claude requests tool
   response = claude_api.chat("Analyze project")
   # → Claude says: "Call find_text(query='gpt-4')"
   
   # Step 2: We execute tool
   mcp_result = mcp.find_text(query="gpt-4")
   
   # Step 3: Send back to Claude
   response = claude_api.chat(f"Results: {mcp_result}")
   # → Claude analyzes and may request more
   ```

**Think of it like this:**
- Claude Desktop = All-in-one kitchen
- Claude API = Chef who gives you orders
- You = The sous chef executing orders

---

### Q3: "Do you use the MCP server installed on my machine?"

**Answer: YES!** ✅

We connect to your **local** `mcp-server-tree-sitter` installation:

```python
server_params = StdioServerParameters(
    command="python",
    args=["-m", "mcp_server_tree_sitter.server"],
    env=None
)
```

This runs on **your machine**, not in the cloud:
- ✅ Your files stay local
- ✅ No files sent to Claude
- ✅ Only search results are sent to Claude API
- ✅ MCP server is free (no cost)

**What goes to Claude API:**
- ❌ NOT your source code
- ❌ NOT your files
- ✅ Just the search results (e.g., "Found gpt-4 in file.js:10")

---

## 💡 Common Misconceptions

### Misconception 1: "Claude API should see my MCP tools"

**Reality:**
- Claude Desktop: Has MCP tools built-in
- Claude API: Has no built-in MCP access
- Solution: We use Claude's "function calling" to simulate MCP access

### Misconception 2: "Iterations waste API tokens"

**Reality:**
- Each iteration uses tokens, yes
- But it's the ONLY way to give Claude API access to MCP
- Alternative is no MCP access at all

### Misconception 3: "Can't we just upload the code to Claude?"

**Reality:**
- Would use MANY more tokens (entire codebase)
- Less accurate (no AST parsing)
- Security concern (uploading proprietary code)
- This tool: Only search results sent, not source code

---

## 🔄 Iteration Breakdown Example

Let's trace a real scan:

### Your Command
```bash
python claude_mcp_scanner.py
```

### What Actually Happens

```
═══════════════════════════════════════════════════════
ITERATION 1
═══════════════════════════════════════════════════════

You → Claude API:
  "Analyze ai-ui project for LLM usage"

Claude API → You:
  {
    "stop_reason": "tool_use",
    "tool_request": {
      "name": "find_text",
      "arguments": {
        "project_name": "ai-ui",
        "query": "(gpt-[0-9]|claude-|gemini)"
      }
    }
  }

You → MCP Server:
  find_text(project="ai-ui", query="(gpt-[0-9]|claude-|gemini)")

MCP Server → You:
  """
  server.js:10: const model = "gpt-4o-mini"
  server.js:15: model: "gpt-4o"
  script.js:5: // Using gpt-4o-mini
  ...
  """

═══════════════════════════════════════════════════════
ITERATION 2
═══════════════════════════════════════════════════════

You → Claude API:
  "Here are the results: [search results]"

Claude API → You:
  {
    "stop_reason": "tool_use",
    "tool_request": {
      "name": "find_text",
      "arguments": {
        "project_name": "ai-ui",
        "query": "completions\\.create"
      }
    }
  }

You → MCP Server:
  find_text(project="ai-ui", query="completions\.create")

MCP Server → You:
  """
  server.js:25: await openai.chat.completions.create({
  server.js:45: const response = await client.chat.completions.create({
  """

═══════════════════════════════════════════════════════
ITERATION 3
═══════════════════════════════════════════════════════

You → Claude API:
  "Here are the API call results: [results]"

Claude API → You:
  {
    "stop_reason": "end_turn",
    "content": {
      "text": "Here's my analysis: {...JSON...}"
    }
  }

DONE! ✅
═══════════════════════════════════════════════════════
```

---

## 🎯 Why Not Just Use Claude Desktop?

| Feature | Claude Desktop | This Tool |
|---------|----------------|-----------|
| **Cost** | 🆓 Free | 💰 ~$0.02-0.30 |
| **Needs iterations?** | ✅ Yes (hidden) | ✅ Yes (visible) |
| **Programmatic** | ❌ No | ✅ Yes |
| **Batch scan** | ❌ Manual | ✅ Automatic |
| **JSON output** | ❌ Chat only | ✅ Structured |
| **CI/CD integration** | ❌ No | ✅ Yes |

**Use Claude Desktop when:**
- Interactive, one-off analysis
- Don't want to pay
- Exploring codebase

**Use this tool when:**
- Need automation
- Batch processing
- Structured reports
- CI/CD integration

---

## 🚀 Performance Tips

### To Minimize Iterations

1. **Use broad regex patterns:**
   ```python
   ✅ GOOD: "(gpt-|claude-|gemini)"  # 1 search
   ❌ BAD:  "gpt-4", "gpt-3.5", ...  # 10 searches
   ```

2. **Be directive in prompts:**
   ```python
   ✅ GOOD: "Use ONE search with regex '(gpt-|claude-)'"
   ❌ BAD:  "Find all AI models"
   ```

3. **Increase max_iterations if needed:**
   ```python
   max_iterations = 20  # For very large projects
   ```

---

## 📊 Cost Breakdown

### What You're Paying For

**Claude API costs:**
- Input tokens: Your prompts + MCP results sent to Claude
- Output tokens: Claude's analysis and tool requests

**Free (no cost):**
- ✅ MCP server (runs locally)
- ✅ Tree-sitter parsing (local)
- ✅ File access (local)

**Example for ai-ui:**
```
Input:  ~10K tokens ($0.015)
Output: ~3K tokens  ($0.045)
Total:  ~$0.06
```

**Each iteration adds:**
- ~1-2K input tokens (sending results back)
- ~500-1K output tokens (Claude's response)

**Optimization = Fewer iterations = Lower cost**

---

## 🔧 Troubleshooting

### "Max iterations reached"

**Cause:** Claude made too many tool calls

**Solutions:**
1. Use the improved v2.0 (just updated!)
2. Check IMPROVEMENTS.md for changes
3. Increase max_iterations if needed

### "Why so many tool calls?"

**Cause:** Prompt was too vague, Claude over-searched

**Solution:** v2.0 has more directive prompting

### "This seems slow"

**Reality check:**
- Claude Desktop: Fast but manual
- This tool: 30-60s but automated
- Trade-off: Speed vs automation

---

## ✨ Summary

1. **Iterations are necessary** because Claude API has no direct MCP access
2. **Can't just send project** because Claude API can't see your files
3. **Uses local MCP server** - yes, your installation
4. **v2.0 improvements** make it 50-70% more efficient
5. **Read ARCHITECTURE.md** for detailed explanations

**Bottom line:**
- This tool bridges Claude API ↔ MCP server
- Iterations are the only way to do this
- We optimized to use as few as possible (2-3 instead of 10+)

---

**Ready to try the improved version?** 🚀

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
python claude_mcp_scanner.py
```

Should complete in just 3-5 iterations now!
