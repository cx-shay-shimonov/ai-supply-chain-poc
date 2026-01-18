#!/bin/bash
# AI Usage Audit - Combined Semantic Search + Static Analysis
# Compares findings from sem (semantic) and semgrep (static) tools
#
# Usage: ./ai-usage-audit.sh [target_directory] [result_limit]
#   target_directory: Path to project (default: projects-samples/ai-ui)
#   result_limit: Max semantic results (default: 100)
#
# Examples:
#   ./ai-usage-audit.sh projects-samples/OpenHands
#   ./ai-usage-audit.sh projects-samples/OpenHands 500
#   ./ai-usage-audit.sh projects-samples/ai-ui 1000

BASEDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASEDIR"

# Default target or use first argument
TARGET="${1:-projects-samples/ai-ui}"

# Extract project name from target path
PROJECT_NAME=$(basename "$TARGET")

# Create timestamped output directory with project name
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
OUTPUT_DIR="$BASEDIR/output/sem-audit-${PROJECT_NAME}-${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

# Default limit or use second argument
LIMIT="${2:-100000}"

# Validate limit is a number
if ! [[ "$LIMIT" =~ ^[0-9]+$ ]]; then
    echo "❌ Error: Result limit must be a positive number"
    echo "   Usage: $0 [target_directory] [result_limit]"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🤖 AI Usage Audit - Semantic Search                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Target: $TARGET"
echo "🔢 Result Limit: $LIMIT"
echo "📂 Output: output/sem-audit-${PROJECT_NAME}-${TIMESTAMP}/"
echo "⏰ Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Check if target exists
if [ ! -d "$TARGET" ]; then
    echo "❌ Error: Directory '$TARGET' not found"
    exit 1
fi

# Check if embeddings exist for sem
EMBEDDINGS_PATH="$TARGET/.embeddings"
if [ ! -f "$EMBEDDINGS_PATH" ]; then
    echo "⚠️  No embeddings found. Generating..."
    echo ""
    venv/bin/sem --embed -p "$TARGET"
    echo ""
    
    if [ -f "$EMBEDDINGS_PATH" ]; then
        echo "✅ Embeddings created successfully!"
        echo ""
        SKIP_SEM=false
    else
        echo "❌ Failed to create embeddings"
        echo ""
        SKIP_SEM=true
    fi
else
    SKIP_SEM=false
fi

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Phase 1: Semantic Search (AI-Powered)"
echo "════════════════════════════════════════════════════════════════"
echo ""

# old queries:
# LLM AI usage
# Calling large language models or AI APIs

if [ "$SKIP_SEM" = true ]; then
    echo "⏭️  Skipping semantic search (no embeddings)"
    SEM_COUNT=0
