"""Fetch a Pakistan wheat paper for noncommercial research.

Publisher license prose says CC BY 4.0, but DC.Rights says BY-NC 4.0.
Apply the stricter noncommercial condition; retain that conflict in provenance.
"""
import csv
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import requests

ROOT=Path(__file__).resolve().parents[1]
URL="https://ojs.aiou.edu.pk/index.php/jpaa/article/view/2436"

class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(); self.meta={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="meta" and "name" in a:
            self.meta.setdefault(a["name"],[]).append(a.get("content",""))

def main():
    response=requests.get(URL,timeout=40); response.raise_for_status()
    page=response.text
    if "Creative Commons Attribution 4.0 International License" not in page or "Attribution-NonCommercial 4.0" not in page:
        raise ValueError("Expected publisher license notices changed. Review terms manually.")
    parser=Metadata(); parser.feed(page); meta=parser.meta
    pdf_url=meta["citation_pdf_url"][0]
    response=requests.get(pdf_url,timeout=60); response.raise_for_status()
    if not response.content.startswith(b"%PDF"):
        # OJS sometimes returns a viewer: follow its explicit download link.
        candidates=re.findall(r'(?:href|src)=[\'\"]([^\'\"]+/article/download/[^\'\"]+)',response.text)
        if not candidates: raise ValueError("Publisher did not return a PDF")
        response=requests.get(candidates[0],timeout=60); response.raise_for_status()
        if not response.content.startswith(b"%PDF"): raise ValueError("Download is not a PDF")
    path="data/corpus/jpaa-2436.pdf"
    (ROOT/path).write_bytes(response.content)
    (ROOT/"data/raw/jpaa-2436.html").write_text(page,encoding="utf-8")
    record=dict(document_id="jpaa-2436",title=meta["citation_title"][0],
        author="; ".join(meta["citation_author"]),date=meta.get("citation_date",meta.get("citation_publication_date",["2024"]))[0],
        url=URL,kind="document",path=path,license="CC BY-NC 4.0 conservative use; publisher prose says CC BY 4.0 but DC.Rights says BY-NC 4.0",
        license_url=URL,accessed_utc=datetime.now(timezone.utc).isoformat(),status="downloaded",
        sha256=hashlib.sha256(response.content).hexdigest())
    record["quality_notes"] = ("Source inconsistency: abstract/results report 257.7 mm seasonal rainfall, "
        "but conclusion reports 225.3 mm. Treatment labels and units require domain review; "
        "do not convert this experiment into a general irrigation prescription.")
    record.update(crops=["wheat"],regions=["Islamabad","NARC"],evidence_type="field_experiment")
    sources=json.loads((ROOT/"data/sources.json").read_text())
    sources=[s for s in sources if s["document_id"]!="jpaa-2436"]+[record]
    (ROOT/"data/sources.json").write_text(json.dumps(sources,indent=2),encoding="utf-8")
    fields=sorted(set().union(*(s.keys() for s in sources)))
    with (ROOT/"source_manifest.csv").open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields); writer.writeheader(); writer.writerows(sources)
    print(json.dumps(record,indent=2))

if __name__=="__main__":main()
