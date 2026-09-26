const test = require('node:test');
const assert = require('node:assert/strict');

const { loadState } = require('../docs/catalog-pagination.js');

test('starts with a bounded first page and exposes the next page size', () => {
  assert.deepEqual(loadState(1864, 0, 24), {
    visible: 0,
    remaining: 1864,
    nextCount: 24,
    done: false,
  });
});

test('never renders or advertises more products than the filtered result count', () => {
  assert.deepEqual(loadState(10, 8, 24), {
    visible: 8,
    remaining: 2,
    nextCount: 2,
    done: false,
  });
  assert.deepEqual(loadState(10, 10, 24), {
    visible: 10,
    remaining: 0,
    nextCount: 0,
    done: true,
  });
});

test('normalizes stale or invalid paging inputs to a safe state', () => {
  assert.deepEqual(loadState(10, -4, 24), {
    visible: 0,
    remaining: 10,
    nextCount: 10,
    done: false,
  });
  assert.deepEqual(loadState(10, 99, 24), {
    visible: 10,
    remaining: 0,
    nextCount: 0,
    done: true,
  });
});
