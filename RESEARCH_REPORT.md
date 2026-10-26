# AgriResearch AI: Evidence Retrieval and Bounded Agricultural Analysis

## 1. Abstract

This portfolio study implements a modular agricultural research assistant using
page-aware retrieval, a bounded LangGraph workflow, and validated numerical tools.
It uses genuine World Bank WDI/FAO national cereal observations and a Pakistan
wheat-irrigation paper. It compares cosine retrieval with dense/lexical reciprocal
rank fusion and measures citation membership, numerical correctness, routing,
unsupported-request handling and local timing. The results below are read from
executed experiment outputs. The small development corpus, implementing-agent
labels and extractive answer mode limit any claim of general research validity.

## 2. Introduction

Evidence-based agricultural decision support needs traceable literature and
numerical analysis. A fluent response can obscure source limitations, mismatch
national statistics with local crop questions, or overstate an experiment's
applicability. This prototype prioritizes inspectable evidence over fluency.

## 3. Problem statement

Can a small, reproducible system combine credible source retrieval with safe
structured analysis while clearly separating quoted findings, calculated results
and unverified interpretations? A secondary question is whether hybrid ranking
improves labeled evidence retrieval under fixed chunking and thresholds.

## 4. Research objectives

1. Preserve document identity, authorship, date, URL, hash and PDF page.
2. Establish a semantic baseline and compare a specific hybrid alternative.
3. Execute allowlisted agricultural operations with explicit state and budgets.
4. Expose uncertainty, missing variables and source inconsistencies.
5. Publish reproducible local measurements without claiming peer review.

## 5. Literature and data sources

The corpus includes the World Bank indicator definitions for cereal yield,
production and harvested area, and Abbas et al. (2024), a wheat supplemental
irrigation experiment at NARC. The numeric dataset selects Pakistan, India and
Bangladesh over 2010–2023: 126 long-form country/year/indicator records. It is
not wheat-specific data. Sources retain their own licenses and attribution.

Publisher license prose for the paper says CC BY 4.0 while DC.Rights says
CC BY-NC 4.0; the stricter noncommercial condition is applied and the PDF is
not committed by default. USDA guidance downloads failed. The FAO crop-water
publication remains a candidate pending edition-specific reuse review.
The manifest records unavailable sources rather than inventing replacements.

Methodologically, Lewis et al. (2020) motivate retrieval-augmented access to
external knowledge; this project does not reproduce their jointly trained RAG
model. Reimers and Gurevych (2019) provide the sentence-embedding background for
cosine retrieval. Cormack, Clarke and Buettcher (2009) motivate reciprocal rank
fusion. Their reported benchmark gains are not assumed to transfer to this
corpus; the implementation measures its own results below.

The paper's abstract/results report 257.7 mm rainfall, whereas its conclusion
states 225.3 mm. This is flagged in provenance and reports; the system does not
resolve the discrepancy or recommend an irrigation schedule from it.

## 6. Methodology

PDF extraction uses pypdf and preserves 1-based file pages. Empty or weak pages
fail explicitly; OCR is out of scope. Text is whitespace-normalized and split
into overlapping word windows without crossing PDF pages. Chunk identifiers
include source digest, page, offset and chunk parameters.

The baseline uses all-MiniLM-L6-v2 normalized embeddings and exact FAISS
IndexFlatIP cosine ranking. The enhanced retriever fuses dense and BM25 ranks
with reciprocal rank constant 60. Both retain the same cosine eligibility
threshold. TF-IDF cosine is a separately labeled fallback, not semantic retrieval.

The deterministic planner selects search, analysis, reporting and verification.
Validated Pandas operations cover summary, consecutive-year comparison, series,
country means and missing/IQR summaries. No model-generated Python, SQL or shell
code is executed. Responses expose rows, units, source and dataset hash.

