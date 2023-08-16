from flask import Flask, request, jsonify, render_template
import ast
from slimit.parser import Parser as JSParser
from slimit.visitors import nodevisitor
from javalang import tree as JavaTree
import jsbeautifier
from pycparser import c_parser, c_ast
import clr
import os

app = Flask(__name__)

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

def get_javascript_functions_and_classes(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
    
    tree = JSParser().parse(code)
    functions = []
    classes = []
    
    for node in nodevisitor.visit(tree):
        if isinstance(node, JSParser.FunctionDeclaration):
            functions.append(node)
        elif isinstance(node, JSParser.ClassDeclaration):
            classes.append(node)

    return functions, classes

def get_java_functions_and_classes(file_path):
    with open(file_path, 'r') as file:
        code = file.read()

    tree = JavaTree.parse(code)
    functions = []
    classes = []

    for path, node in tree.filter(JavaTree.MethodDeclaration):
        functions.append(node)

    for path, node in tree.filter(JavaTree.ClassDeclaration):
        classes.append(node)

    return functions, classes

def get_c_functions_and_classes(file_path):
    with open(file_path, 'r') as file:
        code = file.read()
    
    parser = c_parser.CParser()
    ast_tree = parser.parse(code, filename="<unknown>")
    functions = []
    classes = []

    def visit(node):
        if isinstance(node, c_ast.FuncDef):
            functions.append(node)
        elif isinstance(node, c_ast.Decl) and isinstance(node.type, c_ast.Struct):
            classes.append(node)

        for _, child in node.children():
            visit(child)

    visit(ast_tree)

    return functions, classes

def get_net_functions_and_classes(file_path):
    clr.AddReference('System.Reflection.Metadata')
    import System.Reflection.Metadata as md

    with open(file_path, 'rb') as file:
        code = file.read()

    metadata_reader = md.MetadataReader(code)
    functions = []
    classes = []

    for handle in metadata_reader.TypeDefinitions:
        type_def = metadata_reader.GetTypeDefinition(handle)
        class_name = metadata_reader.GetString(type_def.Name)

        for method_handle in type_def.GetMethods():
            method = metadata_reader.GetMethodDefinition(method_handle)
            method_name = metadata_reader.GetString(method.Name)

            functions.append(f"{class_name}.{method_name}")

    return functions, classes


language_parsers = {
    '.py': get_python_functions_and_classes,
    '.js': get_javascript_functions_and_classes,
    '.java': get_java_functions_and_classes,
    '.c': get_c_functions_and_classes,
    '.cpp': get_c_functions_and_classes,
    '.dll': get_net_functions_and_classes,
    '.exe': get_net_functions_and_classes,
}

def get_python_code_block(node, padded=False):
    code = ast.get_source_segment(open(node.root().file).read(), node)
    if padded:
        code = jsbeautifier.beautify(code)
    return code

def get_javascript_code_block(node, padded=False):
    code = node.to_ecma()
    if padded:
        code = jsbeautifier.beautify(code)
    return code

def get_java_code_block(node, padded=False):
    code = node._position.get_code()
    if padded:
        code = jsbeautifier.beautify(code)
    return code

def get_c_code_block(node, padded=False):
    code = node.show()
    if padded:
        code = jsbeautifier.beautify(code)
    return code

def get_net_code_block(node, padded=False):
    code = node
    if padded:
        code = jsbeautifier.beautify(code)
    return code

def get_code_block(node, file_ext, padded=False):
    if file_ext == '.py':
        return get_python_code_block(node, padded)
    elif file_ext == '.js':
        return get_javascript_code_block(node, padded)
    elif file_ext == '.java':
        return get_java_code_block(node, padded)
    elif file_ext == '.c' or file_ext == '.cpp':
        return get_c_code_block(node, padded)
    elif file_ext == '.dll' or file_ext == '.exe':
        return get_net_code_block(node, padded)
    else:
        return "Unsupported language."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/parse_file', methods=['POST'])
def parse_file():
    file_path = request.json['file_path']
    functions = []
    classes = []

    file_ext = os.path.splitext(file_path)[1]
    parse_function = language_parsers.get(file_ext)

    if parse_function:
        functions, classes = parse_function(file_path)

    function_list = [get_code_block(f, file_ext, padded=False) for f in functions]
    class_list = [get_code_block(c, file_ext, padded=False) for c in classes]
    return jsonify({'functions': function_list, 'classes': class_list})

if __name__ == '__main__':
    app.run(debug=True)
