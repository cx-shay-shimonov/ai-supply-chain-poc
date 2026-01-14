#!/bin/bash
# Demo and test script for sample projects

BASEDIR="/Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc"
cd "$BASEDIR"

echo "==============================================="
echo "🎯 Sample Projects Demo & Test Script"
echo "==============================================="
echo ""

# Show what we have
echo "📦 Sample Projects:"
echo "  1. ai-ui (OpenAI Integration - Node.js)"
echo "  2. cnas-mfe (CNAS MFE - React/TypeScript)"
echo "  3. OpenHands (AI Dev Platform - 2,145 files)"
echo ""

# Count files
AI_UI_FILES=$(find projects-samples/ai-ui -type f \( -name "*.js" -o -name "*.html" \) ! -path "*/node_modules/*" 2>/dev/null | wc -l | xargs)
CNAS_FILES=$(find projects-samples/cnas-mfe/src -type f \( -name "*.ts" -o -name "*.tsx" \) 2>/dev/null | wc -l | xargs)
OH_FILES=$(find projects-samples/OpenHands -type f \( -name "*.py" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" \) ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | wc -l | xargs)

echo "📊 Statistics:"
echo "  AI UI: $AI_UI_FILES source files"
echo "  CNAS MFE: $CNAS_FILES source files"
echo "  OpenHands: $OH_FILES source files"
echo ""

# Check if embeddings exist
echo "🔍 Checking embeddings..."
if [ -f "projects-samples/ai-ui/.embeddings" ]; then
  echo "  ✅ ai-ui embeddings exist"
else
  echo "  ⚠️  ai-ui needs embeddings (run: venv/bin/sem --embed -p projects-samples/ai-ui)"
fi

if [ -f "projects-samples/cnas-mfe/.embeddings" ]; then
  echo "  ✅ cnas-mfe embeddings exist"
else
  echo "  ⚠️  cnas-mfe needs embeddings (run: venv/bin/sem --embed -p projects-samples/cnas-mfe)"
fi

if [ -f "projects-samples/OpenHands/.embeddings" ]; then
  echo "  ✅ OpenHands embeddings exist"
else
  echo "  ⚠️  OpenHands needs embeddings (run: venv/bin/sem --embed -p projects-samples/OpenHands)"
  echo "     Note: OpenHands takes 5-10 minutes to generate embeddings"
fi

echo ""
echo "==============================================="
echo "🚀 Quick Tests"
echo "==============================================="
echo ""

# Test 1: Semantic search on ai-ui
echo "Test 1: Finding OpenAI usage in ai-ui..."
if [ -f "projects-samples/ai-ui/.embeddings" ]; then
  venv/bin/sem -p projects-samples/ai-ui -n 3 'OpenAI usage' 2>/dev/null | head -15
else
  echo "  ⚠️  Generate embeddings first!"
fi

echo ""

# Test 2: Semantic search on cnas-mfe
echo "Test 2: Finding SortedSeverities in cnas-mfe..."
if [ -f "projects-samples/cnas-mfe/.embeddings" ]; then
  venv/bin/sem -p projects-samples/cnas-mfe -n 3 'SortedSeverities function' 2>/dev/null | head -15
else
  echo "  ⚠️  Generate embeddings first!"
fi

echo ""

# Test 3: Semgrep scan
echo "Test 3: Semgrep scan for OpenAI in ai-ui..."
SEMGREP_COUNT=$(semgrep scan --config my-detect-openai.yaml projects-samples/ai-ui/ --json 2>/dev/null | jq '.results | length' 2>/dev/null || echo "0")
echo "  Found $SEMGREP_COUNT patterns"

echo ""

# Test 4: OpenHands large project test (if embeddings exist)
if [ -f "projects-samples/OpenHands/.embeddings" ]; then
  echo "Test 4: Finding LLM integration in OpenHands (2,145 files)..."
  venv/bin/sem -p projects-samples/OpenHands -n 3 'LLM integration' 2>/dev/null | head -15
  echo ""
else
  echo "Test 4: OpenHands embeddings not ready yet"
  echo "  (Run: venv/bin/sem --embed -p projects-samples/OpenHands)"
  echo ""
fi

echo "==============================================="
echo "✅ Tests Complete!"
echo "==============================================="
echo ""
echo "📚 Next steps:"
echo "  1. Generate embeddings if needed"
echo "  2. Try examples from SEM-EXAMPLES.md"
echo "  3. Try examples from SEMGREP-EXAMPLES.md"
echo "  4. Run: bash commands-examples.sh"
echo "  5. Try the non-interactive wrapper:"
echo "     venv/bin/python sem-query.py -p projects-samples/ai-ui --json -n 5 'OpenAI'"

