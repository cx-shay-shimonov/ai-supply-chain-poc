# sem-query.py Enhanced JSON Output

## Overview
The `sem-query.py` script now supports an enhanced JSON output format with rich metadata for AI usage auditing.

## New Features

### 1. Enhanced JSON Structure
```json
{
  "query": "your search query",
  "repository": "/path/to/repository",
  "results": [...]
}
```

### 2. Rich Result Metadata
Each result now includes:

- **`rank`**: Position in results (1-indexed)
- **`score`**: Raw similarity score (0.0-1.0)
- **`certainty`**: Level ("high", "medium", "low")
- **`certainty_percent`**: Percentage confidence (scaled from score)
- **`file`**: Full path to source file
- **`line`**: Line number where code starts
- **`code`**: Full code snippet
- **`match_reason`**: Human-readable explanation of match
- **`matched_tokens`**: Query terms found in code
- **`highlighted_tokens`**: All relevant tokens (including related terms)

### 3. Certainty Calculation
Certainty levels are automatically calculated from the similarity score:
- **High**: ≥ 60% (strong semantic match)
- **Medium**: 50-59% (good semantic match)
- **Low**: < 50% (contextual match)

### 4. Match Reasoning
The `match_reason` field provides clear explanations:
- `"Contains 'openai', 'gpt'"` - Direct token matches
- `"Contains 'openai' | Related: OPENAI_API_KEY"` - Direct + compound tokens
- `"Semantic similarity (contextual match)"` - No direct matches, pure semantic

## Usage Examples

### Basic JSON Output
```bash
venv/bin/python sem-query.py -p projects-samples/ai-ui -n 10 --json 'OpenAI gpt usage'
```

### With sem-audit.sh
The `sem-audit.sh` script automatically uses the enhanced format:
```bash
./sem-audit.sh projects-samples/ai-ui 50
```

### Query Any AI Models
```bash
venv/bin/python sem-query.py -p projects-samples/ai-ui -n 50 --json \
  'usages of gpt-5, gpt-4o, claude, gemini, deepseek, llama, mistral'
```

## Output Files

When running `sem-audit.sh`, you get:

1. **`sem_results.json`**: Full enhanced JSON with all fields
2. **`ai_audit_comparison.csv`**: CSV with rank, certainty, matched tokens
3. **`semantic_ai_providers.json`**: Extracted AI provider/model names
4. **`semantic_assets.json`**: Just the assets for easy parsing

## Example Result

```json
{
  "rank": 1,
  "score": 0.40832629799842834,
  "certainty": "medium",
  "certainty_percent": 57.17,
  "file": "/path/to/server.js",
  "line": 135,
  "code": "app.listen(PORT, () => {\n    console.log(`🚀 Server running at http://localhost:${PORT}`);\n    console.log(`📁 Serving static files from: ${__dirname}`);\n\n    if (!process.env.OPENAI_API_KEY) {\n        console.warn('⚠️  Warning: OPENAI_API_KEY not found in environment');\n    } else {\n        console.log('✅ OpenAI API key loaded from .env');\n    }\n});",
  "match_reason": "Contains 'openai' | Related: OPENAI_API_KEY",
  "matched_tokens": [
    "openai"
  ],
  "highlighted_tokens": [
    "OpenAI",
    "OPENAI_API_KEY"
  ]
}
```

## Benefits

1. **Clear Certainty Levels**: Quickly identify high-confidence matches
2. **Rich Context**: Understand WHY code matched your query
3. **Token Tracking**: See which query terms were found
4. **CSV Export**: Easy to import into spreadsheets for reporting
5. **Asset Extraction**: Automatically identify all AI providers/models

## Integration with CI/CD

The enhanced JSON format makes it easy to:
- Set certainty thresholds for CI/CD gates
- Generate compliance reports
- Track AI usage over time
- Alert on new AI dependencies

## CSV Column Reference

| Column | Description | Example |
|--------|-------------|---------|
| Rank | Result position | 1, 2, 3... |
| Tool | Search tool used | "Semantic Search" |
| Type | Finding type | "AI Usage Pattern" |
| File | Source file | "server.js" |
| Line | Line number | 135 |
| Score | Raw score | 0.4083 |
| Certainty | Level | "medium" |
| Certainty % | Percentage | "57.17%" |
| Match Reason | Explanation | "Contains 'openai'..." |
| Matched Tokens | Found terms | "openai, gpt" |
| Code Preview | First line | "app.listen(PORT..." |

## Notes

- The certainty percentage uses a scaling formula to provide more meaningful values
- Matched tokens are case-insensitive
- Highlighted tokens include both exact matches and related compound tokens (e.g., "openai" in "OPENAI_API_KEY")
- Match reasons are automatically generated based on token analysis
