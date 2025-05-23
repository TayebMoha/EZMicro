# agents/language_detector.py
import re

EXTENSION_MAP = {
    ".py": "python",
    ".php": "php",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript"
}

KEYWORDS_MAP = {
    "python": ["flask", "django", "def ", "import "],
    "php": ["<?php", "use Symfony", "class Controller"],
    "java": ["public class", "@SpringBootApplication", "import javax"],
    "javascript": ["express", "require(", "module.exports"],
    "typescript": ["import {", "@Injectable", "export class"]
}

def detect_language(code_files: dict) -> str:
    score = {lang: 0 for lang in KEYWORDS_MAP.keys()}

    for filename, code in code_files.items():
        ext = re.search(r"\.[^.]+$", filename)
        if ext and ext.group(0) in EXTENSION_MAP:
            lang = EXTENSION_MAP[ext.group(0)]
            score[lang] += 1

        for lang, keywords in KEYWORDS_MAP.items():
            for kw in keywords:
                if kw in code:
                    score[lang] += 2

    # Pick the language with the highest score
    best_match = max(score.items(), key=lambda x: x[1])[0]
    return best_match
