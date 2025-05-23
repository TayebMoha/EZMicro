import os
import itertools
from pathlib import Path
from typing import Dict, List

from chunker import extract_service_candidates
from agents.language_detector import detect_language
from function_extractor import extract_functions
from agents.file_summariser import summarise
from embeddings import label_files, embed_text
from sdg_builder import build_sdg, cluster_sdg, map_clusters_to_services
from service_assembler import stitch_functions
from agents.syntax_fixer import fix_code
from agents.dockerfile_gen import generate_dockerfile
from agents.api_gen import generate_api_docs
from agents.requirements_gen import generate_requirements_file
import shutil, subprocess, shlex
# Architect‑defined desired services
ARCHITECT_SERVICES = [
    "Page1Service",
    "Page2Service",
    "Page3Service",
    "HomepageService",
]

OUTPUT_ROOT = Path("servicesapproche3")

def move_assets(stitched_files: dict, out_dir: Path):
    for fname, code in list(stitched_files.items()):
        if fname.endswith(".html"):
            tgt = out_dir / "templates" / fname
        elif fname.endswith((".css", ".js")):
            tgt = out_dir / "static" / fname
        else:
            continue
        tgt.parent.mkdir(parents=True, exist_ok=True)
        tgt.write_text(code, encoding="utf-8")
        del stitched_files[fname]

def write_service_output(service_name: str,
                         files: Dict[str, str],
                         language: str,
                         api_docs: str):
    fixed_code = fix_code(files, language)
    dockerfile  = generate_dockerfile(fixed_code)
    req_file, req_content = generate_requirements_file(fixed_code)

    out_dir = OUTPUT_ROOT / service_name
    out_dir.mkdir(parents=True, exist_ok=True)

    for fname, code in fixed_code.items():
        (out_dir / fname).write_text(code, encoding="utf-8")

    (out_dir / "Dockerfile").write_text(dockerfile, encoding="utf-8")
    (out_dir / "openapi.yaml").write_text(api_docs, encoding="utf-8")
    (out_dir / req_file).write_text(req_content, encoding="utf-8")



def run_openapi_generator(stub_yaml: Path, stub_dir: Path):
    """
    Call openapi‑generator on Windows/Mac/Linux, whether the wrapper is
    named openapi-generator or openapi-generator-cli.
    """
    exe = (shutil.which("openapi-generator") or
           shutil.which("openapi-generator-cli") or
           shutil.which("openapi-generator-cli.cmd"))
    if not exe:
        print("⚠️  OpenAPI‑Generator CLI not found – skipping stub generation.")
        return

    # quote all paths; .cmd needs to be called through the shell
    cmd = f'"{exe}" generate -g python-fastapi -i "{stub_yaml}" -o "{stub_dir}" --skip-validate-spec'
    print(">>>", cmd)               # shows exact command
    subprocess.run(cmd, shell=True, check=True)


def process_folder(folder_name: str, code_files: Dict[str, str]):
    if not code_files:
        print(f"⚠️ Skipping empty folder '{folder_name}'")
        return

    print(f"\n📂 Processing folder '{folder_name}' with {len(code_files)} files …")
    language = detect_language(code_files)
    print(f"Detected language: {language}")

    summaries = {f: summarise(c) for f, c in code_files.items() if f.endswith(".py")}
    if not summaries:
        print(f"⚠️ No summarizable Python files in '{folder_name}' — skipping.")
        return

    prior_label = label_files(summaries, ARCHITECT_SERVICES)
    svc_vecs = {name: embed_text(name + " logic") for name in ARCHITECT_SERVICES}

    extracted = extract_functions({f: c for f, c in code_files.items() if f.endswith(".py")}, language)
    if not extracted or all(len(v) == 0 for v in extracted.values()):
        print(f"⚠️ No extractable methods in '{folder_name}' — skipping.")
        return

    sdg = build_sdg(extracted, code_files, prior_label)
    if sdg.number_of_nodes() == 0:
        print(f"⚠️ SDG has no nodes in '{folder_name}' — skipping.")
        return

    clusters = cluster_sdg(sdg)
    cluster_map = map_clusters_to_services(clusters, svc_vecs, ARCHITECT_SERVICES)

    for svc_name, node_ids in cluster_map.items():
        files_map: Dict[str, List[str]] = {}
        for node_id in node_ids:
            if "::" not in node_id:
                continue
            file_part, sig_part = node_id.split("::", 1)
            for m in extracted.get(file_part, []):
                if m.get("signature") == sig_part:
                    files_map.setdefault(file_part, []).append(m["method"])
                    break
        if not files_map:
            continue
        stitched_files = {fn: stitch_functions(funcs) for fn, funcs in files_map.items()}
        api_docs = generate_api_docs(stitched_files)
        print(f"   🚀 Generating micro‑service '{svc_name}' with {len(stitched_files)} files …")

        stub_dir = Path("servicesapproche3/stubs/") / svc_name
        stub_dir.mkdir(parents=True, exist_ok=True)
        stub_yaml = stub_dir / "stub.yaml"
        stub_yaml.write_text(api_docs, encoding="utf-8")

        run_openapi_generator(stub_yaml, stub_dir)

        move_assets(stitched_files, stub_dir)
        write_service_output(svc_name, stitched_files, language, api_docs)


def main():
    monolith_path = "monolith"
    top_level = extract_service_candidates(monolith_path)
    for folder, code_files in top_level.items():
        process_folder(folder, code_files)


if __name__ == "__main__":
    main()
