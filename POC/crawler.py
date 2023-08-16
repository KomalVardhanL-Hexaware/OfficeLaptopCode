import os
import re
import argparse
import tree_sitter
from tree_sitter import Language, Parser

def parse_file(file_path):
    # Load the Tree-sitter parser for Python
    python_lang = Language('tree-sitter-python')
    parser = Parser()
    parser.set_language(python_lang)

    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    # Parse the code and get the root of the syntax tree
    tree = parser.parse(bytes(code, 'utf-8'))
    root = tree.root_node

    # Initialize counters and lists to store functions and classes
    function_count = 0
    functions = []
    class_count = 0
    classes = []

    # Helper function to extract the body of a node
    def get_body(node):
        body_start, body_end = node.start_byte, node.end_byte
        return code[body_start:body_end]

    # Traverse the syntax tree to find functions and classes
    for node in root.children:
        if node.type == 'function_definition':
            function_count += 1
            function_name_node = node.children[1]
            function_name = code[function_name_node.start_byte:function_name_node.end_byte].strip()
            function_body = get_body(node.children[-1])
            functions.append((function_name, function_body))
        elif node.type == 'class_definition':
            class_count += 1
            class_name_node = node.children[1]
            class_name = code[class_name_node.start_byte:class_name_node.end_byte].strip()
            class_body = get_body(node.children[-1])
            classes.append((class_name, class_body))

    return function_count, functions, class_count, classes

def main():
    parser = argparse.ArgumentParser(description='Crawl and analyze a repository for functions and classes.')
    parser.add_argument('file_name', type=str, help='Name of the file to analyze')
    args = parser.parse_args()

    file_name = args.file_name
    if not os.path.isfile(file_name):
        print(f"Error: File '{file_name}' does not exist.")
        return

    function_count, functions, class_count, classes = parse_file(file_name)

    print(f"File Name: {file_name}")
    print(f"No of functions: {function_count}")
    for name, body in functions:
        print(f"Function Name: {name}")
        print(f"Function Body:\n{body}")
    print(f"No of Classes: {class_count}")
    for name, body in classes:
        print(f"Class Name: {name}")
        print(f"Class Body:\n{body}")

if __name__ == '__main__':
    main()
