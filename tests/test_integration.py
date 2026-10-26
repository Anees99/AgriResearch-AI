import pytest
from agriresearch.config import ROOT, Settings

pytestmark = pytest.mark.integration

def test_real_corpus_graph(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER","extractive")
    from agriresearch.runtime import build
    agent=build(Settings())
    result=agent.run("Compare Pakistan cereal production in 2021 and 2022")
    assert result["analysis"]["variable"]=="production"
    assert result["verification"]["all_supported"]
    unsupported=agent.run("Which irrigation schedule is optimal for rice in Sindh?")
    assert not unsupported["claims"] and unsupported["analysis"] is None
    assert any("applicability" in e for e in unsupported["errors"])

def test_streamlit_chat(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("MODEL_LOCAL_ONLY","true")
    monkeypatch.setenv("LLM_PROVIDER","extractive")
    app=AppTest.from_file(str(ROOT/"streamlit_app.py"),default_timeout=120).run()
    assert not app.exception
    assert len(app.chat_input)==1, [e.value for e in app.error]
    app.chat_input[0].set_value("What is cereal yield?").run()
    assert not app.exception
    assert len(app.chat_message)==2
    assert any("References" in m.value for m in app.markdown)

def test_streamlit_dataset_and_documents(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("MODEL_LOCAL_ONLY","true")
    monkeypatch.setenv("LLM_PROVIDER","extractive")
    app=AppTest.from_file(str(ROOT/"streamlit_app.py"),default_timeout=120).run()
    app.segmented_control[0].set_value("Dataset").run()
    assert not app.exception
    assert app.selectbox[0].value=="Pakistan"
    app.button(key="calculate").click().run()
    assert not app.exception and app.json
    app.segmented_control[0].set_value("Documents").run()
    assert not app.exception and app.dataframe
