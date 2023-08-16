import os
import ast
import argparse
import subprocess
import shutil
import tempfile
import git

def parse_code_for_symbol_usage(language, symbol_name, repository_path):
    def search_python_files_for_symbol(file_path):
        result = []
        with open(file_path, 'r') as file:
            try:
                tree = ast.parse(file.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if getattr(node.func, 'id', None) == symbol_name:
                            result.append(node.lineno)
            except SyntaxError:
                print(f"Error parsing {file_path}. The file contains syntax errors.")
        return result

    result = {}

    # Check if the repository_path is a local path or a GitHub URL
    if repository_path.startswith("https://github.com/"):
        with tempfile.TemporaryDirectory() as temp_dir:
            print("Cloning the repository...")
            git.Repo.clone_from(repository_path, temp_dir)
            repository_path = temp_dir

    # Handle language-specific parsers
    if language == "python":
        for root, _, files in os.walk(repository_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    usage_lines = search_python_files_for_symbol(file_path)
                    if usage_lines:
                        result[file_path] = usage_lines
    else:
        try:
            parser = subprocess.Popen(['tree-sitter', 'parse', repository_path, language],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            ast_json, error = parser.communicate()
            if parser.returncode == 0:
                ast_result = json.loads(ast_json)
                for node in ast_result["children"]:
                    file_path = os.path.join(repository_path, node["uri"])
                    usage_lines = []
                    _search_tree_for_symbol(node, symbol_name, usage_lines)
                    if usage_lines:
                        result[file_path] = usage_lines
            else:
                print(f"Error parsing {repository_path}: {error}")
        except FileNotFoundError:
            print("tree-sitter executable not found. Make sure you have it installed.")
        except Exception as e:
            print(f"Error parsing {repository_path}: {str(e)}")

    return result

def _search_tree_for_symbol(node, symbol_name, result):
    if node.get("type", "") == "call_expression":
        function_name_node = node.get("function", {}).get("name", "")
        if function_name_node == symbol_name:
            result.append(node.get("start", {}).get("line", 0))

    for child in node.get("children", []):
        _search_tree_for_symbol(child, symbol_name, result)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find symbol (function or class) usage in a code repository.')
    parser.add_argument('language', help='The programming language of the code repository.')
    parser.add_argument('symbol_name', help='The name of the function or class to trace.')
    parser.add_argument('repository_path', help='The local path or GitHub URL of the code repository.')

    args = parser.parse_args()
    language = args.language
    symbol_name = args.symbol_name
    repository_path = args.repository_path

    result = parse_code_for_symbol_usage(language, symbol_name, repository_path)

    if not result:
        print(f"No usage of {symbol_name} found in the repository.")
    else:
        for file_path, line_numbers in result.items():
            print(f"File: {file_path}")
            for line_num in line_numbers:
                with open(file_path, 'r') as file:
                    line_content = file.readlines()[line_num - 1].strip()
                    print(f"  Line {line_num}: {line_content}")
