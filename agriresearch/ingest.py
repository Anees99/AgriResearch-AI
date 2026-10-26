"""Page-aware ingestion. No OCR: weak extraction fails explicitly."""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import re

@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    title: str
    author: str
    date: str
    url: str
    page: int | None
    text: str
    sha256: str
    quality_notes: str = ""
    license: str = "User-authorized upload; redistribution terms unspecified"
    crops: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()
    evidence_type: str = "unreviewed"

    def to_dict(self):
        return asdict(self)

def normalize(text):
    return re.sub(r"\s+", " ", text.replace("\x00", " ")).strip()

def load_pages(path: Path):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Document not found: {path.name}")
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError("Document exceeds 20 MiB limit")
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are unsupported")
        pages = [(i + 1, normalize(p.extract_text() or "")) for i, p in enumerate(reader.pages)]
    elif path.suffix.lower() in {".txt", ".md"}:
        pages = [(None, normalize(path.read_text(encoding="utf-8")))]
    else:
        raise ValueError("Only PDF, TXT and Markdown documents are supported")
    if not pages or any(len(t) < 30 or sum(c.isalpha() for c in t) / max(1, len(t)) < .3 for _, t in pages):
        raise ValueError("Empty or poorly extracted page; provide text or run OCR separately")
    return pages

def chunk_document(path, metadata, size=110, overlap=20):
    if size < 10 or not 0 <= overlap < size:
        raise ValueError("Invalid chunk size/overlap")
    required = {"document_id", "title", "author", "date", "url"}
    if not required <= metadata.keys() or any(not metadata[k] for k in required):
        raise ValueError("Document metadata is incomplete; use 'unknown' for unknown dates")
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    chunks = []
    for page, text in load_pages(path):
        words = text.split()
        for start in range(0, len(words), size - overlap):
            body = " ".join(words[start:start + size])
            identity = f"{metadata['document_id']}:{digest}:{page}:{start}:{size}:{overlap}"
            chunks.append(Chunk(hashlib.sha256(identity.encode()).hexdigest()[:20],
                                **{k: metadata[k] for k in required}, page=page,
                                text=body, sha256=digest, quality_notes=metadata.get("quality_notes", ""),
                                license=metadata.get("license", "User-authorized upload; redistribution terms unspecified"),
                                crops=tuple(metadata.get("crops", [])), regions=tuple(metadata.get("regions", [])),
                                evidence_type=metadata.get("evidence_type", "unreviewed")))
            if start + size >= len(words):
                break
    return chunks

def load_corpus(root, size=110, overlap=20):
    root = Path(root)
    manifest = json.loads((root / "data/sources.json").read_text(encoding="utf-8"))
    chunks = []
    for source in manifest:
        if source.get("kind") != "document" or source.get("status") != "downloaded":
            continue
        path = (root / source["path"]).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("Corpus path leaves project directory")
        if hashlib.sha256(path.read_bytes()).hexdigest() != source["sha256"]:
            raise ValueError(f"Source hash mismatch: {source['document_id']}")
        chunks.extend(chunk_document(path, source, size, overlap))
    if not chunks:
        raise ValueError("No corpus documents. Run python scripts/fetch_sources.py first.")
    return chunks
