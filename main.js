/* ═══════════════════════════════════════════════════
   LUMIÈRE AI AGENT — JavaScript
   Particles · Animations · Interactions
═══════════════════════════════════════════════════ */

/* ─────────────────────────────────────────── */
/* 1. PARTICLE CANVAS                          */
/* ─────────────────────────────────────────── */
(function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, particles;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  function makeParticle() {
    return {
      x:  Math.random() * W,
      y:  Math.random() * H,
      r:  Math.random() * 1.5 + 0.3,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      alpha: Math.random() * 0.6 + 0.1,
      gold: Math.random() > 0.7,
    };
  }

  function init() {
    resize();
    const count = Math.min(Math.floor((W * H) / 12000), 120);
    particles = Array.from({ length: count }, makeParticle);
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      if (p.gold) {
        ctx.fillStyle = `rgba(201,165,90,${p.alpha})`;
      } else {
        ctx.fillStyle = `rgba(250,247,240,${p.alpha * 0.4})`;
      }
      ctx.fill();

      p.x += p.vx;
      p.y += p.vy;
      if (p.x < -10) p.x = W + 10;
      if (p.x > W + 10) p.x = -10;
      if (p.y < -10) p.y = H + 10;
      if (p.y > H + 10) p.y = -10;
    });

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          const a = (1 - dist / 120) * 0.12;
          ctx.strokeStyle = `rgba(201,165,90,${a})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', init);
  init();
  draw();
})();


/* ─────────────────────────────────────────── */
/* 2. NAVBAR                                   */
/* ─────────────────────────────────────────── */
(function initNavbar() {
  const nav = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });

  const hamburger = document.getElementById('hamburger');
  const navLinks  = document.querySelector('.nav-links');
  const navCta    = document.querySelector('.nav-cta');

  if (hamburger) {
    hamburger.addEventListener('click', () => {
      const open = hamburger.classList.toggle('open');
      if (navLinks) {
        navLinks.style.display = open ? 'flex' : '';
        if (open) {
          navLinks.style.cssText = `
            display: flex; flex-direction: column;
            position: fixed; top: 70px; left: 0; right: 0;
            background: rgba(14,12,9,0.97);
            padding: 2rem; gap: 1.5rem;
            border-bottom: 1px solid rgba(201,165,90,0.2);
            backdrop-filter: blur(20px);
            z-index: 999;
          `;
        } else {
          navLinks.style.cssText = '';
        }
      }
    });
  }
})();


/* ─────────────────────────────────────────── */
/* 3. REVEAL ON SCROLL                         */
/* ─────────────────────────────────────────── */
(function initReveal() {
  const els = document.querySelectorAll('.reveal-up');
  const pnodes = document.querySelectorAll('.pnode');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        observer.unobserve(e.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -60px 0px' });

  const pnodeObserver = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        pnodeObserver.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  els.forEach(el => observer.observe(el));
  pnodes.forEach(el => pnodeObserver.observe(el));
})();


/* ─────────────────────────────────────────── */
/* 4. COUNTER ANIMATION                        */
/* ─────────────────────────────────────────── */
(function initCounters() {
  const statEls = document.querySelectorAll('.stat-num[data-target]');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el     = e.target;
      const target = parseInt(el.dataset.target, 10);
      if (isNaN(target)) return;

      let start = 0;
      const duration = 1800;
      const startTime = performance.now();

      function step(now) {
        const elapsed  = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased    = 1 - Math.pow(1 - progress, 4);
        el.textContent = Math.floor(eased * target);
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target;
      }

      requestAnimationFrame(step);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });

  statEls.forEach(el => observer.observe(el));
})();


/* ─────────────────────────────────────────── */
/* 5. TYPEWRITER EFFECT                        */
/* ─────────────────────────────────────────── */
(function initTypewriter() {
  const el = document.getElementById('typing-text');
  if (!el) return;

  const text = `We want to sell premium handcrafted soy candles targeting urban women aged 25–40 in India. Brand name is 'Lumière'. Products are scented candles in luxury packaging — price range ₹599 to ₹2,499. We want to feel like a modern, minimal luxury brand, similar to Forest Essentials but for home fragrance.`;

  let i = 0;
  let started = false;

  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && !started) {
      started = true;
      observer.disconnect();
      function type() {
        if (i < text.length) {
          el.textContent += text[i++];
          setTimeout(type, 22);
        }
      }
      setTimeout(type, 600);
    }
  }, { threshold: 0.5 });

  observer.observe(el.closest('.brief-card') || el);
})();


/* ─────────────────────────────────────────── */
/* 6. PIPELINE NODE INTERACTIONS               */
/* ─────────────────────────────────────────── */
(function initPipeline() {
  const nodes = document.querySelectorAll('.pnode');

  nodes.forEach(node => {
    node.addEventListener('click', () => {
      const isActive = node.classList.contains('active');
      nodes.forEach(n => n.classList.remove('active'));
      if (!isActive) node.classList.add('active');
    });
  });

  // Auto-activate first node after a delay
  setTimeout(() => {
    if (nodes[0]) nodes[0].classList.add('active');
  }, 1200);

  // Animate through nodes sequentially on scroll
  let autoPlay = null;
  const section = document.getElementById('pipeline');
  if (!section) return;

  const sectionObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      if (autoPlay) return;
      let idx = 0;
      autoPlay = setInterval(() => {
        nodes.forEach(n => n.classList.remove('active'));
        nodes[idx].classList.add('active');
        idx = (idx + 1) % nodes.length;
      }, 2500);
    } else {
      if (autoPlay) { clearInterval(autoPlay); autoPlay = null; }
    }
  }, { threshold: 0.3 });

  sectionObserver.observe(section);
  nodes.forEach(n => {
    n.addEventListener('mouseenter', () => {
      if (autoPlay) { clearInterval(autoPlay); autoPlay = null; }
    });
  });
})();


/* ─────────────────────────────────────────── */
/* 7. TABS                                     */
/* ─────────────────────────────────────────── */
(function initTabs() {
  const buttons  = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      buttons.forEach(b => b.classList.remove('active'));
      contents.forEach(c => {
        c.classList.remove('active');
        c.style.opacity = '0';
      });

      btn.classList.add('active');
      const content = document.getElementById(`tab-${target}`);
      if (content) {
        content.classList.add('active');
        requestAnimationFrame(() => {
          content.style.transition = 'opacity 0.4s ease';
          content.style.opacity = '1';
        });

        // Trigger bar animations when research tab opens
        if (target === 'research') {
          setTimeout(() => {
            document.querySelectorAll('.pb-fill').forEach(bar => {
              const w = bar.style.width;
              bar.style.width = '0';
              requestAnimationFrame(() => {
                bar.style.transition = 'width 1s cubic-bezier(0.16, 1, 0.3, 1)';
                bar.style.width = w;
              });
            });
          }, 100);
        }
      }
    });
  });

  // Init first tab opacity
  const firstContent = document.querySelector('.tab-content.active');
  if (firstContent) firstContent.style.opacity = '1';
})();


/* ─────────────────────────────────────────── */
/* 8. SMOOTH HOVER GOLD GLOW ON CARDS          */
/* ─────────────────────────────────────────── */
(function initCardGlow() {
  const cards = document.querySelectorAll('.tech-card, .prod-card, .pnode');

  cards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width)  * 100;
      const y = ((e.clientY - rect.top)  / rect.height) * 100;
      card.style.setProperty('--glow-x', `${x}%`);
      card.style.setProperty('--glow-y', `${y}%`);
    });
  });
})();


/* ─────────────────────────────────────────── */
/* 9. HERO PARALLAX                            */
/* ─────────────────────────────────────────── */
(function initParallax() {
  const overlay = document.querySelector('.hero-image-overlay');
  if (!overlay) return;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    overlay.style.transform = `translateY(${y * 0.3}px)`;
  }, { passive: true });
})();


/* ─────────────────────────────────────────── */
/* 10. ACTIVE NAV LINK HIGHLIGHT               */
/* ─────────────────────────────────────────── */
(function initActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-links a');

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(s => {
      if (window.scrollY >= s.offsetTop - 120) current = s.id;
    });
    navLinks.forEach(a => {
      a.classList.remove('active-nav');
      if (a.getAttribute('href') === `#${current}`) {
        a.style.color = 'var(--gold)';
      } else {
        a.style.color = '';
      }
    });
  }, { passive: true });
})();


/* ─────────────────────────────────────────── */
/* 11. PRICING BARS INITIAL STATE              */
/* ─────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  // Cache widths and set to 0 initially for animation
  document.querySelectorAll('.pb-fill').forEach(bar => {
    bar.dataset.width = bar.style.width;
  });
});
