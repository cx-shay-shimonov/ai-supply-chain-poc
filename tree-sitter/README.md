# Tree-sitter AI Model Scanner

A syntax-aware code scanner that uses Tree-sitter for parsing source code to detect AI model references, variable assignments, and usage patterns across multiple concatenation methods.

## Overview

This scanner uses Abstract Syntax Tree (AST) parsing via Tree-sitter to analyze source code and identify:

- **String literals** containing AI model names (e.g., `'gpt-4o-mini'`, `"claude-3-opus"`)
- **Variable assignments** to AI model names (e.g., `const model = 'gpt-4o-mini';`)
- **Template literals** with model name patterns (e.g., `` const m = `${modelName}-${version}` ``)
- **Binary expressions** with `+` operator (e.g., `const model = name + '-' + version`)
- **Compound assignments** with `+=` operator (e.g., `let m = name; m += '-'; m += version;`)
- **Variable usage** in function calls and API calls
- **API call tracking** with parameter identification

Unlike simple pattern matching, Tree-sitter performs syntactic analysis, understanding the code structure and properly identifying string literals, variable declarations, and function calls across different languages.

## Supported Languages

- JavaScript (`.js`, `.jsx`)
- TypeScript (`.ts`, `.tsx`)
- Python (`.py`)

## Installation

### Prerequisites

- Python 3.11 or higher
- Virtual environment (included in this directory)

### Setup

The virtual environment is already configured with the required dependencies:

```bash
cd tree-sitter
source venv/bin/activate
```

### Dependencies

The following Python packages are installed in the virtual environment:

- **`tree-sitter`** (0.25.2) - Core Tree-sitter parsing library from [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter)
- **`tree-sitter-javascript`** (0.25.0) - JavaScript/TypeScript language parser
- **`tree-sitter-python`** (0.25.0) - Python language parser

All packages are official Tree-sitter projects (MIT License).

## Usage

### Basic Commands

Activate the virtual environment first:

```bash
cd tree-sitter
source venv/bin/activate
```

### Scan ai-ui Project

Scan the ai-ui sample project:

```bash
python scanner.py --dir ../projects-samples/ai-ui --output output/ai-ui-scan.json
```

Expected output:
```
🔍 Tree-sitter AI Model Scanner
==================================================
📁 Scanning: ../projects-samples/ai-ui
📝 Output: output/ai-ui-scan.json
📊 Format: json

✅ Report saved to: output/ai-ui-scan.json
📊 Total findings: 12

📋 Summary:
   String literals: 2
   Variable assignments: 8
   Template literals: 0
   String concatenations: 2
   Unique models: 3
   Models: 4o-mini, gpt, gpt-4o-mini

✅ Scan complete!
```

### Scan OpenHands Project

Scan the OpenHands sample project:

```bash
python scanner.py --dir ../projects-samples/OpenHands --output output/openhands-scan.json
```

### Using the Wrapper Script

Scan both projects at once with timestamped output files:

```bash
./scripts/scan-projects.sh
```

This will create output files with timestamps:
- `output/ai-ui-scan-YYYYMMDD_HHMMSS.json`
- `output/openhands-scan-YYYYMMDD_HHMMSS.json`

## Command Line Options

```bash
python scanner.py [OPTIONS]
```

### Options

- `--dir PATH` (required) - Directory to scan
- `--output FILE` - Output file path (default: `output/scan-results.json`)
- `--format FORMAT` - Output format: `json` or `text` (default: `json`)
- `--help` - Show help message

### Examples

#### JSON Output (default)
```bash
python scanner.py --dir ../projects-samples/ai-ui --output results.json
```

#### Text Output
```bash
python scanner.py --dir ../projects-samples/OpenHands --format text --output results.txt
```

#### Custom Output Location
```bash
python scanner.py --dir ../projects-samples/ai-ui --output /tmp/scan-results.json
```

## Output Format

### JSON Output

The scanner produces structured JSON output with the following schema:

```json
{
  "scan_date": "2026-01-18T18:09:32.234832",
  "total_findings": 12,
  "findings": [
    {
      "type": "variable_assignment",
      "model": "constructed",
      "variable": "m",
      "file": "../projects-samples/ai-ui/server.js",
      "line": 38,
      "column": 15,
      "code": "const m = `${mName}-${mVersion}`;",
      "assigned_value": "`${mName}-${mVersion}`",
      "is_template_construction": true,
      "template_variables": ["mName", "mVersion"],
      "note": "Model name constructed from template using: mName, mVersion",
      "usage_locations": [
        {
          "file": "../projects-samples/ai-ui/server.js",
          "line": 40,
          "column": 13,
          "context": "const stream = await openai.chat.completions.create({",
          "function": "openai.chat.completions.create",
          "parameter": "model",
          "is_api_call": true
        }
      ],
      "usage_count": 1,
      "api_call_count": 1
    }
  ],
  "summary": {
    "string_literals": 2,
    "variable_assignments": 8,
    "template_literals": 0,
    "string_concatenations": 2,
    "models_found": ["gpt-4o-mini", "gpt", "4o-mini"]
  }
}
```

