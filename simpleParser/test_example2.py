import ast
import esprima
import sys
import astor
# import dotnet.parser
import javalang
import re

def get_c_functions_and_classes(code):
    """Gets the list of functions and classes in a C file."""

    functions = []
    classes = []

    for match in re.finditer(r'(def|struct|class)\s+([\w]+)', code):
        name = match.group(2)
        if match.group(1) == 'def':
            functions.append(name)
        elif match.group(1) in ('struct', 'class'):
            classes.append(name)

    return functions, classes

def get_cpp_functions_and_classes(code):
    """Gets the list of functions and classes in a C++ file."""

    functions = []
    classes = []

    for match in re.finditer(r'(def|struct|class)\s+([\w]+)\s*[(]?', code):
        name = match.group(2)
        if match.group(1) == 'def':
            functions.append(name)
        elif match.group(1) in ('struct', 'class'):
            classes.append(name)

    return functions, classes

# def get_dotnet_functions_and_classes(code):
#     """Gets the list of functions and classes in a C# file."""

#     from dotnet.parser import parse

#     nodes = parse(code)
#     functions = []
#     classes = []

#     for node in nodes:
#         if isinstance(node, dotnet.parser.FunctionDeclaration):
#             functions.append(node)
#         elif isinstance(node, dotnet.parser.ClassDeclaration):
#             classes.append(node)

#     return functions, classes


def get_javascript_functions_and_classes(code):
    ast_tree = esprima.parseScript(code)
    functions = []
    classes = []

    for node in ast_tree.body:
        if node.type == 'FunctionDeclaration':
            functions.append(node)
        elif node.type == 'ClassDeclaration':
            classes.append(node)

    return functions, classes

def get_python_functions_and_classes(code):
    tree = ast.parse(code)
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)

    return functions, classes

def get_java_functions_and_classes(code):
    if not code:
        return

    try:
        tree = javalang.parse.parse(code)
    except javalang.parser.ParseException:
        return

    functions = []
    classes = []

    for type in tree.types:
        if isinstance(type, javalang.tree.MethodDeclaration):
            functions.append(type)
        elif isinstance(type, javalang.tree.ClassDeclaration):
            classes.append(type)

    return functions, classes

def get_functions_and_classes(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    if file_path.endswith('.js'):
        functions, classes = get_javascript_functions_and_classes(code)
    elif file_path.endswith('.py'):
        functions, classes = get_python_functions_and_classes(code)
    elif file_path.endswith('.java'):
        functions, classes = get_java_functions_and_classes(code)
    elif file_path.endswith('.c'):
        functions, classes = get_c_functions_and_classes(code)
    elif file_path.endswith('.cpp'):
        functions, classes = get_cpp_functions_and_classes(code)
    # elif file_path.endswith('.cs'):
    #     functions, classes = get_dotnet_functions_and_classes(code)
    else:
        print("File type not supported")

    return functions, classes

def print_function_or_class_info(items):
    for item in items:
        if isinstance(item, ast.FunctionDef):
            print(f"{item.__class__.__name__}: {item.name}")
        elif isinstance(item, esprima.nodes.FunctionDeclaration):
            name = item.id.get('name', '')
            print(f"{item.__class__.__name__}: {name}")
        print("Body:")
        body_code = astor.to_source(item)
        print(body_code)
        print("\n")

if __name__ == "__main__":
    file_path = input("Enter the file path: ")

    functions, classes = get_functions_and_classes(file_path)

    print(f"Number of functions in {file_path}: {len(functions)}")
    print_function_or_class_info(functions)

    print(f"Number of classes in {file_path}: {len(classes)}")
    print_function_or_class_info(classes)
