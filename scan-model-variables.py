#!/usr/bin/env python3
"""
Additional AI Asset Scanner - Scans source files for variable declarations
that construct AI model names through concatenation.

This complements the semantic search by finding models defined as:
  const modelName = 'gpt';
  const modelVersion = '4o-mini';
  const model = `${modelName}-${modelVersion}`; // => gpt-4o-mini
"""

import re
import sys
import json
from pathlib import Path

def scan_file_for_model_variables(file_path):
    """Scan a single file for model variable declarations."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return []
    
    found_models = []
    
    # Pattern: modelName and modelVersion declarations
    name_pattern = r"(?:const|let|var)\s+modelName\s*=\s*['\"]([^'\"]+)['\"]"
    version_pattern = r"(?:const|let|var)\s+modelVersion\s*=\s*['\"]([^'\"]+)['\"]"
    
    name_match = re.search(name_pattern, content)
    version_match = re.search(version_pattern, content)
    
    if name_match and version_match:
        model_name = name_match.group(1)
        model_version = version_match.group(1)
        full_model = f"{model_name}-{model_version}"
        
        # Find line numbers
        name_line = content[:name_match.start()].count('\n') + 1
        version_line = content[:version_match.start()].count('\n') + 1
        
        found_models.append({
            'model': full_model,
            'file': str(file_path),
            'name_line': name_line,
            'version_line': version_line,
            'type': 'concatenated'
        })
    
    # Pattern: Direct model assignments
    direct_pattern = r"(?:const|let|var)\s+(model\d*)\s*=\s*['\"]([a-z0-9\-\.]+)['\"]"
    for match in re.finditer(direct_pattern, content):
        var_name = match.group(1)
        potential_model = match.group(2)
        
        # Check if it looks like an AI model
        if any(x in potential_model.lower() for x in ['gpt', 'claude', 'gemini', 'llama', 'dall-e', 'mistral', 'deepseek']):
            line_num = content[:match.start()].count('\n') + 1
            found_models.append({
                'model': potential_model,
                'file': str(file_path),
                'line': line_num,
                'variable': var_name,
                'type': 'direct'
            })
    
    return found_models

def scan_directory(target_dir):
    """Scan all JavaScript/TypeScript/Python files in directory."""
    target_path = Path(target_dir)
    all_models = []
    
    # File extensions to scan
    extensions = ['*.js', '*.ts', '*.jsx', '*.tsx', '*.py']
    
    for ext in extensions:
        for file_path in target_path.rglob(ext):
            # Skip node_modules, build directories
            if any(skip in str(file_path) for skip in ['node_modules', 'dist', 'build', '.git', '__pycache__']):
                continue
            
            models = scan_file_for_model_variables(file_path)
            all_models.extend(models)
    
    return all_models

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'No target directory provided'}))
        sys.exit(1)
    
    target = sys.argv[1]
    results = scan_directory(target)
    
    # Output as JSON
    print(json.dumps({
        'variable_models': results,
        'count': len(results)
    }, indent=2))
