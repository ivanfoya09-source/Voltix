// VOLTIX / responsive catalog filters. Existing cart_add.js handles AJAX cart.
(() => {
  const toggle = document.querySelector('[data-vx-filter-toggle]');
  const filters = document.getElementById('vx-catalog-filters');
  if (!toggle || !filters) return;
  toggle.addEventListener('click', () => {
    const open = filters.classList.toggle('is-open');
    toggle.setAttribute('aria-expanded', String(open));
    if (open) filters.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
})();
