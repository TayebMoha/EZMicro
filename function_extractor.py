# function_extractor.py (enhanced)
"""
Language‑agnostic extractor that delegates to the best available parser for each
stack.  For Java we now have `java_method_extractor.py`.  This file contains
extractors for Python (AST), PHP (nikic/PHP‑Parser via CLI), and JavaScript/TS
(Esprima via Node).

All extractors return a mapping:
    { filename: [ { "function": code, "signature": sig, ... }, ... ] }

Add more languages by registering a new entry in LANGUAGE_EXTRACTORS at bottom.
"""
import ast
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List

############################
#  Python extractor (AST)  #
############################

def _extract_python(code: str) -> List[dict]:
    functions = []
    try:
        tree = ast.parse(code)
        source_lines = code.splitlines()
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno - 1
                end = node.end_lineno or start + 1
                body = "\n".join(source_lines[start:end])
                sig = f"{node.name}({', '.join(arg.arg for arg in node.args.args)})"
                functions.append({
                    "method": body,
                    "signature": sig,
                    "start_line": start + 1,
                    "end_line": end,
                })
    except SyntaxError:
        pass
    return functions

##################################
#  PHP extractor (nikic parser)  #
##################################
PHP_WRAPPER = Path(__file__).parent / "tools/php_extract.php"

def _run_php_parser(php_code: str) -> List[dict]:
    """Feeds code to a tiny PHP wrapper that echoes JSON of functions."""
    proc = subprocess.run(
        ["php", str(PHP_WRAPPER)],
        input=php_code.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode()[:200])
    try:
        return json.loads(proc.stdout.decode())
    except json.JSONDecodeError:
        return []

#############################################
#  JavaScript / TypeScript extractor (Node) #
#############################################
JS_WRAPPER = Path(__file__).parent / "tools/js_extract.mjs"

def _run_js_parser(js_code: str) -> List[dict]:
    proc = subprocess.run(
        ["node", str(JS_WRAPPER)],
        input=js_code.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode()[:200])
    try:
        return json.loads(proc.stdout.decode())
    except json.JSONDecodeError:
        return []

########################################
#  Public dispatcher for any language  #
########################################

def extract_functions(code_files: Dict[str, str], language: str) -> Dict[str, List[dict]]:
    """Dispatch to language‑specific extractor."""
    out: Dict[str, List[dict]] = {}
    for filename, content in code_files.items():
        if language == "python":
            out[filename] = _extract_python(content)
        elif language == "php":
            out[filename] = _run_php_parser(content)
        elif language in {"javascript", "typescript"}:
            out[filename] = _run_js_parser(content)
        elif language == "java":
            # handled separately by java_method_extractor.py, but fallback regex
            pattern = r"(public|private|protected)?\s+\w+[<\w\s,>]*\s+\w+\s*\([^)]*\)\s*\{[\s\S]*?\}"
            out[filename] = [{"method": m} for m in re.findall(pattern, content)]
        else:
            out[filename] = []
    return out

# Registry placeholder for future languages
LANGUAGE_EXTRACTORS = {
    "python": _extract_python,
    "php": _run_php_parser,
    "javascript": _run_js_parser,
    "typescript": _run_js_parser,
}
