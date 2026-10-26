# Interview preparation

## A two-minute explanation

“AgriResearch AI is an evidence-first agricultural research prototype. It
combines page-aware document retrieval with bounded tools for real cereal
statistics. I compare cosine retrieval against dense/lexical rank fusion and
evaluate the planner separately. Answers expose source excerpts and computed
values. I distinguish citation membership from scientific correctness, and
report failures rather than interpreting a small benchmark as broad validation.”

Demonstrate the actual application and measured files before claiming results.
Read `evaluation/results.json`, `PROGRESS.md` and the research report for the
current tested scope. This is a portfolio prototype, not a publication.

## Why RAG instead of fine-tuning?

The immediate need is traceable source access and refreshable research evidence.
RAG supplies provenance without encoding new facts into weights. It still fails
when extraction, ranking, source quality or query coverage is poor. Fine-tuning
could improve routing or response format later; it is not a citation database.

## Why FAISS and MiniLM?

Normalized dense vectors and exact inner-product search make cosine retrieval
simple to inspect on CPU. Small corpora do not justify approximate index tuning.
MiniLM is compact, but English model coverage, domain vocabulary and truncation
are limitations. Compare agricultural embeddings only with a held-out set.

## Why LangGraph if the planner uses rules?

The graph makes tool budgets, state, failures and verification explicit. Rules
provide a reproducible baseline without a paid API. Do not call this a learned
planner. A future model planner should produce typed allowlisted actions, be
evaluated on routing accuracy, and never obtain arbitrary code execution.

## What makes it agentic?

Question classification selects search, analysis and reporting tools; results
are aggregated and checked before finalization. It supports multi-tool research
requests. It has limited autonomy and no self-directed experimental discovery.

## How are calculations safe and reproducible?

Allowlisted Pandas functions validate variables, countries, years and operations.
Two observed consecutive years are required for YoY; missing fields fail clearly.
Results include rows used, units, source and dataset hash. Test fixtures are
explicitly synthetic and separate from real evaluation observations.

## What does verification prove?

Research quotes occur in a retrieved chunk and cite that chunk. Calculations
match the deterministic tool's serialized result. It does not prove the source
is correct, the excerpt answers the question, or a model's explanation follows
from it. Optional model prose is labeled unverified. Human review remains needed.

## Evaluation questions to anticipate

- Recall@k counts labeled evidence spans recovered; MRR rewards early relevant
  evidence. Labels require both document identity and exact source span.
- Compare semantic baseline and RRF under the same chunking, k and threshold.
  Negative gains are valid results. Avoid changing settings after seeing scores
  without declaring the set a development set.
- Citation membership and answer-span presence are narrow proxies. Explain their
  denominators, missing source labels and why 100% is not proof of factuality.
- Report one-run local latency separately from model/index setup. No claim of
  statistically reliable throughput follows from this small run.
- Labels are implementing-agent reviewed, not independently human annotated.
  Propose researcher adjudication and a held-out multi-paper set before a paper.

## Agricultural reasoning boundaries

Pakistan national cereal yield cannot support Punjab wheat recommendations.
Study-specific irrigation treatments cannot automatically transfer to a different
soil, cultivar, season or region. Correlation/trends are not causal effects.
Explain source limitations before designing an agronomic experiment.

## Proposed research extensions

1. Curate independently licensed wheat/rice papers and extension guidance;
   annotate gold evidence, counterevidence and unanswerable questions with a
   domain researcher. Freeze train/development/test splits by document.
2. Evaluate tokenizer-aware chunking, BM25, agricultural embeddings and a
   cross-encoder reranker using paired queries and uncertainty intervals.
3. Evaluate citation entailment and answer completeness with blinded human
   review; calibrate abstention on a development set and report test coverage.
4. Add Urdu and code-switched queries with a multilingual retrieval ablation.
5. Add approved district crop/weather data only after license and schema review;
   separate observational analysis from controlled experiment claims.

## Honest answers about ownership

The implementation was built with AI assistance using established open-source
libraries. The contribution is source-aware system integration, constrained
analytics, transparent evaluation and failure analysis. Do not claim invention
of RAG, LangGraph, MiniLM or new agronomic findings. Review every module and
reproduce the experiments yourself before the interview.
