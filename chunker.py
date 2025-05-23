import os
from pathlib import Path

def extract_service_candidates(monolith_path: str) -> dict:
    monolith_path = Path(monolith_path)
    services = {}

    for root, _, files in os.walk(monolith_path):
        rel_path = Path(root).relative_to(monolith_path)
        service_name = rel_path.parts[0] if rel_path.parts else "root"

        if '__pycache__' in rel_path.parts:
            continue

        if service_name not in services:
            services[service_name] = {}

        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js')):
                filepath = Path(root) / file
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    services[service_name][str(filepath.name)] = f.read()

    return services
