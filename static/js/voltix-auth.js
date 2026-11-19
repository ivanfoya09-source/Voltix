/* VOLTIX authentication UX — progressive enhancement only. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-vx-password-toggle]').forEach(button => {
    const wrapper = button.closest('.vx-auth-input-wrap');
    const input = wrapper?.querySelector('input[type="password"], input[data-vx-revealed]');
    if (!input) { button.hidden = true; return; }
    button.addEventListener('click', () => {
      const reveal = input.type === 'password';
      input.type = reveal ? 'text' : 'password';
      input.toggleAttribute('data-vx-revealed', reveal);
      button.textContent = reveal ? 'Приховати' : 'Показати';
      button.setAttribute('aria-label', reveal ? 'Приховати пароль' : 'Показати пароль');
      button.setAttribute('aria-pressed', String(reveal));
    });
  });
});
