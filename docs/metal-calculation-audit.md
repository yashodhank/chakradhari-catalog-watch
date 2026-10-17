# Metal calculation audit — 18 October 2026

Scope: extraction, valuation, generated datasets, catalog rendering and filters at baseline d0077d3. No fresh merchant scrape or independent assay was performed.

## Root causes

- `metal_valuation.py` returned on multiple weights before parsing purity. Known 99.6% silver therefore appeared as unknown purity internally.
- All multiple weights shared one ambiguous state, including complete alternating size/weight sequences.
- `update_catalog.py` flattens and deduplicates measurements from several evidence fields. This loses some associations and cannot establish per-piece/per-pair weights or variant prices. Reordered/partial sequences must remain blocked.
- Purity extraction accepted the first percentage without detecting contradictory percentage claims.
- Bullion provenance existed at manifest level but was absent from individual calculations.

## Changes and limits

Parse purity independently of weight; reject conflicting explicit metal percentage claims. Recognize only complete alternating inch/mm/cm–weight sequences with distinct size labels. Calculate each weight conditionally using the same safeguards as a single weight. Never assign the generic listing price to these variants or calculate variant retail residuals. Other multi-weight records remain unavailable.

Display percentage and per-mille purity, stated weight, fine-metal grams, dated reference and per-size estimates. Add a dedicated variant-estimate filter and keep unavailable results separate. Preserve warnings for plating, composites, alloys and missing rates. Price history and raw merchant observations remain unchanged.

Formula: fine-metal grams = stated metal grams × fineness / 1000. Benchmark value = stated metal grams × reference INR/g × product fineness / reference fineness. Round monetary output only after calculation.

## Impact on the stored catalog

1,863 products; 1,230 recognized metal records.

| State | Before | After |
|---|---:|---:|
| Single estimate | 109 | 108 |
| Conditional size estimates | 0 | 8 |
| Ambiguous weight | 41 | 33 |
| Missing weight | 588 | 587 |
| Conflicting percentage purity | 0 | 2 |

Other status totals are unchanged. The Silver Flag has 99.6% and 99% claims and loses its prior estimate. Twin Matasya Rakhi has 99.9% and 9.9% claims; neither is silently corrected.

The pictured Kacchi Kairi Payal uses the stored 16 October 2026 silver-999 rate ₹210,918/kg: 43 g → ₹9,042.24; 47 g → ₹9,883.38; 52 g → ₹10,934.80 at 996 fineness. These are conditional raw-metal values, not resale quotations or merchant charges.

## Remaining gaps

A future extraction schema should retain structured variant IDs, raw specification labels, units, quantity basis, net/gross basis, currency and price association before flattening. Historical flattened observations cannot safely reconstruct these facts. This change intentionally does not reinterpret conflicting lota, set or component weights, or infer alloy recipes. Purity conflict detection added here covers explicit percentage claims; it is not a complete natural-language contradiction detector.

Validation: Python unit suite, Node tests including actual generated screenshot-record rendering and escaping, JS syntax checks, full offline dataset rebuild. No browser visual QA or live merchant-price verification was performed.
