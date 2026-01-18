#!/bin/bash
# Wrapper script for scanning sample projects

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🌲 Tree-sitter AI Model Scanner                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment if it exists
if [ -d "$BASEDIR/venv" ]; then
  source "$BASEDIR/venv/bin/activate"
fi

# Scan ai-ui project
echo "📁 Scanning projects-samples/ai-ui..."
python "$BASEDIR/scanner.py" \
  --dir "$BASEDIR/../projects-samples/ai-ui" \
  --output "$BASEDIR/output/ai-ui-scan.json"

echo ""
echo "────────────────────────────────────────────────────────────────"
echo ""

# Scan OpenHands project
echo "📁 Scanning projects-samples/OpenHands..."
python "$BASEDIR/scanner.py" \
  --dir "$BASEDIR/../projects-samples/OpenHands" \
  --output "$BASEDIR/output/openHands-scan.json"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ All scans complete!"
echo "📊 Results saved in: $BASEDIR/output/"
echo "════════════════════════════════════════════════════════════════"
