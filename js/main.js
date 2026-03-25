/* ── NAV SCROLL ──────────────────────────────────────────────────────────── */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

/* ── REVEAL ON SCROLL ────────────────────────────────────────────────────── */
const revealEls = document.querySelectorAll('.reveal-up, .reveal-left, .reveal-right, .reveal-scale');
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

revealEls.forEach(el => revealObserver.observe(el));

/* ── HERO LOAD ANIMATION ─────────────────────────────────────────────────── */
window.addEventListener('load', () => {
  document.querySelectorAll('.hero .reveal-up, .hero .reveal-left').forEach(el => {
    setTimeout(() => el.classList.add('revealed'), 300);
  });
});

/* ── STAT COUNTER ────────────────────────────────────────────────────────── */
function animateCounter(el) {
  const target  = parseInt(el.dataset.target, 10);
  const prefix  = el.dataset.prefix  || '';
  const suffix  = el.dataset.suffix  || '';
  const duration = 1800;
  const start   = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 4);
    const value = Math.floor(ease * target);
    el.textContent = prefix + value.toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

const statObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounter(entry.target);
      statObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('.stat-num[data-target]').forEach(el => statObserver.observe(el));

/* ── BOOKING FORM ────────────────────────────────────────────────────────── */
const form        = document.getElementById('bookingForm');
const formSuccess = document.getElementById('formSuccess');
const submitBtn   = document.getElementById('submitBtn');
const btnText     = submitBtn?.querySelector('.btn-text');
const btnLoading  = submitBtn?.querySelector('.btn-loading');

if (form) {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    btnText.style.display    = 'none';
    btnLoading.style.display = 'inline';
    submitBtn.disabled       = true;

    const data = {
      name:         form.name.value.trim(),
      email:        form.email.value.trim(),
      company:      form.company.value.trim(),
      availability: form.availability.value.trim(),
      message:      form.message.value.trim(),
    };

    try {
      const res = await fetch('/api/book', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(data),
      });

      if (res.ok) {
        form.style.display        = 'none';
        formSuccess.style.display = 'block';
      } else {
        throw new Error('Server error');
      }
    } catch {
      // Fallback: show success anyway and open mailto
      const subject = encodeURIComponent(`Setup Call Request — ${data.name} @ ${data.company}`);
      const body    = encodeURIComponent(
        `Name: ${data.name}\nEmail: ${data.email}\nCompany: ${data.company}\nAvailability: ${data.availability}\nMessage: ${data.message}`
      );
      window.location.href = `mailto:hello@vlmcreateflow.com?subject=${subject}&body=${body}`;
      form.style.display        = 'none';
      formSuccess.style.display = 'block';
    }
  });
}

/* ── SMOOTH ANCHOR SCROLL ────────────────────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = nav.offsetHeight + 20;
      window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
    }
  });
});
