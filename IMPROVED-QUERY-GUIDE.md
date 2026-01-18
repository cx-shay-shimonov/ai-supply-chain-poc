# Improved Semantic Search Queries for AI Model Usage

This document explains how to write better semantic search queries to find comprehensive AI usage patterns.

## Problem with Your Original Query

```bash
"usages of gpt-5, gpt-5-latest, gpt-5-2025-11-04, gpt-5-pro, gpt-5-mini, ..."
```

**Issues:**
1. Lists 40+ specific model names - semantic search treats this as noise
2. Misses variable assignments: `model = "gpt-4o"`
3. Misses function parameters: `def call_llm(model_name: str)`
4. Misses configuration objects: `config.model = user_selected_model`
5. Not natural language - semantic search works better with descriptions

## Better Approach: 6 Focused Queries

### Query 1: Model String Literals & Assignments
**Goal**: Find where model names are assigned to variables

```bash
'AI language model name strings assigned to variables like model equals gpt-4 claude gemini deepseek llama mistral'
```

**Finds:**
```python
model = "gpt-4o"
MODEL_NAME = "claude-3-5-sonnet"
config['model'] = "gemini-pro"
```

### Query 2: Configuration & Initialization
**Goal**: Find LLM configuration setup

```bash
'LLMConfig model configuration initialization setup with model name parameter temperature'
```

**Finds:**
```python
llm_config = LLMConfig(
    model="gpt-4o",
    temperature=0.7
)

config = {
    "model": "claude-3-sonnet",
    "max_tokens": 4096
}
```

### Query 3: API Calls with Model Parameter
**Goal**: Find actual LLM API invocations

```bash
'chat completions create API call with model parameter streaming messages'
```

**Finds:**
```python
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...]
)

completion = openai.ChatCompletion.create(
    model=model_name,
    stream=True
)
```

### Query 4: Function Parameters & Usage
**Goal**: Find functions that receive/use model names

```bash
'function definition with model parameter passed to LLM client inference call'
```

**Finds:**
```python
def generate_response(model: str, prompt: str):
    return llm.complete(model=model, prompt=prompt)

async def call_ai(model_name: str) -> str:
    response = await client.chat(model=model_name)
```

### Query 5: Environment Variables & Dynamic Selection
**Goal**: Find runtime model selection

```bash
'environment variable for AI model name OPENAI_MODEL getenv model selection logic'
```

**Finds:**
```python
model = os.getenv('OPENAI_MODEL', 'gpt-4o')
selected_model = config.get('model') or DEFAULT_MODEL

if use_gpt4:
    model = "gpt-4-turbo"
else:
    model = "gpt-3.5-turbo"
```

### Query 6: Validation Lists & Constants
**Goal**: Find allowed model lists and validation

```bash
'list array of supported AI model names validation check allowed models'
```

**Finds:**
```python
SUPPORTED_MODELS = [
    "gpt-4o",
    "gpt-4-turbo",
    "claude-3-5-sonnet"
]

ALLOWED_MODELS = {
    "openai": ["gpt-4o", "gpt-4-turbo"],
    "anthropic": ["claude-3-sonnet"]
}

if model not in VALID_MODELS:
    raise ValueError()
```

## Why This Works Better

### 1. Natural Language Descriptions
Semantic search understands **concepts** better than exact strings:
- ❌ "gpt-4o, gpt-4-turbo, gpt-4.1" (too specific)
- ✅ "AI language model name" (conceptual)

### 2. Focuses on Usage Patterns
Each query targets a specific **pattern of usage**:
- String literals
- Configuration
- API calls
- Function parameters
- Dynamic selection
- Validation

### 3. Captures Variable Flow
Finds the entire chain:
```python
# Query 5 finds this
model_name = os.getenv('OPENAI_MODEL')

# Query 4 finds this
def setup_llm(model: str):
    # Query 2 finds this
    config = LLMConfig(model=model)
    # Query 3 finds this
    return client.chat.completions.create(model=config.model)
```

## Usage Examples

### Run on OpenHands project
```bash
./search-ai-comprehensive.sh projects-samples/OpenHands 200
```

### Run on ai-ui project
```bash
./search-ai-comprehensive.sh projects-samples/ai-ui 50
```

### Custom single query
```bash
venv/bin/python sem-query.py -p projects-samples/OpenHands -n 50 --json \
  'functions that call OpenAI Anthropic or Google AI with model parameter'
```

## Expected Results

The comprehensive search will find:

1. **Direct Usage**: `client.chat(model="gpt-4o")`
2. **Variable Assignment**: `model = "claude-3-sonnet"`
3. **Configuration**: `config.model = selected_model`
4. **Function Parameters**: `def call_llm(model_name: str)`
5. **Constants**: `DEFAULT_MODEL = "gpt-4o"`
6. **Validation**: `if model in ALLOWED_MODELS`
7. **Environment**: `os.getenv('OPENAI_MODEL')`
8. **Type Hints**: `model: Literal["gpt-4o", "claude-3"]`

## Tips for Writing Good Queries

### ✅ DO:
- Use natural language descriptions
- Focus on **what the code does** not exact names
- Describe the **pattern** you're looking for
- Target one concept per query

### ❌ DON'T:
- List dozens of specific strings
- Use exact code syntax
- Try to catch everything in one query
- Use overly generic terms

## Query Templates

### Finding Model Assignments
```
'[AI provider] model name assigned to variable or constant'
```

### Finding API Calls
```
'[provider] API call with model parameter [operation]'
```

### Finding Configuration
```
'configuration object with [field] parameter for [purpose]'
```

### Finding Function Usage
```
'function [action] that receives [parameter] and [uses it for]'
```

### Finding Validation
```
'validation logic checking [parameter] against list of allowed values'
```

## Combine with Static Analysis

For best results, combine semantic search with Semgrep:

```bash
# Semantic search finds conceptual usage
./search-ai-comprehensive.sh projects-samples/OpenHands 200

# Semgrep finds exact patterns
semgrep scan --config p/shadow-ai-pro --config my-detect-openai.yaml projects-samples/OpenHands
```

Semantic search is great for:
- Understanding context
- Finding usage patterns
- Discovering related code
- Tracing variable flow

Semgrep is great for:
- Exact string matches
- Import statements
- Specific API patterns
- Security vulnerabilities
