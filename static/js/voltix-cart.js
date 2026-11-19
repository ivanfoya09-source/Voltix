/* VOLTIX cart review dialog — reads live DOM; does not intercept AJAX requests. */
document.addEventListener('DOMContentLoaded', () => {
    const root = document.querySelector('[data-vx-cart]');
    if (!root) return;
    const dialog = root.querySelector('[data-vx-cart-dialog]');
    const openButton = root.querySelector('[data-vx-cart-preview-open]');
    if (!dialog || !openButton || typeof dialog.showModal !== 'function') return;

    const list = dialog.querySelector('[data-vx-cart-dialog-list]');
    const total = dialog.querySelector('[data-vx-cart-dialog-total]');
    const payable = root.querySelector('[data-vx-cart-payable]');

    function getRows() {
        return Array.from(root.querySelectorAll('[data-cart-row]'))
            .filter(row => row.isConnected && !row.hidden && getComputedStyle(row).display !== 'none');
    }
    function syncTotal() {
        const cartTotal = root.querySelector('[data-cart-total]');
        if (payable && cartTotal) payable.textContent = cartTotal.textContent.trim();
    }
    // Keep our supplementary total in sync with the existing AJAX cart.js.
    const cartTotal = root.querySelector('[data-cart-total]');
    if (cartTotal && payable) {
        const observer = new MutationObserver(syncTotal);
        observer.observe(cartTotal, { childList: true, characterData: true, subtree: true });
    }

    openButton.addEventListener('click', () => {
        list.replaceChildren();
        getRows().forEach(row => {
            const article = document.createElement('div');
            article.className = 'vx-cart-dialog-line';
            const image = row.querySelector('.vx-cart-picture img');
            if (image) {
                const copy = document.createElement('img');
                copy.src = image.src;
                copy.alt = image.alt;
                article.appendChild(copy);
            }
            const content = document.createElement('div');
            content.className = 'vx-cart-dialog-line-content';
            const name = document.createElement('strong');
            name.textContent = row.querySelector('.vx-cart-name')?.textContent.trim() || 'Товар';
            const qty = document.createElement('small');
            qty.textContent = 'Кількість: ' + (row.querySelector('input[name="quantity"]')?.value || '1');
            content.append(name, qty);
            const price = document.createElement('span');
            price.className = 'vx-cart-dialog-line-price';
            price.textContent = row.querySelector('[data-item-total]')?.textContent.trim() || '';
            article.append(content, price);
            list.appendChild(article);
        });
        if (!list.childElementCount) {
            const p = document.createElement('p');
            p.textContent = 'Кошик порожній';
            list.appendChild(p);
        }
        total.textContent = root.querySelector('[data-cart-total]')?.textContent.trim() || '0 ₴';
        dialog.showModal();
    });
    dialog.querySelectorAll('[data-vx-cart-preview-close]').forEach(button => {
        button.addEventListener('click', () => dialog.close());
    });
    dialog.addEventListener('click', event => {
        if (event.target === dialog) dialog.close();
    });
});
