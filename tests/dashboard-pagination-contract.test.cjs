const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const docs = path.join(__dirname, '..', 'docs');
const index = fs.readFileSync(path.join(docs, 'index.html'), 'utf8');
const catalog = fs.readFileSync(path.join(docs, 'catalog.js'), 'utf8');
const explore = fs.readFileSync(path.join(docs, 'explore.js'), 'utf8');
const styles = fs.readFileSync(path.join(docs, 'refinements.css'), 'utf8');

test('puts the collection chooser before reference material and the long product browser', () => {
  assert.ok(index.indexOf('id="collections"') < index.indexOf('id="materialBenchmarks"'));
  assert.ok(index.indexOf('id="materialBenchmarks"') < index.indexOf('id="products"'));
  assert.match(index, /class="panel collections-feature"/);
  assert.match(styles, /\.collections-feature\{border-color:var\(--green\)/);
});

test('keeps product loading intentional and reachable without scrolling', () => {
  assert.match(index, /id="loadMoreTop"/);
  assert.match(index, /id="loadMoreBottom"/);
  assert.match(catalog, /batchSize=24/);
  assert.doesNotMatch(catalog, /loadObserver=/);
  assert.doesNotMatch(catalog, /loading as you scroll/);
});

test('uses content-width grids for the affected responsive sections', () => {
  assert.match(styles, /\.collection-grid\{display:grid;grid-template-columns:repeat\(auto-fit,minmax\(190px,1fr\)\)\}/);
  assert.match(styles, /\.type-grid\{display:grid;grid-template-columns:repeat\(auto-fit,minmax\(175px,1fr\)\)\}/);
  assert.match(styles, /\.collection-grid a,.type-grid a\{display:flex;flex-direction:column/);
  assert.match(styles, /\.rate-grid\{grid-template-columns:repeat\(auto-fit,minmax\(180px,1fr\)\)\}/);
});

test('renders benchmark rates as accessible purity cards without a WebGL dependency', () => {
  assert.match(catalog, /class="rate-card rate-card--/);
  assert.match(catalog, /rate-card__purity/);
  assert.match(catalog, /Purity ring shows the published fineness/);
  assert.match(styles, /\.rate-card__visual/);
  assert.match(styles, /\.rate-card__purity::before/);
  assert.doesNotMatch(catalog, /three(?:\.js)?|WebGL/i);
});

test('presents filtered catalog status as labelled metrics instead of one run-on sentence', () => {
  assert.match(explore, /class="scope scope--metrics"/);
  assert.match(explore, /const metric=.*scope__metric/);
  assert.match(explore, /metric\('In stock'/);
  assert.match(explore, /metric\('Median asking price'/);
  assert.match(styles, /\.scope--metrics\{display:grid;grid-template-columns:repeat\(auto-fit,minmax\(132px,1fr\)\)/);
});

test('keeps product evidence compact, legible, and free of raw machine timestamps', () => {
  assert.match(explore, /class="row-detail__title">Product details/);
  assert.match(explore, /class="row-detail__fields"/);
  assert.match(explore, /toLocaleDateString\('en-IN'/);
  assert.match(styles, /\.row-detail__fields\{display:grid;grid-template-columns:repeat\(auto-fit,minmax\(140px,1fr\)\)/);
});
