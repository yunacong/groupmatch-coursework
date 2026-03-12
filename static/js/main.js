document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('primaryNav');

  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
  }

  document.querySelectorAll('.validated-form').forEach(form => {
    form.addEventListener('submit', event => {
      let valid = true;
      form.querySelectorAll('input[required], textarea[required], select[required]').forEach(field => {
        const value = field.type === 'checkbox' ? field.checked : field.value.trim();
        if (!value) {
          valid = false;
          field.setAttribute('aria-invalid', 'true');
        } else {
          field.removeAttribute('aria-invalid');
        }
      });

      if (!valid) {
        event.preventDefault();
        const firstInvalid = form.querySelector('[aria-invalid="true"]');
        if (firstInvalid) firstInvalid.focus();
      }
    });
  });
});
