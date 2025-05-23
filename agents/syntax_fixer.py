from utils.llm_client import call_gpt

def fix_code(code_files: dict, language: str) -> dict:
    fixed_code = {}
    for filename, content in code_files.items():
        prompt = f"""
You're a code fixer. Your task is to fix any syntax or import errors in the following {language} code.
⚠️ Return ONLY the corrected raw code. Do NOT use markdown. Do NOT include triple backticks or language tags.

File: {filename}

{content}
"""
        fixed = call_gpt(prompt)
        fixed_code[filename] = fixed.strip()
    return fixed_code
