#!/usr/bin/env python3
"""
Tree-sitter based AI Model Scanner
Scans source code for AI model name references using syntax-aware parsing
Detects string concatenations, variable tracking, and API call usage
"""

import os
import sys
import json
import argparse
from pathlib import Path
from tree_sitter import Parser, Language
import tree_sitter_javascript as tsjs
import tree_sitter_python as tspy

# Load model names from rules
script_dir = Path(__file__).parent
with open(script_dir / 'rules' / 'ai-models.json', 'r') as f:
    MODEL_RULES = json.load(f)

class ModelScanner:
    def __init__(self, model_rules):
        self.model_rules = model_rules
        self.findings = []
        self.variable_assignments = {}  # Track variable -> value mappings
        self.model_name_parts = set(model_rules.get('model_name_parts', []))
        self.api_patterns = model_rules.get('api_call_patterns', {})
        
        # Initialize parsers  
        self.js_parser = Parser(Language(tsjs.language()))
        self.py_parser = Parser(Language(tspy.language()))
    
    def scan_directory(self, dir_path):
        """Recursively scan directory for source files"""
        dir_path = Path(dir_path)
        skip_dirs = {'node_modules', '.git', 'dist', 'build', '.embeddings', 'venv', '__pycache__'}
        
        for root, dirs, files in os.walk(dir_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                ext = Path(file).suffix
                if ext in ['.js', '.jsx', '.ts', '.tsx', '.py']:
                    file_path = Path(root) / file
                    self.scan_file(file_path)
    
    def scan_file(self, file_path):
        """Scan a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return
        
        ext = file_path.suffix
        try:
            if ext in ['.js', '.jsx', '.ts', '.tsx']:
                tree = self.js_parser.parse(bytes(source_code, 'utf8'))
            elif ext == '.py':
                tree = self.py_parser.parse(bytes(source_code, 'utf8'))
            else:
                return
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            return
        
        # DON'T reset variable tracking - keep across files
        # self.variable_assignments = {}
        
        # Traverse AST
        self.traverse_node(tree.root_node, source_code, str(file_path))
    
    def traverse_node(self, node, source_code, file_path):
        """Recursively traverse AST nodes"""
        # Check for string literals
        if node.type in ['string', 'string_fragment']:
            self.check_string_literal(node, source_code, file_path)
        
        # Check for template strings (concatenation detection)
        if node.type == 'template_string':
            self.check_template_literal(node, source_code, file_path)
        
        # Check for binary expressions (string concatenation with +)
        if node.type == 'binary_expression':
            self.check_binary_expression(node, source_code, file_path)
        
        # Check for variable declarations/assignments
        if node.type in ['variable_declarator', 'assignment', 'assignment_expression']:
            self.track_variable_assignment(node, source_code, file_path)
        
        # Check for augmented assignment (+=, etc.)
        if node.type == 'augmented_assignment_expression':
            self.track_augmented_assignment(node, source_code, file_path)
        
        # Check for function call arguments
        if node.type in ['call_expression', 'call']:
            self.check_function_call(node, source_code, file_path)
        
        # Recurse into children
        for child in node.children:
            self.traverse_node(child, source_code, file_path)
    
    def check_string_literal(self, node, source_code, file_path):
        """Check if string literal contains a model name or part"""
        text = source_code[node.start_byte:node.end_byte]
        clean_text = text.strip('\'"` ')
        
        # Check exact matches
        for model_name in self.model_rules['exact_matches']:
            if clean_text == model_name:
                self.findings.append({
                    'type': 'string_literal',
                    'model': model_name,
                    'file': file_path,
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1] + 1,
                    'code': self.get_line_context(source_code, node.start_point[0])
                })
                return
        
        # Check partial patterns
        for pattern in self.model_rules['partial_patterns']:
            if pattern in clean_text:
                self.findings.append({
                    'type': 'string_literal',
                    'model': clean_text,
                    'pattern': pattern,
                    'file': file_path,
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1] + 1,
                    'code': self.get_line_context(source_code, node.start_point[0])
                })
                return
        
        # Check if it's a model name part (for tracking concatenations)
        if clean_text in self.model_name_parts:
            # Don't report these as findings yet, but note them for potential concatenation
            pass
    
    def check_binary_expression(self, node, source_code, file_path):
        """Check for string concatenation with + operator"""
        operator = None
        parts = []
        
        for child in node.children:
            if child.type == '+':
                operator = '+'
            elif child.type == 'string':
                # Direct string literal
                text = source_code[child.start_byte:child.end_byte].strip('\'"` ')
                parts.append(text)
            elif child.type == 'identifier':
                # Variable reference - resolve it if we can
                var_name = source_code[child.start_byte:child.end_byte]
                if var_name in self.variable_assignments:
                    var_value = self.variable_assignments[var_name]['value']
                    parts.append(var_value.strip('\'"` '))
                else:
                    parts.append(var_name)
            elif child.type == 'binary_expression':
                # Nested binary expression - recurse
                # This handles cases like: a + b + c
                nested_result = self.extract_binary_parts(child, source_code)
                if nested_result:
                    parts.extend(nested_result)
        
        if operator == '+' and len(parts) >= 2:
            # Check if concatenation forms a model name pattern
            combined = ''.join(parts)
            for pattern in self.model_rules['partial_patterns']:
                if pattern in combined:
                    self.findings.append({
                        'type': 'string_concatenation',
                        'model': 'constructed',
                        'pattern': pattern,
                        'components': parts,
                        'file': file_path,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1] + 1,
                        'code': self.get_line_context(source_code, node.start_point[0]),
                        'note': f'Model name constructed from: {", ".join(parts)}'
                    })
                    return
    
    def extract_binary_parts(self, node, source_code):
        """Helper to extract parts from binary expression recursively"""
        parts = []
        for child in node.children:
            if child.type == 'string':
                parts.append(source_code[child.start_byte:child.end_byte].strip('\'"` '))
            elif child.type == 'identifier':
                var_name = source_code[child.start_byte:child.end_byte]
                if var_name in self.variable_assignments:
                    parts.append(self.variable_assignments[var_name]['value'].strip('\'"` '))
                else:
                    parts.append(var_name)
            elif child.type == 'binary_expression':
                nested = self.extract_binary_parts(child, source_code)
                if nested:
                    parts.extend(nested)
        return parts
    
    def check_template_literal(self, node, source_code, file_path):
        """Check template literals for model name patterns and track parts"""
        text = source_code[node.start_byte:node.end_byte]
        
        # Extract all parts from template literal
        template_parts = []
        substitution_vars = []
        
        for child in node.children:
            if child.type == 'template_string':
                continue
            elif 'substitution' in child.type:
                # Extract the expression inside ${}
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        var_name = source_code[subchild.start_byte:subchild.end_byte]
                        substitution_vars.append(var_name)
                        # Check if we know this variable's value
                        if var_name in self.variable_assignments:
                            template_parts.append(self.variable_assignments[var_name]['value'])
                        else:
                            template_parts.append(f'${{{var_name}}}')
            elif child.type in ['string_fragment', 'template_chars']:
                part = source_code[child.start_byte:child.end_byte]
                template_parts.append(part)
        
        # Check if template contains or constructs model name patterns
        for pattern in self.model_rules['partial_patterns']:
            if pattern in text or any(pattern in str(part) for part in template_parts):
                self.findings.append({
                    'type': 'template_literal',
                    'model': 'constructed',
                    'pattern': pattern,
                    'file': file_path,
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1] + 1,
                    'code': self.get_line_context(source_code, node.start_point[0]),
                    'components': template_parts,
                    'variables': substitution_vars
                })
                return
    
    def track_variable_assignment(self, node, source_code, file_path):
        """Track variable assignments to model names"""
        var_name = None
        value_node = None
        value_text = None
        is_template = False
        is_binary = False
        
        # Find variable name and value
        for child in node.children:
            if child.type in ['identifier', 'name']:
                if var_name is None:  # First identifier is the variable name
                    var_name = source_code[child.start_byte:child.end_byte]
                elif value_node is None:  # Second identifier is the value (variable reference)
                    value_node = child
                    value_text = source_code[child.start_byte:child.end_byte]
            elif child.type in ['string', 'string_fragment', 'template_string', 'binary_expression']:
                if value_node is None:
                    value_node = child
                    value_text = source_code[child.start_byte:child.end_byte]
                    if child.type == 'template_string':
                        is_template = True
                    elif child.type == 'binary_expression':
                        is_binary = True
        
        if not var_name:
            return
        
        # Check if template string contains model pattern
        template_has_model = False
        template_components = []
        binary_components = []
        
        if is_template and value_node:
            # Extract variables used in template
            for child in value_node.children:
                if child.type == 'template_substitution':
                    for subchild in child.children:
                        if subchild.type == 'identifier':
                            sub_var = source_code[subchild.start_byte:subchild.end_byte]
                            template_components.append(sub_var)
                            # Check if this variable contains a model part
                            if sub_var in self.variable_assignments:
                                var_value = self.variable_assignments[sub_var].get('value', '')
                                if var_value in self.model_name_parts:
                                    template_has_model = True
        
        # Check if binary expression contains model parts
        binary_has_model = False
        if is_binary and value_node:
            binary_components = self.extract_binary_parts(value_node, source_code)
            # Check if any component is a model part
            for comp in binary_components:
                if comp in self.model_name_parts:
                    binary_has_model = True
                    break
        
        # Store ALL variable assignments for tracking
        stored_value = None
        if value_node:
            clean_value = value_text.strip('\'"` ') if value_text else value_text
            
            # If the value is just an identifier (variable reference), resolve it
            if value_node.type == 'identifier' and clean_value in self.variable_assignments:
                # Use the resolved value instead
                clean_value = self.variable_assignments[clean_value]['value']
            
            stored_value = clean_value  # Save for later use
            
            self.variable_assignments[var_name] = {
                'value': clean_value,
                'file': file_path,
                'line': node.start_point[0] + 1,
                'usage_locations': [],
                'is_template': is_template,
                'is_binary': is_binary,
                'template_components': template_components if is_template else None,
                'binary_components': binary_components if is_binary else None
            }
        
        # Check if value is a model name or part (use stored_value, not value_text)
        if stored_value:
            found_model = None
            is_model_part = False
            
            # Check exact matches
            for model_name in self.model_rules['exact_matches']:
                if stored_value == model_name:
                    found_model = model_name
                    break
            
            # Check partial patterns
            if not found_model:
                for pattern in self.model_rules['partial_patterns']:
                    if pattern in stored_value:
                        found_model = stored_value
                        break
            
            # Check if it's a model name part
            if not found_model and stored_value in self.model_name_parts:
                found_model = stored_value
                is_model_part = True
            
            # Check if template constructs a model
            if not found_model and template_has_model:
                found_model = 'constructed'
                is_model_part = False
            
            # Check if binary expression constructs a model
            if not found_model and binary_has_model:
                found_model = 'constructed'
                is_model_part = False
            
            if found_model:
                finding = {
                    'type': 'variable_assignment',
                    'model': found_model,
                    'variable': var_name,
                    'file': file_path,
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1] + 1,
                    'code': self.get_line_context(source_code, node.start_point[0]),
                    'assigned_value': value_text
                }
                
                if is_model_part:
                    finding['is_model_part'] = True
                    finding['note'] = 'Partial model name - may be used in concatenation'
                
                if is_template and template_components:
                    finding['is_template_construction'] = True
                    finding['template_variables'] = template_components
                    finding['note'] = f'Model name constructed from template using: {", ".join(template_components)}'
                
                if is_binary and binary_components:
                    finding['is_binary_construction'] = True
                    finding['binary_components'] = binary_components
                    finding['note'] = f'Model name constructed from binary expression: {" + ".join(binary_components)}'
                
                self.findings.append(finding)
    
    def track_augmented_assignment(self, node, source_code, file_path):
        """Track compound assignments like x += y"""
        var_name = None
        operator = None
        new_value = None
        
        for child in node.children:
            if child.type == 'identifier' and var_name is None:
                var_name = source_code[child.start_byte:child.end_byte]
            elif child.type in ['+=', '-=', '*=']:
                operator = source_code[child.start_byte:child.end_byte]
            elif child.type in ['string', 'identifier']:
                # For strings, we need to extract the actual string content
                if child.type == 'string':
                    # Extract string_fragment from string node
                    for subchild in child.children:
                        if subchild.type == 'string_fragment':
                            new_value = source_code[subchild.start_byte:subchild.end_byte]
                            break
                    if new_value is None:
                        new_value = source_code[child.start_byte:child.end_byte].strip('\'"` ')
                else:
                    # It's an identifier - resolve it
                    new_value_text = source_code[child.start_byte:child.end_byte]
                    if new_value_text in self.variable_assignments:
                        new_value = self.variable_assignments[new_value_text]['value'].strip('\'"` ')
                    else:
                        new_value = new_value_text
        
        if var_name and operator == '+=' and new_value is not None:
            # Get current value
            if var_name in self.variable_assignments:
                current_value = self.variable_assignments[var_name]['value'].strip('\'"` ')
                # Combine values
                combined_value = current_value + new_value
                
                # Update the variable assignment
                self.variable_assignments[var_name]['value'] = combined_value
                self.variable_assignments[var_name]['line'] = node.start_point[0] + 1
                
                # Check if the combined value matches a model pattern
                found_model = None
                for pattern in self.model_rules['partial_patterns']:
                    if pattern in combined_value:
                        found_model = 'constructed'
                        break
                
                # Check if it's now a complete model name
                if not found_model:
                    for model_name in self.model_rules['exact_matches']:
                        if combined_value == model_name:
                            found_model = model_name
                            break
                
                if found_model:
                    # Update or create a finding for this variable
                    # First, remove any existing finding for this variable
                    self.findings = [f for f in self.findings 
                                    if not (f.get('variable') == var_name and f['type'] == 'variable_assignment')]
                    
                    self.findings.append({
                        'type': 'variable_assignment',
                        'model': found_model,
                        'variable': var_name,
                        'file': file_path,
                        'line': node.start_point[0] + 1,
                        'column': node.start_point[1] + 1,
                        'code': self.get_line_context(source_code, node.start_point[0]),
                        'assigned_value': combined_value,
                        'is_compound_assignment': True,
                        'note': f'Model name constructed from compound assignments (+=): {combined_value}'
                    })
            else:
                # First assignment with +=, treat as regular assignment
                self.variable_assignments[var_name] = {
                    'value': new_value,
                    'file': file_path,
                    'line': node.start_point[0] + 1,
                    'usage_locations': []
                }
    
    
    def check_function_call(self, node, source_code, file_path):
        """Check function call arguments for tracked variables and detect API calls"""
        # Get function name
        function_name = None
        for child in node.children:
            if child.type in ['member_expression', 'attribute']:
                function_name = source_code[child.start_byte:child.end_byte]
                break
            elif child.type == 'identifier':
                function_name = source_code[child.start_byte:child.end_byte]
                break
        
        # Check if this looks like an API call
        is_api_call = False
        if function_name:
            for api_pattern in self.api_patterns.get('function_names', []):
                if api_pattern in function_name:
                    is_api_call = True
                    break
        
        # Check arguments
        for child in node.children:
            if child.type in ['arguments', 'argument_list']:
                self.check_function_arguments(child, source_code, file_path, 
                                             function_name, is_api_call, node.start_point[0])
    
    def check_function_arguments(self, args_node, source_code, file_path, 
                                 function_name, is_api_call, call_line):
        """Check function arguments for model variables"""
        for arg in args_node.children:
            if arg.type == 'identifier':
                arg_name = source_code[arg.start_byte:arg.end_byte]
                
                # Track usage of any known variable
                if arg_name in self.variable_assignments:
                    var_info = self.variable_assignments[arg_name]
                    usage_info = {
                        'file': file_path,
                        'line': call_line + 1,
                        'column': arg.start_point[1] + 1,
                        'context': self.get_line_context(source_code, call_line),
                        'function': function_name
                    }
                    
                    if is_api_call:
                        usage_info['is_api_call'] = True
                    
                    var_info['usage_locations'].append(usage_info)
            
            # Check for object literals with model parameter
            elif arg.type == 'object':
                self.check_object_literal(arg, source_code, file_path, function_name, 
                                         is_api_call, call_line)
    
    def check_object_literal(self, obj_node, source_code, file_path, 
                            function_name, is_api_call, call_line):
        """Check object literal for model parameter"""
        for child in obj_node.children:
            if child.type == 'pair':
                key = None
                value = None
                
                for subchild in child.children:
                    if subchild.type == 'property_identifier':
                        # This is the key (property name)
                        if key is None:
                            key = source_code[subchild.start_byte:subchild.end_byte].strip('\'"')
                    elif subchild.type == 'identifier':
                        # This is the value (variable reference)
                        if value is None:
                            value = source_code[subchild.start_byte:subchild.end_byte]
                    elif subchild.type == 'string':
                        # This is a string value
                        if key is None:
                            key = source_code[subchild.start_byte:subchild.end_byte].strip('\'"')
                
                # Check if this is a model parameter
                if key in self.api_patterns.get('parameter_names', []) and value:
                    if value in self.variable_assignments:
                        var_info = self.variable_assignments[value]
                        var_info['usage_locations'].append({
                            'file': file_path,
                            'line': call_line + 1,
                            'column': child.start_point[1] + 1,
                            'context': self.get_line_context(source_code, call_line),
                            'function': function_name,
                            'parameter': key,
                            'is_api_call': is_api_call
                        })
    
    def get_line_context(self, source_code, row):
        """Get line context for display"""
        lines = source_code.split('\n')
        return lines[row].strip() if row < len(lines) else ''
    
    def generate_report(self, output_path, format='json'):
        """Generate and save report"""
        # Add usage locations to variable assignment findings
        for finding in self.findings:
            if finding['type'] == 'variable_assignment':
                var_info = self.variable_assignments.get(finding['variable'])
                if var_info and var_info['usage_locations']:
                    finding['usage_locations'] = var_info['usage_locations']
                    finding['usage_count'] = len(var_info['usage_locations'])
                    
                    # Count API calls
                    api_call_count = sum(1 for loc in var_info['usage_locations'] 
                                        if loc.get('is_api_call', False))
                    if api_call_count > 0:
                        finding['api_call_count'] = api_call_count
        
        summary = self.generate_summary()
        
        report = {
            'scan_date': __import__('datetime').datetime.now().isoformat(),
            'total_findings': len(self.findings),
            'findings': self.findings,
            'summary': summary
        }
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✅ Report saved to: {output_path}")
            print(f"📊 Total findings: {len(self.findings)}")
        else:
            # Text format
            with open(output_path, 'w') as f:
                f.write("Tree-sitter AI Model Scanner Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Scan Date: {report['scan_date']}\n")
                f.write(f"Total Findings: {report['total_findings']}\n\n")
                
                for finding in self.findings:
                    f.write(f"\n[{finding['type']}] {finding['model']}\n")
                    f.write(f"  File: {finding['file']}:{finding['line']}:{finding['column']}\n")
                    f.write(f"  Code: {finding['code']}\n")
                    
                    if finding.get('components'):
                        f.write(f"  Components: {finding['components']}\n")
                    
                    if finding.get('usage_locations'):
                        f.write(f"  Used in {len(finding['usage_locations'])} location(s):\n")
                        for usage in finding['usage_locations']:
                            api_marker = " [API CALL]" if usage.get('is_api_call') else ""
                            f.write(f"    - {usage['file']}:{usage['line']} in {usage.get('function', 'unknown')}{api_marker}\n")
            print(f"\n✅ Report saved to: {output_path}")
        
        # Print summary
        print(f"\n📋 Summary:")
        print(f"   String literals: {summary['string_literals']}")
        print(f"   Variable assignments: {summary['variable_assignments']}")
        print(f"   Template literals: {summary['template_literals']}")
        print(f"   String concatenations: {summary['string_concatenations']}")
        print(f"   Unique models: {len(summary['models_found'])}")
        if summary['models_found']:
            print(f"   Models: {', '.join(summary['models_found'][:10])}")
            if len(summary['models_found']) > 10:
                print(f"          ... and {len(summary['models_found']) - 10} more")
    
    def generate_summary(self):
        """Generate summary statistics"""
        summary = {
            'string_literals': 0,
            'variable_assignments': 0,
            'template_literals': 0,
            'string_concatenations': 0,
            'models_found': set()
        }
        
        for finding in self.findings:
            if finding['type'] == 'string_literal':
                summary['string_literals'] += 1
            elif finding['type'] == 'variable_assignment':
                summary['variable_assignments'] += 1
            elif finding['type'] == 'template_literal':
                summary['template_literals'] += 1
            elif finding['type'] == 'string_concatenation':
                summary['string_concatenations'] += 1
            
            if finding['model'] != 'constructed':
                summary['models_found'].add(finding['model'])
        
        summary['models_found'] = sorted(list(summary['models_found']))
        return summary

def main():
    parser = argparse.ArgumentParser(
        description='Tree-sitter AI Model Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python scanner.py --dir ../projects-samples/ai-ui
  python scanner.py --dir ../projects-samples/ai-ui --output results.json
  python scanner.py --dir ../projects-samples/OpenHands --format text
        '''
    )
    parser.add_argument('--dir', required=True, help='Directory to scan')
    parser.add_argument('--output', default='output/scan-results.json', help='Output file path')
    parser.add_argument('--format', choices=['json', 'text'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dir):
        print(f"❌ Error: Directory not found: {args.dir}")
        sys.exit(1)
    
    print(f"\n🔍 Tree-sitter AI Model Scanner")
    print("=" * 50)
    print(f"📁 Scanning: {args.dir}")
    print(f"📝 Output: {args.output}")
    print(f"📊 Format: {args.format}\n")
    
    scanner = ModelScanner(MODEL_RULES)
    scanner.scan_directory(args.dir)
    scanner.generate_report(args.output, args.format)
    
    print(f"\n✅ Scan complete!\n")

if __name__ == '__main__':
    main()
