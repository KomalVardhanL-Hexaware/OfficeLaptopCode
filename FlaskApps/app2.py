from flask import Flask, render_template, request
import requests
import os
import re

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/find-classes", methods=["GET"])
def find_classes():
    repo_url = request.args.get("repo_url")

    # Get the list of all Python files in the repo.
    files = get_python_files(repo_url)

    # Find all the classes in the Python files.
    classes = []
    for file in files:
        classes.extend(find_classes_in_file(file))

    # Print the output in a tabular format.
    table = []
    for class_name, functions in classes:
        table.append((file, class_name, functions))
    print(tabulate(table, headers=["File", "Class Name", "Functions"]))

    return "Done!"

def get_python_files(repo_url):
    response = requests.get(repo_url + "/contents")
    if response.status_code == 200:
        contents = response.json()
        files = []
        for item in contents:
            if item["type"] == "file" and item["name"].endswith(".py"):
                files.append(item["path"])
        return files
    else:
        raise Exception(f"Failed to get contents of repo: {repo_url}")

def find_classes_in_file(file_path):
    with open(file_path) as f:
        content = f.read()

    classes = []
    for match in re.finditer(r"class\s+([\w]+)", content):
        class_name = match.group(1)
        classes.append((class_name, find_functions_in_class(content, class_name)))
    return classes

def find_functions_in_class(content, class_name):
    functions = []
    for match in re.finditer(r"def\s+([\w]+)\((.*)\)", content):
        function_name = match.group(1)
        functions.append(function_name)
    return functions

if __name__ == "__main__":
    app.run(debug=True)
