# Architecture: Why Iterations Are Needed

## 🤔 Your Questions Answered

### Q1: "Why iterations? Can't you just send project and prompt?"

**Short answer:** Because Claude API and Claude Desktop work completely differently.

### Q2: "Do you use the MCP server installed on my machine?"

**Yes!** We connect to your local `mcp-server-tree-sitter` installation.

---

## 📐 Architecture Comparison

### Option 1: Claude Desktop (What You're Used To)

```
┌─────────────────┐
│ Claude Desktop  │ ← Built-in MCP support (free)
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
    ┌────────┐    ┌─────────┐
    │  MCP   │    │ Claude  │
    │ Server │    │   AI    │
    └────────┘    └─────────┘
         │
         ▼
    Your Files
```

**How it works:**
1. You type: "Find all GPT models"
2. Claude Desktop internally calls MCP tools
3. Shows you results in chat
4. **No iterations exposed to you** - all handled internally

**Pros:**
- ✅ Free (no API costs)
- ✅ Interactive
- ✅ Easy to use

**Cons:**
- ❌ Manual only
- ❌ Can't automate
- ❌ No programmatic access

---

### Option 2: Claude API + MCP (This Tool)

```
┌──────────────┐
│ Your Script  │ ← You control everything
└──────┬───────┘
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
┌────────────┐    ┌──────────┐    ┌────────────┐
│ Claude API │    │   MCP    │    │    Your    │
│  (Cloud)   │    │  Server  │    │   Files    │
│            │    │ (Local)  │    │  (Local)   │
└────────────┘    └──────────┘    └────────────┘
       ▲                 │
       │                 ▼
       └───── You ───────┘
    (act as bridge)
```

**How it works:**

```python
# Iteration 1
You → Claude API: "Find all GPT models in this project"
Claude API → You: "I want to call find_text tool"
You → MCP Server: find_text(query="gpt-")
MCP → You: "Found 10 matches in file1.js..."
You → Claude API: "Here are the results: 10 matches..."

# Iteration 2
Claude API → You: "I want to call find_text again for API calls"
You → MCP Server: find_text(query="completion")
MCP → You: "Found 3 matches..."
You → Claude API: "Here are the results: 3 matches..."

# Iteration 3
Claude API → You: "Done! Here's my analysis: {...}"
You → Done! ✅
```

**Why iterations?**

1. **Claude API has NO direct access to:**
   - Your filesystem
   - Your MCP server
   - Any local resources

2. **Claude API only knows how to:**
   - Request tools to be called
   - Analyze results you send back
   - Request more tools if needed

3. **You (the script) must:**
   - Execute MCP tools
   - Send results back to Claude
   - Repeat until Claude is satisfied

---

## 🔄 What Happens in Each Iteration

### Iteration Anatomy

```
┌─────────────────────────────────────────────────────────┐
│  ITERATION N                                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Send message to Claude API                         │
│     (prompt + previous results)                         │
│                                                         │
│  2. Claude thinks and responds:                         │
│     - Option A: "I want to call tool X"                │
│     - Option B: "I'm done, here's my answer"           │
│                                                         │
│  3. If Option A:                                        │
│     → Execute MCP tool                                  │
│     → Get results                                       │
│     → Go to next iteration                             │
│                                                         │
│  4. If Option B:                                        │
│     → Extract final answer                              │
│     → Done! ✅                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Example with Your Project

```
Iteration 1:
  You:    "Find all LLM models in ai-ui project"
  Claude: "I'll call find_text with query='gpt-'"
  You:    Execute MCP → "Found: gpt-4o, gpt-4o-mini..."
  
Iteration 2:
  You:    "Here are results: gpt-4o, gpt-4o-mini..."
  Claude: "I'll call find_text with query='claude-'"
  You:    Execute MCP → "Found: claude-3-sonnet..."
  
Iteration 3:
  You:    "Here are results: claude-3-sonnet..."
  Claude: "I'll call find_text with query='completion'"
  You:    Execute MCP → "Found: chat.completions.create..."
  
Iteration 4:
  You:    "Here are results: chat.completions.create..."
  Claude: "Done! Here's my JSON analysis: {...}"
  Done! ✅
```

---

## ⚡ Performance Optimization

### Why Max Iterations Was Reached

Your scan hit 10 iterations because Claude was making **many small searches**:

```
❌ BAD (many iterations):
  - Search for "gpt-4"
  - Search for "gpt-4o"
  - Search for "gpt-3.5"
  - Search for "claude-3"
  - Search for "claude-sonnet"
  - Search for "gemini"
  - ... (10+ searches)
