import subprocess
import os

def get_function_trace_path(repository_path, function_name):
    # Change the current working directory to the repository path
    os.chdir(repository_path)

    # Get the list of all files in the repository
    git_files = subprocess.check_output(['git', 'ls-files']).decode().splitlines()

    # Initialize an empty list to store the trace path
    trace_path = []

    # Iterate through each file in the repository
    for file_path in git_files:
        # Get the content of the file
        file_content = subprocess.check_output(['git', 'show', f':{file_path}']).decode()

        # Check if the function_name appears in the file content
        if function_name in file_content:
            trace_path.append(file_path)

    return trace_path

if __name__ == "__main__":
    repository_path = "https://github.com/KomalVardhanL-Hexaware/portfoliomanager"  # Replace with the path to your repository
    function_name = "get_absolute_url"  # Replace with the function name you want to trace

    trace_path = get_function_trace_path(repository_path, function_name)

    if trace_path:
        print(f"Function '{function_name}' is used in the following files:")
        for file_path in trace_path:
            print(file_path)
    else:
        print(f"Function '{function_name}' is not found in the repository.")
