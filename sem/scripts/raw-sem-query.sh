#!/bin/bash
BASEDIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

"$SCRIPT_DIR/../venv/bin/sem" -p "$BASEDIR/projects-samples/ai-ui" -n 50 'usages of gpt-5, gpt-5-latest, gpt-5-2025-11-04, gpt-5-pro, gpt-5-mini, gpt-5-nano, o4-mini, o3-high, gpt-4.1-mini, gpt-4o, gpt-oss-120b, claude-opus-4-5-latest, claude-opus-4-5-20251101, claude-sonnet-4-5-latest, claude-sonnet-4-5-20250929, claude-haiku-4-5, claude-3-5-haiku-latest, claude-code-2-1, gemini-3-pro, gemini-3-flash, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-live-2.5-flash-native-audio, deepseek-v4, deepseek-v3.2, deepseek-reasoner, deepseek-chat, llama-3.3-70b-instruct, llama-3.1-405b-instruct, llama-4-preview-70b, mistral-large-2511, mistral-nemo-latest, pixtral-large-latest, codestral-latest, grok-4-fast-reasoning, grok-code-fast-1, glm-4.7-thinking, qwen3-72b-instruct, mimo-v2-flash'
