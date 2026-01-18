#!/bin/bash
# Search for AI model usage in ai-ui project
# This script searches for references to various AI models including:
# - GPT models (gpt-5, gpt-4.1, gpt-4o variants)
# - Claude models (opus, sonnet, haiku variants)
# - Gemini models (2.5, 3 variants)
# - DeepSeek models
# - Llama models
# - Mistral, Grok, and other AI models

cd /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc

# Check if embeddings exist
if [ ! -f "projects-samples/ai-ui/.embeddings" ]; then
    echo "⚠️  No embeddings found. Generating..."
    venv/bin/sem --embed -p projects-samples/ai-ui
    echo ""
fi

# Run semantic search for AI model references (interactive mode)
echo "🔍 Searching for AI model references in ai-ui..."
echo ""

venv/bin/sem -p projects-samples/ai-ui -n 50 'usages of gpt-5, gpt-5-latest, gpt-5-2025-11-04, gpt-5-pro, gpt-5-mini, gpt-5-nano, o4-mini, o3-high, gpt-4.1-mini, gpt-4o, gpt-oss-120b, claude-opus-4-5-latest, claude-opus-4-5-20251101, claude-sonnet-4-5-latest, claude-sonnet-4-5-20250929, claude-haiku-4-5, claude-3-5-haiku-latest, claude-code-2-1, gemini-3-pro, gemini-3-flash, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-live-2.5-flash-native-audio, deepseek-v4, deepseek-v3.2, deepseek-reasoner, deepseek-chat, llama-3.3-70b-instruct, llama-3.1-405b-instruct, llama-4-preview-70b, mistral-large-2511, mistral-nemo-latest, pixtral-large-latest, codestral-latest, grok-4-fast-reasoning, grok-code-fast-1, glm-4.7-thinking, qwen3-72b-instruct, mimo-v2-flash'

echo ""
echo "✅ Search complete!"
