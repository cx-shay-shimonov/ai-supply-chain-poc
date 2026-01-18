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
        r'\bgpt-5(?:-\w+)*\b',  # GPT-5 models (check first for specificity)
        r'\bgpt-4[o]?(?:-\w+)*\b',
        r'\bgpt-3\.5-turbo(?:-\w+)*\b',
        r'\bgpt-3(?:-\w+)*\b',
        r'\bo1(?:-\w+)*\b',
        r'\bo3(?:-\w+)*\b',
        r'\bo4(?:-\w+)*\b',
        r'\btext-embedding(?:-\w+)*\b',
        r'\bdall-e(?:-\d+)?\b',  # DALL-E models
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
        r'openai\.(?:chat|completions?|embeddings?|images)',  # Added images for DALL-E
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
    Also detects models constructed from concatenated variables.
    
    Args:
        text: Text to search
        patterns: Dictionary of category -> list of regex patterns
        normalize_categories: Categories where matches should be lowercased
        
    Returns:
        Dictionary of category -> set of assets
    """
    if normalize_categories is None:
        normalize_categories = {'providers', 'apis'}
    
    assets = defaultdict(set)
    
    # Standard pattern matching
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                asset = match.group(0)
                if category in normalize_categories:
                    asset = asset.lower()
                assets[category].add(asset)
    
    # Detect concatenated model patterns like:
    # const modelName = 'gpt'; const modelVersion = '4o-mini';
    # Results in: gpt-4o-mini
    concatenated_models = _detect_concatenated_models(text)
    for model in concatenated_models:
        # Determine category based on model name
        model_lower = model.lower()
        if any(x in model_lower for x in ['gpt', 'dall-e', 'o1', 'o3', 'o4']):
            assets['openai_models'].add(model)
        elif 'claude' in model_lower:
            assets['anthropic_models'].add(model)
        elif 'gemini' in model_lower or 'palm' in model_lower:
            assets['google_models'].add(model)
        elif 'llama' in model_lower:
            assets['meta_models'].add(model)
    
    return assets


def _detect_concatenated_models(text: str) -> List[str]:
    """
    Detect AI models constructed from concatenated variables or template literals.
    
    Examples:
        modelName = 'gpt'; modelVersion = '4o-mini' => 'gpt-4o-mini'
        model = 'claude'; version = '3-5-sonnet' => 'claude-3-5-sonnet'
        `${modelName}-${modelVersion}` with definitions => 'gpt-4o-mini'
    """
    found_models = []
    
    # Pattern 1: Explicit modelName/modelVersion declarations
    name_pattern = r"(?:const|let|var)\s+modelName\s*=\s*['\"]([^'\"]+)['\"]"
    version_pattern = r"(?:const|let|var)\s+modelVersion\s*=\s*['\"]([^'\"]+)['\"]"
    
    name_match = re.search(name_pattern, text)
    version_match = re.search(version_pattern, text)
    
    if name_match and version_match:
        model_name = name_match.group(1)
        model_version = version_match.group(1)
        full_model = f"{model_name}-{model_version}"
        found_models.append(full_model)
    
    # Pattern 2: Direct variable assignments with model names
    # const model1 = 'gpt-4o-mini'
    direct_model_pattern = r"(?:const|let|var)\s+model\d*\s*=\s*['\"]([a-z0-9\-\.]+)['\"]"
    for match in re.finditer(direct_model_pattern, text):
        potential_model = match.group(1)
        # Check if it looks like an AI model name
        if any(x in potential_model.lower() for x in ['gpt', 'claude', 'gemini', 'llama', 'dall-e', 'mistral', 'deepseek']):
            found_models.append(potential_model)
    
    # Pattern 3: Template literals that reference model variables
    # Detect ${modelName}-${modelVersion} pattern and add a generic note
    template_pattern = r'\$\{modelName\}\s*-\s*\$\{modelVersion\}'
    if re.search(template_pattern, text) and not (name_match and version_match):
        # Template found but no definitions - add a placeholder to indicate this pattern exists
        found_models.append('[concatenated-model-variable]')
    
    return found_models


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
    asset_locations = defaultdict(list)  # Track where each asset appears
    
    for result in data.get('results', []):
        code = result.get('code', '')
        file_path = result.get('file', '')
        file_name = file_path.split('/')[-1]
        line = result.get('line', 0)
        column = result.get('column', 0)
        score = result.get('score', 0)
        certainty = result.get('certainty_percent', 0)
        certainty_label = result.get('certainty', '')
        
        # Extract assets from code
        result_assets = extract_assets_from_text(code.lower(), ASSET_PATTERNS)
        
        # Collect found assets for this result
        found_assets = []
        for category, asset_set in result_assets.items():
            for asset in asset_set:
                assets[category].add(asset)
                found_assets.append(asset)
                locations[asset].append({
                    'file': file_name,
                    'line': line,
                    'score': round(score, 4),
                    'certainty_percent': certainty
                })
                # Track with full path for clickable links
                asset_locations[asset].append({
                    'file': file_path,
                    'line': line,
                    'column': column,
                    'certainty': certainty_label,
                    'certainty_percent': certainty
                })
        
        # Store raw result with full path and metadata
        raw_results.append({
            'file': file_path,
            'line': line,
            'column': column,
            'score': round(score, 4),
            'certainty': certainty_label,
            'certainty_percent': certainty,
            'code_preview': code[:150] + ('...' if len(code) > 150 else ''),
            'assets': found_assets,
            'matched_tokens': result.get('matched_tokens', []),
            'match_reason': result.get('match_reason', '')
        })
    
    # Convert to sorted lists
    assets_dict = {k: sorted(list(v)) for k, v in assets.items()}
    total_distinct = sum(len(v) for v in assets_dict.values())
    total_occurrences = sum(len(v) for v in locations.values())
    
    # Format asset locations for easy clicking
    asset_locations_formatted = {
        asset: sorted(locs, key=lambda x: (x['file'], x['line']))
        for asset, locs in sorted(asset_locations.items())
    }
    
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
        'asset_locations': asset_locations_formatted,  # Clickable file:line:column paths
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

