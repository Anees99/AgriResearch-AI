"""Render measured experiment summaries into portfolio documentation.

Does not manufacture metrics: absent outputs remain NOT RUN.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def measured_tables():
    lines=[]
    outputs=[]
    for filename in ["results.json","results_lexical.json"]:
        path=ROOT/"evaluation"/filename
        if not path.exists():
            lines.append(f"{filename}: **NOT RUN**.\n")
            continue
        result=json.loads(path.read_text(encoding="utf-8")); outputs.append(result)
        lines += [f"### {filename}", f"Run timestamp (UTC): {result['timestamp_utc']}. Python {result['python']}. "
                  f"Corpus: {result['corpus_documents']} documents, {result['chunks']} chunks. "
                  f"k={result['settings']['top_k']}; cosine threshold={result['settings']['threshold']}.",
                  "", "| Metric (mean) | System | Value | Cases contributing |", "|---|---|---:|---:|"]
        for system, summary in result["summary"].items():
            for metric,value in summary.items():
                if not isinstance(value,dict): continue
                lines.append(f"| {metric} | {system} | {value['mean']:.4f} | {value['n']} |")
        lines += ["", f"Model/index setup: {result['setup_ms']:.1f} ms (excluded from per-response time).",
                  f"Gold source validation errors: {len(result['source_label_validation_errors'])}.", ""]
        failures=[]
        for row in result["details"]:
            metrics=[k for k in ["recall_at_k","routing_correct","workflow_completed","abstention_correct","analysis_filter_correct","numeric_correct","gold_numeric_correct"] if k in row]
            failed=[k for k in metrics if row[k]<1]
            if failed: failures.append(f"- {row['system']} / {row['id']}: {', '.join(failed)}.")
        lines += ["Failures / incomplete scores:"] + (failures or ["- No failures in the measured narrow checks; this does not establish general correctness."])
        lines += ["", "Detailed per-question results and settings are in the JSON output.", ""]
    return "\n".join(lines),outputs

def main():
    tables,outputs=measured_tables()
    testpath=ROOT/"evaluation/test_status.json"
    tests=json.loads(testpath.read_text()) if testpath.exists() else {"status":"NOT RUN: final full test suite"}
    testtext="```json\n"+json.dumps(tests,indent=2)+"\n```"
    (ROOT/"evaluation/RESULTS.md").write_text("# Actual measured results\n\n"+tables+"\n## Automated test status\n\n"+testtext+"\n\n"
        "Citation membership is not entailment or agronomic validity. Agent cases are evaluated only for enhanced mode. "
        "All labels are implementing-agent reviewed development labels; no independent human adjudication has occurred.\n",encoding="utf-8")
    discussion="Semantic evaluation is not run; no claim about dense/hybrid ranking gains is justified."
    if outputs and (ROOT/"evaluation/results.json").exists():
        semantic=json.loads((ROOT/"evaluation/results.json").read_text())
        a=semantic["summary"]["semantic_baseline"]; b=semantic["summary"]["hybrid_agent"]
        delta=b["recall_at_k"]["mean"]-a["recall_at_k"]["mean"]
        discussion=(f"Hybrid minus baseline Recall@k was {delta:+.4f} on this development set. "
                    "This observed difference is descriptive, not evidence of general superiority. "
                    "Failures are retained above and should guide new held-out experiments, not be hidden by relabeling.")
        lexical_path=ROOT/"evaluation/results_lexical.json"
        if lexical_path.exists():
            lexical=json.loads(lexical_path.read_text())
            score=lexical["summary"]["lexical_baseline"]["recall_at_k"]["mean"]
            discussion+=(f" The separately configured lexical baseline achieved Recall@k {score:.4f}, "
                "higher on these mostly literal lookup questions. Its threshold is 0.05 versus 0.28 "
                "for dense retrieval, so this is not a controlled embedding ablation. It is a useful "
                "warning against assuming dense retrieval must outperform a simple lexical method.")
    report=f'''# AgriResearch AI: Evidence Retrieval and Bounded Agricultural Analysis

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

{tables}

### Automated tests

{testtext}

## 10. Discussion and limitations

{discussion}

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
'''
    (ROOT/"RESEARCH_REPORT.md").write_text(report,encoding="utf-8")
    print("Updated RESEARCH_REPORT.md and evaluation/RESULTS.md from existing outputs")

if __name__=="__main__":main()
