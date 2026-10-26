# AgriResearch AI progress

## Scope and plan
1. Research: verify source terms; preserve provenance, snapshots and hashes.
2. Baseline: PDF/text ingestion, semantic FAISS retrieval, extractive citations.
3. Agent: bounded LangGraph planning, validated data tools, report and verification.
4. Evaluation: source-reviewed development questions, semantic vs hybrid retrieval,
   routing, citation integrity, abstention and timing. No invented results.
5. Finalize: execute tests, document results and interview explanations.

## Decisions
- Dedicated folder; unrelated workspace files are untouched.
- Offline extractive generation is default; optional configured Groq synthesis.
- National cereal aggregates must never be labeled wheat-specific or local data.
- No unrestricted code execution, generated SQL, or shell tools.
- Dependency installation was explicitly approved by the user after auto-review rejection.
- External corpus material retains its own terms; code license does not cover data.

## Status
- Implemented modular ingestion, semantic/lexical retrieval, BM25 rank fusion,
  source hashes, constrained analytics, LangGraph workflow and Streamlit UI.
- Acquired 126 authentic WDI country/year/indicator observations, three indicator
  definitions, and the 9-page Pakistan wheat-irrigation paper.
- Recorded publisher license conflict conservatively as noncommercial use;
  flagged the paper's inconsistent seasonal rainfall figures.
- USDA downloads failed and remain unavailable. FAO full-publication license
  review remains pending. Neither source is fabricated or silently indexed.
- Prepared 12 evidence questions, four tool-workflow questions and four unsupported
  questions, with exact evidence spans and static numerical checks.
- Created README, research-report draft, architecture diagram, source review,
  interview guide, demo prompts and a VS Code workspace file.
- Installed approved dependencies in the project venv; exact versions recorded.
- Final automated suite: **54 passed, 0 failed, 0 skipped**. JUnit XML and
  machine-readable test status are stored under evaluation/.
- Fixed a UI test that selected the wrong button; stable widget keys are used.
- Executed semantic baseline and hybrid-agent evaluation: Recall@3 0.7500 vs
  0.8333, MRR 0.7083 vs 0.7917 on 12 source-reviewed evidence questions.
- Executed separate lexical fallback: Recall@3 0.9167, MRR 0.8194; its threshold
  differs, so this is not a controlled embedding ablation.
- All eight expected tool plans matched. Static numerical gold checks passed
  2/2; independent reference arithmetic passed 3/3. Four unsupported cases were
  handled correctly in the final development run. Raw tool completion was 6/8;
  two unavailable-data requests correctly returned analysis-tool errors.
- Preserved the initial run's 3/4 abstention score and original source manifest.
  Added and tested curated crop/region applicability checks after the observed
  near-topic rice/Sindh false positive. This is development-set iteration.
- Preserved remaining retrieval failures: baseline r10/r11/r12; hybrid r10/r12.
- Generated examples/demo_report.md with real evidence, calculations and a
  four-tool execution. Rebuilt final research report from actual outputs.
- Recorded cached model artifact hashes. Loaded commit was unavailable from
  Transformers; cache inventory is not runtime attestation.
- All five implementation phases completed for the documented prototype scope.

## Remaining limitations
- Small English corpus with one agricultural experiment; no independent human
  annotations, held-out generalization study or domain factuality adjudication.
- Rule-based planner; no persistent conversational follow-up resolution.
- Applicability guard uses finite crop/location lists; no general entailment or
  agronomic recommendation validation. Unreviewed upload scopes cannot support
  recommendation-like requests.
- Exact quotation verification is not relevance, truth or semantic entailment.
- PDF tables/columns and source-study inconsistencies require domain review.
- No OCR, local weather data, provincial or crop-specific structured measurements.
- Groq calls remain disabled/unrun. No production deployment.

## GitHub publication
- Publication requested by the owner on 26 October 2026.
- Repository: https://github.com/Anees99/AgriResearch-AI
- Public source package includes code, licensed WDI data, documentation and
  measured evaluation artifacts. Local environments, credentials, downloads,
  uploaded documents and the separately licensed research PDF are excluded.
