/* ============================================================
   DIVINE TEMPLE — main.js
   ============================================================ */

/* ── Navbar scroll effect ───────────────────────────────────── */
const nav = document.getElementById('mainNav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  }, { passive: true });
}

/* ── Active nav link (URL-based) ────────────────────────────── */
(function () {
  const links = document.querySelectorAll('.navbar-nav .nav-link');
  const path  = window.location.pathname.replace(/\/$/, '') || '/';
  links.forEach(link => {
    const href = link.getAttribute('href').replace(/\/$/, '') || '/';
    if (href === path) link.classList.add('active');
  });
})();

/* ── Scroll reveal ──────────────────────────────────────────── */
(function () {
  const targets = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');
  if (!targets.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(t => io.observe(t));
})();

/* ── Donation amount buttons ────────────────────────────────── */
(function () {
  const amtBtns   = document.querySelectorAll('.amt-btn');
  const customInp = document.getElementById('customAmount');

  if (!amtBtns.length) return;

  amtBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      amtBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      if (btn.dataset.value === 'custom') {
        if (customInp) { customInp.style.display = 'block'; customInp.focus(); }
      } else {
        if (customInp) customInp.style.display = 'none';
      }
    });
  });
})();

/* ── Smooth anchor scroll ───────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = (nav ? nav.offsetHeight : 70) + 16;
      window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - offset, behavior: 'smooth' });
    }
  });
});

/* ── Counter animation ──────────────────────────────────────── */
(function () {
  const counters = document.querySelectorAll('.ctr-num[data-target]');
  if (!counters.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el     = e.target;
      const target = parseInt(el.dataset.target, 10);
      const suffix = el.dataset.suffix || '';
      const dur    = 1800;
      const step   = Math.ceil(target / (dur / 16));
      let current  = 0;
      const timer  = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = current.toLocaleString() + suffix;
        if (current >= target) clearInterval(timer);
      }, 16);
      io.unobserve(el);
    });
  }, { threshold: 0.4 });

  counters.forEach(c => io.observe(c));
})();

/* ── Contact form submit ─────────────────────────────────────── */
(function () {
  const form = document.getElementById('contactForm');
  if (!form) return;

  form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Sending…';
    btn.disabled  = true;
    setTimeout(() => form.submit(), 400);
  });
})();

/* ── Donation form submit ────────────────────────────────────── */
(function () {
  const form = document.getElementById('donationForm');
  if (!form) return;

  form.addEventListener('submit', e => {
    e.preventDefault();
    const btn = form.querySelector('[type="submit"]');
    btn.innerHTML = '<i class="fa fa-spinner fa-spin me-2"></i>Processing…';
    btn.disabled  = true;
    setTimeout(() => form.submit(), 400);
  });
})();

/* ════════════════════════════════════════════════════════════
   ANIMATION ENHANCEMENTS v3 — Micro-interactions & Polish
   ════════════════════════════════════════════════════════════ */

/* ── Scroll progress bar ────────────────────────────────────── */
(function () {
  const bar = document.createElement('div');
  bar.className = 'scroll-progress';
  document.body.prepend(bar);

  window.addEventListener('scroll', () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollable > 0) {
      bar.style.width = (window.scrollY / scrollable * 100).toFixed(2) + '%';
    }
  }, { passive: true });
})();

/* ── Hero stat count-up ─────────────────────────────────────── */
(function () {
  const stats = document.querySelectorAll('.hero-stat .number');
  if (!stats.length) return;

  // Snapshot originals before any mutation
  const originals = Array.from(stats).map(el => el.textContent.trim());

  // Wait for hero fadeInUp animation to settle (~0.9s)
  setTimeout(() => {
    stats.forEach((el, i) => {
      const raw   = originals[i];
      const match = raw.match(/^([\d.]+)(.*)/);
      if (!match) return;
      const target = parseFloat(match[1]);
      const suffix = match[2];
      const dur    = 1800;
      const inc    = target / (dur / 16);
      let current  = 0;

      const timer = setInterval(() => {
        current = Math.min(current + inc, target);
        el.textContent = (Number.isInteger(target)
          ? Math.round(current) : current.toFixed(1)) + suffix;
        if (current >= target) clearInterval(timer);
      }, 16);
    });
  }, 900);
})();

/* ── Button ripple effect ───────────────────────────────────── */
(function () {
  document.querySelectorAll('.btn-saffron, .btn-white, .btn-outline-saffron').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const ripple = document.createElement('span');
      const rect   = this.getBoundingClientRect();
      const size   = Math.max(rect.width, rect.height);
      ripple.className = 'ripple';
      Object.assign(ripple.style, {
        width:  size + 'px',
        height: size + 'px',
        left:   (e.clientX - rect.left - size / 2) + 'px',
        top:    (e.clientY - rect.top  - size / 2) + 'px',
      });
      this.appendChild(ripple);
      ripple.addEventListener('animationend', () => ripple.remove(), { once: true });
    });
  });
})();

/* ── Hero background parallax ───────────────────────────────── */
(function () {
  const bg    = document.querySelector('.hero-bg');
  const limit = window.innerHeight * 1.5;
  if (!bg) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY < limit) {
      bg.style.transform = `scale(1.04) translateY(${window.scrollY * 0.16}px)`;
    }
  }, { passive: true });
})();

/* ── Quote banner + CTA strip scroll-reveal ─────────────────── */
(function () {
  const pairs = [
    ['.quote-banner', 'q-visible',   0.3 ],
    ['.cta-strip',    'cta-visible', 0.2 ],
  ];
  pairs.forEach(([sel, cls, thresh]) => {
    const el = document.querySelector(sel);
    if (!el) return;
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.classList.add(cls);
        io.unobserve(e.target);
      });
    }, { threshold: thresh });
    io.observe(el);
  });
})();

/* ── Navbar shadow boost on deep scroll ─────────────────────── */
(function () {
  if (!nav) return;
  window.addEventListener('scroll', () => {
    const deep = window.scrollY > 200;
    nav.style.boxShadow = deep
      ? '0 8px 40px rgba(0,0,0,.14)'
      : '';
  }, { passive: true });
})();

/* ── Input label micro-feedback: border pulse on type ───────── */
(function () {
  document.querySelectorAll('.form-input').forEach(input => {
    let debounce;
    input.addEventListener('input', function () {
      this.classList.remove('input-typed');
      clearTimeout(debounce);
      debounce = setTimeout(() => this.classList.add('input-typed'), 120);
    });
  });
})();
