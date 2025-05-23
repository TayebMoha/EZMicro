# sdg_builder.py
"""
Builds a Service Dependency Graph (SDG) from the method‑extraction JSON for all
languages and runs Louvain community detection to produce cohesive clusters.

Outputs:
    clusters: List[List[str]] where each inner list is a set of method ids
              formatted as "<filename>::<signature>"

architect_service_list: Optional[List[str]] – if provided, any cluster whose
    dominant label matches one of these names is kept; others grouped under
    MiscService.
"""
import json
import ast
import re
import itertools
import networkx as nx
from cdlib import algorithms
from typing import Dict, List, Tuple
import jellyfish, sentence_transformers.util as util
from embeddings import embed_text

def _add_edges_for_file(methods, g, file_id):
    # existing intra-file edges
    ids = [f"{file_id}::{m['signature']}" for m in methods]
    for i, u in enumerate(ids):
        g.add_node(u)
        for v in ids[i + 1:]:
            g.add_edge(u, v, weight=1.0)


def _import_edges_py(code: str, file_id: str, g: nx.Graph):
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            # import pandas as pd
            for alias in node.names:
                mod = alias.name.split(".")[0]
                g.add_edge(f"{file_id}::file", f"{mod}.py::file", weight=3.0)
        elif isinstance(node, ast.ImportFrom):
            # from pandas import DataFrame
            mod = (node.module or "").split(".")[0]
            g.add_edge(f"{file_id}::file", f"{mod}.py::file", weight=3.0)



IMPORT_RE_JAVA = re.compile(r'import\s+([\w\.]+);')


def _import_edges_java(code: str, file_id: str, g: nx.Graph):
    imports = IMPORT_RE_JAVA.findall(code)
    for imp in imports:
        mod = imp.split(".")[-1]
        target = f"{mod}.java::file"
        source = f"{file_id}::file"
        g.add_edge(source, target, weight=3.0)


def build_sdg(extracted_methods: Dict[str, List[dict]], code_files: Dict[str, str],
              prior_labels: Dict[str, str]) -> nx.Graph:
    g = nx.Graph()

    # Step 1: intra-file edges (unchanged)
    for file_id, methods in extracted_methods.items():
        _add_edges_for_file(methods, g, file_id)

    # Step 2: semantic edges from prior_labels
    for a, b in itertools.combinations(code_files.keys(), 2):
        if prior_labels.get(a) == prior_labels.get(b) and prior_labels[a] != "Unknown":
            g.add_edge(f"{a}::file", f"{b}::file", weight=5.0)

    # Step 3: add import edges based on language
    for file_id, code in code_files.items():
        if file_id.endswith(".py"):
            _import_edges_py(code, file_id, g)
        elif file_id.endswith(".java"):
            _import_edges_java(code, file_id, g)
        # Add PHP/JS extractors here if available

    return g


def cluster_sdg(g: nx.Graph) -> List[List[str]]:
    """Run Louvain community detection."""
    comm = algorithms.louvain(g)
    return comm.communities



def map_clusters_to_services(clusters, svc_vecs, arch_names):
    mapping={}
    for cluster in clusters:
        cluster_vec = embed_text(" ".join(cluster))
        best = max(arch_names,
                   key=lambda n: util.cos_sim(cluster_vec, svc_vecs[n]).item())
        if util.cos_sim(cluster_vec, svc_vecs[best]).item() < 0.20:
            # tie‑break with Jaro‑Winkler on raw tokens
            best = min(arch_names,
                       key=lambda n: jellyfish.jaro_winkler(n.lower()," ".join(cluster).lower()))
        mapping.setdefault(best, []).extend(cluster)
    return mapping

if __name__ == "__main__":
    # Example demo
    with open("extracted.json") as f:
        data = json.load(f)
    g = build_sdg(data)
    clusters = cluster_sdg(g)
    print(clusters)