else
    echo "Running semantic search for AI/LLM usage (limit: $LIMIT)..."
    echo ""
    
    # Use multiple focused queries for better results
    # Query 1: General AI API usage (catches OpenAI, Anthropic, etc.)
    echo "  🔍 Query 1: AI API keys and configuration..."
    venv/bin/python sem-query.py -p "$TARGET" --json -n "$((LIMIT/3))" \
        'usages of gpt-5, gpt-5-latest, gpt-5-2025-11-04, gpt-5-pro, gpt-5-mini, gpt-5-nano, o4-mini, o3-high, gpt-4.1-mini, gpt-4o, gpt-oss-120b, claude-opus-4-5-latest, claude-opus-4-5-20251101, claude-sonnet-4-5-latest, claude-sonnet-4-5-20250929, claude-haiku-4-5, claude-3-5-haiku-latest, claude-code-2-1, gemini-3-pro, gemini-3-flash, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-live-2.5-flash-native-audio, deepseek-v4, deepseek-v3.2, deepseek-reasoner, deepseek-chat, llama-3.3-70b-instruct, llama-3.1-405b-instruct, llama-4-preview-70b, mistral-large-2511, mistral-nemo-latest, pixtral-large-latest, codestral-latest, grok-4-fast-reasoning, grok-code-fast-1, glm-4.7-thinking, qwen3-72b-instruct, mimo-v2-flash' \
        2>/dev/null > "$OUTPUT_DIR/sem_results_q1.json"
    
    # Query 2: LLM completions and chat
    # echo "  🔍 Query 2: LLM completions and chat..."
    # venv/bin/python sem-query.py -p "$TARGET" --json -n "$((LIMIT/3))" \
    #     'GPT Claude Gemini chat completions streaming API calls messages' \
    #     2>/dev/null > "$OUTPUT_DIR/sem_results_q2.json"
    
    # # Query 3: AI model configuration
    # echo "  🔍 Query 3: AI model configuration and usage..."
    # venv/bin/python sem-query.py -p "$TARGET" --json -n "$((LIMIT/3))" \
    #     'AI language model configuration temperature tokens embedding vector' \
    #     2>/dev/null > "$OUTPUT_DIR/sem_results_q3.json"
    
    # Merge results and deduplicate by file:line
    echo "  🔄 Merging and deduplicating results..."
    jq -s '
        {
            query: "Multi-query AI/LLM usage scan",
            repository: .[0].repository,
            results: ([.[].results[]] | 
                      group_by(.file + ":" + (.line | tostring)) | 
                      map(max_by(.score)) |
                      sort_by(-.score) |
                      .[0:'$LIMIT'] |
                      to_entries |
                      map(.value + {rank: (.key + 1)}))
        }
    ' "$OUTPUT_DIR/sem_results_q1.json" \
      "$OUTPUT_DIR/sem_results_q2.json" \
      "$OUTPUT_DIR/sem_results_q3.json" \
      > "$OUTPUT_DIR/sem_results.json"
    
    # Clean up individual query files
    rm -f "$OUTPUT_DIR/sem_results_q1.json" "$OUTPUT_DIR/sem_results_q2.json" "$OUTPUT_DIR/sem_results_q3.json"
    
    # Count results
    SEM_COUNT=$(jq '.results | length' "$OUTPUT_DIR/sem_results.json" 2>/dev/null || echo "0")
    
    echo ""
    echo "✅ Semantic Search Complete"
    echo "   Findings: $SEM_COUNT unique code locations"
    
    # Show top 5 results
    if [ "$SEM_COUNT" -gt 0 ]; then
        echo ""
        echo "   📊 Top 5 Results:"
        jq -r '.results[0:5] | .[] | "      • \(.file | split("/") | last):\(.line):\(.column) (certainty: \(.certainty), \(.certainty_percent)%)"' "$OUTPUT_DIR/sem_results.json" 2>/dev/null
    fi
fi

# echo ""
# echo "════════════════════════════════════════════════════════════════"
# echo "🔍 Phase 2: Static Analysis (Pattern-Based)"
# echo "════════════════════════════════════════════════════════════════"
# echo ""

# echo "Running Semgrep with shadow-ai-pro + custom rules..."

# # Run semgrep and save to temp file with pretty formatting
# semgrep scan \
#     --config p/shadow-ai-pro \
#     --config "$BASEDIR/my-detect-openai.yaml" \
#     "$TARGET" \
#     --json 2>/dev/null | jq '.' > "$OUTPUT_DIR/semgrep_results.json"

# # Count results
# SEMGREP_COUNT=$(jq '.results | length' "$OUTPUT_DIR/semgrep_results.json" 2>/dev/null || echo "0")

# echo "✅ Semgrep Scan Complete"
# echo "   Findings: $SEMGREP_COUNT patterns detected"

# # Show breakdown by rule
# if [ "$SEMGREP_COUNT" -gt 0 ]; then
#     echo ""
#     echo "   📊 Breakdown by Rule:"
#     jq -r '.results | group_by(.check_id) | map("      • \(.[0].check_id | split(".") | last): \(length) occurrences") | .[]' "$OUTPUT_DIR/semgrep_results.json" 2>/dev/null
    
#     echo ""
#     echo "   📊 Breakdown by Severity:"
#     jq -r '.results | group_by(.extra.severity) | map("      • \(.[0].extra.severity): \(length) findings") | .[]' "$OUTPUT_DIR/semgrep_results.json" 2>/dev/null
# fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 Phase 3: Comparison & Analysis"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Calculate totals
TOTAL_FINDINGS=$((SEM_COUNT + SEMGREP_COUNT))

# Scan for variable-based model concatenations
echo ""
echo "🔍 Scanning for concatenated model variables..."
venv/bin/python scan-model-variables.py "$TARGET" > "$OUTPUT_DIR/variable_models.json"
VARIABLE_MODEL_COUNT=$(jq '.count' "$OUTPUT_DIR/variable_models.json" 2>/dev/null || echo "0")

# Show comparison
echo "┌────────────────────────────────────────────────────────────┐"
echo "│                     FINDINGS                               │"
echo "├────────────────────────────────────────────────────────────┤"
printf "│  %-30s %26s  │\n" "Semantic Search (sem):" "$SEM_COUNT findings"
printf "│  %-30s %26s  │\n" "Variable Models:" "$VARIABLE_MODEL_COUNT findings"
# printf "│  %-30s %26s  │\n" "Static Analysis (semgrep):" "$SEMGREP_COUNT findings"
echo "├────────────────────────────────────────────────────────────┤"
# printf "│  %-30s %26s  │\n" "Total Unique Checks:" "$TOTAL_FINDINGS combined"
# echo "└────────────────────────────────────────────────────────────┘"
echo ""

