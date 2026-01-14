#!/bin/bash
# Extract distinct AI models and providers from audit results
# Creates separate JSON files for semantic search and static analysis findings

BASEDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BASEDIR"

# Input files
SEM_RESULTS="${1:-/tmp/sem_results.json}"
SEMGREP_RESULTS="${2:-/tmp/semgrep_results.json}"

# Output files
SEM_ASSETS="/tmp/sem_ai_assets.json"
SEMGREP_ASSETS="/tmp/semgrep_ai_assets.json"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🤖 AI Assets Extraction                             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 Input Files:"
echo "   • Semantic Results: $SEM_RESULTS"
echo "   • Semgrep Results:  $SEMGREP_RESULTS"
echo ""
echo "📊 Output Files:"
echo "   • Semantic Assets: $SEM_ASSETS"
echo "   • Semgrep Assets:  $SEMGREP_ASSETS"
echo ""

# Check if input files exist
if [ ! -f "$SEM_RESULTS" ]; then
    echo "❌ Error: Semantic results file not found: $SEM_RESULTS"
    exit 1
fi

if [ ! -f "$SEMGREP_RESULTS" ]; then
    echo "❌ Error: Semgrep results file not found: $SEMGREP_RESULTS"
    exit 1
fi

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Extracting AI Assets from Semantic Search Results"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Extract AI models and engines from semantic search code snippets
# Looking for patterns like: gpt-4, gpt-3.5-turbo, claude, openai, anthropic, etc.
python3 << PYTHON_SCRIPT > "$SEM_ASSETS"
import json
import re
import sys
from collections import defaultdict

# Load semantic search results
with open('$SEM_RESULTS', 'r') as f:
    data = json.load(f)

# AI asset patterns to search for
patterns = {
    'openai_models': [
        r'\bgpt-4[o]?(?:-\w+)*\b',
        r'\bgpt-3\.5-turbo(?:-\w+)*\b',
        r'\bgpt-3(?:-\w+)*\b',
        r'\bo1(?:-\w+)*\b',
        r'\bo3(?:-\w+)*\b',
        r'\bo4(?:-\w+)*\b',
        r'\btext-davinci(?:-\w+)*\b',
        r'\btext-embedding(?:-\w+)*\b',
    ],
    'anthropic_models': [
        r'\bclaude(?:-\w+)*\b',
        r'\bclaude-3-opus\b',
        r'\bclaude-3-sonnet\b',
        r'\bclaude-3-haiku\b',
        r'\bclaude-2(?:\.\d+)?\b',
    ],
    'google_models': [
        r'\bgemini(?:-\w+)*\b',
        r'\bpalm(?:-\w+)*\b',
        r'\bbard\b',
    ],
    'meta_models': [
        r'\bllama(?:-\w+)*\b',
    ],
    'cohere_models': [
        r'\bcommand(?:-\w+)*\b',
        r'\bcohere\b',
    ],
    'providers': [
        r'\bopenai\b',
        r'\banthropics?\b',
        r'\bOpenAI\b',
        r'\bAnthropic\b',
        r'\bChatGPT\b',
    ]
}

# Extract assets from code
assets = defaultdict(set)
locations = defaultdict(list)

results = data.get('results', [])
for result in results:
    code = result.get('code', '').lower()
    file_path = result.get('file', '').split('/')[-1]
    line = result.get('line', 0)
    score = result.get('score', 0)
    certainty = result.get('certainty_percent', 0)
    
    # Search for each pattern
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                asset = match.group(0)
                # Normalize asset name
                if category == 'providers':
                    asset = asset.lower()
                assets[category].add(asset)
                locations[asset].append({
                    'file': file_path,
                    'line': line,
                    'score': round(score, 4),
                    'certainty_percent': certainty
                })

# Convert sets to sorted lists
assets_dict = {k: sorted(list(v)) for k, v in assets.items()}

# Calculate summary
total_distinct_assets = sum(len(v) for v in assets_dict.values())
total_occurrences = sum(len(v) for v in locations.values())

# Build output
output = {
    'tool': 'Semantic Search (sem)',
    'query': data.get('query', ''),
    'repository': data.get('repository', '').split('/')[-1] if data.get('repository') else '',
    'summary': {
        'total_distinct_assets': total_distinct_assets,
        'total_occurrences': total_occurrences,
        'results_analyzed': len(results),
        'breakdown': {k: len(v) for k, v in assets_dict.items() if v}
    },
    'assets': assets_dict,
    'locations': {k: v[:5] for k, v in sorted(locations.items(), key=lambda x: len(x[1]), reverse=True)}  # Top 5 locations per asset
}

print(json.dumps(output, indent=2))
PYTHON_SCRIPT

