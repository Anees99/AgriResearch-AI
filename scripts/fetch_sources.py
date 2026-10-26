"""Fetch licensed WDI observations/metadata and US federal guidance.

Run from project root. USDA full text is deliberately gitignored: review the
page-specific attribution before any redistribution. No FAO publications are
downloaded until their individual reuse terms have been reviewed.
"""
import csv
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import time
import requests

ROOT = Path(__file__).resolve().parents[1]
INDICATORS = ["AG.YLD.CREL.KG", "AG.PRD.CREL.MT", "AG.LND.CREL.HA"]

def get(url):
    last = None
    for attempt in range(3):
        try:
            response = requests.get(url, timeout=40, headers={"User-Agent": "AgriResearch-AI/0.1 research portfolio"})
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last = exc
            time.sleep(attempt)
    raise RuntimeError(f"Source download failed: {url}") from last

class MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.ignore = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag == "main": self.active = True
        if tag in {"script", "style"}: self.ignore += 1
    def handle_endtag(self, tag):
        if tag == "main": self.active = False
        if tag in {"script", "style"}: self.ignore = max(0, self.ignore-1)
    def handle_data(self, data):
        if self.active and not self.ignore and data.strip(): self.parts.append(data.strip())

def main():
    for directory in ["data/raw", "data/corpus", "data/processed"]:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)
    sources, rows = [], []
    accessed = datetime.now(timezone.utc).isoformat()
    for indicator in INDICATORS:
        url = f"https://api.worldbank.org/v2/country/PAK;IND;BGD/indicator/{indicator}?format=json&date=2010:2023&per_page=1000"
        payload = get(url).json()
        if not isinstance(payload, list) or len(payload) != 2 or payload[0]["pages"] != 1:
            raise ValueError("Unexpected WDI response or incomplete pagination")
        (ROOT / f"data/raw/{indicator}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        for r in payload[1]:
            rows.append({"country": r["country"]["value"], "year": int(r["date"]),
                         "indicator": indicator, "value": r["value"]})
        meta_url = f"https://api.worldbank.org/v2/indicator/{indicator}?format=json"
        metadata = get(meta_url).json()[1][0]
        text = metadata["name"] + "\n\n" + metadata["sourceNote"] + "\n\nSource organization: " + metadata["sourceOrganization"]
        path = f"data/corpus/{indicator}.txt"
        (ROOT / path).write_text(text, encoding="utf-8")
        sources.append(dict(document_id=indicator, title=metadata["name"], author="World Bank / FAO",
            date="unknown (live indicator metadata)", url=meta_url, kind="document", path=path,
            license="CC BY 4.0 (WDI indicator page)", license_url=f"https://data.worldbank.org/indicator/{indicator}",
            accessed_utc=accessed, status="downloaded"))
        sources.append(dict(document_id=indicator+"-DATA", title=metadata["name"]+" observations 2010-2023",
            author="World Bank / FAO", date=payload[0].get("lastupdated", "unknown"), url=url, kind="dataset",
            path="data/processed/cereals.csv", license="CC BY 4.0 (WDI indicator page)",
            license_url=f"https://data.worldbank.org/indicator/{indicator}", accessed_utc=accessed, status="downloaded"))
    with (ROOT / "data/processed/cereals.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["country", "year", "indicator", "value"])
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r:(r["country"],r["indicator"],r["year"])))
    guidance = [
        ("usda-soil", "Soil Health", "https://www.nrcs.usda.gov/conservation-basics/soil/soil-health"),
        ("usda-cover", "Cover Crops for Soil Health", "https://www.nrcs.usda.gov/conservation-basics/natural-resource-concerns/soils/cover-crops-for-soil-health"),
    ]
    for doc_id, title, url in guidance:
        source = dict(document_id=doc_id, title=title, author="USDA Natural Resources Conservation Service",
            date="unknown (undated webpage)", url=url, kind="document", path=f"data/corpus/{doc_id}.txt",
            license="US federal authored text: public domain in US; third-party items excluded; local-use snapshot",
            license_url="https://www.usda.gov/policies-and-links", accessed_utc=accessed)
        try:
            response = get(url)
            parser = MainText()
            parser.feed(response.text)
            text = "\n".join(parser.parts)
            # Strip assistance/application boilerplate, not technical content.
            text = text.split("How to Get Assistance")[0]
            if len(text) < 300: raise ValueError("No meaningful main article extracted")
            (ROOT / source["path"]).write_text(text, encoding="utf-8")
            (ROOT / f"data/raw/{doc_id}.html").write_text(response.text, encoding="utf-8")
            source["status"] = "downloaded"
        except (RuntimeError, ValueError) as exc:
            source.update(status="unavailable", error=str(exc))
        sources.append(source)
    sources.append(dict(document_id="fao-water-candidate", title="Irrigation Water Management: Crop Water Needs",
        author="FAO", date="unknown (verify publication)", url="https://www.fao.org/4/s2022e/s2022e02.htm",
        kind="candidate", path="", license="Document-specific reuse review required; not downloaded",
        license_url="https://www.fao.org/contact-us/terms/en/", accessed_utc=accessed, status="pending-license-review"))
    for s in sources:
        if s.get("kind")=="document" and s["document_id"] in INDICATORS:
            s.update(crops=["cereals"],regions=["national"],evidence_type="statistical_definition")
        if s["status"] == "downloaded":
            s["sha256"] = hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest()
    (ROOT / "data/sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    fields = sorted(set().union(*(s.keys() for s in sources)))
    with (ROOT / "source_manifest.csv").open("w", newline="", encoding="utf-8") as h:
        writer = csv.DictWriter(h, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sources)
    print(json.dumps({"rows": len(rows), "sources": [{"id":s["document_id"], "status":s["status"]} for s in sources]}, indent=2))

if __name__ == "__main__": main()
