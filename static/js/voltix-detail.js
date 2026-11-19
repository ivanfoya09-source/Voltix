/* VOLTIX | Етап 4. Інтерактивна галерея та кількість товару.
   Не перехоплює submit, тому сумісний з існуючим cart_add.js. */
(() => {
  'use strict';
  const page = document.querySelector('[data-vx-product-detail]');
  if (!page) return;

  const gallery = page.querySelector('[data-vx-gallery]');
  const mainImage = gallery?.querySelector('[data-vx-main-image]');
  const thumbs = [...(gallery?.querySelectorAll('[data-vx-thumb]') || [])];
  const lightbox = document.querySelector('[data-vx-lightbox]');
  const lightboxImage = lightbox?.querySelector('[data-vx-lightbox-image]');
  const zoomButton = gallery?.querySelector('[data-vx-zoom]');
  const closeButton = lightbox?.querySelector('[data-vx-close]');
  let lastFocused = null;

  thumbs.forEach((thumb) => {
    thumb.addEventListener('click', () => {
      if (!mainImage) return;
      mainImage.src = thumb.dataset.imageUrl;
      mainImage.alt = thumb.dataset.imageAlt || '';
      thumbs.forEach((t) => {
        const active = t === thumb;
        t.classList.toggle('is-active', active);
        t.setAttribute('aria-pressed', String(active));
      });
    });
  });

  function closeLightbox() {
    if (!lightbox || lightbox.hidden) return;
    lightbox.hidden = true;
    lightbox.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    lastFocused?.focus();
  }
  zoomButton?.addEventListener('click', () => {
    if (!lightbox || !lightboxImage || !mainImage) return;
    lastFocused = document.activeElement;
    lightboxImage.src = mainImage.src;
    lightboxImage.alt = mainImage.alt;
    lightbox.hidden = false;
    lightbox.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    closeButton?.focus();
  });
  closeButton?.addEventListener('click', closeLightbox);
  lightbox?.addEventListener('click', (event) => {
    if (event.target === lightbox) closeLightbox();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closeLightbox();
    if (event.key === 'Tab' && lightbox && !lightbox.hidden) {
      event.preventDefault();
      closeButton?.focus();
    }
  });

  const qty = page.querySelector('[data-vx-qty]');
  const input = qty?.querySelector('input[name="quantity"]');
  if (qty && input) {
    const getLimits = () => ({
      min: Number(input.min) || 1,
      max: Number(input.max) || Number.MAX_SAFE_INTEGER,
    });
    const clamp = (n) => {
      const {min, max} = getLimits();
      return Math.max(min, Math.min(max, Number.isFinite(n) ? n : min));
    };
    const setQuantity = (n) => {
      input.value = String(clamp(n));
    };
    qty.querySelector('[data-vx-qty-minus]')?.addEventListener('click', () => setQuantity(Number(input.value) - 1));
    qty.querySelector('[data-vx-qty-plus]')?.addEventListener('click', () => setQuantity(Number(input.value) + 1));
    input.addEventListener('change', () => setQuantity(Number(input.value)));
  }
})();
