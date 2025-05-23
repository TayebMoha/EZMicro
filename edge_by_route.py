# edge_by_route.py
import re, networkx as nx, yaml, os, ast

PATH_RE = re.compile(r'@app\.(?:get|post|put|delete|patch)\(\s*["\'](.*?)["\']')

with open("path_map.yaml") as f:
    ROUTE_MAP = yaml.safe_load(f)["paths2service"]

def path_to_service(path: str) -> str:
    for pfx, svc in ROUTE_MAP.items():
        if path.startswith(pfx):
            return svc
    return "Unknown"

def add_route_edges(code_files, g: nx.Graph):
    for fname, src in code_files.items():
        for p in PATH_RE.findall(src):
            svc = path_to_service(p)
            if svc != "Unknown":
                g.add_edge(f"{fname}::file", f"{svc}::pseudo", weight=7.0)
