# Material benchmark coverage and research queue

This monitor must never equate a bulk commodity quote with the fair retail price
of a finished article. A rate appears as a product estimate only when the
seller states an identifiable material, unambiguous net material weight and
specific purity. Sources retain publication date, units, conversion basis and
links; a fetch failure preserves the last dated observation.

## Sources in use

| Material | Reference | Frequency | Display and limits |
| --- | --- | --- | --- |
| Gold, silver, platinum | [IBJA](https://www.ibjarates.com/) | Indian business days, AM/PM | INR bullion per gram after explicit unit conversion; no GST or workmanship |
| Copper, tin, zinc, lead, aluminium, nickel | [World Bank Pink Sheet, monthly workbook](https://www.worldbank.org/en/research/commodity-markets) with [ECB daily USD/INR cross rate](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml) | Monthly commodity average; FX on working days | International raw-metal reference converted to INR/g; **not a daily Indian spot price**. Only show a product-level estimate with stated net metal weight and purity. |

The daily job rechecks both sources, keeps their original dates and skips stale
or malformed data. FX refresh does not make the monthly commodity observation
a daily price.

## Still to research and validate

| Material / category | Next source or task | Why a point price is withheld |
| --- | --- | --- |
| Copper, aluminium, nickel, zinc, lead, tin: Indian daily reference | Evaluate [MCX end-of-day bhavcopy](https://www.mcxindia.com/market-data/bhavcopy) for public terms and a stable contract and unit mapping. [LME day-delayed official prices](https://www.lme.com/market-data/reports-and-data) are public to view; review [distribution terms](https://www.lme.com/market-data/market-data-licensing/data-distribution) before republishing. | Futures/wholesale contracts differ from local spot and finished-product retail. No unlicensed redistribution. |
| Iron, steel | Find a specific Indian graded scrap or finished steel reference with public reuse rights. | World Bank iron ore is not finished iron or steel; grade and production route matter. |
| Brass, bronze/kansa, panchdhatu and mixed metals | Capture bill of materials and independently verified composition per product. | No universal alloy recipe; pricing pure copper as brass is misleading. |
| Parad/mercury products | Obtain seller composition and lawful public reference before any estimate. | Claimed mercury content, binding and safety are unknown. |
| Gold or silver plating | Capture actual plating thickness and metal mass if disclosed. | Gross weight and base-metal price cannot identify precious metal content. |
| Diamond | Evaluate a reusable public comparable-stone feed only with verified natural/lab origin, shape, color, clarity, cut, treatment and certification. [GIA explains the quality factors](https://www.gia.edu/diamond-quality-factor). | Carat weight alone cannot establish value; a generic per-carat daily price would mislead. |
| Ruby, sapphire, emerald, opal, coral, turquoise, garnet, chrysoberyl, zircon, topaz and other colored gems | Build attributed, dated comparable sales grouped by stone type, origin, treatment, certification, size, color and quality. [GIA's colored-stone factors](https://www.gia.edu/gia-news-research/value-factors-design-cut-quality-colored-gemstone-value-factors) guide required fields. | No defensible uniform daily spot rate; listings are asking prices, not confirmed sales. |
| Rudraksha, beads and malas | Collect seller-described mukhi count, origin, certification, size and condition; compare like-for-like listings with sample sizes. | No commodity exchange benchmark or reliable per-bead spot rate. |

## Data and UX work

- Collect product-level add-ons separately from the base offer, with observed
  amount, selection requirements and quote-only state. Never treat ₹1 quote
  placeholders as the finished product price.
- Capture all selectable metal, ring-size and gender options without merging
  distinct variants. Mark any unsupported combinations rather than computing
  a total from assumptions.
- Validate source reuse and stability before enabling daily gemstone or base
  metal scraping. Preserve unverified leads here with date and provenance.
- Measure how many products have usable **net material weight and purity**; a
  benchmark without these fields is an informational reference only.