Extractive generation quotes evidence. Optional Groq synthesis is disabled for
evaluation and labeled unverified when configured. The verifier checks excerpt
membership and calculation serialization, not semantic entailment or truth.
A conservative curated-scope guard checks recognized crop and location facets
for recommendation-like questions. Unreviewed uploads/statistical definitions
cannot establish intervention recommendations. Its finite entity lists do not
constitute a general entailment model.

## 7. Architecture

See [the architecture diagram](docs/ARCHITECTURE.md). The graph runs planning,
bounded execution, evidence aggregation, generation, checking and finalization.
Default budget is four tool calls. The graph is acyclic and invocation has a
recursion limit. Provider calls use a timeout and no automatic cost-amplifying
retry loop. Acquisition has a bounded retry policy. Streamlit isolates uploaded
evidence by session and caches only the shared corpus resource.

## 8. Experimental setup

The development set has 12 document-evidence questions, four analytical/multi-tool
questions and four unsupported requests, including a near-topic rice/Sindh
irrigation question unsupported by the wheat experiment. Gold labels pair source IDs, pages
where applicable and inspected exact passages. Static numeric gold values are
supplemented by independent Pandas reference expressions. Labels were reviewed
by the implementing agent, not independently human annotated.

Recall@k counts recovered evidence units; MRR uses the first matching ranked
chunk. Answer-span presence is a narrow proxy. Citation membership checks whether
the quoted text occurs under its cited identifier. Routing compares planned
allowlisted tools with expected tools; execution completion is separate from
correct abstention. Expected unsupported-data errors can therefore reduce raw
completion while correctly refusing the requested calculation.

Enhanced evidence questions execute the full graph; baseline questions execute
retrieval plus extracts. Agent-only cases have no baseline numeric/tool score.
Efficiency metrics prefixed `evidence_` compare the same 12 questions. Aggregate
response_ms/retrieval_ms/tool_calls for enhanced mode also include the eight tool
and abstention cases, so their workload differs from the baseline aggregate.
Each case runs once locally; model/index setup is reported separately. Timing
differences combine graph overhead, search mode and warm-cache effects. No
statistical significance, API factuality or production-throughput claim is made.
Exact dependency versions are recorded in `docs/environment_versions.txt`.
Transformers did not expose the loaded model commit; `docs/model_artifacts.json`
is a separate post-run cache inventory with artifact hashes, not runtime
attestation. Pin the recorded cached revision for reproduction. The local venv
reuses installed packages, so a clean cross-platform install is not validated.

## 9. Results

### results.json
Run timestamp (UTC): 2026-10-25T17:38:58.627323+00:00. Python 3.14.7. Corpus: 4 documents, 72 chunks. k=3; cosine threshold=0.28.

| Metric (mean) | System | Value | Cases contributing |
|---|---|---:|---:|
| recall_at_k | hybrid_agent | 0.8333 | 12 |
| mrr | hybrid_agent | 0.7917 | 12 |
| answer_span_present | hybrid_agent | 0.9167 | 12 |
| citation_membership | hybrid_agent | 1.0000 | 16 |
| routing_correct | hybrid_agent | 1.0000 | 8 |
| workflow_completed | hybrid_agent | 0.7500 | 8 |
| abstention_correct | hybrid_agent | 1.0000 | 4 |
| analysis_filter_correct | hybrid_agent | 1.0000 | 4 |
| numeric_correct | hybrid_agent | 1.0000 | 3 |
| gold_numeric_correct | hybrid_agent | 1.0000 | 2 |
| response_ms | hybrid_agent | 168.7081 | 20 |
| retrieval_ms | hybrid_agent | 21.4589 | 20 |
| tool_calls | hybrid_agent | 2.0500 | 20 |
| evidence_response_ms | hybrid_agent | 255.0221 | 12 |
| evidence_retrieval_ms | hybrid_agent | 29.5455 | 12 |
| evidence_tool_calls | hybrid_agent | 2.0000 | 12 |
| recall_at_k | semantic_baseline | 0.7500 | 12 |
| mrr | semantic_baseline | 0.7083 | 12 |
| answer_span_present | semantic_baseline | 0.7500 | 12 |
| citation_membership | semantic_baseline | 1.0000 | 12 |
| response_ms | semantic_baseline | 23.0905 | 12 |
| retrieval_ms | semantic_baseline | 22.9947 | 12 |
| tool_calls | semantic_baseline | 1.0000 | 12 |
| evidence_response_ms | semantic_baseline | 23.0905 | 12 |
| evidence_retrieval_ms | semantic_baseline | 22.9947 | 12 |
| evidence_tool_calls | semantic_baseline | 1.0000 | 12 |

