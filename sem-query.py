#!/usr/bin/env python3
"""
Non-interactive wrapper for semantic-code-search (sem).

This script provides a non-interactive interface to the sem tool, allowing:
- JSON output for automation
- Text output for logs
- Token highlighting to show matched terms
- Match reasoning to explain why code was matched
- File output for saving results

Usage:
    python sem-query.py -p /path/to/repo 'your search query'
    python sem-query.py -p /path/to/repo --json 'your query' > results.json
    python sem-query.py -p /path/to/repo -o output.txt 'your query'

Options:
    -p, --path PATH          Path to the git repository (required)
    -n, --num-results N      Number of results to return (default: 5)
    -o, --output FILE        Save output to file
    -x, --extension EXT      Filter by file extension
    --json                   Output as JSON
    --no-code                Hide code snippets in output
"""

import sys
import os
import argparse
import json
import re
from pathlib import Path

# Suppress MPS warning on Apple Silicon
os.environ['PYTORCH_MPS_DISABLE'] = '1'

# Add semantic_code_search to path
sys.path.insert(0, str(Path(__file__).parent / 'venv/lib/python3.11/site-packages'))

from semantic_code_search.search import do_search
from sentence_transformers import SentenceTransformer
import argparse as arg_module

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'


def strip_ansi(text):
    """Remove ANSI color codes from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def highlight_code(code_text, query_text):
    """
    Highlight matching tokens in code with color codes.
    Returns code with ANSI color highlighting.
    """
    matches, highlighted = find_matching_tokens(query_text, code_text)
    
    if not highlighted:
        return code_text
    
    # Sort by length (longest first) to avoid partial replacements
    highlighted_sorted = sorted(highlighted, key=len, reverse=True)
    
    result = code_text
    for token in highlighted_sorted:
        # Use word boundaries for exact matches
        pattern = re.compile(r'\b' + re.escape(token) + r'\b', re.IGNORECASE)
        result = pattern.sub(f'{Colors.YELLOW}{Colors.BOLD}{token}{Colors.RESET}', result)
    
    return result


def find_matching_tokens(query_text, code_text):
    """
    Find tokens from the query that appear in the code (case-insensitive).
    Returns matched tokens and their locations in the code.
    """
    code_lower = code_text.lower()
    
    # Extract meaningful tokens from query (remove common words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                  'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                  'including', 'until', 'against', 'among', 'throughout', 'despite',
                  'towards', 'upon', 'concerning', 'how', 'where', 'what', 'usage', 'using'}
    
    query_tokens = [t.lower() for t in re.findall(r'\b\w+\b', query_text) 
                    if t.lower() not in stop_words and len(t) > 2]
    
    matches = []
    highlighted_tokens = []
    
    # Find exact token matches
    for token in query_tokens:
        # Check for exact match
        if token in code_lower:
            matches.append(token)
            # Get all instances with original casing
            for match in re.finditer(r'\b' + re.escape(token) + r'\w*', code_lower, re.IGNORECASE):
                highlighted_tokens.append(code_text[match.start():match.end()])
    
    # Find tokens that are part of larger identifiers (camelCase, snake_case, etc.)
    for token in query_tokens:
        # Check if token appears in camelCase (e.g., 'open' in 'openai')
        pattern = re.compile(r'\b\w*' + re.escape(token) + r'\w*', re.IGNORECASE)
        for match in pattern.finditer(code_lower):
            word = code_text[match.start():match.end()]
            if word.lower() not in [m.lower() for m in highlighted_tokens]:
                if len(word) > len(token):  # It's part of a larger word
                    highlighted_tokens.append(word)
    
    return list(set(matches)), list(set(highlighted_tokens))


def explain_match(query_text, code_text):
    """
    Generate a human-readable explanation of why the code matched.
    """
    matches, highlighted = find_matching_tokens(query_text, code_text)
    
    if not matches and not highlighted:
        return "Semantic similarity"
    
    reasons = []
    
    # Show direct matches
    if matches:
        if len(matches) <= 3:
            reasons.append(f"Contains '{', '.join(matches)}'")
        else:
            match_list = ', '.join(matches[:3])
            reasons.append(f"Contains '{match_list}' +{len(matches)-3} more")
    
    # Show tokens that are part of larger identifiers
    compound_tokens = [h for h in highlighted if h.lower() not in [m.lower() for m in matches]]
    if compound_tokens:
        if len(compound_tokens) <= 3:
            reasons.append(f"Related: {', '.join(compound_tokens)}")
        else:
            token_list = ', '.join(compound_tokens[:3])
            reasons.append(f"Related: {token_list} +{len(compound_tokens)-3} more")
    
    return ' | '.join(reasons) if reasons else "Semantic similarity"


def format_text_output(results, query_text, show_code=True, use_color=True):
    """Format results as human-readable text"""
    output = []
    
    header = f"🔍 Semantic Search Results for: '{query_text}'"
    if use_color:
        output.append(f"{Colors.BOLD}{Colors.CYAN}{header}{Colors.RESET}")
    else:
        output.append(header)
    
    output.append("=" * 80)
    output.append("")
    
    for i, result in enumerate(results, 1):
        file_path = result['file']
        line_num = result['line']
        score = result['score']
        code = result['code']
        
        # Header for this result
        if use_color:
            output.append(f"{Colors.BOLD}{i}. {Colors.GREEN}{file_path}:{line_num}{Colors.RESET} "
                         f"{Colors.GRAY}(score: {score:.4f}){Colors.RESET}")
        else:
            output.append(f"{i}. {file_path}:{line_num} (score: {score:.4f})")
        
        # Show match reasoning
        reason = explain_match(query_text, code)
        if use_color:
            output.append(f"    {Colors.MAGENTA}💡 Match: {reason}{Colors.RESET}")
        else:
            output.append(f"    💡 Match: {reason}")
        
        output.append("")
        
        # Show code with highlighting
        if show_code:
            if use_color:
                highlighted_code = highlight_code(code, query_text)
                for line in highlighted_code.split('\n'):
                    output.append(f"  {Colors.BLUE}➤{Colors.RESET} │ {line}")
            else:
                for line in code.split('\n'):
                    output.append(f"  ➤ │ {line}")
            output.append("")
        
        output.append("─" * 80)
        output.append("")
    
    return '\n'.join(output)


def format_json_output(results, query_text):
    """Format results as JSON"""
    json_results = {
        'query': query_text,
        'total_results': len(results),
        'results': []
    }
    
    for result in results:
        # Get highlighted tokens to mark them in the code
        matches, highlighted = find_matching_tokens(query_text, result['code'])
        
        json_results['results'].append({
            'file': result['file'],
            'line': result['line'],
            'score': result['score'],
            'code': result['code'],
            'match_reason': explain_match(query_text, result['code']),
            'matched_tokens': matches,
            'highlighted_tokens': highlighted
        })
    
    return json.dumps(json_results, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Non-interactive semantic code search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python sem-query.py -p ~/my-project 'authentication logic'
    python sem-query.py -p ~/my-project --json 'API endpoints' > results.json
    python sem-query.py -p ~/my-project -n 10 -x py 'error handling'
    python sem-query.py -p ~/my-project -o output.txt 'database queries'
        """
    )
    
    parser.add_argument('query', help='Search query (natural language)')
    parser.add_argument('-p', '--path', required=True, help='Path to git repository')
    parser.add_argument('-n', '--num-results', type=int, default=5, 
                       help='Number of results (default: 5)')
    parser.add_argument('-o', '--output', help='Save output to file')
    parser.add_argument('-x', '--extension', help='Filter by file extension')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--no-code', action='store_true', help='Hide code snippets')
    parser.add_argument('--no-color', action='store_true', help='Disable color output')
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.path).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    # Check for embeddings
    embeddings_file = repo_path / '.embeddings'
    if not embeddings_file.exists():
        print(f"Error: No embeddings found at {repo_path}", file=sys.stderr)
        print(f"Run: venv/bin/sem --embed -p {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    # Load model
    model_name = 'krlvi/sentence-msmarco-bert-base-dot-v5-nlpl-code_search_net'
    try:
        model = SentenceTransformer(model_name, device='cpu')
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create args for do_search
    search_args = arg_module.Namespace(
        path_to_repo=str(repo_path),
        query_text=args.query,
        num_results=args.num_results,
        extension=args.extension,
        editor=None
    )
    
    # Perform search
    try:
        results = do_search(search_args, model)
    except Exception as e:
        print(f"Error during search: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Format output
    use_color = not args.no_color and not args.json and sys.stdout.isatty()
    
    if args.json:
        output_text = format_json_output(results, args.query)
    else:
        show_code = not args.no_code
        output_text = format_text_output(results, args.query, show_code, use_color)
    
    # Write output
    if args.output:
        # Strip ANSI codes when writing to file
        clean_output = strip_ansi(output_text) if not args.json else output_text
        with open(args.output, 'w') as f:
            f.write(clean_output)
        print(f"Results saved to: {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == '__main__':
    main()
