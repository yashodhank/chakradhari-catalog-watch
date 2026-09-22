# Chakradhari Catalog Watch

An independent, public monitor for the product catalog at [chakradhari.com](https://www.chakradhari.com/). It records additions, removals, stock changes and price history, and publishes a searchable static dashboard.

## Public data

- `data/current-products.csv` — latest known state for every monitored product
- `data/price-history.csv` — append-only price observations
- `data/change-events.csv` — append-only meaningful changes
- `data/sources.json` — source registry and source-status history
- `data/run-log.md` — scan coverage and reliability log
- `data/metal-rates.json` — dated IBJA gold, silver and platinum benchmark observations

Historical rows are never deliberately overwritten. A product is confirmed removed only after two consecutive successful complete sitemap comparisons. Failed or partial scans do not advance removal streaks.

## Automation

GitHub Actions scans the public catalog each day at approximately 08:00 IST, rebuilds the dashboard dataset and commits new observations. A manual run is also available from the Actions tab.

Run locally with Python 3.12+ and no third-party packages:

```bash
python scripts/update_catalog.py
python scripts/update_metal_rates.py
python scripts/build_site.py
```

### Metal-value estimates

When a product exposes a usable metal, weight and purity, the dashboard estimates its raw-metal benchmark value. Rates come from IBJA and exclude GST and making charges. Purity inferred from a hallmark is labelled; when purity is absent, the scenario assumption is shown explicitly. The residual is labelled a **non-metal retail premium**, because it can include workmanship, design, stones, packaging, seller margin and other components—not just making charges. An indicative GST component uses 3% of the GST-inclusive jewellery transaction value, consistent with the CBIC gems and jewellery FAQ; it is not an invoice or tax determination.

## Accuracy and affiliation

This is an independent observational project and is not affiliated with or endorsed by Chakradhari. Availability and prices can change between scans; verify important information on the linked product page. The monitor reads public pages and structured data only.

## License

Code is MIT licensed. Product names, imagery and other catalog content remain the property of their respective owners.
