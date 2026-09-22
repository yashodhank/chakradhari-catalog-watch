# Chakradhari Catalog Watch

An independent, public monitor for the product catalog at [chakradhari.com](https://www.chakradhari.com/). It records additions, removals, stock changes and price history, and publishes a searchable static dashboard.

## Public data

- `data/current-products.csv.gz` — compressed latest known state for every monitored product
- `data/price-history.csv.gz.part-*` — compressed, split append-only price observations
- `data/change-events.csv` — append-only meaningful changes
- `data/sources.json.gz` — compressed source registry and source-status history
- `data/run-log.md` — scan coverage and reliability log
- `data/metal-rates.json` — dated IBJA gold, silver and platinum benchmark observations

Price history records actual detail-page fetches on new scans; old history may contain prices carried forward from cached rows and must not be treated as independently observed daily prices. A product is confirmed removed only after two consecutive successful complete sitemap comparisons.

## Automation

GitHub Actions scans the public catalog each day at approximately 08:00 IST, rebuilds the dashboard dataset and commits new observations. A manual run is also available from the Actions tab.

Run locally with Python 3.12+ and no third-party packages:

```bash
gunzip -c data/current-products.csv.gz > data/current-products.csv
cat data/price-history.csv.gz.part-* | gunzip -c > data/price-history.csv
gunzip -c data/sources.json.gz > data/sources.json
python scripts/update_catalog.py
python scripts/update_metal_rates.py
python scripts/build_site.py
```

### Metal-value estimates

When a product exposes an unambiguous metal, net metal weight, seller-stated purity and a sourced rate, the dashboard estimates a raw-metal benchmark value. Ambiguous alloys, plating, composite weights and missing purity show an explicit reason instead. The difference between listed retail and benchmark may include taxes, workmanship, design, stones, packaging and margin; it is not a making-charge or GST determination. Additional metals are recognized but do not get invented benchmark rates.

## Product metadata

The dashboard shows merchant gender choices as Male, Female, Unisex (both choices), or Not stated. A gender claim is descriptive metadata, not a recommendation. Missing images use same-product candidates when available, then a neutral fallback. When the merchant shows “Contact us for price,” the catalog withholds older structured prices and offers a link to the merchant page. The `data-guide.md` explains each public JSON field and its freshness limits.

## Accuracy and affiliation

This is an independent observational project and is not affiliated with or endorsed by Chakradhari. Availability and prices can change between scans; verify important information on the linked product page. The monitor reads public pages and structured data only.

## License

Code is MIT licensed. Product names, imagery and other catalog content remain the property of their respective owners.
