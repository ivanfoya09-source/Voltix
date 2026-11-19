
// ============================================
// VOLTIX — AJAX ADD TO CART
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    // Створюємо контейнер для повідомлень.
    const notification = document.createElement("div");

    notification.className = "voltix-cart-toast";
    notification.setAttribute("role", "status");
    notification.setAttribute("aria-live", "polite");

    notification.hidden = true;

    document.body.appendChild(notification);

    let notificationTimeout = null;

    // Показ повідомлення.
    function showNotification(message, isError = false) {

        clearTimeout(notificationTimeout);

        notification.textContent = message;

        notification.classList.toggle(
            "is-error",
            isError
        );

        notification.hidden = false;

        notificationTimeout = setTimeout(() => {
            notification.hidden = true;
        }, 3500);
    }

    // Відстежуємо відправлення форм додавання.
    document.addEventListener("submit", async (event) => {

        const form = event.target;

        if (!form.matches("[data-ajax-add-to-cart]")) {
            return;
        }

        // Якщо JavaScript працює,
        // скасовуємо звичайне відправлення форми.
        event.preventDefault();

        // Захист від повторного натискання.
        if (form.dataset.submitting === "true") {
            return;
        }

        form.dataset.submitting = "true";

        const button = form.querySelector(
            'button[type="submit"]'
        );

        const originalButtonText = button
            ? button.textContent
            : "";

        if (button) {
            button.disabled = true;
            button.textContent = "Додаємо...";
        }

        try {

            const formData = new FormData(form);

            // Для форм без поля кількості
            // за замовчуванням додаємо 1 одиницю.
            if (!formData.has("quantity")) {
                formData.set("quantity", "1");
            }

            const response = await fetch(
                form.dataset.ajaxUrl,
                {
                    method: "POST",
                    body: formData,
                    credentials: "same-origin",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                }
            );

            const contentType = (
                response.headers.get("content-type") || ""
            );

            if (!contentType.includes("application/json")) {
                throw new Error(
                    "Сервер не повернув JSON. Перевір URL."
                );
            }

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(
                    data.error ||
                    "Не вдалося додати товар."
                );
            }

            // Оновлюємо лічильник у шапці.
            document.querySelectorAll(
                ".cart-counter"
            ).forEach(counter => {
                counter.textContent = data.cart_count;
            });

            // Оновлюємо підпис для доступності.
            document.querySelectorAll(
                ".header-cart"
            ).forEach(link => {
                link.setAttribute(
                    "aria-label",
                    `Кошик, товарів: ${data.cart_count}`
                );
            });

            showNotification(
                "✓ " + data.message
            );

        } catch (error) {

            showNotification(
                error.message,
                true
            );

        } finally {

            form.dataset.submitting = "false";

            if (button) {
                button.disabled = false;
                button.textContent = originalButtonText;
            }

        }

    });

});
