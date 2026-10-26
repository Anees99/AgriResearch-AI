# Attribution and third-party components

This project integrates original application code with these external projects;
no existing end-to-end agricultural chatbot repository was copied.

| Component | Role | Upstream license / source |
|---|---|---|
| LangGraph / LangChain core | Graph execution and state | MIT; https://github.com/langchain-ai/langgraph |
| FAISS | Exact dense retrieval | MIT; https://github.com/facebookresearch/faiss |
| Sentence Transformers | Embeddings | Apache-2.0; https://github.com/huggingface/sentence-transformers |
| all-MiniLM-L6-v2 | Embedding model | Apache-2.0 model card; https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 |
| Streamlit | UI and AppTest | Apache-2.0; https://github.com/streamlit/streamlit |
| Pandas / NumPy | Validated numerical analysis | BSD-3-Clause; https://pandas.pydata.org / https://numpy.org |
| pypdf | Page-aware PDF extraction | BSD-3-Clause; https://github.com/py-pdf/pypdf |
| Requests | Public data and optional Groq HTTP access | Apache-2.0; https://requests.readthedocs.io |
| python-dotenv | Environment loading | BSD-3-Clause; https://github.com/theskumar/python-dotenv |
| Pytest | Tests | MIT; https://github.com/pytest-dev/pytest |
| ReportLab | Synthetic PDF test fixtures | BSD-style; https://www.reportlab.com |
| PyTorch / Transformers | Model inference dependencies | BSD-style / Apache-2.0; https://pytorch.org / https://github.com/huggingface/transformers |

Dependencies are installed separately, not vendored; retain their bundled
copyright/license notices when redistributing environments or containers.
The environment snapshot identifies the versions actually used. Review full
upstream license files before redistributing binaries; this table is attribution,
not a replacement for their license texts.

World Bank / FAO data and the Pakistan wheat paper have separate attribution and
license records in docs/DATA_SOURCES.md and source_manifest.csv. Source PDFs are
unmodified; extracted/chunked text and selected CSV observations are transformed
representations. No institutional endorsement is claimed.
