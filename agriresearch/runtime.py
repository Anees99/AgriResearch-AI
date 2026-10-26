from .config import ROOT, Settings
from .ingest import load_corpus
from .retrieval import Retriever
from .analysis import DatasetTool
from .agent import ResearchAgent
import json

def build(settings=None, persist=False):
    settings = settings or Settings.from_env()
    retriever = Retriever(load_corpus(ROOT, settings.chunk_size, settings.overlap), settings)
    if persist: retriever.save(ROOT / "data/index")
    manifest = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    dataset_sources = [s for s in manifest if s.get("kind") == "dataset" and s.get("status") == "downloaded"]
    if not dataset_sources:
        raise ValueError("No verified dataset source in manifest")
    expected = {s["sha256"] for s in dataset_sources}
    if len(expected) != 1:
        raise ValueError("Dataset source hashes disagree")
    dataset = DatasetTool(ROOT / "data/processed/cereals.csv", expected.pop())
    return ResearchAgent(retriever, dataset, settings)
