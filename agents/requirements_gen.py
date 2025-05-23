from utils.llm_client import call_gpt

def generate_requirements_file(code_files: dict) -> tuple[str, str]:
    joined_code = "\n\n".join(code_files.values())
    prompt = f"""
You are a build tool assistant.
Given the following code, infer the programming language and framework.
Generate the appropriate dependency file (like requirements.txt, package.json, pom.xml, etc.).
Only return the requirements content (no explanations, no code fences, just purely the requirements). 
Do NOT use markdown. Do NOT include ``` or any triple backticks.

Code:
{joined_code}
"""
    dependency_file = call_gpt(prompt).strip()

    if 'flask' in dependency_file.lower() or 'fastapi' in dependency_file.lower():
        filename = "requirements.txt"
    elif '{' in dependency_file and 'dependencies' in dependency_file:
        filename = "package.json"
    elif '<project' in dependency_file:
        filename = "pom.xml"
    elif 'gem' in dependency_file:
        filename = "Gemfile"
    else:
        filename = "dependencies.txt"

    return filename, dependency_file