# Show variable-constructed models if found
if [ "$VARIABLE_MODEL_COUNT" -gt 0 ]; then
    echo "📦 Variable-Constructed Models Found:"
    jq -r '.variable_models[] | 
           if .type == "concatenated" then
             "   • \(.model) (\(.file | split("/") | .[-1]):\(.name_line) concatenated)"
           else
             "   • \(.model) (\(.file | split("/") | .[-1]):\(.line) direct)"
           end' "$OUTPUT_DIR/variable_models.json"
    echo ""
fi

# Analysis
echo "📈 Analysis:"
echo ""

if [ "$SKIP_SEM" = true ]; then
    echo "   ⚠️  Semantic search was skipped (no embeddings)"
    echo "      Generate embeddings for complete analysis"
elif [ "$SEM_COUNT" -eq 0 ] && [ "$SEMGREP_COUNT" -eq 0 ]; then
    echo "   ✅ No AI usage detected by either tool"
    echo "      Project appears to be AI-free"
elif [ "$SEM_COUNT" -gt "$SEMGREP_COUNT" ]; then
    echo "   🔍 Semantic search found MORE locations ($SEM_COUNT vs $SEMGREP_COUNT)"
    echo "      • Semantic search detects usage patterns and context"
    echo "      • Static analysis focuses on specific patterns"
    echo "      • Combined approach recommended for thorough audit"
# elif [ "$SEMGREP_COUNT" -gt "$SEM_COUNT" ]; then
#     echo "   🎯 Static analysis found MORE patterns ($SEMGREP_COUNT vs $SEM_COUNT)"
#     echo "      • Semgrep excels at detecting specific imports/APIs"
#     echo "      • Semantic search finds conceptual usage"
#     echo "      • Both tools complement each other"
# else
#     echo "   ⚖️  Both tools found similar counts ($SEM_COUNT vs $SEMGREP_COUNT)"
#     echo "      • Strong correlation between tools"
#     echo "      • High confidence in findings"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📊 Phase 4: Generating CSV Comparison Report"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Generate CSV comparison report
CSV_FILE="$OUTPUT_DIR/ai_audit_comparison.csv"

echo "Creating CSV report..."

# CSV Header
echo "Rank,Tool,Type,File,Line,Column,Score,Certainty,Certainty %,Match Reason,Matched Tokens,Code Preview" > "$CSV_FILE"

# Add Semantic Search results
if [ "$SKIP_SEM" = false ] && [ "$SEM_COUNT" -gt 0 ]; then
    jq -r '.results[] | [
        .rank,
        "Semantic Search",
        "AI Usage Pattern",
        (.file | split("/") | last),
        .line,
        .column,
        (.score | tostring | .[0:6]),
        .certainty,
        (.certainty_percent | tostring) + "%",
        .match_reason,
        (.matched_tokens | join(", ")),
        (.code | split("\n") | first | gsub("\""; "\"\""))
    ] | @csv' "$OUTPUT_DIR/sem_results.json" >> "$CSV_FILE" 2>/dev/null
fi

# # Add Semgrep results
# if [ "$SEMGREP_COUNT" -gt 0 ]; then
#     jq -r '.results[] | [
#         "Static Analysis",
#         (.check_id | split(".") | last),
#         "",
#         (.path | split("/") | last),
#         .start.line,
#         .extra.severity,
#         "N/A",
#         (.extra.message + ": " + (.extra.lines | split("\n") | first | gsub("\""; "\"\"")))
#     ] | @csv' "$OUTPUT_DIR/semgrep_results.json" >> "$CSV_FILE" 2>/dev/null
# fi

# Add summary rows
echo "" >> "$CSV_FILE"
echo "SUMMARY,,,,,," >> "$CSV_FILE"
echo "Semantic Search,Total Findings,$SEM_COUNT,,,," >> "$CSV_FILE"
echo "Static Analysis,Total Findings,$SEMGREP_COUNT,,,," >> "$CSV_FILE"
echo "Combined,Total Findings,$TOTAL_FINDINGS,,,," >> "$CSV_FILE"

echo "✅ CSV report generated!"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "🤖 Phase 5: Extracting All AI Provider Assets"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Output files for all AI assets
SEM_ASSETS_FILE="$OUTPUT_DIR/semantic_ai_providers.json"
# SEMGREP_ASSETS_FILE="$OUTPUT_DIR/semgrep_ai_providers.json"

