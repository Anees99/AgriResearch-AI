import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import platform
from statistics import mean
from time import perf_counter
from agriresearch.config import ROOT, Settings
from agriresearch.runtime import build
from agriresearch.generation import evidence_claims, verify

def ranking_metrics(hits, evidence):
    relevant = []
    for h in hits:
        c=h["chunk"]
        relevant.append({i for i,e in enumerate(evidence) if c["document_id"]==e["document_id"] and
            ("page" not in e or c["page"]==e["page"]) and e["span"].lower() in c["text"].lower()})
    found=set().union(*relevant) if relevant else set()
    return len(found)/len(evidence), next((1/(i+1) for i,r in enumerate(relevant) if r),0.)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--lexical",action="store_true")
    args=parser.parse_args()
    os.environ["LLM_PROVIDER"]="extractive"  # No network model calls in evaluation.
    os.environ["LANGSMITH_TRACING"]="false"
    settings=Settings.from_env()
    if args.lexical: settings=replace(settings,backend="lexical",threshold=.05)
    cases=json.loads((ROOT/"evaluation/questions.json").read_text())
    start=perf_counter(); agent=build(settings,persist=True); setup=(perf_counter()-start)*1000
    validation=[]
    for case in cases:
        for e in case.get("evidence",[]):
            exists=any(c.document_id==e["document_id"] and ("page" not in e or c.page==e["page"]) and
                       e["span"].lower() in c.text.lower() for c in agent.retriever.chunks)
            if not exists: validation.append({"id":case["id"],"error":"Gold source span missing; needs label/source review"})
    # Never silently drop missing gold labels or convert them into successful scores.
    detail=[]
    for hybrid in [False,True]:
        name=("hybrid_agent" if hybrid else "semantic_baseline") if not args.lexical else ("lexical_hybrid_agent" if hybrid else "lexical_baseline")
        for case in cases:
            t=perf_counter()
            if "evidence" in case:
                if hybrid:
                    state=agent.run(case["question"],hybrid=True)
                    hits=state["hits"]; retrieval_ms=state["retrieval_ms"]
                    claims=state["claims"]; checked=state["verification"]; calls=state["tool_calls"]
                else:
                    rt=perf_counter(); hits=agent.retriever.search(case["question"],hybrid=False); retrieval_ms=(perf_counter()-rt)*1000
                    claims=evidence_claims(hits,None); checked=verify(claims,hits,None); calls=1
                recall,mrr=ranking_metrics(hits,case["evidence"])
                joined=" ".join(c["text"] for c in claims).lower()
                detail.append(dict(system=name,id=case["id"],recall_at_k=recall,mrr=mrr,
                    answer_span_present=case["answer_contains"].lower() in joined,
                    citation_membership=checked["all_supported"],retrieval_ms=retrieval_ms,
                    response_ms=(perf_counter()-t)*1000,tool_calls=calls,
                    retrieved=[h["chunk"]["id"] for h in hits]))
            elif hybrid:
                result=agent.run(case["question"],hybrid=True)
                executed={x["tool"] for x in result["trace"] if "tool" in x and x["status"]=="ok"}
                expected=set(case["tools"])
                row=dict(system=name,id=case["id"],routing_correct=set(result["plan"])==expected,
                    workflow_completed=expected<=executed,response_ms=result["elapsed_ms"],
                    retrieval_ms=result["retrieval_ms"],tool_calls=result["tool_calls"],errors=result["errors"])
                if case.get("abstain"):
                    row["abstention_correct"]=not result["claims"] and result["analysis"] is None
                if "analysis" in case:
                    a=result["analysis"]
                    row["analysis_filter_correct"]=a is not None and all(a[k]==v for k,v in case["analysis"].items() if k!="years")
                    # Independent pandas reference calculations against the frozen CSV.
                    import pandas as pd
                    spec=case["analysis"]; f=agent.dataset.frame
                    code={"yield":"AG.YLD.CREL.KG","production":"AG.PRD.CREL.MT"}[spec["variable"]]
                    f=f[(f.country==spec["country"]) & (f.indicator==code)]
                    if spec.get("years"): f=f[f.year.isin(spec["years"])]
                    f=f.dropna(subset=["value"]).sort_values("year")
                    if spec["operation"]=="summary":
                        row["numeric_correct"]=a is not None and abs(a["result"]["mean"]-float(f.value.sum()/len(f)))<1e-8
                    elif spec["operation"]=="yoy":
                        expected_change=(float(f.value.iloc[-1])/float(f.value.iloc[0])-1)*100
                        row["numeric_correct"]=a is not None and abs(a["result"]["percent_change"]-expected_change)<1e-8
                    row["citation_membership"]=result["verification"]["all_supported"]
                    if "expected_result" in case:
                        row["gold_numeric_correct"]=a is not None and all(abs(a["result"][k]-v)<1e-8 for k,v in case["expected_result"].items())
                detail.append(row)
    summaries={}
    for name in sorted({r["system"] for r in detail}):
        group=[r for r in detail if r["system"]==name]
        summary={"cases":len(group)}
        for metric in ["recall_at_k","mrr","answer_span_present","citation_membership","routing_correct","workflow_completed","abstention_correct","analysis_filter_correct","numeric_correct","gold_numeric_correct","response_ms","retrieval_ms","tool_calls"]:
            values=[r[metric] for r in group if metric in r]
            if values: summary[metric]={"mean":mean(values),"n":len(values)}
        # Compare efficiency on the same 12 evidence questions, not mixed workloads.
        evidence_rows=[r for r in group if "recall_at_k" in r]
        for metric in ["response_ms","retrieval_ms","tool_calls"]:
            values=[r[metric] for r in evidence_rows]
            if values: summary["evidence_"+metric]={"mean":mean(values),"n":len(values)}
        summaries[name]=summary
    result=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),python=platform.python_version(),
        platform=platform.platform(),settings=vars(settings),setup_ms=setup,
        corpus_documents=len({c.document_id for c in agent.retriever.chunks}),chunks=len(agent.retriever.chunks),
        resolved_model_revision=getattr(agent.retriever,"model_revision",None),
        manifest_sha256=hashlib.sha256((ROOT/"data/sources.json").read_bytes()).hexdigest(),
        dataset_sha256=agent.dataset.sha256,gold_sha256=hashlib.sha256((ROOT/"evaluation/questions.json").read_bytes()).hexdigest(),
        dependencies={p:importlib.metadata.version(p) for p in ["numpy","pandas","langgraph","sentence-transformers","faiss-cpu"]},
        source_label_validation_errors=validation,summary=summaries,details=detail,
        limitations=["Development questions authored and source-reviewed by implementing agent, not independently human annotated.",
            "Single local timing observation per case; warm inference, no statistical significance claim.",
            "Citation membership is exact excerpt membership, not factual or entailment scoring.",
            "Gold answer span presence is a narrow proxy, not complete answer quality.",
            "Baseline is retrieval plus extracts; agent workflows are evaluated only for the enhanced system.",
            "No paid LLM calls; Groq live generation not run."])
    target=ROOT/("evaluation/results_lexical.json" if args.lexical else "evaluation/results.json")
    target.write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps({"summary":summaries,"label_errors":validation,"output":str(target)},indent=2))

if __name__=="__main__": main()
