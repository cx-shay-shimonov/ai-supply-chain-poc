#!/bin/sh
# Command examples using sample projects in projects-samples/
# Run from the sem/scripts directory

BASEDIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AI_UI="$BASEDIR/projects-samples/ai-ui"
CNAS_MFE="$BASEDIR/projects-samples/cnas-mfe"
OPENHANDS="$BASEDIR/projects-samples/OpenHands"

echo "=== Semantic Code Search (sem) Examples ==="
echo ""

echo "1. Find usages of SortedSeverities function (CNAS MFE)"
"$SCRIPT_DIR/../venv/bin/sem" -p "$CNAS_MFE" -n 100 'usages of SortedSeverities function'

echo ""
echo "2. Find OpenAI/AI usage (ai-ui)"
"$SCRIPT_DIR/../venv/bin/sem" -p "$AI_UI" -n 100 'OpenAI and gpt-4o-mini'

echo ""
echo "3. Find React functional components (CNAS MFE)"
"$SCRIPT_DIR/../venv/bin/sem" -p "$CNAS_MFE" -n 50 'React functional components'

echo ""
echo "4. Find array methods (CNAS MFE)"
"$SCRIPT_DIR/../venv/bin/sem" -p "$CNAS_MFE" -n 50 'array methods like reduce and map'

echo ""
echo "5. Find LLM integration (OpenHands - large project)"
"$SCRIPT_DIR/../venv/bin/sem" -p "$OPENHANDS" -n 50 'LLM integration and API calls'

echo ""
echo "=== Semgrep Static Analysis Examples ==="
echo ""

echo "6. Find OpenAI usage with custom rules (ai-ui)"
semgrep scan -c "$BASEDIR/semgrep/rules/my-detect-openai.yaml" --json "$AI_UI" 2>/dev/null | jq -r '["RULE", "FILE:LINE", "FINDING"], (.results[] | [(.check_id | split(".") | last), "\(.path | split("/") | last):\(.start.line)", (.extra.lines | split("\n") | first | gsub("^\\s+"; ""))]) | @tsv' | column -t -s $'\t'

echo ""
echo "7. Find OpenAI usage with full code context (ai-ui)"
semgrep scan -c "$BASEDIR/semgrep/rules/my-detect-openai.yaml" --json "$AI_UI" 2>/dev/null | jq -r '.results[] | "=== \(.path | split("/") | last):\(.start.line)-\(.end.line) ===\nRule: \(.check_id | split(".") | last)\n\(.extra.lines)\n"'

echo ""
echo "8. Shadow AI detection with p/shadow-ai-pro + custom rules (ai-ui)"
semgrep scan --config p/shadow-ai-pro --config "$BASEDIR/semgrep/rules/shadow-ai-extended.yaml" --json "$AI_UI" 2>/dev/null | jq -r '["RULE", "FILE:LINE", "FINDING"], (.results[] | [(.check_id | split(".") | last), "\(.path | split("/") | last):\(.start.line)", (.extra.lines | split("\n") | first | gsub("^\\s+"; ""))]) | @tsv' | column -t -s $'\t'

echo ""
echo "9. Shadow AI detection on large project (OpenHands)"
semgrep scan --config p/shadow-ai-pro --json "$OPENHANDS" 2>/dev/null | jq '.results | length'
echo "   findings in OpenHands project"

echo ""
echo "=== Combined Analysis Example ==="
echo ""

echo "10. Full audit: Semantic search + Static analysis (ai-ui)"
echo "Running semantic search for OpenAI..."
python "$BASEDIR/sem-query.py" -p projects-samples/ai-ui --json 'OpenAI and AI usage' > /tmp/semantic_results.json 2>/dev/null
echo "Running semgrep scan..."
semgrep scan --config p/shadow-ai-pro --json "$AI_UI" 2>/dev/null > /tmp/semgrep_results.json
echo "Results:"
echo "  Semantic findings: $(jq '.findings | length' /tmp/semantic_results.json 2>/dev/null || echo '0')"
echo "  Semgrep findings: $(jq '.results | length' /tmp/semgrep_results.json)"