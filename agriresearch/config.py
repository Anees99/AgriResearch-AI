from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

@dataclass(frozen=True)
class Settings:
    backend: str = "semantic"
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    revision: str | None = None
    local_only: bool = True
    chunk_size: int = 110  # words; keep MiniLM's tokenizer limit in mind
    overlap: int = 20
    top_k: int = 3
    threshold: float = .28
    max_tools: int = 4

    def __post_init__(self):
        if self.backend not in {"semantic", "lexical"}:
            raise ValueError("Unknown embedding backend")
        if not 0 <= self.overlap < self.chunk_size or self.chunk_size < 10:
            raise ValueError("Require chunk_size >= 10 and 0 <= overlap < chunk_size")
        if not 1 <= self.top_k <= 20 or not -1 <= self.threshold <= 1:
            raise ValueError("Invalid retrieval configuration")
        if not 1 <= self.max_tools <= 8:
            raise ValueError("max_tools must be in 1..8")

    @classmethod
    def from_env(cls):
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        return cls(backend=os.getenv("EMBEDDING_BACKEND", "semantic"),
                   model=os.getenv("EMBEDDING_MODEL", cls.model),
                   revision=os.getenv("EMBEDDING_REVISION") or None,
                   local_only=os.getenv("MODEL_LOCAL_ONLY", "true").lower() == "true",
                   chunk_size=int(os.getenv("CHUNK_SIZE", "110")),
                   overlap=int(os.getenv("CHUNK_OVERLAP", "20")),
                   top_k=int(os.getenv("TOP_K", "3")),
                   threshold=float(os.getenv("SIMILARITY_THRESHOLD", ".28")),
                   max_tools=int(os.getenv("MAX_TOOL_CALLS", "4")))
