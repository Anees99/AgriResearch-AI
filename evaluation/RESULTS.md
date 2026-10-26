# Actual measured results

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

## Automated test status

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

Citation membership is not entailment or agronomic validity. Agent cases are evaluated only for enhanced mode. All labels are implementing-agent reviewed development labels; no independent human adjudication has occurred.
