import requests
import re

class FunctionAnalyzer:
    def __init__(self):
        self.exclude_functions = ['__init__', '__str__', '__repr__', '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__', '__len__']
    
    def analyze_repo_github(self, repo_url):
        try:
            username, repo = self.extract_github_info(repo_url)
            api_url = f"https://api.github.com/repos/{username}/{repo}/contents"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                repo_contents = response.json()
                results = []

                for file_info in repo_contents:
                    if file_info['type'] == 'file' and file_info['name'].endswith('.py'):
                        file_contents = requests.get(file_info['download_url']).text
                        functions = self.extract_functions(file_contents)
                        functions = [func for func in functions if func not in self.exclude_functions]
                        results.append((file_info['name'], len(functions), functions))
                
                return results
            else:
                print("Error: Unable to fetch GitHub repository.")
                return []
        except Exception as e:
            print("An error occurred:", e)
            return []

    def analyze_repo_azure_devops(self, repo_url):
        try:
            org, project, repo = self.extract_azure_devops_info(repo_url)
            api_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/items?api-version=7.1"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                repo_contents = response.json()
                results = []

                for item in repo_contents['value']:
                    if item['gitObjectType'] == 'tree':
                        folder_contents = self.get_azure_devops_folder_contents(item['url'])
                        functions = self.extract_functions_from_folder(folder_contents)
                        functions = [func for func in functions if func not in self.exclude_functions]
                        results.extend([(item['path'], len(functions), functions)])
                
                return results
            else:
                print("Error: Unable to fetch Azure DevOps repository.")
                return []
        except Exception as e:
            print("An error occurred:", e)
            return []

    def extract_github_info(self, repo_url):
        parts = repo_url.rstrip('/').split('/')
        username, repo = parts[-2], parts[-1]
        return username, repo

    def extract_azure_devops_info(self, repo_url):
        # Modify this function based on the actual format of Azure DevOps URLs
        parts = repo_url.rstrip('/').split('/')
        org, project, repo = parts[parts.index("dev.azure.com") + 1], parts[-2], parts[-1]
        return org, project, repo

    def get_azure_devops_folder_contents(self, folder_url):
        response = requests.get(folder_url)
        if response.status_code == 200:
            return response.json()
        else:
            return []

    def extract_functions(self, code):
        return re.findall(r'def\s+(\w+)\s*\(.*\)\s*:', code)

    def extract_functions_from_folder(self, folder_contents):
        functions = []
        for item in folder_contents['value']:
            if item['gitObjectType'] == 'blob' and item['path'].endswith('.py'):
                file_contents = requests.get(item['url']).json()['content']
                decoded_contents = self.decode_azure_devops_content(file_contents)
                functions.extend(self.extract_functions(decoded_contents))
        return functions

def main():
    print("Repo Function Analyzer")
    print("======================")
    print("Supported platforms: GitHub, Azure DevOps")
    
    repo_url = input("Enter the repository URL: ")
    
    analyzer = FunctionAnalyzer()
    
    if "github.com" in repo_url:
        results = analyzer.analyze_repo_github(repo_url)
    elif "dev.azure.com" in repo_url:
        results = analyzer.analyze_repo_azure_devops(repo_url)
    else:
        print("Unsupported repository platform.")
        return
    
    if results:
        print("File Name | No of functions | Functions (excluding defaults)")
        print("===========================================================")
        for file_info in results:
            file_name, num_functions, functions = file_info
            functions_str = ', '.join(functions)
            print(f"{file_name} | {num_functions} | {functions_str}")
    else:
        print("No functions found in the repository.")

if __name__ == "__main__":
    main()
