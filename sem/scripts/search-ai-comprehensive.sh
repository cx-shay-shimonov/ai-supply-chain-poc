#!/bin/bash
# Comprehensive AI Model Usage Search
# Finds: model assignments, variable usage, function calls, configurations

BASEDIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

TARGET="${1:-$BASEDIR/projects-samples/OpenHands}"
LIMIT="${2:-200}"

# Extract project name from target path
PROJECT_NAME=$(basename "$TARGET")
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_DIR="$SCRIPT_DIR/../output/ai-comprehensive-${PROJECT_NAME}-${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "🔍 Comprehensive AI Model Usage Search"
echo "Target: $TARGET"
echo "Output: $OUTPUT_DIR"
echo ""

# Check/generate embeddings
if [ ! -f "$TARGET/.embeddings" ]; then
    echo "⚠️  No embeddings found. Generating..."
    PYTORCH_MPS_DISABLE=1 "$SCRIPT_DIR/../venv/bin/sem" --embed -p "$TARGET"
    echo ""
fi

echo "Running 6 focused semantic queries..."
echo ""

# Query 1: Model string literals and assignments
echo "  🔍 Query 1: Model name string literals and variable assignments..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$TARGET" --json -n "$((LIMIT/6))" \
    'AI language model name strings assigned to variables like model equals gpt-4 claude gemini deepseek llama mistral' \
    2>/dev/null > "$OUTPUT_DIR/q1_model_strings.json"

# Query 2: Model configuration and initialization
echo "  🔍 Query 2: LLM configuration objects and model initialization..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$TARGET" --json -n "$((LIMIT/6))" \
    'LLMConfig model configuration initialization setup with model name parameter temperature' \
    2>/dev/null > "$OUTPUT_DIR/q2_config.json"

# Query 3: API calls with model parameter
echo "  🔍 Query 3: LLM API calls with model parameter..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$TARGET" --json -n "$((LIMIT/6))" \
    'chat completions create API call with model parameter streaming messages' \
    2>/dev/null > "$OUTPUT_DIR/q3_api_calls.json"

# Query 4: Model parameter passing and function calls
echo "  🔍 Query 4: Functions receiving model parameter and usage..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$TARGET" --json -n "$((LIMIT/6))" \
    'function definition with model parameter passed to LLM client inference call' \
    2>/dev/null > "$OUTPUT_DIR/q4_function_params.json"

# Query 5: Environment variables and model selection
echo "  🔍 Query 5: Environment variables and dynamic model selection..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$TARGET" --json -n "$((LIMIT/6))" \
    'environment variable for AI model name OPENAI_MODEL getenv model selection logic' \
    2>/dev/null > "$OUTPUT_DIR/q5_env_vars.json"

# Query 6: Model validation and constants
echo "  🔍 Query 6: Model name validation lists and constants..."
"$SCRIPT_DIR/../venv/bin/python" "$SCRIPT_DIR/../sem-query.py" -p "$TARGET" --json -n "$((LIMIT/6))" \
    'list array of supported AI model names validation check allowed models' \
    2>/dev/null > "$OUTPUT_DIR/q6_validation.json"

echo ""
echo "  🔄 Merging and deduplicating results..."

