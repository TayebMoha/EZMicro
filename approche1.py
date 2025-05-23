import os
import ast
import json
import shutil
from pathlib import Path
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from transformers import AutoTokenizer, AutoModel
import torch


#######################################
# Step 1: Extract Code Entities
#######################################

def extract_code_entities(file_path):
    """
    Parse a Python file and extract top-level function and class definitions.
    Returns a list of dictionaries with keys: 'name', 'type', 'code', 'file'.
    """
    entities = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        tree = ast.parse(source, filename=file_path)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return entities

    lines = source.splitlines()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', start + 20)
            code_snippet = "\n".join(lines[start:end])
            entity = {
                'name': node.name,
                'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                'code': code_snippet,
                'file': file_path
            }
            entities.append(entity)
    return entities


def gather_entities(monolith_dir):
    """
    Recursively walk through monolith_dir and extract code entities from all Python files.
    """
    entities = []
    p = Path(monolith_dir)
    for file in p.rglob("*.py"):
        # Optionally, skip test files or hidden files
        if file.name.lower().startswith("test") or file.name.startswith("."):
            continue
        ents = extract_code_entities(str(file))
        entities.extend(ents)
    return entities


#######################################
# Step 2: Compute Embeddings
#######################################

def compute_embeddings(entities, tokenizer, model):
    """
    Compute a semantic embedding for each entity using CodeBERT.
    Uses the entity's name and code.
    """
    embeddings = []
    for ent in entities:
        text = ent['name'] + "\n" + ent['code']
        inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
        with torch.no_grad():
            output = model(**inputs)
        # Mean-pool the token embeddings
        emb = output.last_hidden_state.mean(dim=1).squeeze().numpy()
        embeddings.append(emb)
    return np.vstack(embeddings)


#######################################
# Step 3: Cluster Entities
#######################################

def cluster_embeddings(embeddings, n_clusters=None):
    """
    Cluster the embeddings using Agglomerative Clustering.
    If n_clusters is not provided, use the heuristic: max(2, ceil(sqrt(n_entities))).
    """
    n_entities = embeddings.shape[0]
    if n_entities < 2:
        return np.array([0] * n_entities)
    if n_clusters is None:
        n_clusters = max(2, int(np.ceil(np.sqrt(n_entities))))
    clustering = AgglomerativeClustering(n_clusters=n_clusters)
    labels = clustering.fit_predict(embeddings)
    return labels


#######################################
# Step 4: Generate Microservice Artifacts
#######################################

def generate_microservice_scaffolds(entities, labels, output_dir):
    """
    For each cluster (microservice candidate), generate a folder with:
      - service.py: Aggregated code from entities in that cluster.
      - main.py: A simple Flask app that serves as a placeholder.
      - requirements.txt: Minimal dependencies.
      - Dockerfile: Containerization instructions.
    """
    clusters = {}
    for ent, label in zip(entities, labels):
        clusters.setdefault(label, []).append(ent)

    microservice_dirs = []
    for label, ents in clusters.items():
        service_name = f"microservice_{label}"
        service_dir = Path(output_dir) / service_name
        service_dir.mkdir(parents=True, exist_ok=True)
        microservice_dirs.append(service_dir)

        # Create service.py: aggregate code entities
        with open(service_dir / "service.py", "w", encoding="utf-8") as f:
            f.write("# Auto-generated service module\n\n")
            for ent in ents:
                f.write(f"# From file: {ent['file']}\n")
                f.write(ent['code'] + "\n\n")

        # Create main.py: basic Flask application
        with open(service_dir / "main.py", "w", encoding="utf-8") as f:
            f.write("from flask import Flask\n")
            f.write("from service import *\n\n")
            f.write("app = Flask(__name__)\n\n")
            f.write("@app.route('/')\n")
            f.write("def index():\n")
            f.write(f"    return 'Service: {service_name}'\n\n")
            f.write("if __name__ == '__main__':\n")
            f.write("    app.run(debug=True, port=8000)\n")

        # Create requirements.txt
        with open(service_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("flask\n")

        # Create Dockerfile
        with open(service_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write("FROM python:3.9-slim\n")
            f.write("WORKDIR /app\n")
            f.write("COPY . .\n")
            f.write("RUN pip install -r requirements.txt\n")
            f.write("CMD [\"python\", \"main.py\"]\n")

    return microservice_dirs


def generate_docker_compose(microservice_dirs, output_dir):
    """
    Generate a docker-compose.yml file that builds and runs all microservices.
    """
    lines = ["version: '3.8'", "services:"]
    port = 8000
    for service_dir in microservice_dirs:
        service_name = service_dir.name
        lines.append(f"  {service_name}:")
        lines.append(f"    build: ./{service_name}")
        lines.append("    ports:")
        lines.append(f"      - '{port}:8000'")
        port += 1
    lines.append("networks:")
    lines.append("  default:")
    lines.append("    driver: bridge")
    with open(Path(output_dir) / "docker-compose.yml", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


#######################################
# Main Pipeline Function
#######################################

def main(monolith_dir, output_dir="./servicesapproche1"):
    # Load CodeBERT for embeddings
    model_id = "microsoft/codebert-base"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id)
    model.eval()

    print("Extracting code entities from monolith...")
    entities = gather_entities(monolith_dir)
    print(f"Extracted {len(entities)} entities.")

    print("Computing embeddings...")
    embeddings = compute_embeddings(entities, tokenizer, model)

    print("Clustering entities...")
    labels = cluster_embeddings(embeddings)

    print("Generating microservice scaffolds...")
    microservice_dirs = generate_microservice_scaffolds(entities, labels, output_dir)

    print("Generating docker-compose.yml...")
    generate_docker_compose(microservice_dirs, output_dir)

    print("✅ Microservices generated successfully in", output_dir)


if __name__ == "__main__":
    main("./monolith")