### Finding Types

- **`string_literal`** - Direct string containing a model name
- **`variable_assignment`** - Variable assigned to a model name with optional usage tracking
- **`string_concatenation`** - Binary expression using `+` operator to build model names
- **`template_literal`** - Template string with model name pattern (includes `components` showing substitutions)

### Special Annotations

- **`is_template_construction`** - Model built using template literals
- **`is_binary_construction`** - Model built using `+` operator
- **`is_compound_assignment`** - Model built using `+=` operator across multiple statements
- **`is_api_call`** - Usage in an API function call
- **`api_call_count`** - Number of times used in API calls
- **`usage_locations`** - Array of locations where the variable is used

## Configuration

### Model Names

The scanner looks for AI model names defined in `rules/ai-models.json`. This file contains:

- **`exact_matches`** - Array of exact model name strings to match
- **`partial_patterns`** - Array of partial patterns (e.g., `"gpt-"`, `"claude-"`)
- **`model_name_parts`** - Parts used in concatenation (e.g., `"gpt"`, `"4o-mini"`)
- **`api_call_patterns`** - Function names and parameter names to identify API calls

To add new model names:

1. Edit `rules/ai-models.json`
2. Add model names to the `exact_matches` array
3. Add patterns to the `partial_patterns` array for substring matching
4. Add name parts to `model_name_parts` for concatenation detection

Example:

```json
{
  "exact_matches": [
    "gpt-4o",
    "gpt-4o-mini",
    "claude-3-opus"
  ],
  "partial_patterns": [
    "gpt-",
    "claude-",
    "gemini-"
  ],
  "model_name_parts": [
    "gpt",
    "claude",
    "4o",
    "4o-mini"
  ],
  "api_call_patterns": {
    "function_names": [
      "chat.completions.create",
      "completions.create"
    ],
    "parameter_names": [
      "model",
      "engine"
    ]
  }
}
```

## How It Works

1. **Parse Source Files**: Tree-sitter parses each source file into an Abstract Syntax Tree (AST)
2. **Traverse AST**: The scanner recursively visits all nodes in the tree
3. **Detect Patterns**:
   - String nodes are checked against model name lists
   - Variable declarators track model assignments and resolve references
   - Template strings are analyzed for model patterns with variable substitution
   - Binary expressions detect `+` concatenation across variables
   - Augmented assignments track `+=` operations across multiple statements
   - Function calls identify API usage and parameter passing
4. **Track Data Flow**: Variable values are tracked across assignments and usage
5. **Report Results**: Findings are aggregated with usage locations and API call identification

### Concatenation Detection

The scanner handles multiple concatenation methods:

#### 1. Template Literals
```javascript
const mName = 'gpt';
const mVersion = '4o-mini';
const model = `${mName}-${mVersion}`;  // ✅ Detected as "constructed"
```

#### 2. Binary Expressions
```javascript
const model = mName + '-' + mVersion;  // ✅ Detected as "constructed"
```

#### 3. Compound Assignments
```javascript
let model = mName;     // Starts as "gpt"
model += '-';          // Becomes "gpt-"
model += mVersion;     // Becomes "gpt-4o-mini" ✅ Detected
```

### API Call Detection

The scanner identifies when constructed models are used in API calls:

```javascript
const m = `${mName}-${mVersion}`;

openai.chat.completions.create({
    model: m,  // ✅ Tracked with is_api_call=true, parameter="model"
    messages: []
});
```

### Advantages of AST-based Parsing

- **Language-aware**: Understands code structure, not just text patterns
- **Accurate**: Distinguishes strings from comments, identifiers from literals
- **Context-sensitive**: Can track variable flow and usage across statements
- **Data flow analysis**: Resolves variable references and tracks mutations
- **Fast**: Efficient parsing with minimal false positives

## Limitations

- Only scans supported file types (`.js`, `.jsx`, `.ts`, `.tsx`, `.py`)
- Skips directories: `node_modules`, `.git`, `dist`, `build`, `.embeddings`, `venv`, `__pycache__`
- Variable tracking is limited to single-file scope (doesn't follow imports/exports)
- Template literal and concatenation detection requires variables to be defined in the same file
- Complex control flow (if/else branches, loops) may affect compound assignment tracking

## Troubleshooting

### "Could not parse" Warnings

If you see warnings like:
```
Warning: Could not parse ../path/to/file.js: Parsing failed
```

This can happen if:
- The file has syntax errors
- The file uses very new syntax not yet supported by the parser version
- The file is minified or obfuscated

These warnings can usually be ignored - the scanner will continue with other files.

### No Results Found

If the scanner finds 0 results:
1. Check that the model names are in `rules/ai-models.json`
2. Verify the directory path is correct
3. Ensure the repository contains supported file types
4. Check if files are being skipped (see excluded directories above)

## License

This tool is part of the AI Supply Chain POC evaluation project.

## Related Tools

See the main [README.md](../README.md) for comparisons with other AI detection tools:
- Semgrep (pattern-based static analysis)
- semantic-code-search (ML embeddings for natural language search)
- xbom (extended Bill of Materials)