# Merge all queries, deduplicate, and sort by score
jq -s '
    {
        query: "Comprehensive AI model usage scan (6 queries)",
        repository: (.[0].repository // ""),
        queries: [
            "Model string literals and assignments",
            "Configuration and initialization", 
            "API calls with model parameter",
            "Function parameters and usage",
            "Environment variables",
            "Model validation and constants"
        ],
        results: ([.[].results[]] | 
                  group_by(.file + ":" + (.line | tostring)) | 
                  map(max_by(.score)) |
                  sort_by(-.score) |
                  .[0:'$LIMIT'] |
                  to_entries |
                  map(.value + {rank: (.key + 1)}))
    }
' "$OUTPUT_DIR"/q*.json > "$OUTPUT_DIR/comprehensive_results.json"

# Clean up individual query files
# rm -f "$OUTPUT_DIR"/q*.json

# Count results
TOTAL=$(jq '.results | length' "$OUTPUT_DIR/comprehensive_results.json" 2>/dev/null || echo "0")

echo ""
echo "✅ Search Complete!"
echo "   Total unique findings: $TOTAL"
echo ""

# Show top 10 results with context
if [ "$TOTAL" -gt 0 ]; then
    echo "📊 Top 10 Results:"
    echo ""
    jq -r '.results[0:10] | .[] | 
        "  \(.rank). 📄 \(.file):\(.line):\(.column)\n" +
        "     🎯 Certainty: \(.certainty | ascii_upcase) (\(.certainty_percent)%)\n" +
        "     💡 Match: \(.match_reason)\n" +
        "     🔍 Matched: \(.matched_tokens | join(", "))\n" +
        (if (.highlighted_tokens | length) > 0 then
            "     ✨ Highlighted: \(.highlighted_tokens | join(", "))\n"
         else "" end) +
        "     📝 Preview: \(.code | split("\n") | first | .[0:80])\n"
    ' "$OUTPUT_DIR/comprehensive_results.json"
    
    echo ""
    echo "📂 Full results saved to: $OUTPUT_DIR/comprehensive_results.json"
    
    # Generate summary by file
    echo ""
    echo "📊 Findings by File (top 10):"
    jq -r '.results | group_by(.file) | 
           map({file: .[0].file, count: length, avg_certainty: (map(.certainty_percent) | add / length)}) |
           sort_by(-.count) |
           .[0:10] |
           .[] | 
           "  • \(.file | split("/") | .[-2:] | join("/")): \(.count) findings (avg \(.avg_certainty | floor)%)"
    ' "$OUTPUT_DIR/comprehensive_results.json"
    
    # Extract all AI providers and models found
    echo ""
    echo "🤖 Extracting AI providers and models..."
    python3 "$BASEDIR/shared/ai_asset_extractor.py" semantic "$OUTPUT_DIR/comprehensive_results.json" > "$OUTPUT_DIR/ai_assets.json"
    
    # Also scan for variable-based model concatenations
    echo "🔍 Scanning for concatenated model variables..."
    "$SCRIPT_DIR/../venv/bin/python" "$BASEDIR/shared/scan-model-variables.py" "$TARGET" > "$OUTPUT_DIR/variable_models.json"
    
    # Extract models found via variable scanning
    VARIABLE_MODELS=$(jq -r '.variable_models[].model' "$OUTPUT_DIR/variable_models.json" 2>/dev/null | sort -u)
    
    echo ""
    echo "📈 AI Assets Found in Code:"
    
    # Show variable-constructed models first if found
    if [ -n "$VARIABLE_MODELS" ]; then
        echo "  "
        echo "  📦 Variable-Constructed Models (from source):"
        echo "$VARIABLE_MODELS" | while read -r model; do
            # Get location info
            LOCATION=$(jq -r ".variable_models[] | select(.model==\"$model\") | 
                       if .type == \"concatenated\" then 
                         \"\(.file):\(.name_line) (concatenated)\"
                       else 
                         \"\(.file):\(.line) (direct)\"
                       end" "$OUTPUT_DIR/variable_models.json" | head -1)
            echo "     $model ($LOCATION)"
        done
    fi
    
    # Show each category with actual model names
    for category in "openai_models" "anthropic_models" "google_models" "meta_models" "cohere_models" "mistral_models" "providers" "apis"; do
        ASSETS=$(jq -r ".assets.${category} // [] | join(\", \")" "$OUTPUT_DIR/ai_assets.json" 2>/dev/null)
        if [ -n "$ASSETS" ] && [ "$ASSETS" != "" ]; then
            CATEGORY_NAME=$(echo "$category" | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
            echo "  "
            echo "  📦 $CATEGORY_NAME:"
            echo "     $ASSETS"
        fi
    done
    
    echo ""
    echo "📊 Asset Summary:"
    jq -r '.summary | 
        "  Total Distinct Assets: \(.total_distinct_assets)\n" +
        "  Total Occurrences: \(.total_occurrences)"
    ' "$OUTPUT_DIR/ai_assets.json"
    
    # Show which files contain which assets with clickable paths
    echo ""
    echo "📍 AI Assets by Location (Cmd+Click to open):"
    jq -r '
        .asset_locations | 
        to_entries | 
        sort_by(.key) | 
        .[] | 
        "\n  🔹 \(.key | ascii_upcase):" as $header |
        (.value | sort_by(.file, .line) | group_by(.file) | 
         map(
           "     \(.[0].file):\n" +
           (map("        → \(.file):\(.line):\(.column) (\(.certainty_percent | floor)% \(.certainty))") | join("\n"))
         ) | 
         if length > 0 then $header + "\n" + join("\n") else empty end
        )
    ' "$OUTPUT_DIR/ai_assets.json" 2>/dev/null | head -150
fi

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Comprehensive AI Usage Search Complete!"
echo "═══════════════════════════════════════════════════"
