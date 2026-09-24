# Chakradhari Catalog Watch — searchable product catalog, prices and stock

[![Open public dashboard](https://img.shields.io/badge/Open-public%20dashboard-176b52?style=for-the-badge)](https://yashodhank.github.io/chakradhari-catalog-watch/)
[![Daily catalog scan](https://github.com/yashodhank/chakradhari-catalog-watch/actions/workflows/daily-catalog-scan.yml/badge.svg)](https://github.com/yashodhank/chakradhari-catalog-watch/actions/workflows/daily-catalog-scan.yml)
[![GitHub Pages deployment](https://github.com/yashodhank/chakradhari-catalog-watch/actions/workflows/pages.yml/badge.svg)](https://github.com/yashodhank/chakradhari-catalog-watch/actions/workflows/pages.yml)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**[Explore the free public catalog dashboard →](https://yashodhank.github.io/chakradhari-catalog-watch/)**

An independent, searchable view of [Chakradhari's public product catalog](https://www.chakradhari.com/). Browse jewelry, gemstones, metals and other listed products; filter by category, stock, material, gender claim and price; inspect product images, seller claims and observed changes. The dashboard is a static site hosted on GitHub Pages, so visitors need no account.

## What you can do

- **Find products quickly:** Search names, category, material, size and common metal names in English, Hindi or transliteration. Combine search with stock, gender, metal, price and data-availability filters; share filtered results by URL.
- **Check price and availability:** See observed INR prices, sale indicators, explicit stock states and direct links to the merchant. Products marked **Contact seller for price** never display an older numeric price as a current offer.
- **Review catalog changes:** Follow additions, confirmed removals, stock transitions and price or sale changes, with a link to the relevant product. A removal requires two consecutive successful complete sitemap scans.
- **Assess metal content cautiously:** Where the seller states a usable net metal weight and purity and a dated reference is available, see the estimated raw-metal amount next to the asking price and their difference. Monthly international base-metal references are labeled separately from daily Indian bullion rates. The retail remainder is unexplained retail cost; it is not a quoted making charge or tax amount.
- **Inspect evidence:** Check first and last catalog sightings, detail-page verification, seller material and size claims, image availability and source coverage. Download a filtered JSON selection.

**Dashboard:** https://yashodhank.github.io/chakradhari-catalog-watch/  
**Source catalog:** https://www.chakradhari.com/  
**Field definitions and freshness:** [Data guide](docs/data-guide.md)

## Public datasets

| File | Contents |
| --- | --- |
| [Current products](data/current-products.csv.gz) | Latest known product state, including canonical URL, price, stock, material and image evidence |
| [Price history](data/) | Append-only observations split into `price-history.csv.gz.part-*` archives |
| [Change events](data/change-events.csv) | Meaningful additions, removals, stock and price events |
| [Sources](data/sources.json.gz) | Source registry with status and historical observations |
| [Run log](data/run-log.md) | Sitemap coverage, detail-page success and errors |
| [Metal rates](data/metal-rates.json) | Dated bullion benchmark observations |
| [Dashboard manifest](docs/products-manifest.json) | Summary, recent events and product chunk references for the public UI |

See the [material coverage and rate-source research queue](docs/RATE-SOURCES-TODO.md) for metals, gemstones, Rudraksha and unresolved sources.

The dashboard's [JSON manifest](docs/products-manifest.json) and linked product chunks are convenient for scripts and AI assistants. See the [data guide](docs/data-guide.md) for field meanings and limitations.

## How updates work

GitHub Actions scans the public sitemap and selected product pages daily at approximately **08:00 IST**. It preserves source and change history, refreshes metal benchmarks, builds the static dashboard and deploys it to GitHub Pages. Check the [scan workflow](https://github.com/yashodhank/chakradhari-catalog-watch/actions/workflows/daily-catalog-scan.yml) and [deployment workflow](https://github.com/yashodhank/chakradhari-catalog-watch/actions/workflows/pages.yml) for current status. A manual scan can be started from GitHub Actions.

To run a local scan with Python 3.12 or newer (no third-party packages):

```bash
gunzip -c data/current-products.csv.gz > data/current-products.csv
cat data/price-history.csv.gz.part-* | gunzip -c > data/price-history.csv
gunzip -c data/sources.json.gz > data/sources.json
python -m unittest discover -s tests -v
python scripts/update_catalog.py
python scripts/update_metal_rates.py
python scripts/build_site.py
```

Open `docs/index.html` through a local static HTTP server to explore the generated site.

## Your catalog should earn trust before a customer asks

A missing product image, an outdated price or a slow storefront can quietly lose a buyer before they ever contact you. This project shows what a searchable catalog and regular product checks can reveal. If your own site has gaps you have not measured, every day leaves those decisions to your customers.

**Securiace can help you build a clearer digital storefront:** searchable product catalogs, custom dashboards, price and stock monitoring, and the hosting infrastructure behind them. Tell us what you sell and where the current experience breaks down; we can scope a practical solution around your business.

- **[Discuss a catalog or custom solution with Securiace →](https://my.securiace.com/contact.php)**
- **[Explore shared web hosting →](https://my.securiace.com/store/web-hosting)**
- **[Explore managed VPS →](https://my.securiace.com/store/managed-vps)** · **[self-managed VPS →](https://my.securiace.com/store/self-managed-vps)**

Service availability, scope and current ordering terms are shown in the [Securiace client portal](https://my.securiace.com/). This independent catalog monitor is an example of the problem space, not a claim that Securiace operates the merchant's store.

## Interpretation and limits

This monitor records **publicly observed claims**, not independently verified product properties. A catalog sighting does not prove that a price or stock state was rechecked that day; inspect the detail verification timestamp and the linked merchant page before purchasing. Some merchant pages are inaccessible, and variant coverage is incomplete. Those records remain visible with an unknown state or a neutral image fallback instead of an invented price or thumbnail.

Gender filters describe the merchant's available choices. “Unisex” can mean that both male and female options are offered; it does not establish a single universal size. Metal estimates need a clear weight and purity claim and a sourced rate. Composite products, plating, unknown alloy composition and missing weights do not receive a fabricated metal valuation.

This project is **independent** and is not affiliated with or endorsed by Chakradhari. The code is [MIT licensed](LICENSE); merchant names, product descriptions and images belong to their respective owners.
