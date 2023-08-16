from flask import Flask, render_template, request
import requests
import os
import re

app = Flask(__name__)

def extract_owner_repo(url):
    parts = url.split('/')
    owner = parts[-2]
    repo = parts[-1].replace(".git", "")
    return owner, repo

def fetch_repo_content(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    response = requests.get(url)
    repo_content = response.json()
    return repo_content

def find_python_files(repo_content):
    python_files = []
    for item in repo_content:
        if item['type'] == 'file' and item['name'].endswith('.py'):
            python_files.append(item['path'])
    return python_files

def count_functions(url, class_name):
    response = requests.get(url)
    content = response.text
    pattern = fr'def\s+{class_name}\s*\(.*\):'
    functions = re.findall(pattern, content)
    return len(functions)

def get_class_info(owner, repo, python_files):
    class_info = {}
    for file in python_files:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{file}"
        print(url)  # Add this line to print the URL
        response = requests.get(url)
        content = response.text
        classes = re.findall(r'class\s+(\w+)\s*:', content)
        class_info[file] = [(class_name, count_functions(url, class_name)) for class_name in classes]
    return class_info

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        owner, repo = extract_owner_repo(repo_url)
        repo_content = fetch_repo_content(owner, repo)
        python_files = find_python_files(repo_content)
        class_info = get_class_info(owner, repo, python_files)
        return render_template('result.html', class_info=class_info)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
