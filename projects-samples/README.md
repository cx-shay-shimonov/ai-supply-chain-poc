# Sample Projects for Demos

This folder contains real projects for demonstrating semantic code search and static analysis tools.

> **Note:** Sample projects are excluded from git. You need to clone them manually.

## 🚀 Setup: Clone Sample Projects

Before running demos, clone the sample projects:

```bash
# Navigate to projects-samples folder
cd projects-samples

# Clone ai-ui (small project with OpenAI integration)
git clone https://github.com/shayshimonov/ai-ui.git

# Clone OpenHands (large AI development platform)
git clone https://github.com/All-Hands-AI/OpenHands.git
```

### Optional: Clone additional projects

```bash
# Clone cnas-mfe (micro-frontend project)
git clone https://github.com/shayshimonov/cnas-mfe.git
```

## Projects

### 1. ai-ui/
Your AI UI project with OpenAI integration

**What it is:**
- Node.js application with OpenAI API integration
- Real implementation of gpt-4o-mini usage
- Frontend with HTML/CSS/JavaScript

**Use Cases:**
- Shadow AI detection demonstrations
- OpenAI API pattern detection
- Model usage tracking
- Real-world AI integration examples

**Clone:**
```bash
git clone https://github.com/shayshimonov/ai-ui.git
```

---

### 2. OpenHands/
AI-Driven Development platform - Open source project

**Stats:**
- 2,145+ source files (Python, TypeScript, JavaScript)
- 308 MB codebase
- Active open-source project
- Full-stack application (backend + frontend)

**What it is:**
OpenHands is an AI-powered development platform that uses LLMs to assist with software engineering tasks. Perfect for demonstrating semantic search on a large, real-world codebase.

**Use Cases:**
- Large-scale semantic search
- Finding patterns in real codebases
- AI integration in production apps
- Complex architecture exploration
- Performance testing with realistic data

**Clone:**
```bash
git clone https://github.com/All-Hands-AI/OpenHands.git
```

---

### 3. cnas-mfe/ (Optional)
Your CNAS Micro-Frontend project

**What it is:**
- React/TypeScript micro-frontend application
- Real production codebase with 300+ files
- Contains `SortedSeverities` function and utilities
- Complex React patterns and components

**Use Cases:**
- React component search
- TypeScript type exploration  
- Function usage tracking (SortedSeverities)
- Array methods and utilities
- Real-world MFE patterns

**Clone:**
```bash
git clone https://github.com/shayshimonov/cnas-mfe.git
```

---

## Quick Start

### 1. Clone Projects

```bash
cd projects-samples
git clone https://github.com/shayshimonov/ai-ui.git
git clone https://github.com/All-Hands-AI/OpenHands.git
```

### 2. Generate Embeddings

```bash
# Navigate to ai-supply-chain-poc directory
cd ..

# AI UI project (small - ~1 minute)
venv/bin/sem --embed -p projects-samples/ai-ui

# OpenHands (large - 5-10 minutes for 2,145 files)
venv/bin/sem --embed -p projects-samples/OpenHands
```

### 3. Run Semantic Search

```bash
# AI UI project
venv/bin/sem -p projects-samples/ai-ui -n 20 'OpenAI and gpt-4o-mini usage'
venv/bin/sem -p projects-samples/ai-ui -n 20 'API endpoints'

# OpenHands (large project)
venv/bin/sem -p projects-samples/OpenHands -n 50 'LLM integration'
venv/bin/sem -p projects-samples/OpenHands -n 50 'React components'
venv/bin/sem -p projects-samples/OpenHands -n 100 'authentication'
```

### 4. Run Semgrep

```bash
# Scan AI UI for Shadow AI
semgrep scan --config p/shadow-ai-pro --config ../my-detect-openai.yaml ai-ui

# Scan OpenHands (large project)
semgrep scan --config p/shadow-ai-pro OpenHands
semgrep scan --config p/python OpenHands
```

### 5. Run Full Audit

```bash
# From ai-supply-chain-poc directory
cd ..

# Audit ai-ui
bash ai-usage-audit.sh projects-samples/ai-ui 50

# Audit OpenHands (use higher limit for large project)
bash ai-usage-audit.sh projects-samples/OpenHands 500
```

---

## Folder Structure After Setup

```
projects-samples/
├── README.md          ← You are here
├── ai-ui/             ← Clone from GitHub
│   ├── server.js
│   ├── script.js
│   ├── styles.css
│   └── ...
├── OpenHands/         ← Clone from GitHub
│   ├── openhands/
│   ├── frontend/
│   ├── evaluation/
│   └── ...
└── cnas-mfe/          ← Optional clone
    ├── src/
    ├── package.json
    └── ...
```

---

## Demo Scenarios

All examples in `SEM-EXAMPLES.md` and `SEMGREP-EXAMPLES.md` use these sample projects.

## Troubleshooting

### No embeddings found
```bash
# Generate embeddings first
venv/bin/sem --embed -p projects-samples/<project-name>
```

### Project folder is empty
```bash
# Clone the project
cd projects-samples
git clone <repository-url>
```

### Permission denied
```bash
# Make sure you're in the right directory
cd /path/to/ai-supply-chain-poc/projects-samples
```
