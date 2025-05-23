from utils.llm_client import call_gpt

def generate_api_docs(code_files: dict) -> str:
    joined_code = "\n\n".join(code_files.values())
    prompt = f"""
You're an API documentation assistant.
Based on the following Python web app code, generate an OpenAPI 3.0 spec (in YAML format).
Assume the app uses either Flask or FastAPI.
Do NOT use markdown. Do NOT include ```yaml or any triple backticks.
Do not include explanations or markdown formatting — just the YAML spec.

Code:

{joined_code}
"""
    return call_gpt(prompt)
