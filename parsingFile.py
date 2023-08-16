import os
import sys
import git
import tree_sitter
from pathlib import Path

# Function to parse a single file using Tree-sitter and find usages of className or functionName
def find_usages_in_file(file_path, class_or_function_name):
    parser = tree_sitter.Language("python").get_parser()
    with open(file_path, "r") as file:
        code = file.read().encode()
    tree = parser.parse(code)
    root_node = tree.root_node

    usages = []
    for node in root_node.walk():
        if node.type == "class_definition" or node.type == "function_definition":
            name_node = node.children[0]
            name = code[name_node.start_byte:name_node.end_byte].decode()
            if name == class_or_function_name:
                usages.append(file_path)
        elif node.type == "identifier":
            identifier_name = code[node.start_byte:node.end_byte].decode()
            if identifier_name == class_or_function_name:
                usages.append(file_path)

    return usages

# Function to search for usages in a Git repository
def search_git_repository(repo_path, class_or_function_name):
    repo = git.Repo(repo_path)
    usages = []

    for file_path in repo.git.ls_files().splitlines():
        file_path = os.path.join(repo_path, file_path)
        if file_path.endswith(".py"):  # Replace this with appropriate file extensions for other languages
            usages.extend(find_usages_in_file(file_path, class_or_function_name))

    return usages

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python find_usages.py <git_repository_path> <class_or_function_name>")
        sys.exit(1)

    git_repository_path = sys.argv[1]
    class_or_function_name = sys.argv[2]

    if not os.path.exists(git_repository_path):
        print("Error: Git repository path does not exist.")
        sys.exit(1)

    results = search_git_repository(git_repository_path, class_or_function_name)

    if results:
        print("Usages found in the following files:")
        for file_path in results:
            print(Path(file_path).relative_to(git_repository_path))
    else:
        print("No usages found.")