echo "Analyzing results to identify ALL AI providers and models..."
echo ""

# Extract assets from Semantic Search results
if [ "$SKIP_SEM" = false ] && [ "$SEM_COUNT" -gt 0 ]; then
    echo "🔍 Processing Semantic Search results..."
    python3 "$BASEDIR/ai_asset_extractor.py" semantic "$OUTPUT_DIR/sem_results.json" > "$SEM_ASSETS_FILE"
    echo "   ✅ Semantic assets extracted"
fi

# Extract assets from Semgrep results
# if [ "$SEMGREP_COUNT" -gt 0 ]; then
#     echo "🎯 Processing Semgrep results..."
#     python3 "$BASEDIR/ai_asset_extractor.py" semgrep "$OUTPUT_DIR/semgrep_results.json" > "$SEMGREP_ASSETS_FILE"
#     echo "   ✅ Semgrep assets extracted"
# fi

echo ""

# Display comprehensive summary
if [ "$SKIP_SEM" = false ] && [ "$SEM_COUNT" -gt 0 ]; then
    echo "📊 Semantic Search - AI Assets Summary:"
    jq -r '.summary | "   Total Distinct Assets: \(.total_distinct_assets)\n   Total Occurrences: \(.total_occurrences)"' "$SEM_ASSETS_FILE" 2>/dev/null
    
    # Display breakdown by provider
    echo ""
    echo "   By Provider:"
    for provider in openai anthropic google meta cohere mistral; do
        COUNT=$(jq -r ".assets.${provider}_models // [] | length" "$SEM_ASSETS_FILE" 2>/dev/null)
        if [ "$COUNT" -gt 0 ]; then
            PROVIDER_NAME=$(echo $provider | sed 's/.*/\u&/')
            printf "      • %-12s %d models\n" "$PROVIDER_NAME:" "$COUNT"
        fi
    done
    
    # Show sample models
    echo ""
    echo "   Sample Models Found:"
    jq -r '.assets | to_entries[] | select(.value | length > 0) | "      • \(.key): \(.value[0:3] | join(", "))"' "$SEM_ASSETS_FILE" 2>/dev/null | head -6
fi

# if [ "$SEMGREP_COUNT" -gt 0 ]; then
#     echo ""
#     echo "📊 Static Analysis - AI Assets Summary:"
#     jq -r '.summary | "   Total Distinct Assets: \(.total_distinct_assets)\n   Total Occurrences: \(.total_occurrences)"' "$SEMGREP_ASSETS_FILE" 2>/dev/null
    
#     echo ""
#     echo "   Assets Found:"
#     jq -r '.assets | to_entries[] | select(.value | length > 0) | "      • \(.key): \(.value | join(", "))"' "$SEMGREP_ASSETS_FILE" 2>/dev/null
# fi

echo ""

# Create separate .assets.json files for easy access
echo "════════════════════════════════════════════════════════════════"
echo "📝 Creating Assets-Only Files"
echo "════════════════════════════════════════════════════════════════"
echo ""

SEM_ASSETS_ONLY_FILE="$OUTPUT_DIR/semantic_assets.json"
# SEMGREP_ASSETS_ONLY_FILE="$OUTPUT_DIR/semgrep_assets.json"

# Extract assets to separate files for easy parsing
if [ "$SKIP_SEM" = false ] && [ "$SEM_COUNT" -gt 0 ]; then
    jq '.assets' "$SEM_ASSETS_FILE" > "$SEM_ASSETS_ONLY_FILE" 2>/dev/null
    echo "✅ Semantic Search assets-only file created"
fi

# if [ "$SEMGREP_COUNT" -gt 0 ]; then
#     jq '.assets' "$SEMGREP_ASSETS_FILE" > "$SEMGREP_ASSETS_ONLY_FILE" 2>/dev/null
#     echo "✅ Static Analysis assets-only file created"
# fi

echo ""

echo "════════════════════════════════════════════════════════════════"
echo "💾 All Results Saved"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📂 Output Directory: output/sem-audit-${PROJECT_NAME}-${TIMESTAMP}/"
echo ""
echo "📊 Files Created:"
echo "   • ai_audit_comparison.csv"
echo "   • sem_results.json (raw semantic search output)"
if [ "$SKIP_SEM" = false ] && [ "$SEM_COUNT" -gt 0 ]; then
    echo "   • semantic_ai_providers.json (complete: summary + raw_results + assets)"
    echo "   • semantic_assets.json (assets only)"
fi
echo ""

echo "⏰ Completed: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Audit Complete!"
echo "═══════════════════════════════════════════════════════════════"

