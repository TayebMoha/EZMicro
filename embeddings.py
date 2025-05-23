from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("microsoft/codebert-base")

def embed_text(text: str):
    return model.encode(text, normalize_embeddings=True)

def label_files(summaries: dict, architect_names: list, sim_thr=0.25):
    arch_vecs = {n: embed_text(n + " logic") for n in architect_names}
    labels = {}

    for fname, summ in summaries.items():
        fv = embed_text(summ)
        best, score = max(
            ((name, util.cos_sim(fv, v).item()) for name, v in arch_vecs.items()),
            key=lambda t: t[1]
        )
        labels[fname] = best if score > sim_thr else "Unknown"
    return labels
