# Source and license review

`source_manifest.csv` and `data/sources.json` are the authoritative acquisition
records: source title, author, date (or explicit unknown), URL, identifier,
license review, access timestamp, local path, status and SHA256.
Chunk records add 1-based page numbers for PDFs; web/text sources use null.

## World Bank World Development Indicators / FAO

- AG.YLD.CREL.KG: cereal yield, kg per hectare.
- AG.PRD.CREL.MT: cereal production, metric tons.
- AG.LND.CREL.HA: land under cereal production, hectares.
- Observations requested: Pakistan, India, Bangladesh, 2010–2023 inclusive.
- API: https://api.worldbank.org/v2/country/PAK;IND;BGD/indicator/AG.YLD.CREL.KG?format=json&date=2010:2023&per_page=1000
- Indicator pages show license attribution; general terms:
  https://datacatalog.worldbank.org/public-licenses
- Attribution: World Bank, World Development Indicators, sourced from FAO.
  The project selects years/countries, normalizes records to long CSV and stores
  API metadata as text; values are not interpolated, rounded or fabricated.
- The statistical indicators aggregate cereal crops, not wheat alone. Crops for
  hay, green feed, silage or grazing are excluded. Harvest-year assignment and
  country reporting differences matter when interpreting comparisons.
- Publication dates for live metadata are unknown, not inferred from access date.
  Observation source records preserve the API's last-updated field.

## Pakistan wheat-irrigation paper

Abbas, S. H., Islam, Z., Shakoor, A., Qamar, M., Tanveer, S. K., Hussain, I.,
and Majeed, A. (2024). *Impact of supplemental irrigation through sprinkler
raingun at alternate phenological stages of wheat crop.* Journal of Pure and
Applied Agriculture, 9(1).
https://ojs.aiou.edu.pk/index.php/jpaa/article/view/2436

Publisher license prose states CC BY 4.0, but its DC.Rights metadata says
CC BY-NC 4.0. Use the stricter noncommercial condition for this portfolio;
commercial reuse requires clarification. `fetch_paper.py` checks both notices.
The original PDF is kept locally and gitignored, without alteration;
text extraction/chunking is a derivative representation with page provenance.
This study is evidence for its particular experiment, not a nationally validated
irrigation prescription. Bibliographic publication date is distinct from the
experiment's growing season. No claim of endorsement is made.
Curated applicability metadata declare wheat and the Islamabad/NARC study setting;
they do not grant nationwide or other-crop intervention coverage.

## USDA NRCS guidance candidates

Soil Health and Cover Crops for Soil Health were attempted as federal-authored
guidance. Federal employee works are generally public domain in the US, but
third-party materials on government websites can retain copyright. See
https://www.usa.gov/government-copyright . Full snapshots are gitignored pending
page-level review, and failed acquisitions remain explicitly unavailable.
They must not count as successful corpus evidence when unavailable.

## FAO publication candidate

*Irrigation Water Management: Crop Water Needs*, chapter 2:
https://www.fao.org/4/s2022e/s2022e02.htm . Public accessibility is not assumed
to grant redistribution rights. No full publication is downloaded or bundled
until the specific edition's terms are reviewed. FAO as an original contributor
to WDI is distinct from a license to redistribute unrelated FAO publications.

## Reproducibility

Source servers can revise historical estimates. Keep the supplied snapshots and
their hashes to reproduce a run. Re-fetching changes the manifest and requires
rerunning evaluation and reviewing gold passages. Run `fetch_sources.py` before
`fetch_paper.py` (the first script rebuilds the manifest). Never add sensitive or
unauthorized uploads to the corpus or Git. No credentials are required to fetch
the public sources.
