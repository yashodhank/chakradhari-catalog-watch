const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const docs = path.join(__dirname, '..', 'docs');
const index = fs.readFileSync(path.join(docs, 'index.html'), 'utf8');
const catalog = fs.readFileSync(path.join(docs, 'catalog.js'), 'utf8');
const styles = fs.readFileSync(path.join(docs, 'refinements.css'), 'utf8');

test('puts material benchmarks before the potentially long product browser', () => {
  assert.ok(index.indexOf('id="materialBenchmarks"') < index.indexOf('id="products"'));
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
