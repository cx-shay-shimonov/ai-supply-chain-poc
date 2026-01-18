#!/bin/bash
# Interactive setup and demo script for AI Supply Chain POC

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASEDIR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          AI Supply Chain POC - Setup & Demo                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "sem/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the installation steps from README.md first"
    exit 1
fi

# Check if embeddings exist
if [ ! -f ""$BASEDIR/projects-samples/cnas-mfe/.embeddings" ]; then
    echo "⚠️  cnas-mfe embeddings not found"
fi

if [ ! -f ""$BASEDIR/projects-samples/ai-ui/.embeddings" ]; then
    echo "⚠️  ai-ui embeddings not found"
fi

echo "📋 Setup Status:"
echo "  ✅ Virtual environment exists"
echo "  ✅ Semantic search tool installed"
echo ""

read -p "Would you like to generate embeddings for sample projects? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Generating embeddings for cnas-mfe..."
    "$BASEDIR/sem/venv/bin/sem" --embed -p "$BASEDIR/projects-samples/cnas-mfe
    echo ""
    
    echo "📦 Generating embeddings for ai-ui..."
    "$BASEDIR/sem/venv/bin/sem" --embed -p "$BASEDIR/projects-samples/ai-ui
    echo ""
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                     Quick Start Guide                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "1️⃣  Semantic Search Examples:"
echo ""
echo "   # Search cnas-mfe for React components"
echo "   "$BASEDIR/sem/venv/bin/sem" -p "$BASEDIR/projects-samples/cnas-mfe -n 20 'React components'"
echo ""
echo "   # Search ai-ui for OpenAI usage"
echo "   "$BASEDIR/sem/venv/bin/sem" -p "$BASEDIR/projects-samples/ai-ui -n 20 'openai'"
echo ""
echo "2️⃣  Static Analysis Examples:"
echo ""
echo "   # Scan ai-ui for Shadow AI"
echo "   semgrep scan --config p/shadow-ai-pro "$BASEDIR/projects-samples/ai-ui/"
echo ""
echo "3️⃣  Full Audit:"
echo ""
echo "   # Run complete audit on ai-ui"
echo "   bash ai-usage-audit.sh "$BASEDIR/projects-samples/ai-ui 50"
echo ""
echo "4️⃣  More Examples:"
echo ""
echo "   # See SEM-EXAMPLES.md for semantic search examples"
echo "   # See SEMGREP-EXAMPLES.md for static analysis examples"
echo ""

read -p "Would you like to run a quick demo? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "Demo 1: Semantic Search on cnas-mfe"
    echo "═══════════════════════════════════════════════════════════════"
    "$BASEDIR/sem/venv/bin/sem" -p "$BASEDIR/projects-samples/cnas-mfe -n 5 'React components'
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════"
    echo "Demo 2: Semantic Search on ai-ui"
    echo "═══════════════════════════════════════════════════════════════"
    "$BASEDIR/sem/venv/bin/sem" -p "$BASEDIR/projects-samples/ai-ui -n 5 'openai usage'
    echo ""
    
    echo "═══════════════════════════════════════════════════════════════"
    echo "Demo 3: Semgrep Scan on ai-ui"
    echo "═══════════════════════════════════════════════════════════════"
    semgrep scan --config "$BASEDIR/semgrep/rules/my-detect-openai.yaml" "$BASEDIR/projects-samples/ai-ui/ --json 2>/dev/null | jq -r '["RULE", "FILE:LINE", "CODE"], (.results[] | [(.check_id | split(".") | last), "\(.path | split("/") | last):\(.start.line)", (.extra.lines | split("\n")[0] | gsub("^\\s+"; ""))]) | @tsv' | column -t -s $'\t'
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! 🎉                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
