# Semgrep Examples - Shadow AI Detection

A comprehensive guide for detecting and auditing AI library usage in codebases using Semgrep.

## About the Tool

**Repository**: [semgrep/semgrep](https://github.com/semgrep/semgrep)  
**License**: LGPL-2.1  
**GitHub Stats**: ⭐ 13.8k stars | 🍴 854 forks | 👥 202+ contributors  
**Languages**: OCaml 77.9%, Python 18.4%, Other 3.7%  
**Maintainer**: Semgrep Inc. (formerly r2c)  
**Status**: ✅ Actively maintained (314 releases, latest: v1.147.0 on Jan 7, 2026)

**Key Features**:
- Static analysis for 30+ languages
- Extensive rule registry (community + pro rulesets)
- Fast, lightweight, and customizable
- CI/CD integration ready
- Open-source with enterprise options

## Table of Contents

- [Quick Start](#quick-start)
- [Detection Strategies](#detection-strategies)
- [Output Formats](#output-formats)
- [Real-World Examples](#real-world-examples)
- [Demo Scenarios](#demo-scenarios)
- [Advanced Usage](#advanced-usage)

---

## Quick Start

### Basic Scan

```bash
# Scan a project with community rules + custom rules
semgrep scan \
  --config p/shadow-ai-pro \
  --config my-detect-openai.yaml \
  projects-samples/ai-ui/
```

### Quick Count

```bash
# Just count the findings
semgrep scan \
  --config p/shadow-ai-pro \
  --config my-detect-openai.yaml \
  projects-samples/ai-ui/ \
  --json 2>/dev/null | jq '.results | length'
```

---

## Detection Strategies

### 1. Using Community Rulesets

```bash
# Use Semgrep's curated shadow AI rules
semgrep scan --config p/shadow-ai-pro projects-samples/ai-ui/

# Use multiple community rulesets
semgrep scan \
  --config p/shadow-ai-pro \
  --config p/security-audit \
  --config p/secrets \
  projects-samples/ai-ui/
```

### 2. Custom Rules Only

```bash
# Use your custom OpenAI detection rules
semgrep scan \
  --config my-detect-openai.yaml \
  projects-samples/ai-ui/
```

### 3. Combined Approach (Recommended)

```bash
# Combine community rules with custom patterns
semgrep scan \
  --config p/shadow-ai-pro \
  --config my-detect-openai.yaml \
  --config shadow-ai-extended.yaml \
  projects-samples/ai-ui/
```

---

## Output Formats

### Format 1: Clean Table View

**Best for:** Quick overview, terminal presentations

```bash
semgrep scan \
  --config p/shadow-ai-pro \
  --config my-detect-openai.yaml \
  projects-samples/ai-ui/ \
  --json 2>/dev/null | jq -r '
["RULE", "FILE:LINE", "SEVERITY", "FINDING"], 
(.results[] | [
  (.check_id | split(".") | last), 
  "\(.path | split("/") | last):\(.start.line)", 
  .extra.severity,
  (.extra.lines | split("\n") | first | gsub("^\\s+"; ""))
]) | @tsv' | column -t -s $'\t'
```

**Output example:**
```
RULE                  FILE:LINE       SEVERITY  FINDING
detect-openai         script.js:5     WARNING   import OpenAI from "openai"
detect-openai-model   script.js:12    INFO      model: "gpt-4o-mini"
```

---

### Format 2: Detailed Code Blocks

**Best for:** Code review, debugging

```bash
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
.results[] | 
"════════════════════════════════════════════════════════════════
📋 Rule: \(.check_id)
📁 File: \(.path)
📍 Location: Line \(.start.line)-\(.end.line), Col \(.start.col)-\(.end.col)
⚠️  Severity: \(.extra.severity)
💬 Message: \(.extra.message)
📝 Code:
\(.extra.lines)
════════════════════════════════════════════════════════════════
"'
```

---

### Format 3: Summary + Details

**Best for:** Executive reports, demonstrations

```bash
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
"════════════════════════════════════════════════════════════════",
"📊 SCAN SUMMARY",
"════════════════════════════════════════════════════════════════",
"Total Findings: \(.results | length)",
"Files Scanned: \(.paths.scanned | length)",
"Unique Files with Findings: \(.results | map(.path) | unique | length)",
"",
"By Severity:",
(.results | group_by(.extra.severity) | map("  - \(.[0].extra.severity): \(length) findings") | join("\n")),
"",
"By Rule:",
(.results | group_by(.check_id) | map("  - \(.[0].check_id | split(".") | last): \(length) findings") | join("\n")),
"",
"════════════════════════════════════════════════════════════════",
"📋 DETAILED FINDINGS",
"════════════════════════════════════════════════════════════════",
"",
(.results[] | 
"[\(.extra.severity)] \(.check_id | split(".") | last)",
"📁 \(.path | split("/") | last):\(.start.line):\(.start.col)",
"💬 \(.extra.message)",
"📝 Code:",
"   \(.extra.lines | split("\n") | map("   " + .) | join("\n"))",
"────────────────────────────────────────────────────────────────",
""
)'
```

---

### Format 4: JSON Export

**Best for:** Automation, integrations, dashboards

```bash
# Full JSON output
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null > scan_results.json

# Structured JSON with key fields
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq '{
  scan_date: now | strftime("%Y-%m-%d %H:%M:%S"),
  total_findings: (.results | length),
  files_scanned: (.paths.scanned | length),
  findings: .results[] | {
    rule: .check_id,
    file: .path,
    line_start: .start.line,
    line_end: .end.line,
    severity: .extra.severity,
    message: .extra.message,
    code_snippet: .extra.lines
  }
}' > structured_results.json
```

---

### Format 5: CSV for Excel/Sheets

**Best for:** Spreadsheet analysis, reporting

```bash
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
["Rule","File","Line","Severity","Message","Code"], 
(.results[] | [
  .check_id, 
  .path, 
  .start.line, 
  .extra.severity, 
  .extra.message, 
  (.extra.lines | gsub("\n"; " | "))
]) | @csv' > findings.csv

# Open in Excel or Numbers
open findings.csv
```

---

### Format 6: Markdown Report

**Best for:** Documentation, GitHub issues

```bash
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
"# Shadow AI Detection Report",
"",
"**Scan Date:** " + (now | strftime("%Y-%m-%d %H:%M:%S")),
"**Total Findings:** \(.results | length)",
"**Files Scanned:** \(.paths.scanned | length)",
"",
"## Summary by Severity",
"",
(.results | group_by(.extra.severity) | map("- **\(.[0].extra.severity)**: \(length) findings") | join("\n")),
"",
"## Summary by Rule",
"",
(.results | group_by(.check_id) | map("- `\(.[0].check_id)`: \(length) findings") | join("\n")),
"",
"## Detailed Findings",
"",
(.results[] | 
"### \(.check_id)",
"",
"- **File:** `\(.path)`",
"- **Line:** \(.start.line)-\(.end.line)",
"- **Severity:** \(.extra.severity)",
"- **Message:** \(.extra.message)",
"",
"```" + (.path | split(".") | last),
(.extra.lines),
"```",
"",
"---",
""
)' > SCAN_REPORT.md
```

---

## Real-World Examples

### Example 1: Audit a Node.js Project

```bash
# Scan for OpenAI usage in a Node/TypeScript project
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
["FILE", "LINE", "WHAT", "CODE"],
(.results[] | [
  (.path | split("/") | last),
  "\(.start.line)",
  (.check_id | split(".") | last),
  (.extra.lines | split("\n") | first | gsub("^\\s+"; "") | .[0:60] + "...")
]) | @tsv' | column -t -s $'\t'
```

### Example 2: Find Only High-Risk Issues

```bash
# Filter for WARNING and ERROR severity only
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
.results[] | 
select(.extra.severity == "WARNING" or .extra.severity == "ERROR") | 
"🚨 [\(.extra.severity)] \(.check_id | split(".") | last)
   📁 \(.path):\(.start.line)
   💬 \(.extra.message)
   📝 \(.extra.lines | split("\n") | first)
"'
```

### Example 3: List All Affected Files

```bash
# Get unique list of files with AI usage
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
.results | map(.path) | unique | .[]'
```

### Example 4: Count by File

```bash
# Show count of findings per file
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
["FILE", "FINDINGS"],
(.results | group_by(.path) | map([
  (.[0].path | split("/") | last),
  "\(length)"
])) | .[] | @tsv' | column -t -s $'\t'
```

---

## Demo Scenarios

### Scenario 1: Security Audit Demo

**Objective:** Show how to find unauthorized AI usage in a codebase

```bash
echo "🔍 Starting Shadow AI Security Audit..."
echo ""

# Run scan
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
"📊 AUDIT RESULTS",
"═══════════════",
"Total Issues Found: \(.results | length)",
"Files Affected: \(.results | map(.path) | unique | length)",
"",
"🔴 Critical Issues: \(.results | map(select(.extra.severity == "ERROR")) | length)",
"🟡 Warnings: \(.results | map(select(.extra.severity == "WARNING")) | length)",
"🔵 Info: \(.results | map(select(.extra.severity == "INFO")) | length)",
"",
"📋 Breakdown by Detection Type:",
(.results | group_by(.check_id) | map("   • \(.[0].check_id | split(".") | last): \(length) occurrences") | join("\n"))
'
```

### Scenario 2: Compliance Check Demo

**Objective:** Generate a compliance report for stakeholders

```bash
#!/bin/bash
# compliance-check.sh

PROJECT=$1
OUTPUT_FILE="compliance-report-$(date +%Y%m%d).md"

echo "Running compliance check on: $PROJECT"

semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  "$PROJECT" \
  --json 2>/dev/null | jq -r '
"# AI Usage Compliance Report",
"",
"**Generated:** " + (now | strftime("%Y-%m-%d %H:%M:%S")),
"**Project:** " + "'$PROJECT'",
"",
"## Executive Summary",
"",
"- **Total AI Usage Detected:** \(.results | length) instances",
"- **Files with AI Code:** \(.results | map(.path) | unique | length)",
"- **Compliance Status:** " + (if (.results | length) > 0 then "⚠️ REVIEW REQUIRED" else "✅ COMPLIANT" end),
"",
"## Findings by Category",
"",
(.results | group_by(.extra.severity) | map(
  "### \(.[0].extra.severity)",
  "",
  (map("- \(.check_id | split(".") | last) in `\(.path | split("/") | last):\(.start.line)`") | join("\n")),
  ""
) | join("\n")),
"",
"## Recommendations",
"",
(if (.results | length) > 0 then
  "1. Review all detected AI usage for compliance with company policy",
  "2. Ensure proper API key management (no hardcoded keys)",
  "3. Document approved AI tools and usage patterns",
  "4. Update security guidelines for AI development"
else
  "✅ No unauthorized AI usage detected"
end)
' > "$OUTPUT_FILE"

echo "Report saved to: $OUTPUT_FILE"
open "$OUTPUT_FILE"
```

### Scenario 3: Developer Demo

**Objective:** Show developers what's being flagged

```bash
# Interactive scan with colored output
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
.results[] | 
"┌─────────────────────────────────────────",
"│ 🔍 \(.check_id | split(".") | last)",
"│ 📁 \(.path | split("/")[-2:] | join("/"))",
"│ 📍 Line \(.start.line):\(.start.col) → \(.end.line):\(.end.col)",
"│ ⚠️  \(.extra.severity): \(.extra.message)",
"├─────────────────────────────────────────",
"│ Code:",
((.extra.lines | split("\n")) | map("│   " + .) | join("\n")),
"└─────────────────────────────────────────",
""
'
```

---

## Advanced Usage

### Filter by File Type

```bash
# Scan only TypeScript files
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --include="*.ts" --include="*.tsx"
```

### Exclude Directories

```bash
# Exclude node_modules and test files
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --exclude="node_modules" \
  --exclude="*.test.js" \
  --exclude="*.spec.ts"
```

### Compare Two Scans

```bash
# Scan 1: Before changes
semgrep scan \
  --config p/shadow-ai-pro \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null > scan_before.json

# Make changes...

# Scan 2: After changes
semgrep scan \
  --config p/shadow-ai-pro \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null > scan_after.json

# Compare
echo "Findings before: $(jq '.results | length' scan_before.json)"
echo "Findings after: $(jq '.results | length' scan_after.json)"
```

### CI/CD Integration

```bash
# Exit with error if findings detected
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -e '.results | length == 0' || {
    echo "❌ Shadow AI usage detected! Failing build."
    exit 1
}
```

### Search for Specific Model Usage

```bash
# Find all gpt-4o-mini usage
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
.results[] | 
select(.extra.lines | contains("gpt-4o-mini")) | 
"📄 \(.path | split("/") | last):\(.start.line) → \(.extra.lines | split("\n") | first)"
'
```

### Generate Statistics

```bash
semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq '{
  statistics: {
    total_findings: (.results | length),
    total_files_scanned: (.paths.scanned | length),
    files_with_findings: (.results | map(.path) | unique | length),
    scan_percentage: ((.results | map(.path) | unique | length) / (.paths.scanned | length) * 100 | round),
    by_severity: (.results | group_by(.extra.severity) | map({
      severity: .[0].extra.severity,
      count: length,
      percentage: (length / ($total_count | tonumber) * 100 | round)
    })),
    by_language: (.results | group_by(.extra.metadata.category) | map({
      category: .[0].extra.metadata.category,
      count: length
    })),
    most_common_rule: (.results | group_by(.check_id) | max_by(length) | {
      rule: .[0].check_id,
      count: length
    }),
    most_affected_file: (.results | group_by(.path) | max_by(length) | {
      file: (.[0].path | split("/") | last),
      count: length
    })
  }
}' --argjson total_count "$(semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --json 2>/dev/null | jq '.results | length')"
```

---

## Quick Reference Commands

### Count Findings
```bash
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --json 2>/dev/null | jq '.results | length'
```

### List Affected Files
```bash
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --json 2>/dev/null | jq -r '.results[].path' | sort -u
```

### Get Severity Breakdown
```bash
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --json 2>/dev/null | jq -r '.results | group_by(.extra.severity) | map("\(.[0].extra.severity): \(length)") | .[]'
```

### Export to HTML (requires additional tool)
```bash
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --sarif -o report.sarif
# Then use a SARIF viewer or convert to HTML
```

---

## Troubleshooting

### No Results Found

If you get 0 results but expect findings:

```bash
# Run with verbose output
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --verbose

# Check what files are being scanned
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --json 2>/dev/null | jq '.paths.scanned[]'
```

### Too Many Results

```bash
# Filter by severity
semgrep scan --config p/shadow-ai-pro ~/Projects/ai-ui/ --severity ERROR --severity WARNING
```

### Performance Issues

```bash
# Run with limited rules for faster scanning
semgrep scan --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml ~/Projects/ai-ui/ --jobs 4
```

---

## Resources

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [Semgrep Registry](https://semgrep.dev/explore)
- [Shadow AI Detection Blog](https://semgrep.dev/blog/2024/detecting-shadow-ai)
- [Writing Custom Rules](https://semgrep.dev/docs/writing-rules/overview)

---

## Quick Demo Script

Save this as `demo.sh`:

```bash
#!/bin/bash
# Quick demonstration of shadow AI detection

clear
echo "🔍 Shadow AI Detection Demo"
echo "═══════════════════════════"
echo ""
read -p "Press Enter to scan for AI usage..."

semgrep scan \
  --config p/shadow-ai-pro \
  --config /Users/shayshimonov/Projects/ai-supply-chain/ai-supply-chain-poc/my-detect-openai.yaml \
  ~/Projects/ai-ui/ \
  --json 2>/dev/null | jq -r '
"",
"📊 Results:",
"   • Total Findings: \(.results | length)",
"   • Files Affected: \(.results | map(.path) | unique | length)",
"   • Severity: ERROR=\(.results | map(select(.extra.severity == "ERROR")) | length), WARNING=\(.results | map(select(.extra.severity == "WARNING")) | length), INFO=\(.results | map(select(.extra.severity == "INFO")) | length)",
"",
"📋 Top Issues:",
(.results[0:5][] | "   • \(.check_id | split(".") | last) in \(.path | split("/") | last):\(.start.line)"),
"",
"✅ Scan complete!"
'
```

Run with: `bash demo.sh`

---

**Last Updated:** $(date +%Y-%m-%d)

