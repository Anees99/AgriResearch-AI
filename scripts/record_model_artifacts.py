"""Inventory cached model artifacts without network access or inference."""
import hashlib
import json
from pathlib import Path
from huggingface_hub import try_to_load_from_cache

ROOT=Path(__file__).resolve().parents[1]
MODEL="sentence-transformers/all-MiniLM-L6-v2"

def main():
    artifacts=[]
    for name in ["config.json","model.safetensors","tokenizer.json","1_Pooling/config.json"]:
        cached=try_to_load_from_cache(MODEL,name,revision="main")
        if not isinstance(cached,str): raise ValueError(f"Required cached artifact unavailable: {name}")
        path=Path(cached)
        parts=path.parts
        revision=parts[parts.index("snapshots")+1] if "snapshots" in parts else "unknown"
        artifacts.append({"file":name,"cached_revision":revision,
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size})
    record={"model":MODEL,"artifacts":artifacts,"scope":"Post-run inventory of cached main snapshot, not runtime attestation. "
        "Transformers returned no loaded commit identifier in this environment. Pin EMBEDDING_REVISION to this snapshot when reproducing."}
    (ROOT/"docs/model_artifacts.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    print(json.dumps(record,indent=2))

if __name__=="__main__":main()
