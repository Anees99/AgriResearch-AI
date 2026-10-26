"""Conservative curated-scope guard for recommendation-like questions.

Entity lists are intentionally finite; this is not an entailment model or a
comprehensive location/crop recognizer. Unknown source scopes fail closed for
recommendations, while ordinary evidence lookup remains unchanged.
"""
import re

CROPS={"wheat","rice","maize","banana","cotton","sugarcane"}
REGIONS={"sindh","punjab","islamabad","narc","pakistan","india","bangladesh"}

def filter_applicable(question, hits):
    q=question.lower()
    if not re.search(r"\b(optimal|recommend\w*|schedule|dosage|dose|should)\b",q):
        return hits, []
    terms=set(re.findall(r"[a-z]+",q))
    wanted_crops=CROPS & terms
    wanted_regions=REGIONS & terms
    kept=[]
    for hit in hits:
        source=hit["chunk"]
        crops={c.lower() for c in source.get("crops",[])}
        regions={r.lower() for r in source.get("regions",[])}
        if source.get("evidence_type")!="field_experiment": continue
        if wanted_crops and not wanted_crops <= crops: continue
        if wanted_regions and not wanted_regions <= regions: continue
        kept.append(hit)
    errors=[]
    if len(kept)<len(hits):
        errors.append("Source applicability check rejected evidence with an unreviewed or mismatched crop/region scope. "
                      "The available experiment does not establish a recommendation for the requested setting.")
    return kept, errors
