"""Exact cosine baseline and reciprocal rank fusion with a BM25 lexical ranker."""
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
import numpy as np
from .ingest import Chunk

STOP = set("a an the is are of for in on and to what how does do by with which explain about".split())
def tokens(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP]

class Retriever:
    def __init__(self, chunks, settings):
        if not chunks:
            raise ValueError("Cannot index an empty corpus")
        if len({c.id for c in chunks}) != len(chunks):
            raise ValueError("Duplicate chunk identifiers")
        self.chunks, self.settings = list(chunks), settings
        self.counts = [Counter(tokens(c.text)) for c in chunks]
        self.vocab = sorted(set().union(*[c.keys() for c in self.counts]))
        if not self.vocab:
            raise ValueError("Corpus has no searchable terms after normalization")
        self.df = {w: sum(w in c for c in self.counts) for w in self.vocab}
        self.model = None
        self.index = None
        if settings.backend == "semantic":
            import faiss
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.model, local_files_only=settings.local_only,
                                             revision=settings.revision, trust_remote_code=False,
                                             model_kwargs={"use_safetensors": True})
            self.model_revision = getattr(self.model[0].auto_model.config, "_commit_hash", None)
            vectors = self.model.encode([c.text for c in chunks], normalize_embeddings=True)
            self.index = faiss.IndexFlatIP(vectors.shape[1])
            self.index.add(np.asarray(vectors, dtype="float32"))
        else:
            # Explicit offline fallback: TF-IDF cosine, never reported as semantic.
            self.matrix = self._lexical_vectors([c.text for c in chunks])

    def _lexical_vectors(self, texts):
        rows = []
        for text in texts:
            counts = Counter(tokens(text))
            row = np.array([counts[w] * math.log(1 + len(self.chunks) / (1 + self.df[w]))
                            for w in self.vocab], dtype="float32")
            rows.append(row / max(float(np.linalg.norm(row)), 1e-12))
        return np.array(rows)

    def _bm25(self, query):
        avg = max(sum(sum(c.values()) for c in self.counts) / len(self.counts), 1e-12)
        scores = []
        for counts in self.counts:
            score = 0.
            for w in set(tokens(query)):
                df, tf = self.df.get(w, 0), counts[w]
                idf = math.log(1 + (len(self.chunks) - df + .5) / (df + .5))
                score += idf * tf * 2.5 / (tf + 1.5 * (.25 + .75 * sum(counts.values()) / avg))
            scores.append(score)
        return np.array(scores)

    def search(self, query, hybrid=False, top_k=None):
        if not isinstance(query, str) or not query.strip() or len(query) > 4000:
            raise ValueError("Question must contain 1..4000 characters")
        k = self.settings.top_k if top_k is None else top_k
        if not isinstance(k, int) or not 1 <= k <= 20:
            raise ValueError("top_k must be 1..20")
        if self.index is not None:
            vector = np.asarray(self.model.encode([query], normalize_embeddings=True), dtype="float32")
            sims, indices = self.index.search(vector, len(self.chunks))
            cosine = np.zeros(len(self.chunks))
            cosine[indices[0]] = sims[0]
        else:
            cosine = self.matrix @ self._lexical_vectors([query])[0]
        order = np.argsort(-cosine, kind="stable")
        scores = cosine.copy()
        if hybrid:
            bm = self._bm25(query)
            lex = np.argsort(-bm, kind="stable")
            scores = np.zeros(len(self.chunks))
            for rank, idx in enumerate(order):
                scores[idx] += 1 / (60 + rank + 1)
            for rank, idx in enumerate(lex):
                if bm[idx] > 0:
                    scores[idx] += 1 / (60 + rank + 1)
            order = np.argsort(-scores, kind="stable")
        return [{"chunk": self.chunks[i].to_dict(), "score": float(scores[i]),
                 "cosine": float(cosine[i])} for i in order
                if cosine[i] >= self.settings.threshold][:k]

    def save(self, directory):
        """Persist JSON provenance and safe FAISS index; no pickle loading."""
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            import faiss
            faiss.write_index(self.index, str(path / "vectors.faiss"))
        else:
            np.save(path / "tfidf.npy", self.matrix, allow_pickle=False)
        (path / "chunks.json").write_text(json.dumps([c.to_dict() for c in self.chunks], indent=2), encoding="utf-8")
        identity = json.dumps([c.to_dict() for c in self.chunks], sort_keys=True).encode()
        (path / "index_metadata.json").write_text(json.dumps({"backend": self.settings.backend,
            "model": self.settings.model, "corpus_sha256": hashlib.sha256(identity).hexdigest(),
            "resolved_model_revision": getattr(self, "model_revision", None),
            "chunk_size_words": self.settings.chunk_size, "overlap_words": self.settings.overlap}, indent=2), encoding="utf-8")
