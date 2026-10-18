# Material evidence audit — 18 October 2026

Scope: all 1,864 active records at baseline 0935acc; extraction, persisted CSV, valuation, generated JSON and frontend display. Fresh material evidence was fetched successfully for 185 calculation candidates, including the Ritika Brass Thali Set. This was a material-only refresh; prior price/stock verification dates remain unchanged. Other records retain their previous evidence until the regular scanner revisits them.

## Findings and repairs

- Specification tables and structured product fields were read but their wording was discarded before valuation. Added persistent specification evidence, its check time, and frontend disclosure. Preserve purity/fineness labels, all table value columns, and relevant structured field names.
- Mixed-metal/plated early returns discarded ingredient claims. Retain claims independently of eligibility. The thali shows copper 99.9% and zinc 99.9% as component claims, not a finished-alloy purity or copper/zinc ratio. Tin coating, wooden spoon, absent ratios and missing net component weights still prevent a value.
- “99.9% Nepaliya Copper” was missed by the old adjacency pattern. Recognize that observed wording without assigning purity from the word “pure” alone.
- Unrelated standalone numbers could be interpreted as fineness. Require metal-linked grades or explicitly labelled percentages. Check disagreements across percentage, grade and karat notation; do not choose the first.
- Flattened measurements lost gross/shipping/range context. Retain and inspect original wording. Fix thousands separators and leading decimal weights. Block bounded/ranged measurements from becoming exact point values.
- Pack/pair weights could be compared against an entire-set asking price without a quantity basis. Require evidence of combined weight; accept explicit matching parenthetical pair/set/piece counts.
- Preserve ingredient/component claims for coated products without treating the grade as the whole product’s purity. Keep composite non-metal weights out of raw-metal calculations.
- Currency was discarded by the build. Preserve it, display observed currency, and do not compute an INR retail residual from a non-INR asking price.
- The frontend hid metal evidence for quote-only products. It now displays the evidence independently of price availability. Expose default option metadata; it is not a verified per-variant price association.

## Catalog impact

| Valuation state | Before | After |
|---|---:|---:|
| composition_unknown | 211 | 207 |
| estimated | 109 | 169 |
| net_metal_weight_unknown | 122 | 121 |
| no_metal_claim | 626 | 626 |
| plated_or_coated | 0 | 4 |
| purity_conflict | 2 | 2 |
| purity_unknown | 187 | 114 |
| quantity_basis_unknown | 0 | 11 |
| variant_estimates | 8 | 8 |
| weight_ambiguous | 33 | 43 |
| weight_missing | 566 | 559 |

Numeric purity recovered for 112 records. 5 previously displayed single estimates were withdrawn after the stronger evidence checks:

- 99.9% Silver Bangle Pair for Kids (3 Year To 7 Year): quantity_basis_unknown.
- 99.9% Silver Bangle Pair for Kids (6 Month to 3 Year): quantity_basis_unknown.
- 99.9% Silver Nail (Vastu and Astrological Remedy) 5 pc set: quantity_basis_unknown.
- 99.9% Gold Bindumani Kundal Pair: quantity_basis_unknown.
- 99.9% Gold Ear Pin (1 Piece): weight_missing.

## Remaining limits

Merchant claims are not assays. No standard brass/bronze recipe, unspecified purity, coating mass, stone deduction, or per-variant price is invented. Explicit alloy recipes are retained as evidence but automated multi-component valuation is not implemented. Image-only claims need manual review; no OCR was performed. Conservative text matching can reject usable cases where a net weight or a negated coating claim is worded differently. Existing records without captured specification evidence are clearly labelled; regular version-based rescanning fills them progressively, up to 1,000 additional records per run. This audit does not claim a fresh full-site scrape.

Formula: stated metal grams × reference INR/g × product fineness / reference fineness. Fine metal grams = stated metal grams × fineness / 1,000. Reference rates retain their source dates and can be older than the material check.

Validation: 44 Python tests and 16 Node tests pass; JS syntax checks and full dataset rebuild pass. Regression cases cover the screenshots, structured/table evidence, mixed ingredients, conflicting notations, gross/range weights, quantity basis, decimal/thousands parsing, currency isolation, and escaped rendering.
