# AI Supply Chain POC - File Structure

## Overview
This repository demonstrates tools for detecting AI API and model usage in codebases using semantic search (`sem`) and static analysis (`semgrep`). The project is organized by tool for better maintainability.

---

## 📁 Root Structure

```
ai-supply-chain-poc/
├── sem/                        # Semantic search tool
│   ├── venv/                  # Python virtual environment
│   ├── scripts/               # Sem-specific scripts
│   ├── docs/                  # Sem documentation
│   ├── output/                # Sem tool outputs
│   └── sem-query.py           # Non-interactive wrapper
├── semgrep/                    # Static analysis tool
│   ├── rules/                 # YAML detection rules
│   ├── scripts/               # Semgrep-specific scripts
│   ├── docs/                  # Semgrep documentation
│   └── output/                # Semgrep outputs
├── xbom/                       # XBOM reports
│   └── reports/               # HTML reports
├── shared/                     # Shared Python utilities
│   ├── ai_asset_extractor.py
│   └── scan-model-variables.py
├── tools/                      # Combined tool scripts
│   ├── ai-usage-audit.sh
│   ├── test-samples.sh
│   ├── setup-and-demo.sh
│   └── output/                # Combined tool outputs
├── projects-samples/           # Sample projects for testing
│   ├── ai-ui/
│   ├── cnas-mfe/
│   ├── OpenHands/
│   └── README.md
├── README.md                   # Main documentation
├── FILE-STRUCTURE.md           # This file
├── READY_FOR_PUSH.md
├── COMMIT_MESSAGE.txt
└── .gitignore
```

---

## 📂 SEM Tool (`sem/`)

**Semantic code search using machine learning embeddings**

### Scripts (`sem/scripts/`)

| File | Description |
|------|-------------|
| `sem-audit.sh` | **Semantic-only audit** - Runs semantic search, extracts AI assets |
| `search-ai-comprehensive.sh` | **Multi-query search** - 6 focused queries for comprehensive AI detection |
| `search-ai-models.sh` | **Model search** - Searches for specific AI model names |
| `test.sh` | **Quick test** - Fast semantic search test on ai-ui project |
| `commands-examples.sh` | **Usage examples** - Working examples for sem and semgrep |
| `raw-sem-query.sh` | **Raw query** - Direct sem query for model names |

### Python Files

| File | Description |
|------|-------------|
| `sem-query.py` | **Non-interactive wrapper** - Enables automation, JSON output, token highlighting |

### Documentation (`sem/docs/`)

| File | Description |
|------|-------------|
| `SEM-EXAMPLES.md` | Comprehensive guide with real-world queries |
| `SEM-QUERY-ENHANCEMENTS.md` | Details on enhanced JSON output features |
| `IMPROVED-QUERY-GUIDE.md` | Multi-query strategy guide |

### Virtual Environment (`sem/venv/`)

**Key packages:**
- `semantic-code-search` - Semantic search tool
- `sentence-transformers` - ML models for code embeddings
- `torch` - ML framework
- `tree-sitter` - Code parsing

**Modified file:** `venv/lib/python3.11/site-packages/semantic_code_search/embed.py` - Added arrow_function support

---

## 📂 Semgrep Tool (`semgrep/`)

**Static analysis for pattern-based detection**

### Rules (`semgrep/rules/`)

| File | Description |
|------|-------------|
| `my-detect-openai.yaml` | Custom rules for OpenAI and AI API detection |
| `shadow-ai-extended.yaml` | Extended ruleset for comprehensive AI detection |

### Scripts (`semgrep/scripts/`)

| File | Description |
|------|-------------|
| `extract-ai-assets.sh` | Standalone asset extraction from semgrep results |

### Documentation (`semgrep/docs/`)

| File | Description |
|------|-------------|
| `SEMGREP-EXAMPLES.md` | Usage guide, detection strategies, output formats |

---

## 📂 XBOM (`xbom/`)

**eXtended Bill of Materials reports**

### Reports (`xbom/reports/`)

| File | Description |
|------|-------------|
| `xbom-report.html` | General XBOM report |
| `ai-ui-xbom-report.html` | AI UI project XBOM report |

---

## 📂 Shared Utilities (`shared/`)

**Python modules used by multiple tools**

| File | Description |
|------|-------------|
| `ai_asset_extractor.py` | Extracts AI models and providers from search results (OpenAI, Anthropic, Google, Meta, Cohere, Mistral) |
| `scan-model-variables.py` | Detects AI models constructed by concatenating string parts |

---

## 📂 Combined Tools (`tools/`)

**Scripts that use both sem and semgrep**

