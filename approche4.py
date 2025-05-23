
import json
import os
import shutil
import ast
from pathlib import Path
from typing import Dict, List, Set

import networkx as nx
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SERVICE_MAP_PATH = "path_map.json"
MONOLITH_DIR = Path("monolith")
OUTPUT_DIR = Path("servicesapproche4")
PY_BASE_IMAGE = "python:3.10-slim"

# Load service map
with open(SERVICE_MAP_PATH) as f:
    SERVICE_MAP: Dict[str, List[str]] = json.load(f)
route_to_service = {r: svc for svc, routes in SERVICE_MAP.items() for r in routes}

# ─── COLLECT IMPORTS ──────────────────────────────────────────────────────────
IMPORT_LINES: Set[str] = set()
for py in MONOLITH_DIR.rglob("*.py"):
    lines = py.read_text(encoding="utf-8").splitlines()
    tree = ast.parse("\n".join(lines))
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            IMPORT_LINES.add(lines[node.lineno - 1].strip())

# ─── EXTRACT GLOBAL DEFINITIONS ─────────────────────────────────────────────────
CLASS_DEFS: Dict[str, str] = {}
FUNCTION_DEFS: Dict[str, str] = {}
OBJECT_DEFS: Dict[str, str] = {}

class GlobalDefExtractor(ast.NodeVisitor):
    def __init__(self, lines: List[str]):
        self.lines = lines
        self.scope = 0

    def visit_ClassDef(self, node: ast.ClassDef):
        if self.scope == 0:
            CLASS_DEFS[node.name] = "\n".join(self.lines[node.lineno-1:node.end_lineno])
        self.scope += 1
        self.generic_visit(node)
        self.scope -= 1

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.scope == 0:
            FUNCTION_DEFS[node.name] = "\n".join(self.lines[node.lineno-1:node.end_lineno])
        self.scope += 1
        self.generic_visit(node)
        self.scope -= 1

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def visit_Assign(self, node: ast.Assign):
        if self.scope == 0:
            for t in node.targets:
                if isinstance(t, ast.Name):
                    OBJECT_DEFS[t.id] = "\n".join(self.lines[node.lineno-1:node.end_lineno])

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if self.scope == 0 and isinstance(node.target, ast.Name):
            OBJECT_DEFS[node.target.id] = "\n".join(self.lines[node.lineno-1:node.end_lineno])

# populate definitions
for py in MONOLITH_DIR.rglob("*.py"):
    lines = py.read_text(encoding="utf-8").splitlines()
    tree = ast.parse("\n".join(lines))
    GlobalDefExtractor(lines).visit(tree)

# remove reserved names to avoid duplicate app/template instantiation
for reserved in ('app', 'templates'):
    OBJECT_DEFS.pop(reserved, None)
    FUNCTION_DEFS.pop(reserved, None)
    CLASS_DEFS.pop(reserved, None)

# ─── ROUTE HANDLER EXTRACTION ─────────────────────────────────────────────────
class RouteExtractor(ast.NodeVisitor):
    def __init__(self, source: str):
        self.src_lines = source.splitlines()
        self.handlers: Dict[str, str] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        for deco in node.decorator_list:
            target = None
            if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute) and deco.func.attr in {"get","post","put","delete","patch"}:
                target = deco
            elif isinstance(deco, ast.Attribute) and deco.attr in {"get","post","put","delete","patch"}:
                target = deco
            if target:
                start = min(d.lineno for d in node.decorator_list) - 1
                block = "\n".join(self.src_lines[start:node.end_lineno])
                route = None
                if isinstance(target, ast.Call) and target.args and isinstance(target.args[0], ast.Constant):
                    route = target.args[0].value
                key = route or node.name
                self.handlers[key] = block
        self.generic_visit(node)


def find_route_handlers(py_path: Path) -> Dict[str, str]:
    src = py_path.read_text(encoding="utf-8")
    extr = RouteExtractor(src)
    extr.visit(ast.parse(src))
    return extr.handlers

# ─── DEPENDENCY GRAPH ──────────────────────────────────────────────────────────
def resolve_dependencies_static(py_path: Path, graph: nx.DiGraph):
    src = py_path.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.ImportFrom) and node.module:
            cand = MONOLITH_DIR / f"{node.module}.py"
            if cand.exists(): graph.add_edge(py_path, cand)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                cand = MONOLITH_DIR / f"{alias.name.split('.')[0]}.py"
                if cand.exists(): graph.add_edge(py_path, cand)

