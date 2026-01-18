#!/bin/bash
BASEDIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Create test output directory
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
TEST_OUTPUT="$SCRIPT_DIR/../output/sem-test/$TIMESTAMP"
mkdir -p "$TEST_OUTPUT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  🧪 Test: Semantic Search                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Target: projects-samples/ai-ui"
echo "🔍 Query: 'OpenAI gpt usage'"
echo "📂 Output: $TEST_OUTPUT/"
echo ""

# Check if embeddings exist
if [ ! -f "$BASEDIR/projects-samples/ai-ui/.embeddings" ]; then
    echo "⚠️  No embeddings found. Generating..."
    "$SCRIPT_DIR/../venv/bin/sem" --embed -p "$BASEDIR/projects-samples/ai-ui"
    echo ""
fi

# Run semantic search and save to JSON
echo "Running semantic search..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$BASEDIR/projects-samples/ai-ui" --json -n 10 'OpenAI gpt usage' > "$TEST_OUTPUT/search_results.json" 2>/dev/null

# Check if successful
if [ $? -eq 0 ] && [ -s "$TEST_OUTPUT/search_results.json" ]; then
    echo "✅ Search complete!"
    
    # Display summary
    RESULT_COUNT=$(jq '.results | length' "$TEST_OUTPUT/search_results.json" 2>/dev/null)
    echo ""
    echo "📊 Results: $RESULT_COUNT findings"
    
    # Show top 3 results
    echo ""
    echo "🔍 Top 3 Results:"
    jq -r '.results[0:3] | .[] | "  [Score: \(.score | tostring | .[0:6])] \(.file | split("/") | last):\(.line)"' "$TEST_OUTPUT/search_results.json" 2>/dev/null
    
    # Create a text summary
    echo ""
    echo "Creating text summary..."
    "$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$BASEDIR/projects-samples/ai-ui" -n 10 'OpenAI gpt usage' > "$TEST_OUTPUT/search_results.txt" 2>/dev/null
    
    echo "✅ Summary created!"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "💾 Files Created:"
    echo "   • $TEST_OUTPUT/search_results.json"
    echo "   • $TEST_OUTPUT/search_results.txt"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "📖 View results:"
    echo "   cat $TEST_OUTPUT/search_results.txt"
    echo "   jq . $TEST_OUTPUT/search_results.json"
else
    echo "❌ Search failed or returned no results"
    exit 1
fi