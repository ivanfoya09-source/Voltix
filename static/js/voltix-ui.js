(() => {
  "use strict";
  const toggle = document.querySelector("[data-vx-menu-toggle]");
  const menu = document.querySelector("[data-vx-menu]");
  const close = document.querySelector("[data-vx-menu-close]");
  if (!toggle || !menu) return;

  function setOpen(open) {
    menu.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    if (open) close?.focus();
  }
  toggle.addEventListener("click", () => setOpen(menu.hidden));
  close?.addEventListener("click", () => { setOpen(false); toggle.focus(); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !menu.hidden) {
      setOpen(false);
      toggle.focus();
    }
  });
  document.addEventListener("click", (event) => {
    if (!menu.hidden && !menu.contains(event.target) && !toggle.contains(event.target)) {
      setOpen(false);
    }
  });
})();
