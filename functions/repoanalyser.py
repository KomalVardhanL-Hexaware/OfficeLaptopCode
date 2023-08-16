import requests
import ast

# Set your GitHub personal access token here
GITHUB_TOKEN = "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"

def extract_owner_repo(url):
    parts = url.split('/')
    owner = parts[-2]
    repo = parts[-1].replace(".git", "")
    return owner, repo

def fetch_repo_content(owner, repo, path=''):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repo_content = response.json()
        return repo_content
    else:
        print("Error fetching repo content:", response.status_code)
        return []

def extract_classes_functions(code):
    classes = []
    functions = []

    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    functions.append(item.name)

    return classes, functions

def get_class_info(owner, repo, path=''):
    class_info = {}
    repo_content = fetch_repo_content(owner, repo, path)
    for item in repo_content:
        if item['type'] == 'file' and item['name'].endswith('.py'):
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}/{item['name']}"
            headers = {'Authorization': f'token {GITHUB_TOKEN}'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                code = response.text
                classes, functions = extract_classes_functions(code)
                if classes or functions:  # Check if there are classes or functions before printing
                    print(f"Classes and Functions in {item['name']}:")
                    for class_name in classes:
                        print(f"  Class: {class_name}")
                        if functions:
                            print("    Functions:")
                            for function in functions:
                                print(f"      {function}")
            print()  # Add a blank line between files
    for item in repo_content:
        if item['type'] == 'dir':
            sub_path = f"{path}/{item['name']}" if path else item['name']
            get_class_info(owner, repo, sub_path)


def main():
    repo_url = input("Enter GitHub or Azure DevOps repo URL: ")
    owner, repo = extract_owner_repo(repo_url)
    get_class_info(owner, repo)

if __name__ == '__main__':
    main()
