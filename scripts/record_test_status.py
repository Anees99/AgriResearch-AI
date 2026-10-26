"""Summarize actual Pytest JUnit XML. Run only after the tests finish."""
from datetime import datetime, timezone
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]

def main():
    source=ROOT/"evaluation/pytest-results.xml"
    tree=ET.parse(source).getroot()
    suites=[tree] if tree.tag=="testsuite" else list(tree.findall("testsuite"))
    counts={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ["tests","errors","failures","skipped"]}
    counts["passed"]=counts["tests"]-counts["errors"]-counts["failures"]-counts["skipped"]
    counts["status"]="passed" if not counts["errors"] and not counts["failures"] else "failed"
    counts["recorded_utc"]=datetime.now(timezone.utc).isoformat()
    counts["source"]="evaluation/pytest-results.xml"
    counts["command"]=".venv/Scripts/python.exe -m pytest -q --basetemp=.pytest-tmp-final --junitxml=evaluation/pytest-results.xml"
    (ROOT/"evaluation/test_status.json").write_text(json.dumps(counts,indent=2),encoding="utf-8")
    print(json.dumps(counts,indent=2))

if __name__=="__main__":main()
