from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import streamlit as st
from agriresearch.config import ROOT, Settings
from agriresearch.runtime import build
from agriresearch.ingest import chunk_document
from agriresearch.retrieval import Retriever
from agriresearch.agent import ResearchAgent

st.set_page_config(page_title="AgriResearch AI", page_icon=":material/eco:", layout="wide")
st.title("AgriResearch AI")
st.caption("Agricultural evidence • reproducible calculations • inspectable research workflows")

@st.cache_resource(max_entries=2)
def load_agent(settings, fingerprint):
    return build(settings)

with st.sidebar:
    st.subheader("Research configuration")
    lexical = st.checkbox("Use offline lexical fallback", value=False,
                          help="TF-IDF cosine; this is not semantic RAG.")
    hybrid = st.checkbox("Hybrid retrieval", value=True)
    top_k = st.slider("Evidence chunks", 1, 8, 3)
    threshold = st.slider("Minimum cosine similarity", 0., 1., .05 if lexical else .28, .01)
    st.caption("Extractive mode needs no API key. Optional Groq settings come from .env.")
    st.caption("National cereal aggregates cannot answer crop-specific or district questions.")
    if st.button("Clear session", key="clear_session"):
        for key in ["messages", "uploaded_chunks"]: st.session_state.pop(key, None)
        st.rerun()

try:
    settings = replace(Settings.from_env(), backend="lexical" if lexical else "semantic", top_k=top_k, threshold=threshold)
except ValueError as exc:
    st.error(f"Invalid environment configuration: {exc}")
    st.stop()
view = st.segmented_control("Workspace", ["Research chat", "Documents", "Dataset", "Evaluation"], default="Research chat", required=True)
manifest_path = ROOT / "data/sources.json"
if not manifest_path.exists():
    st.info("Download the documented sources first: python scripts/fetch_sources.py")
    st.stop()
try:
    fingerprint = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    agent = load_agent(settings, fingerprint)
    if st.session_state.get("uploaded_chunks"):
        chunks = agent.retriever.chunks + st.session_state.uploaded_chunks
        # Per-session resource: never mutate shared cached corpus or another user's evidence.
        if st.session_state.get("upload_index_key") != (settings, tuple(c.id for c in chunks)):
            st.session_state.upload_retriever = Retriever(chunks, settings)
            st.session_state.upload_index_key = (settings, tuple(c.id for c in chunks))
        agent = ResearchAgent(st.session_state.upload_retriever, agent.dataset, settings)
except Exception as exc:
    st.error(f"Research resources unavailable ({type(exc).__name__}). Verify dependencies, source files and embedding model cache.")
    st.code("python scripts/fetch_sources.py\npython -m agriresearch \"What is cereal yield?\" --lexical")
    st.stop()

if view == "Research chat":
    st.info("Answers quote retrieved evidence. Similarity and quotation checks do not establish relevance, causation, or local applicability.")
    st.session_state.setdefault("messages", [])
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask about soil health or compare Pakistan cereal production in 2021 and 2022", submit_mode="disable")
    if prompt:
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Retrieving evidence and running validated tools…"):
                try: result = agent.run(prompt, hybrid=hybrid)
                except (ValueError, RuntimeError) as exc:
                    st.error(str(exc)); st.stop()
            st.markdown(result["answer"])
            with st.expander("Evidence and execution summary"):
                st.json({k:result[k] for k in ["plan","trace","verification","tool_calls","elapsed_ms"]})
                for hit in result["hits"]:
                    c = hit["chunk"]
                    st.markdown(f"**{c['title']}** — page {c['page'] or 'n/a'}, cosine {hit['cosine']:.3f}")
                    st.text(c["text"])
            st.download_button("Download research report", result["answer"], "research_report.md", "text/markdown")
        st.session_state.messages += [{"role":"user","content":prompt},{"role":"assistant","content":result["answer"]}]
elif view == "Documents":
    st.subheader("Corpus and source provenance")
    st.dataframe(json.loads(manifest_path.read_text(encoding="utf-8")), alt="Source manifest including licenses and snapshot hashes")
    st.caption("Upload authorized PDFs or text. Uploads stay in this session and do not enter Git or the shared corpus.")
    with st.form("upload"):
        file = st.file_uploader("Research document", type=["pdf","txt","md"], max_upload_size=20)
        title = st.text_input("Document title")
        author = st.text_input("Author or organization")
        date = st.text_input("Publication date", value="unknown")
        url = st.text_input("Source URL or identifier")
        authorized = st.checkbox("I am authorized to use this document")
        submitted = st.form_submit_button("Index document")
    if submitted:
        if not file or not authorized or not all([title.strip(),author.strip(),date.strip(),url.strip()]):
            st.error("Provide a document, complete metadata and usage authorization.")
        else:
            try:
                body = file.getvalue()
                with tempfile.TemporaryDirectory() as temp:
                    path = Path(temp) / ("upload"+Path(file.name).suffix.lower())
                    path.write_bytes(body)
                    new = chunk_document(path, dict(document_id="upload-"+hashlib.sha256(body).hexdigest()[:12],title=title,
                        author=author,date=date,url=url),settings.chunk_size,settings.overlap)
                existing = {c.id:c for c in st.session_state.get("uploaded_chunks",[])}
                existing.update({c.id:c for c in new})
                if len(existing)>1000: raise ValueError("Session limit: 1000 uploaded chunks")
                st.session_state.uploaded_chunks = list(existing.values())
                st.success(f"Indexed {len(new)} chunks. Open Research chat to query them.")
            except Exception as exc: st.error(f"Ingestion rejected: {exc}")
elif view == "Dataset":
    st.subheader("Cereal dataset exploration")
    st.caption("World Bank WDI / FAO • 2010–2023 • Pakistan, India, Bangladesh • no imputation")
    countries = sorted(agent.dataset.frame.country.unique())
    country = st.selectbox("Country", countries, index=countries.index("Pakistan"))
    variable = st.selectbox("Variable", ["yield","production","land"])
    operation = st.selectbox("Operation", ["summary","trend","yoy","quality","regions"])
    years = st.multiselect("Years (select two consecutive years for year-over-year)", sorted(agent.dataset.frame.year.unique().tolist()))
    if st.button("Calculate", key="calculate"):
        try:
            result = agent.dataset.run(operation,country,variable,years or None)
            st.json(result)
        except ValueError as exc: st.warning(str(exc))
    st.dataframe(agent.dataset.frame, alt="National cereal observations with country, year, indicator and values")
elif view == "Evaluation":
    st.subheader("Measured evaluation results")
    result_path = ROOT / "evaluation/results.json"
    if result_path.exists(): st.json(json.loads(result_path.read_text(encoding="utf-8")))
    else: st.info("Not run. Execute python -m evaluation.run")
    st.caption("Small development set; independent human review and a larger held-out corpus remain necessary.")
