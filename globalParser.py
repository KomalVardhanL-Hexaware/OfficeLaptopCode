import os
import json
import argparse
import subprocess

def parse_code_for_function_usage(language, function_name, repository_path):
    def search_files_for_function(tree, file_path):
        result = []

        def traverse_tree(node):
            if node.type == 'function_call' and node.children[0].type == 'identifier':
                if node.children[0].text == function_name:
                    result.append(node.start_point.row + 1)

            for child in node.children:
                traverse_tree(child)

        traverse_tree(tree.root_node)
        return result

    def parse_file(file_path):
        try:
            parser = subprocess.Popen(['tree-sitter', 'parse', file_path, language],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            ast_json, error = parser.communicate()
            if parser.returncode == 0:
                return json.loads(ast_json)
            else:
                print(f"Error parsing {file_path}: {error}")
        except FileNotFoundError:
            print("tree-sitter executable not found. Make sure you have it installed.")
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")

        return None

    result = {}

    for root, _, files in os.walk(repository_path):
        for file in files:
            if file.endswith(f'.{language}'):
                file_path = os.path.join(root, file)
                ast = parse_file(file_path)
                if ast:
                    usage_lines = search_files_for_function(ast, file_path)
                    if usage_lines:
                        result[file_path] = usage_lines

    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find function usage in a code repository.')
    parser.add_argument('language', help='The programming language of the code repository.')
    parser.add_argument('function_name', help='The name of the function or class to trace.')
    parser.add_argument('repository_path', help='The path to the code repository.')

    args = parser.parse_args()
    language = args.language
    function_name = args.function_name
    repository_path = args.repository_path

    result = parse_code_for_function_usage(language, function_name, repository_path)

    if not result:
        print(f"No usage of {function_name} found in the repository.")
    else:
        for file_path, line_numbers in result.items():
            print(f"File: {file_path}")
            for line_num in line_numbers:
                with open(file_path, 'r') as file:
                    line_content = file.readlines()[line_num - 1].strip()
                    print(f"  Line {line_num}: {line_content}")
