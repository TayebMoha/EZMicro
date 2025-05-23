from utils.llm_client import call_gpt

def generate_dockerfile(code_files: dict) -> str:
    all_code = "\n\n".join(code_files.values())
    prompt = f"""
You are a DevOps assistant. Given the following source code, generate a production-ready Dockerfile.
Only return the Dockerfile content (no explanations, no code fences, just purely the dockerfile). 
Do NOT use markdown. Do NOT include ```Dockerfile or any triple backticks.
Code:
{all_code}
"""
    return call_gpt(prompt).strip()
