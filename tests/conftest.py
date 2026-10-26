import pytest

@pytest.fixture(autouse=True)
def offline_test_defaults(monkeypatch):
    """Tests never inherit a configured paid/live provider or model download."""
    monkeypatch.setenv("LLM_PROVIDER", "extractive")
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("LANGSMITH_TRACING", "false")