| File | Description |
|------|-------------|
| `ai-usage-audit.sh` | **Main audit script** - Runs both semantic search and semgrep, generates CSV comparison |
| `test-samples.sh` | **Validation script** - Tests setup with file counts and embedding status |
| `setup-and-demo.sh` | **Interactive setup** - Guided setup for dependencies and demos |

---

## 📂 Sample Projects (`projects-samples/`)

**Real-world codebases for testing**

Contains projects cloned separately (excluded from git):

| Project | Description |
|---------|-------------|
| `ai-ui/` | Node.js app with OpenAI integration |
| `cnas-mfe/` | React/TypeScript micro-frontend |
| `OpenHands/` | Large AI development platform (2,145 files) |

**Clone Commands:**
```bash
cd projects-samples
git clone https://github.com/shayshimonov/ai-ui.git
git clone https://github.com/All-Hands-AI/OpenHands.git
```

---

## 🎯 Key Workflows

### Full Combined Audit
```bash
bash tools/ai-usage-audit.sh projects-samples/OpenHands 500
# → Creates tools/output/YYYYMMDD_HHMMSS/ with results
```

### Semantic-Only Audit
```bash
bash sem/scripts/sem-audit.sh projects-samples/ai-ui 100
# → Creates sem/output/sem-audit-ai-ui-YYYYMMDD_HHMMSS/
```

### Comprehensive Search
```bash
bash sem/scripts/search-ai-comprehensive.sh projects-samples/OpenHands 200
# → Creates sem/output/ai-comprehensive-OpenHands-YYYYMMDD_HHMMSS/
```

### Quick Test
```bash
bash sem/scripts/test.sh
# → Creates sem/output/sem-test/YYYYMMDD_HHMMSS/
```

### Direct Semantic Search
```bash
python sem/sem-query.py -p projects-samples/ai-ui -n 10 'OpenAI usage'
# → Prints results to terminal
```

---

## 📝 File Relationships

```
Combined Tools:
  tools/ai-usage-audit.sh
    ├── Uses: sem/venv/bin/python + sem/sem-query.py
    ├── Uses: shared/ai_asset_extractor.py
    ├── Uses: shared/scan-model-variables.py
    ├── Uses: semgrep + semgrep/rules/*.yaml
    └── Creates: tools/output/YYYYMMDD_HHMMSS/*

  tools/setup-and-demo.sh
    ├── Uses: sem/venv/bin/sem
    └── Guides: Setup and demo workflows

Sem Tool:
  sem/scripts/sem-audit.sh
    ├── Uses: sem/venv/bin/python + sem/sem-query.py
    ├── Uses: shared/ai_asset_extractor.py
    ├── Uses: shared/scan-model-variables.py
    └── Creates: sem/output/sem-audit-PROJECT-YYYYMMDD_HHMMSS/*

  sem/scripts/search-ai-comprehensive.sh
    ├── Uses: sem/venv/bin/python + sem/sem-query.py
    ├── Uses: shared/ai_asset_extractor.py
    ├── Uses: shared/scan-model-variables.py
    └── Creates: sem/output/ai-comprehensive-PROJECT-YYYYMMDD_HHMMSS/*

  sem/sem-query.py
    ├── Uses: sem/venv/lib/.../semantic_code_search
    ├── Reads: projects-samples/*/.embeddings
    └── Enhanced with: certainty, match_reason, highlighted_tokens

Shared Utilities:
  shared/ai_asset_extractor.py
    ├── Called by: All audit scripts
    └── Extracts: AI models and providers from JSON results

  shared/scan-model-variables.py
    ├── Called by: Audit scripts
    └── Detects: Concatenated model names in source code
```

---

## 🚀 Getting Started

1. **Setup environment:**
   ```bash
   cd /path/to/ai-supply-chain-poc
   python3 -m venv sem/venv
   sem/venv/bin/pip install semantic-code-search semgrep
   ```

2. **Clone sample projects:**
   ```bash
   cd projects-samples
   git clone https://github.com/shayshimonov/ai-ui.git
   git clone https://github.com/All-Hands-AI/OpenHands.git
   ```

3. **Run a test:**
   ```bash
   bash sem/scripts/test.sh
   ```

4. **Run full audit:**
   ```bash
   bash tools/ai-usage-audit.sh projects-samples/ai-ui 50
   ```

---

## 📚 More Information

- See `README.md` for detailed setup and usage
- See `sem/docs/SEM-EXAMPLES.md` for semantic search examples
- See `semgrep/docs/SEMGREP-EXAMPLES.md` for static analysis examples
- See `projects-samples/README.md` for sample project details