Model/index setup: 40131.5 ms (excluded from per-response time).
Gold source validation errors: 0.

Failures / incomplete scores:
- semantic_baseline / r10: recall_at_k.
- semantic_baseline / r11: recall_at_k.
- semantic_baseline / r12: recall_at_k.
- hybrid_agent / r10: recall_at_k.
- hybrid_agent / r12: recall_at_k.
- hybrid_agent / u02: workflow_completed.
- hybrid_agent / u03: workflow_completed.

Detailed per-question results and settings are in the JSON output.

### results_lexical.json
Run timestamp (UTC): 2026-10-25T17:39:18.965286+00:00. Python 3.14.7. Corpus: 4 documents, 72 chunks. k=3; cosine threshold=0.05.

| Metric (mean) | System | Value | Cases contributing |
|---|---|---:|---:|
| recall_at_k | lexical_baseline | 0.9167 | 12 |
| mrr | lexical_baseline | 0.8194 | 12 |
| answer_span_present | lexical_baseline | 0.9167 | 12 |
| citation_membership | lexical_baseline | 1.0000 | 12 |
| response_ms | lexical_baseline | 1.3287 | 12 |
| retrieval_ms | lexical_baseline | 1.2824 | 12 |
| tool_calls | lexical_baseline | 1.0000 | 12 |
| evidence_response_ms | lexical_baseline | 1.3287 | 12 |
| evidence_retrieval_ms | lexical_baseline | 1.2824 | 12 |
| evidence_tool_calls | lexical_baseline | 1.0000 | 12 |
| recall_at_k | lexical_hybrid_agent | 0.9167 | 12 |
| mrr | lexical_hybrid_agent | 0.8194 | 12 |
| answer_span_present | lexical_hybrid_agent | 0.9167 | 12 |
| citation_membership | lexical_hybrid_agent | 1.0000 | 16 |
| routing_correct | lexical_hybrid_agent | 1.0000 | 8 |
| workflow_completed | lexical_hybrid_agent | 0.7500 | 8 |
| abstention_correct | lexical_hybrid_agent | 1.0000 | 4 |
| analysis_filter_correct | lexical_hybrid_agent | 1.0000 | 4 |
| numeric_correct | lexical_hybrid_agent | 1.0000 | 3 |
| gold_numeric_correct | lexical_hybrid_agent | 1.0000 | 2 |
| response_ms | lexical_hybrid_agent | 130.9467 | 20 |
| retrieval_ms | lexical_hybrid_agent | 2.9143 | 20 |
| tool_calls | lexical_hybrid_agent | 2.0500 | 20 |
| evidence_response_ms | lexical_hybrid_agent | 206.7997 | 12 |
| evidence_retrieval_ms | lexical_hybrid_agent | 4.3226 | 12 |
| evidence_tool_calls | lexical_hybrid_agent | 2.0000 | 12 |

Model/index setup: 2217.7 ms (excluded from per-response time).
Gold source validation errors: 0.

Failures / incomplete scores:
- lexical_baseline / r12: recall_at_k.
- lexical_hybrid_agent / r12: recall_at_k.
- lexical_hybrid_agent / u02: workflow_completed.
- lexical_hybrid_agent / u03: workflow_completed.

Detailed per-question results and settings are in the JSON output.


### Automated tests

