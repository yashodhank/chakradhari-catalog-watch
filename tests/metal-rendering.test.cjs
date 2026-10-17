const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('docs/catalog.js', 'utf8');
const context = vm.createContext({Intl});
vm.runInContext(source.slice(0, source.indexOf('\n}', source.indexOf('function metalLine(')) + 2), context);
test('variant rendering shows each weight and purity without a retail residual', () => {
  const products = fs.readdirSync('docs').filter(f => /^products-\d+.json$/.test(f)).flatMap(f => JSON.parse(fs.readFileSync('docs/'+f)));
  const p = products.find(p => p.id === '4e11dbb4beaf85921dd9');
  const html = context.metalLine(p);
  for (const text of ['99.6%', '996‰', '43 g', '47 g', '52 g', '42.828', '2026-10-16', 'price is not matched']) assert.ok(html.includes(text), text);
  assert.ok(!html.includes('Asking price − raw material'));
});
test('unknown weight still displays known purity and escapes variant evidence', () => {
  assert.match(context.metalLine({metalEstimate:{metal:'Silver',purity:996,status:'weight_missing'}}), /99.6%/);
  const html = context.metalLine({metalEstimate:{metal:'Silver',purity:996,status:'variant_estimates',variants:[{size:'<img src=x>',weightGrams:43,metalValue:100,fineMetalGrams:42.828}]}});
  assert.ok(!html.includes('<img'));
  assert.ok(html.includes('&lt;img'));
});