echo "✅ Semantic assets extracted"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Extracting AI Assets from Semgrep Results"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Extract AI models and engines from Semgrep findings
python3 << PYTHON_SCRIPT > "$SEMGREP_ASSETS"
import json
import re
import sys
from collections import defaultdict

# Load semgrep results
with open('$SEMGREP_RESULTS', 'r') as f:
    data = json.load(f)

# AI asset patterns
patterns = {
    'openai_models': [
        r'\bgpt-4[o]?(?:-\w+)*\b',
        r'\bgpt-3\.5-turbo(?:-\w+)*\b',
        r'\bgpt-3(?:-\w+)*\b',
        r'\bo1(?:-\w+)*\b',
        r'\bo3(?:-\w+)*\b',
        r'\btext-davinci(?:-\w+)*\b',
        r'\btext-embedding(?:-\w+)*\b',
    ],
    'anthropic_models': [
        r'\bclaude(?:-\w+)*\b',
        r'\bclaude-3-opus\b',
        r'\bclaude-3-sonnet\b',
        r'\bclaude-3-haiku\b',
    ],
    'google_models': [
        r'\bgemini(?:-\w+)*\b',
        r'\bpalm(?:-\w+)*\b',
    ],
    'meta_models': [
        r'\bllama(?:-\w+)*\b',
    ],
    'providers': [
        r'\bopenai\b',
        r'\banthropics?\b',
        r'\bOpenAI\b',
        r'\bAnthropic\b',
    ],
    'apis': [
        r'openai\.(?:chat|completions?|embeddings?)',
        r'anthropic\.(?:messages|completions?)',
    ]
}

# Extract assets
assets = defaultdict(set)
locations = defaultdict(list)
rules_triggered = defaultdict(int)

results = data.get('results', [])
for result in results:
    rule_id = result.get('check_id', '').split('.')[-1]
    path = result.get('path', '').split('/')[-1]
    line = result.get('start', {}).get('line', 0)
    severity = result.get('extra', {}).get('severity', 'UNKNOWN')
    message = result.get('extra', {}).get('message', '')
    code_lines = result.get('extra', {}).get('lines', '')
    
    rules_triggered[rule_id] += 1
    
    # Search in message and code
    search_text = (message + ' ' + code_lines).lower()
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.finditer(pattern, search_text, re.IGNORECASE)
            for match in matches:
                asset = match.group(0)
                if category == 'providers' or category == 'apis':
                    asset = asset.lower()
                assets[category].add(asset)
                locations[asset].append({
                    'file': path,
                    'line': line,
                    'severity': severity,
                    'rule': rule_id
                })

# Convert sets to sorted lists
assets_dict = {k: sorted(list(v)) for k, v in assets.items()}

# Calculate summary
total_distinct_assets = sum(len(v) for v in assets_dict.values())
total_occurrences = sum(len(v) for v in locations.values())

# Build output
output = {
    'tool': 'Static Analysis (Semgrep)',
    'version': data.get('version', ''),
    'summary': {
        'total_distinct_assets': total_distinct_assets,
        'total_occurrences': total_occurrences,
        'findings_analyzed': len(results),
        'rules_triggered': len(rules_triggered),
        'breakdown': {k: len(v) for k, v in assets_dict.items() if v}
    },
    'assets': assets_dict,
    'rules': dict(sorted(rules_triggered.items(), key=lambda x: x[1], reverse=True)),
    'locations': {k: v[:5] for k, v in sorted(locations.items(), key=lambda x: len(x[1]), reverse=True)}  # Top 5 locations per asset
}

print(json.dumps(output, indent=2))
PYTHON_SCRIPT

echo "✅ Semgrep assets extracted"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📊 Summary"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Display summary from both files
echo "🔍 Semantic Search Assets:"
jq -r '.summary | "   Total Distinct Assets: \(.total_distinct_assets)\n   Total Occurrences: \(.total_occurrences)\n   Results Analyzed: \(.results_analyzed)"' "$SEM_ASSETS"
echo ""

echo "🎯 Static Analysis Assets:"
jq -r '.summary | "   Total Distinct Assets: \(.total_distinct_assets)\n   Total Occurrences: \(.total_occurrences)\n   Findings Analyzed: \(.findings_analyzed)\n   Rules Triggered: \(.rules_triggered)"' "$SEMGREP_ASSETS"
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "💾 Output Files Generated"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "   📄 $SEM_ASSETS"
echo "   📄 $SEMGREP_ASSETS"
echo ""
echo "View detailed assets:"
echo "   cat $SEM_ASSETS | jq ."
echo "   cat $SEMGREP_ASSETS | jq ."
echo ""
echo "View specific categories:"
echo "   cat $SEM_ASSETS | jq '.assets.openai_models'"
echo "   cat $SEMGREP_ASSETS | jq '.assets.providers'"
echo ""

echo "✅ AI Assets Extraction Complete!"
echo ""

