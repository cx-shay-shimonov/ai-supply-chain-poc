# Semantic Code Search POC

A proof of concept using [semantic-code-search](https://github.com/sturdy-dev/semantic-code-search) - a CLI tool that lets you search your codebase using natural language queries.

## Installation

### Prerequisites

- macOS (ARM64/Apple Silicon)
- Homebrew

### Step-by-Step Installation

The `semantic-code-search` package has strict version dependencies that conflict with Python 3.13 and ARM64 Macs. Here's how we resolved it:

#### 1. Install Python 3.11 via Homebrew

```bash
brew install python@3.11
```

#### 2. Create a Virtual Environment with Python 3.11

```bash
cd /path/to/this/project
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
```

#### 3. Upgrade pip and Install Build Tools

```bash
pip install --upgrade pip setuptools wheel
```

#### 4. Install Dependencies with Compatible Versions

The package requires specific old versions that don't work on ARM64 Macs. We install newer compatible versions first:

```bash
pip install torch numpy sentence-transformers prompt-toolkit pygments tree-sitter tree-sitter-languages
```

#### 5. Install semantic-code-search Without Dependency Checks

```bash
pip install --no-deps semantic-code-search
```

## Usage

### Quick Setup (Recommended)

Add an alias to your `~/.zshrc` so you can run `sem` from anywhere:

```bash
echo "alias sem='/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/venv/bin/sem'" >> ~/.zshrc
source ~/.zshrc
```

### Alternative: Activate the Virtual Environment

```bash
source /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/venv/bin/activate
```

### Basic Search

Run a natural language search in any git repository:

```bash
sem 'your search query'
```

**Note:** You must be inside a git repository or specify one with the `-p` flag.

### Examples

```bash
# Search for authentication logic
sem 'Where is user authentication handled?'

# Search for database operations
sem 'Saving data to the database'

# Search for API endpoints
sem 'REST API request handling'

# Search for error handling patterns
sem 'How are exceptions caught and logged?'
```

### Command Line Options

```
sem [-h] [-p PATH] [-m MODEL] [-d] [-b BS] [-x EXT] [-n N] [-e {vscode,vim}] [-c] [query]

Options:
  -h, --help            Show help message
  -p PATH               Path to the git repo to search
  -m MODEL              Name or path of the model to use
  -d, --embed           (Re)create the embeddings index
  -b BS                 Batch size for embeddings generation
  -x EXT                File extension filter (e.g., "py", "js")
  -n N                  Number of results to return
  -e {vscode,vim}       Editor to open selected result in
  -c, --cluster         Find semantically similar code clusters (text output)
```

### Non-Interactive Query Mode (sem-query.py)

For search queries without an interactive terminal, use the included `sem-query.py` script:

```bash
# Basic usage
python sem-query.py -p /path/to/repo 'your search query'

# Save results to file
python sem-query.py -p /path/to/repo -o results.txt 'your query'

# JSON output
python sem-query.py -p /path/to/repo --json 'your query'

# Filter by file extension
python sem-query.py -p /path/to/repo -x tsx 'react components'

# More results
python sem-query.py -p /path/to/repo -n 10 'your query'
```

Options:
- `-p PATH` - Path to the git repository
- `-n N` - Number of results (default: 5)
- `-o FILE` - Save output to file
- `-x EXT` - Filter by file extension
- `--json` - Output as JSON
- `--no-code` - Hide code snippets

### Cluster Mode (Text Output)

The `--cluster` mode outputs results as plain text to the terminal. It finds duplicate/similar code patterns:

```bash
sem --cluster -p /path/to/repo
```

Options for cluster mode:
- `--cluster-max-distance 0.3` - How close code needs to be (0 = identical, lower = stricter)
- `--cluster-min-lines 5` - Ignore small snippets
- `--cluster-min-cluster-size 3` - Only show clusters with 3+ matches

**Note:** Cluster mode does NOT support search queries - it analyzes all code for similarity.

### First Run

On the first search of a codebase:

1. The ML model will be downloaded (~500 MB) - this happens only once
2. Code embeddings will be generated and cached in a `.embeddings` file
3. Subsequent searches will be fast

### Navigating Results

- Use `↑` `↓` arrow keys or vim bindings to navigate
- Press `Return` to open the selected file in your editor
- Use `-e vscode` or `-e vim` to specify your editor

## Supported Languages

- Python
- JavaScript
- TypeScript
- Ruby
- Go
- Rust
- Java
- C / C++
- Kotlin

## Troubleshooting

### MPS/GPU Tensor Error on Apple Silicon

If you see this error:
```
TypeError: can't convert mps:0 device type tensor to numpy
```

You need to regenerate embeddings with CPU mode. Run this in Python:

```python
import os
os.environ['PYTORCH_MPS_DISABLE'] = '1'
import torch
torch.set_default_device('cpu')

from sentence_transformers import SentenceTransformer
from semantic_code_search.embed import do_embed
import argparse

args = argparse.Namespace(
    path_to_repo='/path/to/your/repo',
    model_name_or_path='krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net',
    batch_size=32
)
model = SentenceTransformer(args.model_name_or_path, device='cpu')
do_embed(args, model)
```

Or delete the `.embeddings` file and regenerate.

### Must Run in Interactive Terminal

The `sem` command requires an **interactive terminal** to display results. It will **NOT work** in:
- Cursor's built-in terminal (sandboxed)
- Non-interactive shells
- CI/CD pipelines

**Solution:** Run `sem` from Terminal.app, iTerm2, or another real terminal emulator.

### "Not a git repo" Error

Make sure you're inside a git repository or specify the path:

```bash
sem -p /path/to/git/repo 'your query'
```

### Re-generate Embeddings

If files have changed and you want to refresh the embeddings:

```bash
sem --embed
```

## License

semantic-code-search is distributed under AGPL-3.0-only.
