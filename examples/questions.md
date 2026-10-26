# Demonstration sequence

1. `What units are used to measure cereal yield?` — retrieval with citation.
2. `Compare Pakistan cereal production in 2021 and 2022` — validated YoY.
3. `Report on cereal harvest evidence and Pakistan average cereal yield` —
   successful multi-tool example, saved as `demo_report.md`.
4. `Report on wheat irrigation evidence and Pakistan average cereal yield` —
   asks for research and analysis; the narrow parser may reject the calculation
   because wheat is not a dataset field. Explain this limitation openly.
5. `Report on soil health and Pakistan average cereal yield` — multi-tool graph;
   if soil guidance is unavailable, inspect retrieved evidence and avoid treating
   statistical metadata or unrelated paper passages as a soil-health answer.
6. `Calculate wheat yield for Punjab in 2022` — unavailable variable/region.
7. `Calculate Pakistan rainfall data in 2020` — missing environmental field.
8. `Which irrigation schedule is optimal for rice in Sindh?` — source-scope refusal.
9. Upload an authorized PDF; inspect title, date, page and chunk references.

Use dataset explorer controls for explicit filters. Download a Markdown report,
inspect its data hash and references, then reproduce with the CLI.
