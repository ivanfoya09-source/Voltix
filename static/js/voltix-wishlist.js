
/* ==========================================
   VOLTIX — WISHLIST AJAX
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    const wishlistForms = document.querySelectorAll(
        "[data-wishlist-form]"
    );

    wishlistForms.forEach((form) => {

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const button = form.querySelector(
                "[data-wishlist-heart]"
            );

            if (!button || button.disabled) return;

            button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    credentials: "same-origin"
                });

                if (!response.ok) {
                    throw new Error(
                        "Помилка сервера: " + response.status
                    );
                }

                const data = await response.json();

                if (!data.success) return;

                // Оновлюємо всі сердечка цього товару
                document.querySelectorAll(
                    "[data-wishlist-heart]"
                ).forEach((heart) => {

                    if (
                        heart.dataset.productId ===
                        String(data.product_id)
                    ) {
                        heart.classList.toggle(
                            "is-active",
                            data.is_favorite
                        );

                        heart.textContent = data.is_favorite
                            ? "♥"
                            : "♡";

                        heart.setAttribute(
                            "aria-pressed",
                            String(data.is_favorite)
                        );

                        heart.title = data.is_favorite
                            ? "Видалити з обраного"
                            : "Додати до обраного";
                    }
                });

                // Оновлюємо лічильник у шапці
                document.querySelectorAll(
                    "[data-wishlist-count]"
                ).forEach((counter) => {
                    counter.textContent = data.wishlist_count;
                });

            } catch (error) {
                console.error(
                    "VOLTIX Wishlist:",
                    error
                );

                alert(
                    "Не вдалося оновити обране. Спробуйте ще раз."
                );

            } finally {
                button.disabled = false;
            }
        });
    });

});
