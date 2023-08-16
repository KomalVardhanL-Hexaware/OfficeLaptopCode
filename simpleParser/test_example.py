import ast
import esprima
import sys
import astor

def get_python_functions_and_classes(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node)
        elif isinstance(node, ast.ClassDef):
            classes.append(node)

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

    if file_path.endswith('.py'):
        functions, classes = get_python_functions_and_classes(file_path)
    else:
        print("File type not supported")

    print(f"Number of functions in {file_path}: {len(functions)}")
    print_function_or_class_info(functions)

    print(f"Number of classes in {file_path}: {len(classes)}")
    print_function_or_class_info(classes)




