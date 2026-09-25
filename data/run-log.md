# Chakradhari catalog monitor run log

## 2026-09-15T05:12:04Z

- Run ID: 20260915T051204Z
- Result: Partial enrichment baseline; catalog listing coverage complete across discovered navigation categories.
- Comparison: No earlier successful snapshot exists. No additions, removals, restocks, or price changes are asserted.
- Active products: 1,731
- In stock: 1,723
- Out of stock: 8
- Currency detected: INR (₹)
- Category coverage: 144/144 successful
- Product detail enrichment: 1/1731 product pages inspected; category-card fields are present for all rows.
- Pagination discovered: 0 public pagination links; category result grids exposed their listed products directly.
- Access errors: robots.txt and sitemap.xml could not be retrieved because direct text/XML navigation was blocked.
- Evidence: https://www.chakradhari.com/ and the source/product URLs retained in sources.json and current-products.csv.

This baseline must not be used to infer removals. A product is only confirmed removed after two consecutive successful full catalog scans.

## 2026-09-15T07:17:46Z

- Run ID: 20260915T071746Z
- Result: Successful validation of the same-day category snapshot; detail enrichment remains partial.
- Comparison: No meaningful changes detected. This is not an independent full-detail snapshot and cannot advance removal streaks.
- Active products: 1,731
- In stock: 1,723
- Out of stock: 8
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Currency detected: INR (₹)
- Category coverage: 144/144 successful in the underlying same-day snapshot.
- Product detail enrichment: 1/1731 pages.
- Access errors: robots.txt and sitemap.xml remained unavailable to the public crawler; homepage/navigation was reachable.
- Evidence: https://www.chakradhari.com/ and per-row source URLs.

Removal state was deliberately unchanged because the crawl is partial.

## 2026-09-16 08:26 IST — partial crawl

- Run ID: `2026-09-16T02:56:33Z-partial`
- Result: Partial; no reliable whole-catalog comparison
- Previous active snapshot retained: 1,731 products
- Snapshot stock totals retained: 1,723 in stock; 8 out of stock
- Public pages successfully checked: homepage and Copper Bracelet category
- Directly re-observed unchanged products recorded: 9
- Homepage prices checked: unchanged for the directly verified sample
- Access errors: `robots.txt`, `sitemap.xml`
- Missing/removal streaks advanced: no
- Change events appended: 0
- Evidence: https://www.chakradhari.com/ ; https://www.chakradhari.com/categories/copper-bracelet-1

## 2026-09-17T03:10:49Z

- Run ID: 20260917T031049Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,864
- Active products: 1,861
- In stock: 1,847
- Out of stock: 14
- Added: 130; suspected removals: 3; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 143/137
- Access errors: 6
- Currency detected: INR
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml


### Same-run repair note

Six sitemap-listed Rudraksha URLs whose detail pages were malformed or returned HTTP 404 were retained as active catalog entries with unknown stock/price, because the complete product sitemap still lists them. The three products absent from today's sitemap remain suspected removals (missing streak 1); the internal rerun did not advance them to confirmed removal.

## 2026-09-18T03:09:13Z

- Run ID: 20260918T030913Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,862
- Active products: 1,864
- In stock: 1,844
- Out of stock: 14
- Added: 0; suspected removals: 2; confirmed removals: 3; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 66/66
- Access errors: 0
- Currency detected: INR
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-19T02:57:19Z

- Run ID: 20260919T025719Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,862
- Active products: 1,862
- In stock: 1,842
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 2; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 69/69
- Access errors: 0
- Currency detected: INR
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-20T03:03:12Z

- Run ID: 20260920T030312Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1863
- Active products: 1864
- In stock: 1844
- Out of stock: 14
- Stock unknown: 6
- Added: 2; suspected removals: 1; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 9/9
- Access errors: 0
- Currency detected: INR
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-21T02:36:16Z

- Run ID: 20260921T023616Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,843
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 1; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 78/78
- Access errors: 0
- Currency detected: INR
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-22T02:41:07Z

+- Run ID: `20260922T024107Z`
+- Result: Partial crawl; no reliable whole-catalog comparison.
+- Previous active snapshot retained: 1863 products
+- In stock: 1843; out of stock: 14; stock unknown: 6
+- Homepage products directly re-observed: 47
+- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 2.
+- Product sitemap, sitemap index, and robots.txt were inaccessible (HTTP 403 / browser client blocked).
+- Missing/removal streaks advanced: no
+- Currency detected: INR (₹)
+- Evidence: https://www.chakradhari.com/ and directly verified product URLs for price changes.
+
## 2026-09-23T07:52:08Z

- Run ID: 20260923T075208Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,835
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 89.
- Detail pages attempted/succeeded: 89/89
- Access errors: 0
- Currency detected: INR
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T03:14:42Z

- Run ID: 20260924T031442Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,835
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 95.
- Detail pages attempted/succeeded: 100/100
- Access errors: 0
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T03:19:08Z

- Run ID: 20260924T031908Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 15
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 7.
- Detail pages attempted/succeeded: 263/263
- Access errors: 0
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 183
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T03:22:30Z

- Run ID: 20260924T032230Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 15
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 1.
- Detail pages attempted/succeeded: 81/81
- Access errors: 0
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T03:26:43Z

- Run ID: 20260924T032643Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,833
- Out of stock: 16
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 80/80
- Access errors: 0
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T04:48:26Z

- Run ID: 20260924T044826Z
- Result: Successful complete sitemap comparison with targeted detail refresh.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,836
- Out of stock: 13
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 3; price changes: 0.
- Detail pages attempted/succeeded: 1000/1000
- Access errors: 0
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T04:52:00Z

- Run ID: 20260924T045200Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 429/423
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T04:54:38Z

- Run ID: 20260924T045438Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 6/0
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T05:29:53Z

- Run ID: 20260924T052953Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 7/1
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T05:31:10Z

- Run ID: 20260924T053110Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 7/1
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T05:33:49Z

- Run ID: 20260924T053349Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 7/1
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T05:34:27Z

- Run ID: 20260924T053427Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 7/1
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-24T07:42:12Z

- Run ID: 20260924T074212Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,863
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 0; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 14/8
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml

## 2026-09-25T08:01:29Z

- Run ID: 20260925T080129Z
- Result: Partial detail refresh; complete product-sitemap catalog boundary.
- Product sitemap URLs: 1,862
- Active products: 1,863
- In stock: 1,834
- Out of stock: 14
- Added: 0; suspected removals: 1; confirmed removals: 0; restocks: 0; price changes: 0.
- Detail pages attempted/succeeded: 398/392
- Access errors: 6
- Currency detected: INR
- Currency-mismatched localized prices ignored: 0
- Localized price observations repaired from compatible structured data: 0
- Evidence: https://www.chakradhari.com/sitemap/products/1.xml
