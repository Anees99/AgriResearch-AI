# Evidence-label review record

Reviewed on 25 October 2026 by the implementing AI agent. These labels have
not been independently reviewed by the project owner or an agronomist.

## WDI labels r01–r06

The downloaded indicator metadata were inspected directly. The yield definition
states kilograms per hectare, lists included cereal crops, and explains harvest
year assignment. The production definition states metric tons and excludes hay,
green feed, silage and grazing. The area definition describes harvested area
and acknowledges sown/cultivated reporting in some countries. Golden labels pair
exact text with indicator IDs; overlapping chunks do not create extra relevant
evidence units.

## Pakistan paper labels r07–r12

The original PDF has nine file pages, corresponding to printed pages 56–64.
Evaluation page numbers use the file's 1-based page index, not printed numbers.

| Label | Verified evidence | PDF page |
|---|---|---|
| r07 | Chakwal-50 variety in methods | 2 |
| r08 | RCBD, three replications in methods | 2 |
| r09 | Tukey's Honestly Significant Difference in statistical analysis | 4 |
| r10 | Sandy loam in soil table | 3 |
| r11 | Additional irrigation depths 10 mm and 25 mm | 2 |
| r12 | Abstract reports 257.7 mm seasonal rainfall | 1 |

The abstract/results rainfall value conflicts with 225.3 mm in the conclusion
(PDF page 7). The r12 wording deliberately asks what the abstract reports; it
does not assert which measurement is correct. The report carries a source quality
note. Units, numerical summaries and treatment-label consistency need agronomic
review before using this paper to guide a real intervention.

These are factual lookup questions tied to inspected passages, not a broad test
of scientific synthesis. For r07, pypdf extracts the cultivar as `Chakwal -50`;
the exact-span gold retains that extraction artifact. Source-span validation checks that gold text still
exists in the frozen corpus before evaluating rankings. A missing source span
is recorded as a validation error rather than silently dropped.

## Numeric labels

Source CSV inspected for Pakistan:

- 2020 cereal yield: 3353.4 kg/ha.
- 2021 cereal yield: 3489.4 kg/ha.
- a01 arithmetic mean: 3421.4 kg/ha, n=2.
- 2021 cereal production: 51,304,736 metric tonnes.
- 2022 cereal production: 48,519,329 metric tonnes.
- a02 absolute change: -2,785,407 metric tonnes; percent change uses the 2021 base.

Values are actual downloaded national observations, not wheat-specific yields.
The static expected answers supplement separate reference arithmetic in the
evaluation script. No source observations are interpolated or fabricated.

## Routing and unsupported questions

a01/a02 require analysis and verification. a03 requests search, analysis, report
and verification. a04 exercises missing/outlier summaries. Unsupported cases
cover a nonagricultural question, unavailable Punjab wheat data, and rainfall.
The fourth negative asks for an optimal rice irrigation schedule in Sindh. A
wheat experiment at NARC does not establish that answer even if similar irrigation
passages rank highly. This deliberately probes near-topic false positives.
Routing gold tests the explicit rule planner, not general reasoning ability.

## Review protocol before an interview or publication

Re-run the acquisition-independent evaluation against the frozen files, inspect
every retrieved passage and compare the CSV arithmetic. Then have a researcher
adjudicate relevance, completeness, source reliability and abstentions. Expand
the benchmark with independently held-out documents and hard agricultural
unanswerable questions; this development set is too small for general claims.