# ─── SERVICE ASSEMBLY ─────────────────────────────────────────────────────────
def assemble_service(service_name: str, handlers: Dict[str, str], deps: Set[Path]):
    svc_dir = OUTPUT_DIR / service_name
    shutil.rmtree(svc_dir, ignore_errors=True)
    svc_dir.mkdir(parents=True, exist_ok=True)

    # copy dependencies + static/templates
    for dep in deps:
        shutil.copy(dep, svc_dir / dep.name)
    for folder in ('static', 'templates'):
        src = MONOLITH_DIR / folder
        if src.exists(): shutil.copytree(src, svc_dir / folder)

    # copy original requirements
    orig_req = MONOLITH_DIR / 'requirements.txt'
    if orig_req.exists(): shutil.copy(orig_req, svc_dir / 'requirements.txt')

    # build main.py
    import_block = sorted(IMPORT_LINES)
    imports = import_block + [
        'app = FastAPI()',
        "app.mount('/static', StaticFiles(directory='static'), name='static')",
        'templates = Jinja2Templates(directory="templates")',
    ]

    def names_in_code(src_block: str) -> Set[str]:
        return {node.id for node in ast.walk(ast.parse(src_block)) if isinstance(node, ast.Name)}

    used_names: Set[str] = set()
    for block in handlers.values(): used_names |= names_in_code(block)

    seen_defs: Set[str] = set()
    ordered_defs: List[str] = []

    def add_defs(name: str):
        if name in seen_defs: return
        seen_defs.add(name)
        for mapping in (CLASS_DEFS, FUNCTION_DEFS, OBJECT_DEFS):
            if name in mapping:
                for sub in names_in_code(mapping[name]): add_defs(sub)
                ordered_defs.append(mapping[name])
                break

    for nm in list(used_names): add_defs(nm)

    main_py = "\n".join(imports + ordered_defs + list(handlers.values()))
    (svc_dir / 'main.py').write_text(main_py, encoding='utf-8')

    # write Dockerfile with libgomp1 for LightGBM
    dockerfile = f"""
FROM {PY_BASE_IMAGE}
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","80"]
"""
    (svc_dir / 'Dockerfile').write_text(dockerfile.strip(), encoding='utf-8')

def write_gateway_and_compose():
    # pick the service that owns "/" (your homepage)
    default_svc = list(SERVICE_MAP.keys())[0].lower()

    # 1) Upstreams for each service
    upstreams = [
        f"upstream {svc.lower()} {{ server {svc.lower()}:80; }}"
        for svc in SERVICE_MAP
    ]

    # 2) Server block: static + API routes + fallback
    locations = [
        # static assets → homepage service
        "    location /static/ { proxy_pass http://%s; }" % default_svc,
        # API routes
    ]
    for svc, routes in SERVICE_MAP.items():
        name = svc.lower()
        for route in routes:
            if route in ("/", "/static"):
                continue
            path = route.rstrip("/") or "/"
            locations.append(
                f"    location {path} {{ proxy_pass http://{name}{path}; }}"
            )
    # fallback for everything else
    locations.append(f"    location / {{ proxy_pass http://{default_svc}/; }}")

    # 3) Write conf.d/default.conf
    gateway_conf = Path("gateway_conf")
    gateway_conf.mkdir(exist_ok=True)
    (gateway_conf / "default.conf").write_text(
        "\n".join(upstreams)
        + "\n\nserver {\n    listen 80;\n"
        + "\n".join(locations)
        + "\n}\n",
        encoding="utf-8"
    )

    # 4) Write docker-compose.yaml
    lines = ['version: "3.8"', 'services:']
    # microservices
    for svc in SERVICE_MAP:
        name = svc.lower()
        lines += [
            f"  {name}:",
            f"    build: ./{OUTPUT_DIR}/{svc}",
            "    networks:",
            "      - appnet",
        ]
    # gateway
    lines += [
        "  gateway:",
        "    image: nginx:stable-alpine",
        "    ports:",
        "      - \"80:80\"",
        "    volumes:",
        "      - ./gateway_conf/default.conf:/etc/nginx/conf.d/default.conf:ro",
        "    depends_on:",
    ]
    for svc in SERVICE_MAP:
        lines.append(f"      - {svc.lower()}")
    lines += [
        "    networks:",
        "      - appnet",
        "networks:",
        "  appnet:",
    ]
    Path("docker-compose.yaml").write_text("\n".join(lines), encoding="utf-8")



if __name__ == '__main__':
    OUTPUT_DIR.mkdir(exist_ok=True)
    G = nx.DiGraph()
    py_files = list(MONOLITH_DIR.rglob('*.py'))
    # collect handlers
    route_handlers: Dict[str, Dict[str, str]] = {svc: {} for svc in SERVICE_MAP}
    for py in py_files:
        for r, code in find_route_handlers(py).items():
            svc = route_to_service.get(r, 'MiscService')
            route_handlers.setdefault(svc, {})[r] = code
    # resolve deps
    for py in py_files:
        resolve_dependencies_static(py, G)
    # assemble services
    for svc, handlers in route_handlers.items():
        deps = {p for p in py_files if p in G and any(p.name in h for h in handlers.values())}
        assemble_service(svc, handlers, deps)
    # write gateway and compose
    write_gateway_and_compose()