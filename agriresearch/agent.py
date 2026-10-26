"""Deterministic, inspectable planner in a bounded LangGraph state machine."""
import re
import requests
import os
from time import perf_counter
from typing import TypedDict
from .generation import evidence_claims, verify, synthesize, report
from .applicability import filter_applicable

class State(TypedDict, total=False):
    question: str
    plan: list[str]
    hits: list[dict]
    analysis: dict | None
    claims: list[dict]
    verification: dict
    interpretation: str
    answer: str
    errors: list[str]
    trace: list[dict]
    tool_calls: int
    retrieval_ms: float
    elapsed_ms: float
    options: dict

def plan_question(question):
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        raise ValueError("Question must contain 1..4000 characters")
    q = question.lower()
    agriculture = re.search(r"\b(crop|crops|soil|water|irrigation|cereal|cereals|yield|wheat|rice|maize|farm|production|rainfall|fertilizer|roots|cover|harvest|agricultur\w*)\b", q)
    if not agriculture: return ["verify"]
    analytical = re.search(r"\b(mean|average|statistics|trend|compare|comparison|year.over.year|yoy|missing|outlier|calculate|data|dataset)\b|\b20\d\d\b", q)
    research = re.search(r"\b(soil|water|irrigation|why|evidence|explain|guideline|report|literature|cover|roots|harvest)\b", q)
    tools = []
    if research or not analytical: tools.append("search")
    if analytical: tools.append("analysis")
    if re.search(r"\breport\b", q): tools.append("report")
    return tools + ["verify"]

def analysis_options(question):
    q = question.lower()
    for entity in re.findall(r"\b(?:for|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", question):
        if entity not in {"Pakistan", "India", "Bangladesh"}:
            raise ValueError(f"Unrecognized or unavailable country/region: {entity}; use explicit dataset controls")
    if re.search(r"\b(china|afghanistan|australia|usa|united states|brazil)\b",q):
        raise ValueError("Requested country unavailable; available countries: Pakistan, India, Bangladesh")
    if re.search(r"\b(rainfall|irrigation|temperature|fertilizer|wheat|rice|maize|district|punjab|sindh)\b", q):
        raise ValueError("Dataset contains national cereal aggregates only; requested crop/local/environmental variable unavailable")
    country = "Bangladesh" if "bangladesh" in q else "India" if re.search(r"\bindia\b",q) else "Pakistan"
    variable = "production" if "production" in q else "land" if "land" in q or "area" in q else "yield"
    operation = "yoy" if re.search(r"year.over.year|\byoy\b|\bcompare\b|\bcomparison\b",q) else "quality" if "missing" in q or "outlier" in q else "regions" if "countries" in q or "region" in q else "trend" if "trend" in q else "summary"
    years = sorted(set(map(int,re.findall(r"\b(?:19|20)\d{2}\b",q))))
    if len(years) == 2 and " to " in q and operation != "yoy": years = list(range(years[0], years[1]+1))
    return dict(operation=operation, country=country, variable=variable, years=years or None)

class ResearchAgent:
    def __init__(self, retriever, dataset, settings):
        self.retriever, self.dataset, self.settings = retriever, dataset, settings

    def run(self, question, hybrid=True, options=None):
        os.environ["LANGSMITH_TRACING"] = "false"
        from langgraph.graph import StateGraph, START, END
        started = perf_counter()
        def plan(s):
            selected = plan_question(s["question"])
            return {"plan": selected, "trace": [{"node":"plan", "tools":selected}], "errors":[],
                    "hits":[], "analysis":None, "tool_calls":0, "retrieval_ms":0.}
        def execute(s):
            hits, data, errors, trace, count, retrieval_ms = [], None, [], list(s["trace"]), 0, 0.
            for tool in s["plan"]:
                if tool in {"verify", "report"}: continue
                # Reserve budget for required verification/report actions.
                reserved = 1 + int("report" in s["plan"])
                if count >= self.settings.max_tools - reserved:
                    errors.append("Tool execution limit reached before all requested work completed.")
                    break
                count += 1
                t = perf_counter()
                try:
                    if tool == "search":
                        hits = self.retriever.search(s["question"], hybrid=hybrid)
                        hits, scope_errors = filter_applicable(s["question"], hits)
                        errors.extend(scope_errors)
                        retrieval_ms = (perf_counter()-t)*1000
                    else:
                        data = self.dataset.run(**(s.get("options") or analysis_options(s["question"])))
                    trace.append({"tool":tool,"status":"ok", "ms":(perf_counter()-t)*1000})
                except (ValueError, OSError, RuntimeError) as exc:
                    errors.append(str(exc))
                    trace.append({"tool":tool,"status":"error", "ms":(perf_counter()-t)*1000})
            if not hits and data is None: errors.append("Insufficient evidence; no supported answer is available.")
            return {"hits":hits,"analysis":data,"errors":errors,"trace":trace,"tool_calls":count,"retrieval_ms":retrieval_ms}
        def aggregate(s):
            return {"claims": evidence_claims(s["hits"],s["analysis"])}
        def generate(s):
            errors = list(s["errors"])
            interpretation = ""
            if s["claims"]:
                try: interpretation = synthesize(s["question"],s["claims"])
                except (ValueError, requests.RequestException, KeyError, TypeError) as exc:
                    # Never expose provider response bodies or API credentials.
                    errors.append(f"Provider unavailable ({type(exc).__name__}); returning grounded excerpts.")
            return {"interpretation":interpretation,"errors":errors}
        def check(s):
            result = verify(s["claims"],s["hits"],s["analysis"])
            return {"verification":result,"tool_calls":s["tool_calls"]+1,
                    "trace":s["trace"]+[{"tool":"verify","status":"ok"}]}
        def finish(s):
            extra = int("report" in s["plan"] and s["tool_calls"] < self.settings.max_tools)
            answer = report(s["question"],s["claims"],s["hits"],s["analysis"],s["interpretation"],s["errors"])
            return {"answer":answer,"tool_calls":s["tool_calls"]+extra,
                    "trace":s["trace"]+([{"tool":"report","status":"ok"}] if extra else []),
                    "elapsed_ms":(perf_counter()-started)*1000}
        graph = StateGraph(State)
        for name, fn in [("plan",plan),("execute",execute),("aggregate",aggregate),("generate",generate),("check",check),("finish",finish)]: graph.add_node(name,fn)
        graph.add_edge(START,"plan")
        for a,b in zip(["plan","execute","aggregate","generate","check"],["execute","aggregate","generate","check","finish"]): graph.add_edge(a,b)
        graph.add_edge("finish",END)
        return graph.compile().invoke({"question":question,"options":options or {}}, {"recursion_limit":12})
