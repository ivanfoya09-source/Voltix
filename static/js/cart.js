
// ============================================
// VOLTIX — AJAX CART
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    const cartContainer = document.querySelector(
        "[data-cart-container]"
    );

    if (!cartContainer) {
        return;
    }

    const money = (value) => {
        return new Intl.NumberFormat("uk-UA", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(Number(value)) + " ₴";
    };

    // Повідомлення про помилки
    function showCartMessage(text, type = "danger") {
        const messageBox = document.querySelector(
            "[data-cart-message]"
        );

        if (!messageBox) {
            alert(text);
            return;
        }

        messageBox.textContent = text;
        messageBox.className =
            `alert alert-${type} mt-3`;

        messageBox.hidden = false;
    }

    function clearCartMessage() {
        const messageBox = document.querySelector(
            "[data-cart-message]"
        );

        if (messageBox) {
            messageBox.hidden = true;
            messageBox.textContent = "";
        }
    }

    // Оновлюємо загальну суму та лічильник
    function updateCartTotals(data) {

        document.querySelectorAll(
            "[data-cart-total]"
        ).forEach(element => {
            element.textContent = money(data.cart_total);
        });

        document.querySelectorAll(
            ".cart-counter"
        ).forEach(element => {
            element.textContent = data.cart_count;
        });

    }

    // AJAX POST
    async function sendCartRequest(url, formData) {

        const response = await fetch(url, {
            method: "POST",
            body: formData,
            credentials: "same-origin",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        const contentType = response.headers.get(
            "content-type"
        ) || "";

        if (!contentType.includes("application/json")) {
            throw new Error(
                "Сервер не повернув JSON. Перевір авторизацію та URL."
            );
        }

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Не вдалося оновити кошик."
            );
        }

        return data;
    }

    // Зміна кількості товару
    async function changeQuantity(row, newQuantity) {

        const form = row.querySelector(
            "[data-cart-update-form]"
        );

        if (!form) {
            return;
        }

        const input = form.querySelector(
            'input[name="quantity"]'
        );

        const maxStock = Number(
            row.dataset.stock
        );

        if (
            !Number.isInteger(newQuantity) ||
            newQuantity < 1
        ) {
            showCartMessage(
                "Мінімальна кількість товару — 1."
            );
            return;
        }

        if (newQuantity > maxStock) {
            showCartMessage(
                `На складі доступно лише ${maxStock} шт.`
            );
            return;
        }

        clearCartMessage();

        const formData = new FormData(form);
        formData.set("quantity", newQuantity);

        const buttons = row.querySelectorAll(
            "button"
        );

        buttons.forEach(button => {
            button.disabled = true;
        });

        try {

            const data = await sendCartRequest(
                form.dataset.ajaxUrl,
                formData
            );

            // Кількість
            input.value = data.quantity;

            const quantityLabel = row.querySelector(
                "[data-cart-quantity]"
            );

            if (quantityLabel) {
                quantityLabel.textContent = data.quantity;
            }

            // Сума одного товару
            const itemTotal = row.querySelector(
                "[data-item-total]"
            );

            if (itemTotal) {
                itemTotal.textContent = money(
                    data.item_total
                );
            }

            updateCartTotals(data);

        } catch (error) {

            showCartMessage(error.message);

        } finally {

            buttons.forEach(button => {
                button.disabled = false;
            });

        }

    }

    // Кнопки + та -
    cartContainer.addEventListener("click", async (event) => {

        const button = event.target.closest(
            "[data-cart-action]"
        );

        if (!button) {
            return;
        }

        const row = button.closest(
            "[data-cart-row]"
        );

        if (!row) {
            return;
        }

        const input = row.querySelector(
            'input[name="quantity"]'
        );

        if (!input) {
            return;
        }

        const currentQuantity = Number(input.value);

        if (button.dataset.cartAction === "increase") {
            await changeQuantity(
                row,
                currentQuantity + 1
            );
        }

        if (button.dataset.cartAction === "decrease") {
            await changeQuantity(
                row,
                currentQuantity - 1
            );
        }

    });

    // Зміна кількості вручну
    cartContainer.addEventListener("submit", async (event) => {

        const form = event.target;

        if (form.matches("[data-cart-update-form]")) {

            event.preventDefault();

            const row = form.closest(
                "[data-cart-row]"
            );

            const input = form.querySelector(
                'input[name="quantity"]'
            );

            await changeQuantity(
                row,
                Number(input.value)
            );

            return;
        }

        // Видалення товару
        if (form.matches("[data-cart-remove-form]")) {

            event.preventDefault();

            const row = form.closest(
                "[data-cart-row]"
            );

            if (!row) {
                return;
            }

            clearCartMessage();

            const buttons = row.querySelectorAll(
                "button"
            );

            buttons.forEach(button => {
                button.disabled = true;
            });

            try {

                const data = await sendCartRequest(
                    form.dataset.ajaxUrl,
                    new FormData(form)
                );

                row.remove();

                updateCartTotals(data);

                if (data.cart_count === 0) {
                    // Показуємо стандартну
                    // сторінку порожнього кошика.
                    window.location.reload();
                }

            } catch (error) {

                showCartMessage(error.message);

                buttons.forEach(button => {
                    button.disabled = false;
                });

            }

        }

    });

});