```

### What We Fixed

```
✅ GOOD (fewer iterations):
  - Search for "(gpt-[0-9]|claude-[0-9]|gemini|dall-e)" (ALL models)
  - Search for "(completion|messages\\.create)" (ALL API calls)
  - Analyze and done! (2-3 searches total)
```

### Improvements Made

1. **More directive prompt** - Tell Claude to use broad regex patterns
2. **Increased limit** - 10 → 15 iterations (safety net)
3. **Better progress** - Show tool call count and iteration progress
4. **Partial results** - If limit hit, still return analysis
5. **Pre-fetch context** - Get file list first to help Claude plan

---

## 💡 Why Not Just Use MCP Directly?

### Option 3: Direct MCP (No Claude)

```python
# Direct MCP usage
result = mcp.find_text(query="gpt-4")
# Result: Raw text matches, no analysis
```

**Pros:**
- ✅ Free
- ✅ Fast
- ✅ No iterations

**Cons:**
- ❌ No AI analysis
- ❌ You must write all search patterns
- ❌ No interpretation or recommendations
- ❌ No categorization

---

### Option 4: This Tool (Claude API + MCP)

```python
# Hybrid approach
result = scanner.scan_for_llm_usage(project_path, project_name)
# Result: AI-analyzed JSON with insights and recommendations
```

**Pros:**
- ✅ AI-powered analysis
- ✅ Automatic pattern discovery
- ✅ Categorization and insights
- ✅ Recommendations
- ✅ Programmatic (automate, batch, CI/CD)

**Cons:**
- ⚠️ API costs ($0.02-0.30 per scan)
- ⚠️ Requires iterations
- ⚠️ Slightly slower

---

## 🎯 When to Use Each Option

### Use Claude Desktop + MCP When:
- ✅ You want interactive exploration
- ✅ One-off analysis
- ✅ Don't want to pay for API
- ✅ Need real-time chat

### Use This Tool (Claude API + MCP) When:
- ✅ Need to automate scanning
- ✅ Batch process multiple projects
- ✅ Generate structured reports (JSON)
- ✅ Integrate into CI/CD
- ✅ Want AI insights programmatically

### Use Direct MCP When:
- ✅ Know exactly what to search for
- ✅ Don't need AI analysis
- ✅ Want maximum speed
- ✅ Writing custom tooling

### Use Pure Tree-sitter When:
- ✅ Need AST-level analysis
- ✅ Custom detection logic
- ✅ Want full control
- ✅ Building a scanner tool

---

## 📊 Cost vs Benefit

| Approach | Speed | Cost | AI Analysis | Automation |
|----------|-------|------|-------------|------------|
| Claude Desktop | Fast | Free | ✅ Full | ❌ No |
| This Tool | Medium | $0.02-0.30 | ✅ Full | ✅ Yes |
| Direct MCP | Fast | Free | ❌ None | ✅ Yes |
| Tree-sitter | Very Fast | Free | ❌ None | ✅ Yes |

---

## 🔧 Optimization Tips

### Make Fewer Iterations

1. **Use broad regex patterns:**
   ```python
   # BAD: Multiple searches
   find_text(query="gpt-4")
   find_text(query="gpt-3.5")
   find_text(query="claude")
   
   # GOOD: One comprehensive search
   find_text(query="(gpt-[0-9]|claude-|gemini)")
   ```

2. **Be specific in prompt:**
   ```python
   # BAD: Vague
   "Find all AI models"
   
   # GOOD: Directive
   "Use ONE regex search for ALL models: (gpt-|claude-|gemini)"
   ```

3. **Provide context:**
   ```python
   # Provide file count, project info upfront
   # So Claude can plan efficiently
   ```

---

## 🎓 Summary

**Q: Why iterations?**
A: Because Claude API can't access your MCP server directly. We bridge them.

**Q: Can't we just send project and prompt?**
A: No - Claude API has no access to your files or MCP server. We execute tools on its behalf.

**Q: Do you use local MCP server?**
A: Yes! We connect to `mcp-server-tree-sitter` installed on your machine.

**Q: Why not use Claude Desktop?**
A: Claude Desktop is great for interactive use, but can't be automated or scripted.

---

## 🚀 The Improvements

Your scanner now:

1. ✅ Uses broad regex patterns (fewer searches)
2. ✅ Has 15 iteration limit (was 10)
3. ✅ Shows progress (iteration N/15, X tool calls)
4. ✅ Returns partial results if limit reached
5. ✅ Pre-fetches file context for better planning
6. ✅ More efficient prompting

**Try it again - should complete in 3-5 iterations now!** 🎯

---

*For more details, see READY.md and USAGE.md*