```json
{
  "tests": 54,
  "errors": 0,
  "failures": 0,
  "skipped": 0,
  "passed": 54,
  "status": "passed",
  "recorded_utc": "2026-10-25T17:38:29.031199+00:00",
  "source": "evaluation/pytest-results.xml",
  "command": ".venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp-final --junitxml=evaluation/pytest-results.xml"
}
```

## 10. Discussion and limitations

Hybrid minus baseline Recall@k was +0.0833 on this development set. This observed difference is descriptive, not evidence of general superiority. Failures are retained above and should guide new held-out experiments, not be hidden by relabeling. The separately configured lexical baseline achieved Recall@k 0.9167, higher on these mostly literal lookup questions. Its threshold is 0.05 versus 0.28 for dense retrieval, so this is not a controlled embedding ablation. It is a useful warning against assuming dense retrieval must outperform a simple lexical method.

The initial run is preserved in `evaluation/results_initial.json`: its hard
rice/Sindh negative returned near-topic wheat evidence, producing 3/4 correct
abstentions. That observed failure motivated the curated-scope guard, followed
by rerunning tests and evaluation. This is an explicitly disclosed development
iteration on the same questions, not a held-out improvement claim. Initial
source metadata are preserved in `evaluation/initial_source_manifest.json`.

Exact quotation checks can score highly by construction and cannot establish
answer completeness, relevance, source reliability or correct interpretation.
The corpus is small and English-only; metadata and one experiment cannot support
broad agricultural advice. Retrieval may return reference-list passages or text
with table/column extraction artifacts. The deterministic planner has narrow
language coverage and defaults to Pakistan/cereal yield when filters are omitted.
Use explicit dataset controls for unambiguous analysis.

There is no independent human factuality evaluation, held-out generalization
study, live Groq benchmark, OCR validation, or production deployment. Synthetic
unit-test fixtures are used only to test code; all portfolio numeric examples and
evaluation observations come from the actual downloaded dataset. No new
agronomic finding, causal effect or published research contribution is claimed.

## 11. Future work

Independently annotate a larger licensed multi-paper corpus, hold out documents,
add difficult unanswerable agricultural questions, and assess answer entailment
and completeness with agronomists. Compare tokenizer-aware chunks, agricultural
embeddings, lexical baselines and cross-encoder reranking with paired confidence
intervals. Add Urdu queries and approved district-level crop/weather data only
after coverage, license and schema validation. Resolve source discrepancies
before translating study findings into interventions.

## 12. References

- Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive
  NLP Tasks. https://arxiv.org/abs/2005.11401
- Reimers, N., and Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using
  Siamese BERT-Networks. https://arxiv.org/abs/1908.10084
- Cormack, G. V., Clarke, C. L. A., and Buettcher, S. (2009). Reciprocal rank
  fusion outperforms condorcet and individual rank learning methods. SIGIR,
  pp. 758–759. https://doi.org/10.1145/1571941.1572114
- Abbas, S. H., Islam, Z., Shakoor, A., Qamar, M., Tanveer, S. K., Hussain, I.,
  and Majeed, A. (2024). Impact of supplemental irrigation through sprinkler
  raingun at alternate phenological stages of wheat crop. *Journal of Pure and
  Applied Agriculture*, 9(1), 56–64.
  https://ojs.aiou.edu.pk/index.php/jpaa/article/view/2436
- World Bank / FAO. Cereal yield (AG.YLD.CREL.KG), production (AG.PRD.CREL.MT)
  and land under cereal production (AG.LND.CREL.HA), World Development Indicators.
  https://data.worldbank.org/indicator/AG.YLD.CREL.KG
- World Bank. Data access and licensing.
  https://datacatalog.worldbank.org/public-licenses
- Sentence Transformers. SentenceTransformer API documentation.
  https://www.sbert.net/docs/package_reference/sentence_transformer/model.html
- LangChain. LangGraph StateGraph reference.
  https://reference.langchain.com/python/langgraph/graph

This document describes a portfolio engineering experiment and has not been
submitted, peer reviewed or published as a research paper.
