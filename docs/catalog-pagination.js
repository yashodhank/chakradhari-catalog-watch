(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.catalogPagination = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  function toFiniteInteger(value, fallback) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.floor(number) : fallback;
  }

  function loadState(total, visible, pageSize) {
    const safeTotal = Math.max(0, toFiniteInteger(total, 0));
    const safeVisible = Math.min(safeTotal, Math.max(0, toFiniteInteger(visible, 0)));
    const safePageSize = Math.max(1, toFiniteInteger(pageSize, safeTotal || 1));
    const remaining = safeTotal - safeVisible;

    return {
      visible: safeVisible,
      remaining,
      nextCount: Math.min(safePageSize, remaining),
      done: remaining === 0,
    };
  }

  return { loadState };
});
