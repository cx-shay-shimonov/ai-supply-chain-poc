#!/usr/bin/env python3
"""
AI Asset Extractor - Common utilities for extracting AI models and providers
from semantic search and static analysis results.
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Set, Tuple


# Comprehensive AI asset patterns for ALL providers
ASSET_PATTERNS = {
    'openai_models': [
        r'\bgpt-4[o]?(?:-\w+)*\b',
        r'\bgpt-3\.5-turbo(?:-\w+)*\b',
        r'\bgpt-3(?:-\w+)*\b',
        r'\bo1(?:-\w+)*\b',
        r'\bo3(?:-\w+)*\b',
        r'\bo4(?:-\w+)*\b',
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
    'mistral_models': [
        r'\bmistral(?:-\w+)*\b',
        r'\bmixtral(?:-\w+)*\b',
    ],
    'providers': [
        r'\bopenai\b',
        r'\banthropics?\b',
        r'\bOpenAI\b',
        r'\bAnthropic\b',
        r'\bChatGPT\b',
        r'\bGoogle AI\b',
        r'\bMeta AI\b',
        r'\bCohere\b',
        r'\bMistral\b',
    ],
    'apis': [
        r'openai\.(?:chat|completions?|embeddings?)',
        r'anthropic\.(?:messages|completions?)',
    ]
}


def extract_assets_from_text(
    text: str,
    patterns: Dict[str, List[str]],
    normalize_categories: Set[str] = None
) -> Tuple[Dict[str, Set[str]], Dict[str, List]]:
    """
    Extract AI assets from text using regex patterns.
    
    Args:
        text: Text to search
        patterns: Dictionary of category -> list of regex patterns
        normalize_categories: Categories where matches should be lowercased
        
    Returns:
        Tuple of (assets_dict, locations_dict)
    """
    if normalize_categories is None:
        normalize_categories = {'providers', 'apis'}
    
    assets = defaultdict(set)
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                asset = match.group(0)
                if category in normalize_categories:
                    asset = asset.lower()
                assets[category].add(asset)
    
    return assets


def extract_from_semantic_results(results_file: str) -> Dict:
    """
    Extract AI assets from semantic search results.
    
    Args:
        results_file: Path to semantic search JSON results
        
    Returns:
        Dictionary with tool, summary, raw_results, and assets
    """
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    assets = defaultdict(set)
    locations = defaultdict(list)
    raw_results = []
    
    for result in data.get('results', []):
        code = result.get('code', '')
        file_path = result.get('file', '').split('/')[-1]
        line = result.get('line', 0)
        score = result.get('score', 0)
        certainty = result.get('certainty_percent', 0)
        certainty_label = result.get('certainty', '')
        
        # Store raw result with snippet
        raw_results.append({
            'file': file_path,
            'line': line,
            'score': round(score, 4),
            'certainty': certainty_label,
            'certainty_percent': certainty,
            'snippet': code[:200] + ('...' if len(code) > 200 else '')  # First 200 chars
        })
        
        # Extract assets from code
        result_assets = extract_assets_from_text(code.lower(), ASSET_PATTERNS)
        
        # Merge assets and track locations
        for category, asset_set in result_assets.items():
            for asset in asset_set:
                assets[category].add(asset)
                locations[asset].append({
                    'file': file_path,
                    'line': line,
                    'score': round(score, 4),
                    'certainty_percent': certainty
                })
    
    # Convert to sorted lists
    assets_dict = {k: sorted(list(v)) for k, v in assets.items()}
    total_distinct = sum(len(v) for v in assets_dict.values())
    total_occurrences = sum(len(v) for v in locations.values())
    
    return {
        'tool': 'Semantic Search (sem)',
        'query': data.get('query', ''),
        'repository': data.get('repository', '').split('/')[-1] if data.get('repository') else '',
        'summary': {
            'total_distinct_assets': total_distinct,
            'total_occurrences': total_occurrences,
            'results_analyzed': len(data.get('results', [])),
            'breakdown': {k: len(v) for k, v in assets_dict.items() if v}
        },
        'raw_results': raw_results,
        'assets': assets_dict,
        'top_locations': {
            k: v[:3] 
            for k, v in sorted(locations.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        }
    }


def extract_from_semgrep_results(results_file: str) -> Dict:
    """
    Extract AI assets from Semgrep static analysis results.
    
    Args:
        results_file: Path to Semgrep JSON results
        
    Returns:
        Dictionary with tool, summary, raw_results, assets, and rules
    """
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    assets = defaultdict(set)
    locations = defaultdict(list)
    rules_triggered = defaultdict(int)
    raw_results = []
    
    for result in data.get('results', []):
        rule_id = result.get('check_id', '').split('.')[-1]
        path = result.get('path', '').split('/')[-1]
        line = result.get('start', {}).get('line', 0)
        severity = result.get('extra', {}).get('severity', 'UNKNOWN')
        message = result.get('extra', {}).get('message', '')
        snippet = result.get('extra', {}).get('lines', '')
        search_text = (message + ' ' + snippet).lower()
        
        rules_triggered[rule_id] += 1
        
        # Store raw result with snippet
        raw_results.append({
            'file': path,
            'line': line,
            'rule': rule_id,
            'severity': severity,
            'message': message,
            'snippet': snippet[:200] + ('...' if len(snippet) > 200 else '')  # First 200 chars
        })
        
        # Extract assets from text
        result_assets = extract_assets_from_text(search_text, ASSET_PATTERNS)
        
        # Merge assets and track locations
        for category, asset_set in result_assets.items():
            for asset in asset_set:
                assets[category].add(asset)
                locations[asset].append({
                    'file': path,
                    'line': line,
                    'severity': severity,
                    'rule': rule_id
                })
    
    # Convert to sorted lists
    assets_dict = {k: sorted(list(v)) for k, v in assets.items()}
    total_distinct = sum(len(v) for v in assets_dict.values())
    total_occurrences = sum(len(v) for v in locations.values())
    
    return {
        'tool': 'Static Analysis (Semgrep)',
        'version': data.get('version', ''),
        'summary': {
            'total_distinct_assets': total_distinct,
            'total_occurrences': total_occurrences,
            'findings_analyzed': len(data.get('results', [])),
            'rules_triggered': len(rules_triggered),
            'breakdown': {k: len(v) for k, v in assets_dict.items() if v}
        },
        'raw_results': raw_results,
        'assets': assets_dict,
        'rules': dict(sorted(rules_triggered.items(), key=lambda x: x[1], reverse=True)),
        'top_locations': {
            k: v[:3] 
            for k, v in sorted(locations.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        }
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python ai_asset_extractor.py <type> <results_file>")
        print("  type: 'semantic' or 'semgrep'")
        print("  results_file: Path to JSON results file")
        sys.exit(1)
    
    extract_type = sys.argv[1]
    results_file = sys.argv[2]
    
    if extract_type == 'semantic':
        output = extract_from_semantic_results(results_file)
    elif extract_type == 'semgrep':
        output = extract_from_semgrep_results(results_file)
    else:
        print(f"Error: Unknown type '{extract_type}'. Use 'semantic' or 'semgrep'")
        sys.exit(1)
    
    print(json.dumps(output, indent=2))

