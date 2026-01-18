# Semantic Code Search (sem) Examples

A comprehensive guide for using `sem` - an AI-powered semantic code search tool that understands natural language queries.

## About the Tool

**Repository**: [sturdy-dev/semantic-code-search](https://github.com/sturdy-dev/semantic-code-search)  
**License**: AGPL-3.0  
**GitHub Stats**: ⭐ 381 stars | 🍴 41 forks | 👥 2 contributors  
**Language**: Python 100%  
**Maintainer**: Kiril Videlov ([@krlvi](https://github.com/krlvi))  
**Status**: ⚠️ Low activity (38 total commits, 11 open issues)  
**Installation**: `pip3 install semantic-code-search`

**Key Features**:
- Natural language code search using ML embeddings
- 100% local processing (no data leaves your computer)
- Supports 10 programming languages
- ~500 MB model download (one-time)
- Caches embeddings for fast subsequent searches

## Table of Contents

- [Quick Start](#quick-start)
- [Basic Usage](#basic-usage)
- [Real-World Query Examples](#real-world-query-examples)
- [Output Formats](#output-formats)
- [Advanced Features](#advanced-features)
- [Demo Scenarios](#demo-scenarios)
- [Non-Interactive Mode (sem-query.py)](#non-interactive-mode-sem-querypy)
- [Tips & Best Practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Setup

```bash
# Add alias to your ~/.zshrc (one-time setup)
echo "alias sem='/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/venv/bin/sem'" >> ~/.zshrc
source ~/.zshrc

# Now you can use 'sem' from anywhere!
```

### First-Time Setup for Sample Projects

```bash
# Navigate to the ai-supply-chain-poc directory
cd /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc

# Generate embeddings for cnas-mfe (first time only, takes a minute)
venv/bin/sem --embed -p projects-samples/cnas-mfe

# Generate embeddings for ai-ui
venv/bin/sem --embed -p projects-samples/ai-ui

# After that, search is instant!
venv/bin/sem -p projects-samples/cnas-mfe 'React components'
```

---

## Basic Usage

### Command Syntax

```bash
sem -p <repo-path> -n <num-results> 'your natural language query'
```

### Quick Examples with Sample Projects

```bash
# Search in cnas-mfe (React/TypeScript project)
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'React components'

# Search in ai-ui (OpenAI integration project)
venv/bin/sem -p projects-samples/ai-ui -n 50 'OpenAI usage'

# Get more results
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'array methods'

# Filter by file extension
venv/bin/sem -p projects-samples/cnas-mfe -x tsx 'button components'
```

---

## Real-World Query Examples

*Based on actual commands from development history*

### Finding Specific Functions

```bash
# Find usages of a specific function
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'usages of SortedSeverities function'

# Find function declarations
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'function definitions with error handling'

# Find specific patterns
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'array reduce methods'
```

### React Development Queries

```bash
# Find React components
venv/bin/sem -p projects-samples/cnas-mfe -n 10 'react components'

# More specific - functional components
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'react functional components'

# Find FC TypeScript types
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'React FC TypeScript type'

# Find React imports
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'React imports'

# Find hooks usage
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'useState and useEffect hooks'
```

### JavaScript/TypeScript Patterns

```bash
# Find array methods
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'array methods'

# Find reduce usage
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'reduce'

# Find sort implementations
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'sort'

# Find specific type definitions
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'TypeScript type definitions'
```

### API and Integration Queries

```bash
# Find API calls
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'API requests'

# Find OpenAI usage
venv/bin/sem -p projects-samples/ai-ui -n 100 'openai'

# Find specific model references
venv/bin/sem -p projects-samples/ai-ui -n 100 'gpt-4o-mini'

# Find authentication
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'authentication and login'

# Find embeddings
venv/bin/sem -p projects-samples/ai-ui -n 50 'embeddings'
```

### SVG and Assets

```bash
# Find SVG usage
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'svg'

# Find icon components
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'icon components'

# Find SVG paths
venv/bin/sem -p projects-samples/cnas-mfe -n 50 'SVG paths and shapes'
```

### Real-World Project Queries (OpenHands - 2,145 Files) ⭐

#### First-Time Setup (One Time Only)

```bash
# Check if embeddings exist
ls -lh projects-samples/OpenHands/.embeddings

# If not found, generate embeddings (takes 5-10 minutes)
venv/bin/sem --embed -p projects-samples/OpenHands

# Monitor progress (in another terminal)
tail -f ~/.cursor/projects/*/terminals/2.txt
```

#### LLM/AI Integration Queries

```bash
# Find LLM integration patterns
venv/bin/sem -p projects-samples/OpenHands -n 50 'LLM integration and API calls'

# Find specific AI providers
venv/bin/sem -p projects-samples/OpenHands -n 50 'OpenAI and Claude integration'

# Find AI model configuration
venv/bin/sem -p projects-samples/OpenHands -n 100 'AI model configuration'

# Find prompt engineering
venv/bin/sem -p projects-samples/OpenHands -n 50 'prompt templates and engineering'
```

#### Backend/API Queries

```bash
# Find Flask API endpoints
venv/bin/sem -p projects-samples/OpenHands -n 50 'Flask API endpoints'

# Find Python API routes
venv/bin/sem -p projects-samples/OpenHands -n 50 'Python API routes'

# Find WebSocket handlers
venv/bin/sem -p projects-samples/OpenHands -n 100 'WebSocket handlers'

# Find event handling
venv/bin/sem -p projects-samples/OpenHands -n 50 'event handling and listeners'
```

#### Frontend/React Queries

```bash
# Find React hooks usage
venv/bin/sem -p projects-samples/OpenHands -n 50 'React hooks usage'

# Find React components with state
venv/bin/sem -p projects-samples/OpenHands -n 50 'React components with state'

# Find TypeScript React components
venv/bin/sem -p projects-samples/OpenHands -n 100 'TypeScript React components'

# Find state management
venv/bin/sem -p projects-samples/OpenHands -n 50 'state management with zustand'
```

#### Authentication & Security

```bash
# Find authentication logic
venv/bin/sem -p projects-samples/OpenHands -n 100 'authentication and authorization'

# Find JWT token handling
venv/bin/sem -p projects-samples/OpenHands -n 50 'JWT token handling'

# Find session management
venv/bin/sem -p projects-samples/OpenHands -n 50 'session management'
```

#### Database & Storage

```bash
# Find database models
venv/bin/sem -p projects-samples/OpenHands -n 50 'database models and queries'

# Find SQL and ORM usage
venv/bin/sem -p projects-samples/OpenHands -n 100 'SQL and ORM'

# Find data persistence
venv/bin/sem -p projects-samples/OpenHands -n 50 'data persistence and storage'
```

#### Error Handling & Testing

```bash
# Find error handling patterns
venv/bin/sem -p projects-samples/OpenHands -n 100 'error handling and exceptions'

# Find logging
venv/bin/sem -p projects-samples/OpenHands -n 50 'logging and monitoring'

# Find test utilities
venv/bin/sem -p projects-samples/OpenHands -n 50 'test utilities and mocks'
```

### General Code Exploration

```bash
# Find error handling
venv/bin/sem -p ~/Projects/my-app -n 100 'error handling patterns'

# Find testing code
venv/bin/sem -p ~/Projects/my-app -n 100 'unit tests'

# Find configuration
venv/bin/sem -p ~/Projects/my-app -n 50 'configuration and environment variables'

# Find security-related code
venv/bin/sem -p ~/Projects/my-app -n 50 'security validation and sanitization'
```

---

## Output Formats

### Default Interactive Mode

```bash
# Opens interactive picker
venv/bin/sem -p ~/Projects/my-app -n 100 'your query'

# Navigate with arrow keys or vim bindings (j/k)
# Press Enter to open in default editor
# Press q to quit
```

### Open in Specific Editor

```bash
# Open in VS Code
venv/bin/sem -p ~/Projects/my-app -n 100 -e vscode 'your query'

# Open in Vim
venv/bin/sem -p ~/Projects/my-app -n 100 -e vim 'your query'
```

### Cluster Mode (Find Similar Code)

```bash
# Find duplicate/similar code patterns
venv/bin/sem --cluster -p ~/Projects/my-app

# Adjust similarity threshold
venv/bin/sem --cluster -p ~/Projects/my-app --cluster-max-distance 0.3

# Minimum lines to consider
venv/bin/sem --cluster -p ~/Projects/my-app --cluster-min-lines 5

# Minimum cluster size
venv/bin/sem --cluster -p ~/Projects/my-app --cluster-min-cluster-size 3
```

---

## Advanced Features

### Filter by File Extension

```bash
# Search only TypeScript files
venv/bin/sem -p ~/Projects/my-app -x ts 'authentication'

# Search only React/TSX files
venv/bin/sem -p ~/Projects/my-app -x tsx 'button components'

# Search only Python files
venv/bin/sem -p ~/Projects/my-app -x py 'database models'

# Search only JavaScript
venv/bin/sem -p ~/Projects/my-app -x js 'utility functions'
```

### Regenerate Embeddings

```bash
# When code has changed significantly
venv/bin/sem --embed -p ~/Projects/my-app

# Or delete and regenerate
rm ~/Projects/my-app/.embeddings
venv/bin/sem --embed -p ~/Projects/my-app
```

### Adjust Result Count

```bash
# Quick overview (10 results)
venv/bin/sem -p ~/Projects/my-app -n 10 'react components'

# Comprehensive search (100+ results)
venv/bin/sem -p ~/Projects/my-app -n 200 'function definitions'

# Default is 15 results
venv/bin/sem -p ~/Projects/my-app 'your query'
```

### Custom Model

```bash
# Use a different model
venv/bin/sem -p ~/Projects/my-app -m 'custom-model-name' 'your query'

# Default model: krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net
```

---

## Real-World Scale Testing (OpenHands)

### Why OpenHands is Perfect for Demos

**Small Samples vs Real Project:**
- Small samples: 7 files, instant search
- OpenHands: 2,145 files, still fast search
- Demonstrates scale and production readiness

### Setup Time Comparison

```bash
# Small samples: ~1 minute each
venv/bin/sem --embed -p projects-samples/cnas-mfe    # 30 seconds
venv/bin/sem --embed -p projects-samples/ai-ui       # 30 seconds

# Real project: ~5-10 minutes (one time only)
venv/bin/sem --embed -p projects-samples/OpenHands           # 5-10 minutes
```

### Performance Demonstration

```bash
# Show instant results even on large codebase
time venv/bin/sem -p projects-samples/OpenHands -n 50 'React components'
# Output: Results in < 1 second even with 2,145 files!

# Compare search quality
venv/bin/sem -p projects-samples/cnas-mfe -n 10 'authentication'    # Small
venv/bin/sem -p projects-samples/OpenHands -n 50 'authentication'           # Large, better context
```

### Progressive Demo Strategy

**Step 1: Start Small**
```bash
# "Here's how semantic search works on simple code"
venv/bin/sem -p projects-samples/cnas-mfe -n 10 'React components'
```

**Step 2: Scale Up**
```bash
# "Now let's try it on a real production codebase with 2,145 files"
venv/bin/sem -p projects-samples/OpenHands -n 50 'React components'
```

**Step 3: Show Complexity**
```bash
# "It understands complex patterns across the entire codebase"
venv/bin/sem -p projects-samples/OpenHands -n 50 'LLM integration with error handling'
```

**Step 4: Performance**
```bash
# "And it's still instant, even at scale"
time venv/bin/sem -p projects-samples/OpenHands -n 100 'authentication patterns'
```

## Demo Scenarios

### Scenario 1: Code Review - Find All API Calls

**Objective:** Review all external API integrations

```bash
#!/bin/bash
echo "🔍 Finding All API Calls..."
echo "=========================="

# Search for API patterns
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'API requests and HTTP calls' > api_calls.txt

echo "✅ Results saved to api_calls.txt"
echo ""
echo "Preview:"
head -20 api_calls.txt
```

### Scenario 2: Onboarding - Understand React Architecture

**Objective:** Help new developers understand React structure

```bash
#!/bin/bash
PROJECT="projects-samples/cnas-mfe"

echo "📚 React Architecture Guide"
echo "==========================="
echo ""

echo "1️⃣ Finding Main Components..."
venv/bin/sem -p "$PROJECT" -n 20 'main application components'
echo ""

echo "2️⃣ Finding Hooks Usage..."
venv/bin/sem -p "$PROJECT" -n 20 'useState and useEffect hooks'
echo ""

echo "3️⃣ Finding TypeScript Types..."
venv/bin/sem -p "$PROJECT" -n 20 'TypeScript type definitions'
echo ""

echo "4️⃣ Finding API Integration..."
venv/bin/sem -p "$PROJECT" -n 20 'API calls and data fetching'
```

### Scenario 3: Security Audit - Find Sensitive Operations

**Objective:** Identify security-critical code

```bash
#!/bin/bash
echo "🔒 Security Audit"
echo "================="

CNAS_MFE="projects-samples/cnas-mfe"
AI_UI="projects-samples/ai-ui"

echo "Finding authentication code..."
venv/bin/sem -p "$CNAS_MFE" -n 50 'authentication and login'

echo ""
echo "Finding API key usage..."
venv/bin/sem -p "$AI_UI" -n 50 'API keys and environment variables'

echo ""
echo "Finding data validation..."
venv/bin/sem -p "$CNAS_MFE" -n 50 'input validation'
```

### Scenario 4: Technical Debt - Find Code Duplication

**Objective:** Identify duplicate code for refactoring

```bash
#!/bin/bash
echo "🔧 Finding Code Duplication..."

venv/bin/sem --cluster \
  -p projects-samples/cnas-mfe \
  --cluster-max-distance 0.2 \
  --cluster-min-lines 10 \
  --cluster-min-cluster-size 2 \
  > duplication_report.txt

echo "✅ Report saved to duplication_report.txt"
echo ""
echo "Top duplications found:"
head -50 duplication_report.txt
```

### Scenario 5: AI Usage Audit

**Objective:** Find all AI/LLM usage in codebase

```bash
#!/bin/bash
echo "🤖 AI Usage Audit"
echo "================="

PROJECT="projects-samples/ai-ui"

echo "Finding OpenAI usage..."
venv/bin/sem -p "$PROJECT" -n 100 'openai'

echo ""
echo "Finding specific models..."
venv/bin/sem -p "$PROJECT" -n 100 'gpt-4o-mini and gpt-4o'

echo ""
echo "Finding embedding usage..."
venv/bin/sem -p "$PROJECT" -n 100 'embeddings and vector'

echo ""
echo "Finding streaming API..."
venv/bin/sem -p "$PROJECT" -n 100 'streaming completions'
```

### Scenario 6: Real-World Project Exploration (OpenHands)

**Objective:** Demonstrate semantic search at scale

```bash
#!/bin/bash
echo "🔍 Exploring OpenHands (2,145 files)"
echo "===================================="

PROJECT="projects-samples/OpenHands"

# Check embeddings
if [ ! -f "$PROJECT/.embeddings" ]; then
  echo "⚙️  Generating embeddings (one-time, 5-10 minutes)..."
  venv/bin/sem --embed -p "$PROJECT"
fi

echo ""
echo "1️⃣ Finding LLM Integration..."
venv/bin/sem -p "$PROJECT" -n 20 'LLM integration and API calls'

echo ""
echo "2️⃣ Finding React Components..."
venv/bin/sem -p "$PROJECT" -n 20 'React hooks and state'

echo ""
echo "3️⃣ Finding Backend APIs..."
venv/bin/sem -p "$PROJECT" -n 20 'Flask API endpoints'

echo ""
echo "4️⃣ Finding Authentication..."
venv/bin/sem -p "$PROJECT" -n 20 'authentication middleware'

echo ""
echo "✅ Search across 2,145 files completed instantly!"
```

---

## Non-Interactive Mode (sem-query.py)

For CI/CD, automation, or when you need programmatic access.

### Basic Usage

```bash
# Simple query
python sem-query.py -p projects-samples/cnas-mfe 'React components'

# Save to file
python sem-query.py -p projects-samples/ai-ui -o results.txt 'OpenAI usage'

# JSON output
python sem-query.py -p projects-samples/cnas-mfe --json 'array methods' > results.json

# Hide code snippets
python sem-query.py -p projects-samples/cnas-mfe --no-code 'function names'

# More results
python sem-query.py -p projects-samples/ai-ui -n 20 'gpt models'

# Filter by extension
python sem-query.py -p projects-samples/cnas-mfe -x tsx 'button components'
```

### Automation Examples

```bash
# Daily code quality report
#!/bin/bash
DATE=$(date +%Y-%m-%d)
python sem-query.py -p projects-samples/cnas-mfe --json 'TODO and FIXME comments' > "todos_${DATE}.json"

# CI/CD integration
#!/bin/bash
RESULTS=$(python sem-query.py -p projects-samples/ai-ui --json 'hardcoded credentials' | jq '.findings | length')
if [ "$RESULTS" -gt 0 ]; then
  echo "⚠️ Found $RESULTS potential security issues!"
  exit 1
fi

# Generate documentation
python sem-query.py -p projects-samples/cnas-mfe -n 100 'exported functions' -o api_reference.txt
```

### Comparison with sem

| Feature | `sem` (Interactive) | `sem-query.py` (Non-interactive) |
|---------|-------------------|----------------------------------|
| Terminal UI | ✅ Yes | ❌ No |
| Editor integration | ✅ Yes | ❌ No |
| JSON output | ❌ No | ✅ Yes |
| Save to file | ❌ No | ✅ Yes |
| CI/CD friendly | ❌ No | ✅ Yes |
| Cursor terminal | ❌ No | ✅ Yes |
| Speed | Fast | Fast |

---

## Creating Service Wrappers for sem-query.py

Transform `sem-query.py` into various service interfaces for different use cases.

### 1. REST API Service (Flask)

Create a web service for semantic code search:

**File: `sem-api-service.py`**

```python
#!/usr/bin/env python3
"""
REST API wrapper for semantic code search.
Provides HTTP endpoints for code search queries.

Usage:
    python sem-api-service.py
    # Then: curl http://localhost:5000/search?repo=projects-samples/ai-ui&query=OpenAI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc"
PYTHON_BIN = f"{BASE_DIR}/venv/bin/python"
SEM_QUERY = f"{BASE_DIR}/sem-query.py"

# Allowed repositories (security)
ALLOWED_REPOS = {
    "ai-ui": f"{BASE_DIR}/projects-samples/ai-ui",
    "cnas-mfe": f"{BASE_DIR}/projects-samples/cnas-mfe",
    "openhands": f"{BASE_DIR}/projects-samples/OpenHands"
}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "sem-api"}), 200

@app.route('/repos', methods=['GET'])
def list_repos():
    """List available repositories"""
    repos = []
    for name, path in ALLOWED_REPOS.items():
        has_embeddings = os.path.exists(f"{path}/.embeddings")
        repos.append({
            "name": name,
            "path": path,
            "embeddings_ready": has_embeddings
        })
    return jsonify({"repositories": repos}), 200

@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Search code semantically
    
    Query params:
        repo: Repository name (ai-ui, cnas-mfe, openhands)
        query: Search query
        n: Number of results (default: 10)
        extension: File extension filter (optional)
    """
    # Parse request
    if request.method == 'POST':
        data = request.json or {}
        repo_name = data.get('repo')
        query = data.get('query')
        n_results = data.get('n', 10)
        extension = data.get('extension')
    else:
        repo_name = request.args.get('repo')
        query = request.args.get('query')
        n_results = request.args.get('n', 10, type=int)
        extension = request.args.get('extension')
    
    # Validate
    if not repo_name or not query:
        return jsonify({"error": "Missing repo or query parameter"}), 400
    
    if repo_name not in ALLOWED_REPOS:
        return jsonify({"error": f"Invalid repo. Allowed: {list(ALLOWED_REPOS.keys())}"}), 400
    
    repo_path = ALLOWED_REPOS[repo_name]
    
    # Check embeddings
    if not os.path.exists(f"{repo_path}/.embeddings"):
        return jsonify({
            "error": "Embeddings not generated",
            "message": f"Run: venv/bin/sem --embed -p {repo_path}"
        }), 400
    
    # Build command
    cmd = [PYTHON_BIN, SEM_QUERY, '-p', repo_path, '--json', '-n', str(n_results)]
    if extension:
        cmd.extend(['-x', extension])
    cmd.append(query)
    
    # Execute
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return jsonify({
                "error": "Search failed",
                "stderr": result.stderr
            }), 500
        
        # Parse JSON output
        data = json.loads(result.stdout)
        return jsonify(data), 200
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Search timeout"}), 504
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON response"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/embed', methods=['POST'])
def generate_embeddings():
    """Generate embeddings for a repository"""
    data = request.json or {}
    repo_name = data.get('repo')
    
    if not repo_name or repo_name not in ALLOWED_REPOS:
        return jsonify({"error": "Invalid repo"}), 400
    
    repo_path = ALLOWED_REPOS[repo_name]
    
    # This would be better as a background job in production
    return jsonify({
        "message": "Embedding generation should be done manually",
        "command": f"venv/bin/sem --embed -p {repo_path}"
    }), 200

if __name__ == '__main__':
    print("🔍 Semantic Code Search API")
    print(f"📁 Base: {BASE_DIR}")
    print(f"🚀 Starting on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /health              - Health check")
    print("  GET  /repos               - List repositories")
    print("  GET  /search?repo=&query= - Search code")
    print("  POST /search              - Search code (JSON body)")
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**Usage:**

```bash
# Start the service
python sem-api-service.py

# In another terminal:

# Check health
curl http://localhost:5000/health

# List repos
curl http://localhost:5000/repos

# Search
curl "http://localhost:5000/search?repo=ai-ui&query=OpenAI%20usage&n=5"

# POST search
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"repo": "cnas-mfe", "query": "React components", "n": 10}'

# With extension filter
curl "http://localhost:5000/search?repo=cnas-mfe&query=array%20methods&n=20&extension=tsx"
```

### 2. CLI Service Wrapper

Simplified CLI tool for common searches:

**File: `sem-cli-wrapper.sh`**

```bash
#!/bin/bash
# Friendly CLI wrapper for semantic code search

BASEDIR="/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc"
SEM_QUERY="$BASEDIR/sem-query.py"

# Repository shortcuts
declare -A REPOS=(
    ["ai"]="$BASEDIR/projects-samples/ai-ui"
    ["ui"]="$BASEDIR/projects-samples/ai-ui"
    ["mfe"]="$BASEDIR/projects-samples/cnas-mfe"
    ["cnas"]="$BASEDIR/projects-samples/cnas-mfe"
    ["oh"]="$BASEDIR/projects-samples/OpenHands"
    ["openhands"]="$BASEDIR/projects-samples/OpenHands"
)

usage() {
    cat << EOF
🔍 Semantic Code Search CLI Wrapper

Usage:
    $(basename $0) <repo-shortcut> <query> [options]

Repository Shortcuts:
    ai, ui       - AI UI project
    mfe, cnas    - CNAS MFE project
    oh, openhands - OpenHands project

Options:
    -n NUM      Number of results (default: 10)
    -x EXT      File extension filter
    --json      JSON output
    -o FILE     Output to file

Examples:
    $(basename $0) ai "OpenAI usage"
    $(basename $0) mfe "React components" -n 20
    $(basename $0) oh "LLM integration" --json
    $(basename $0) cnas "array methods" -x tsx -n 50
    $(basename $0) ui "API keys" -o results.txt

EOF
    exit 1
}

# Parse arguments
if [ $# -lt 2 ]; then
    usage
fi

REPO_KEY="$1"
QUERY="$2"
shift 2

# Resolve repo
REPO_PATH="${REPOS[$REPO_KEY]}"
if [ -z "$REPO_PATH" ]; then
    echo "❌ Unknown repository: $REPO_KEY"
    echo "Available: ${!REPOS[@]}"
    exit 1
fi

# Check embeddings
if [ ! -f "$REPO_PATH/.embeddings" ]; then
    echo "❌ Embeddings not found for $REPO_KEY"
    echo "Run: venv/bin/sem --embed -p $REPO_PATH"
    exit 1
fi

# Execute search
python "$SEM_QUERY" -p "$REPO_PATH" "$@" "$QUERY"
```

**Usage:**

```bash
chmod +x sem-cli-wrapper.sh

# Simple searches
./sem-cli-wrapper.sh ai "OpenAI usage"
./sem-cli-wrapper.sh mfe "React components" -n 20
./sem-cli-wrapper.sh oh "LLM integration" -n 50

# With filters
./sem-cli-wrapper.sh cnas "array methods" -x tsx
./sem-cli-wrapper.sh ui "API endpoints" --json

# Save to file
./sem-cli-wrapper.sh mfe "SortedSeverities" -n 100 -o results.txt
```

### 3. Batch Processing Service

Process multiple queries in batch:

**File: `sem-batch-processor.py`**

```python
#!/usr/bin/env python3
"""
Batch processor for semantic code search.
Run multiple queries from a config file.

Usage:
    python sem-batch-processor.py queries.yaml
"""

import yaml
import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
SEM_QUERY = BASE_DIR / "sem-query.py"
PYTHON_BIN = BASE_DIR / "venv/bin/python"

def run_query(repo_path, query, n_results=10, extension=None):
    """Run a single semantic search query"""
    cmd = [str(PYTHON_BIN), str(SEM_QUERY), '-p', repo_path, '--json', '-n', str(n_results)]
    if extension:
        cmd.extend(['-x', extension])
    cmd.append(query)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python sem-batch-processor.py queries.yaml")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    # Load queries config
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Process queries
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"batch_results_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    print(f"🔍 Processing {len(config['queries'])} queries...")
    print(f"📁 Output: {output_dir}/")
    print("")
    
    results_summary = []
    
    for i, query_config in enumerate(config['queries'], 1):
        name = query_config.get('name', f'query_{i}')
        repo = query_config['repo']
        query = query_config['query']
        n_results = query_config.get('n_results', 10)
        extension = query_config.get('extension')
        
        print(f"[{i}/{len(config['queries'])}] {name}...")
        
        result = run_query(repo, query, n_results, extension)
        
        # Save individual result
        output_file = output_dir / f"{i:02d}_{name.replace(' ', '_')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Summary
        if 'error' in result:
            status = "❌ ERROR"
            count = 0
        else:
            status = "✅ OK"
            count = len(result.get('results', []))
        
        results_summary.append({
            "name": name,
            "repo": repo,
            "query": query,
            "status": status,
            "results_count": count,
            "output_file": str(output_file)
        })
        
        print(f"   {status} - {count} results")
    
    # Save summary
    summary_file = output_dir / "summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "total_queries": len(config['queries']),
            "results": results_summary
        }, f, indent=2)
    
    print("")
    print("✅ Batch processing complete!")
    print(f"📊 Summary: {summary_file}")

if __name__ == '__main__':
    main()
```

**Config file: `queries.yaml`**

```yaml
queries:
  - name: "Find OpenAI Usage"
    repo: "projects-samples/ai-ui"
    query: "OpenAI and GPT models"
    n_results: 20

  - name: "Find React Components"
    repo: "projects-samples/cnas-mfe"
    query: "React functional components"
    n_results: 50
    extension: "tsx"

  - name: "Find SortedSeverities"
    repo: "projects-samples/cnas-mfe"
    query: "SortedSeverities function usage"
    n_results: 100

  - name: "Find LLM Integration"
    repo: "projects-samples/OpenHands"
    query: "LLM integration and API calls"
    n_results: 50

  - name: "Find Authentication"
    repo: "projects-samples/OpenHands"
    query: "authentication middleware"
    n_results: 30
```

**Usage:**

```bash
# Run batch queries
python sem-batch-processor.py queries.yaml

# Output:
# 🔍 Processing 5 queries...
# 📁 Output: batch_results_20260111_143022/
# 
# [1/5] Find OpenAI Usage...
#    ✅ OK - 20 results
# [2/5] Find React Components...
#    ✅ OK - 50 results
# ...
# 
# ✅ Batch processing complete!
# 📊 Summary: batch_results_20260111_143022/summary.json

# View results
cat batch_results_*/summary.json | jq .
ls -lh batch_results_*/
```

### 4. GitHub Actions Integration

CI/CD workflow for automated code audits:

**File: `.github/workflows/code-audit.yml`**

```yaml
name: Semantic Code Audit

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install semantic-code-search
          pip install sentence-transformers
      
      - name: Generate embeddings
        run: |
          sem --embed -p .
      
      - name: Run security audit
        run: |
          python sem-query.py -p . --json 'hardcoded credentials' > security.json
          python sem-query.py -p . --json 'TODO and FIXME' > todos.json
      
      - name: Check for issues
        run: |
          SECURITY_COUNT=$(jq '.results | length' security.json)
          if [ "$SECURITY_COUNT" -gt 0 ]; then
            echo "⚠️ Found $SECURITY_COUNT potential security issues"
            jq '.results[] | "\(.file):\(.line) - \(.code[:100])"' security.json
            exit 1
          fi
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: audit-results
          path: |
            security.json
            todos.json
```

### 5. Slack Bot Integration

Notify team about code patterns:

**File: `sem-slack-bot.py`**

```python
#!/usr/bin/env python3
"""
Slack bot for semantic code search notifications.
Sends daily/weekly code audit reports to Slack.

Usage:
    export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
    python sem-slack-bot.py
"""

import os
import json
import subprocess
import requests
from datetime import datetime

SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')
BASE_DIR = "/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc"
SEM_QUERY = f"{BASE_DIR}/sem-query.py"
PYTHON_BIN = f"{BASE_DIR}/venv/bin/python"

def search_code(repo_path, query, n=10):
    """Run semantic search"""
    cmd = [PYTHON_BIN, SEM_QUERY, '-p', repo_path, '--json', '-n', str(n), query]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None

def send_slack_message(text, attachments=None):
    """Send message to Slack"""
    payload = {"text": text}
    if attachments:
        payload["attachments"] = attachments
    
    response = requests.post(SLACK_WEBHOOK, json=payload)
    return response.status_code == 200

def daily_audit():
    """Run daily code audit"""
    repos = {
        "AI UI": f"{BASE_DIR}/projects-samples/ai-ui",
        "CNAS MFE": f"{BASE_DIR}/projects-samples/cnas-mfe"
    }
    
    queries = [
        ("Security Issues", "hardcoded credentials and API keys"),
        ("TODO Items", "TODO and FIXME comments"),
        ("AI Usage", "OpenAI and AI model usage")
    ]
    
    report_date = datetime.now().strftime('%Y-%m-%d')
    message = f"🔍 *Daily Code Audit Report* - {report_date}"
    
    attachments = []
    
    for repo_name, repo_path in repos.items():
        for query_name, query in queries:
            results = search_code(repo_path, query, n=5)
            
            if results and results.get('results'):
                count = len(results['results'])
                top_result = results['results'][0]
                
                attachments.append({
                    "color": "#ff9900" if count > 0 else "#36a64f",
                    "title": f"{repo_name}: {query_name}",
                    "text": f"Found {count} matches",
                    "fields": [
                        {
                            "title": "Top Match",
                            "value": f"`{top_result['file']}:{top_result['line']}`",
                            "short": False
                        }
                    ]
                })
    
    send_slack_message(message, attachments)
    print(f"✅ Sent report to Slack: {len(attachments)} findings")

if __name__ == '__main__':
    if not SLACK_WEBHOOK:
        print("❌ Set SLACK_WEBHOOK_URL environment variable")
        exit(1)
    
    daily_audit()
```

**Usage:**

```bash
# Set webhook
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Run manually
python sem-slack-bot.py

# Or schedule with cron
crontab -e
# Add: 0 9 * * * cd /path/to/ai-supply-chain-poc && python sem-slack-bot.py
```

---

## Tips & Best Practices

### Writing Better Queries

#### ✅ Good Queries (Specific and Clear)

```bash
# Specific about what you're looking for
venv/bin/sem -p ~/app -n 50 'React functional components with hooks'

# Include context
venv/bin/sem -p ~/app -n 50 'authentication functions in user service'

# Describe behavior, not implementation
venv/bin/sem -p ~/app -n 50 'functions that validate email addresses'

# Use domain language
venv/bin/sem -p ~/app -n 50 'shopping cart checkout logic'
```

#### ❌ Bad Queries (Too Vague or Generic)

```bash
# Too generic
venv/bin/sem -p ~/app -n 50 'code'

# Too short
venv/bin/sem -p ~/app -n 50 'js'

# Implementation details instead of behavior
venv/bin/sem -p ~/app -n 50 'if statements'

# Single word (use exact search instead)
venv/bin/sem -p ~/app -n 50 'button'
```

### Performance Tips

```bash
# For large repos, generate embeddings once
venv/bin/sem --embed -p ~/large-project -b 64

# Use file extension filters for faster results
venv/bin/sem -p ~/large-project -x tsx -n 50 'your query'

# Reduce result count for faster responses
venv/bin/sem -p ~/large-project -n 10 'your query'
```

### Organization Tips

```bash
# Save common queries in a script
cat > ~/quick-search.sh << 'EOF'
#!/bin/bash
PROJECT="$1"
QUERY="$2"
venv/bin/sem -p "$PROJECT" -n 50 "$QUERY"
EOF

chmod +x ~/quick-search.sh

# Usage:
~/quick-search.sh ~/Projects/my-app "React components"
```

---

## Troubleshooting

### Issue: "Not a git repo"

```bash
# Make sure you're in a git repository
cd ~/Projects/my-app
git status

# Or specify full path
venv/bin/sem -p /full/path/to/git/repo 'your query'
```

### Issue: "Embeddings not found"

```bash
# Generate embeddings first
venv/bin/sem --embed -p ~/Projects/my-app

# Then search
venv/bin/sem -p ~/Projects/my-app 'your query'
```

### Issue: "MPS/GPU tensor error" (Apple Silicon)

```bash
# Delete old embeddings
rm ~/Projects/my-app/.embeddings

# Regenerate with CPU mode (handled automatically in our setup)
venv/bin/sem --embed -p ~/Projects/my-app
```

### Issue: "Can't run in Cursor terminal"

```bash
# sem requires an interactive terminal
# Run from Terminal.app or iTerm2 instead

# OR use sem-query.py which works in Cursor:
python sem-query.py -p ~/Projects/my-app 'your query'
```

### Issue: No results found

```bash
# Try broader query
venv/bin/sem -p ~/Projects/my-app -n 100 'function'

# Check what files were indexed
ls -lh ~/Projects/my-app/.embeddings

# Try regenerating embeddings
rm ~/Projects/my-app/.embeddings
venv/bin/sem --embed -p ~/Projects/my-app
```

### Issue: Too many irrelevant results

```bash
# Be more specific in your query
venv/bin/sem -p ~/app -n 20 'React button components with onClick handlers'

# Filter by file type
venv/bin/sem -p ~/app -x tsx -n 20 'button components'

# Reduce result count
venv/bin/sem -p ~/app -n 10 'your query'
```

---

## Command Reference

### Core Options

```
-p PATH               Path to git repository
-n N                  Number of results (default: 15)
-x EXT                File extension filter (py, js, tsx, etc.)
-e {vscode,vim}       Editor to open results in
-m MODEL              Model name or path
-d, --embed           Regenerate embeddings
-b BS                 Batch size for embedding generation
-c, --cluster         Find code duplication
```

### Cluster Mode Options

```
--cluster-max-distance     Similarity threshold (0-1, lower = stricter)
--cluster-min-lines        Minimum lines to consider
--cluster-min-cluster-size Minimum matches to report
```

---

## Quick Reference: Common Tasks

### Find all instances of a pattern
```bash
venv/bin/sem -p ~/app -n 100 'your pattern'
```

### Find in specific file type
```bash
venv/bin/sem -p ~/app -x tsx -n 50 'your query'
```

### Find and open in editor
```bash
venv/bin/sem -p ~/app -n 50 -e vscode 'your query'
```

### Find duplicated code
```bash
venv/bin/sem --cluster -p ~/app
```

### Export results
```bash
python sem-query.py -p ~/app -o results.txt 'your query'
```

### JSON for automation
```bash
python sem-query.py -p ~/app --json 'your query' | jq .
```

---

## Real Commands from History

*Actual commands used during development - proven patterns that work!*

### Small Sample Projects

```bash
# Finding specific function usage in the sample
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'usages of SortedSeverities function'

# Finding React patterns
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'React FC TypeScript function type instances'

# Finding array operations
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'array methods'

# Finding API calls
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'API requests'

# Finding AI usage
venv/bin/sem -p projects-samples/ai-ui -n 100 'gpt-4o-mini'
venv/bin/sem -p projects-samples/ai-ui -n 100 'openai'

# Finding SVG components
venv/bin/sem -p projects-samples/cnas-mfe -n 100 'svg'
```

### Real-World Project (OpenHands - 2,145 Files)

```bash
# First-time setup (5-10 minutes, one time only)
venv/bin/sem --embed -p projects-samples/OpenHands

# Check embedding status
ls -lh projects-samples/OpenHands/.embeddings

# LLM integration patterns
venv/bin/sem -p projects-samples/OpenHands -n 50 'LLM integration and API calls'
venv/bin/sem -p projects-samples/OpenHands -n 50 'OpenAI and Claude integration'
venv/bin/sem -p projects-samples/OpenHands -n 100 'AI model configuration'

# Frontend development
venv/bin/sem -p projects-samples/OpenHands -n 50 'React hooks usage'
venv/bin/sem -p projects-samples/OpenHands -n 100 'TypeScript React components'

# Backend APIs
venv/bin/sem -p projects-samples/OpenHands -n 50 'Flask API endpoints'
venv/bin/sem -p projects-samples/OpenHands -n 100 'WebSocket handlers'

# Authentication & Security
venv/bin/sem -p projects-samples/OpenHands -n 100 'authentication and authorization'
venv/bin/sem -p projects-samples/OpenHands -n 50 'JWT token handling'

# Performance test
time venv/bin/sem -p projects-samples/OpenHands -n 100 'error handling patterns'
# Shows instant results even with 2,145 files!
```

---

## Demo Script

Save as `demo-sem.sh`:

```bash
#!/bin/bash
# Semantic Code Search Demo

clear
echo "🔍 Semantic Code Search Demo"
echo "============================"
echo ""

CNAS_MFE="projects-samples/cnas-mfe"
AI_UI="projects-samples/ai-ui"

echo "📁 Sample projects ready for scanning"
echo ""

read -p "Press Enter to find React components..."
venv/bin/sem -p "$CNAS_MFE" -n 10 'react components'

echo ""
read -p "Press Enter to find OpenAI usage..."
venv/bin/sem -p "$AI_UI" -n 10 'openai usage'

echo ""
read -p "Press Enter to find array methods..."
venv/bin/sem -p "$CNAS_MFE" -n 10 'array methods'

echo ""
echo "✅ Demo complete!"
```

Run with:
```bash
bash demo-sem.sh
```

---

## Integration with Semgrep

Combine semantic search with static analysis for powerful code auditing:

```bash
#!/bin/bash
# Combined AI detection: Semantic + Static Analysis

CNAS_MFE="projects-samples/cnas-mfe"
AI_UI="projects-samples/ai-ui"

echo "🔍 Phase 1: Semantic Search (AI-powered)"
echo "========================================"
python sem-query.py -p "$AI_UI" --json 'openai and AI usage' > semantic_results.json

echo ""
echo "🔍 Phase 2: Static Analysis (Pattern-based)"
echo "==========================================="
semgrep scan --config p/shadow-ai-pro "$AI_UI" --json > semgrep_results.json

echo ""
echo "📊 Combined Results:"
echo "Semantic findings: $(jq '.findings | length' semantic_results.json)"
echo "Semgrep findings: $(jq '.results | length' semgrep_results.json)"
```

---

## Resources

- **Project README**: See `README.md` for installation details
- **Non-interactive script**: `sem-query.py` for automation
- **Semgrep examples**: `SEMGREP-EXAMPLES.md` for static analysis
- **Command examples**: `commands-examples.sh` for quick reference
- **GitHub**: [semantic-code-search](https://github.com/sturdy-dev/semantic-code-search)

---

**Last Updated:** 2026-01-11

**Pro Tip:** 💡 Semantic search works best when you describe *what* you want to find, not *how* it's implemented. Think "authentication logic" instead of "if password equals".

