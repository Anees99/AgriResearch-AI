"""Record exact runtime versions without dumping environment variables/secrets."""
from importlib.metadata import distribution, PackageNotFoundError
from pathlib import Path
import platform

ROOT=Path(__file__).resolve().parents[1]
PACKAGES=["numpy","pandas","streamlit","langgraph","langchain-core","langgraph-checkpoint",
    "langgraph-prebuilt","langgraph-sdk","sentence-transformers","faiss-cpu","torch",
    "transformers","huggingface-hub","tokenizers","safetensors","scikit-learn","scipy",
    "pypdf","requests","python-dotenv","pytest","reportlab"]
lines=["Python "+platform.python_version(), platform.platform(),
       "Local venv reuses preinstalled packages through --system-site-packages.",
       "This is an environment record, not a complete portable transitive lockfile.", ""]
for name in PACKAGES:
    try:
        dist=distribution(name)
        lines.append(name+"=="+dist.version)
    except PackageNotFoundError:
        lines.append(name+": NOT INSTALLED")
(ROOT/"docs/environment_versions.txt").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("\n".join(lines))
