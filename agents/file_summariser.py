# agents/file_summariser.py   ← replace entire file
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline

MODEL_ID = "Salesforce/codet5-small"       # ≈ 220 MB, no tiktoken / blobfile deps
tok    = AutoTokenizer.from_pretrained(MODEL_ID)
model  = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID).to("cpu")  # or .cuda()/ .mps

summariser = pipeline("summarization",
                      model=model,
                      tokenizer=tok,
                      device=0 if model.device.type != "cpu" else -1)

def summarise(code: str) -> str:
    """Return a ≤40‑token one‑line summary for a source‑file."""
    return summariser(code, max_length=40, truncation=True)[0]["summary_text"]
