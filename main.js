/* ═══════════════════════════════════════════════
   LUMIÈRE AI — Full App JavaScript
   Views · Form · SSE Streaming · Results
═══════════════════════════════════════════════ */

// ── State ────────────────────────────────────────
let currentStep  = 1;
let selectedVibes = [];
let currentJobId  = null;
let currentResult = null;

// ── View Management ───────────────────────────────
function showView(id) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  const el = document.getElementById('view-' + id);
  if (el) { el.classList.add('active'); window.scrollTo(0, 0); }
}

// ── Particles (Landing hero) ──────────────────────
(function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, pts;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  function makePt() {
    return {
      x: Math.random() * W, y: Math.random() * H,
      r: Math.random() * 1.2 + 0.3,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      a: Math.random() * 0.5 + 0.08,
      gold: Math.random() > 0.65,
    };
  }
  function init() {
    resize();
    const n = Math.min(Math.floor(W * H / 10000), 130);
    pts = Array.from({ length: n }, makePt);
  }
  function draw() {
    ctx.clearRect(0, 0, W, H);
    for (let i = 0; i < pts.length; i++) {
      const p = pts[i];
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.gold ? `rgba(201,165,90,${p.a})` : `rgba(250,247,240,${p.a * 0.35})`;
      ctx.fill();
      p.x += p.vx; p.y += p.vy;
      if (p.x < -5) p.x = W + 5;
      if (p.x > W + 5) p.x = -5;
      if (p.y < -5) p.y = H + 5;
      if (p.y > H + 5) p.y = -5;
      for (let j = i + 1; j < pts.length; j++) {
        const q = pts[j];
        const d = Math.hypot(p.x - q.x, p.y - q.y);
        if (d < 110) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
          ctx.strokeStyle = `rgba(201,165,90,${(1 - d / 110) * 0.1})`;
          ctx.lineWidth = 0.5; ctx.stroke();
        }
      }
    }
    requestAnimationFrame(draw);
  }
  window.addEventListener('resize', init);
  init(); draw();
})();

// ── Form Step Navigation ──────────────────────────
function nextStep() {
  if (!validateStep(currentStep)) return;

  const cur  = document.getElementById('sp-' + currentStep);
  const next = document.getElementById('sp-' + (currentStep + 1));
  if (!next) return;

  cur.classList.remove('active');
  next.classList.add('active');

  // Mark step indicator done
  const siCur  = document.getElementById('si-' + currentStep);
  const siNext = document.getElementById('si-' + (currentStep + 1));
  const slCur  = document.getElementById('sl-' + currentStep);
  if (siCur)  { siCur.classList.remove('active'); siCur.classList.add('done'); }
  if (siNext) { siNext.classList.add('active'); }
  if (slCur)  { slCur.classList.add('done'); }

  currentStep++;
  updatePreview();
}

function prevStep() {
  if (currentStep <= 1) { showView('landing'); return; }

  const cur  = document.getElementById('sp-' + currentStep);
  const prev = document.getElementById('sp-' + (currentStep - 1));
  cur.classList.remove('active');
  prev.classList.add('active');

  const siCur  = document.getElementById('si-' + currentStep);
  const siPrev = document.getElementById('si-' + (currentStep - 1));
  const slPrev = document.getElementById('sl-' + (currentStep - 1));
  if (siCur)  { siCur.classList.remove('active'); }
  if (siPrev) { siPrev.classList.remove('done'); siPrev.classList.add('active'); }
  if (slPrev) { slPrev.classList.remove('done'); }

  currentStep--;
}

function validateStep(step) {
  if (step === 1) {
    const name = document.getElementById('f-brand-name').value.trim();
    const prod = document.getElementById('f-product').value.trim();
    if (!name) { shake('f-brand-name'); showToast('Please enter your brand name'); return false; }
    if (!prod) { shake('f-product'); showToast('Please enter what you sell'); return false; }
  }
  if (step === 2) {
    const aud = document.getElementById('f-audience').value.trim();
    const loc = document.getElementById('f-location').value.trim();
    if (!aud) { shake('f-audience'); showToast('Please describe your target customer'); return false; }
    if (!loc) { shake('f-location'); showToast('Please enter your target market/location'); return false; }
  }
  return true;
}

function shake(fieldId) {
  const el = document.getElementById(fieldId);
  if (!el) return;
  el.style.animation = 'shake 0.4s ease';
  el.addEventListener('animationend', () => { el.style.animation = ''; }, { once: true });
}

// Add shake keyframes
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
@keyframes shake {
  0%,100% { transform: translateX(0); }
  20%      { transform: translateX(-6px); }
  60%      { transform: translateX(6px); }
}`;
document.head.appendChild(shakeStyle);

// ── Vibe Chips ────────────────────────────────────
function toggleVibe(el) {
  const vibe = el.dataset.vibe;
  if (el.classList.contains('selected')) {
    el.classList.remove('selected');
    selectedVibes = selectedVibes.filter(v => v !== vibe);
  } else {
    el.classList.add('selected');
    selectedVibes.push(vibe);
  }
  updatePreview();
}

// ── Brief Preview ─────────────────────────────────
function updatePreview() {
  const name    = (document.getElementById('f-brand-name')?.value || '').trim();
  const product = (document.getElementById('f-product')?.value || '').trim();
  const desc    = (document.getElementById('f-product-desc')?.value || '').trim();
  const audience = (document.getElementById('f-audience')?.value || '').trim();
  const ageFrom  = (document.getElementById('f-age-from')?.value || '').trim();
  const ageTo    = (document.getElementById('f-age-to')?.value || '').trim();
  const location = (document.getElementById('f-location')?.value || '').trim();
  const currency = (document.getElementById('f-currency')?.value || '₹');
  const priceMin = (document.getElementById('f-price-min')?.value || '').trim();
  const priceMax = (document.getElementById('f-price-max')?.value || '').trim();
  const competitors = (document.getElementById('f-competitors')?.value || '').trim();
  const extra    = (document.getElementById('f-extra')?.value || '').trim();

  const el = document.getElementById('brief-preview-text');
  if (!el) return;

  if (!name && !product && !audience) {
    el.className = 'bpc-text empty';
    el.textContent = 'Fill in the form to see your AI brief preview...';
    return;
  }

  let brief = '';
  if (product || audience) {
    brief += `We want to sell ${product || '[product]'}`;
    if (audience) brief += ` targeting ${audience}`;
    if (ageFrom && ageTo) brief += ` aged ${ageFrom}–${ageTo}`;
    if (location) brief += ` in ${location}`;
    brief += '.';
  }
  if (name) brief += ` Brand name is '${name}'.`;
  if (desc) brief += ` ${desc}.`;
  if (priceMin && priceMax) brief += ` Price range ${currency}${priceMin} to ${currency}${priceMax}.`;
  if (selectedVibes.length > 0) {
    brief += ` We want to feel ${selectedVibes.join(', ').toLowerCase()}.`;
  }
  if (competitors) brief += ` Similar to ${competitors}.`;
  if (extra) brief += ` ${extra}`;

  el.className = 'bpc-text';
  el.textContent = brief.trim();
}

// ── Build & Generate Brief ────────────────────────
function buildBrief() {
  const name     = document.getElementById('f-brand-name')?.value.trim() || '';
  const product  = document.getElementById('f-product')?.value.trim() || '';
  const desc     = document.getElementById('f-product-desc')?.value.trim() || '';
  const audience = document.getElementById('f-audience')?.value.trim() || '';
  const ageFrom  = document.getElementById('f-age-from')?.value.trim() || '';
  const ageTo    = document.getElementById('f-age-to')?.value.trim() || '';
  const location = document.getElementById('f-location')?.value.trim() || '';
  const currency = document.getElementById('f-currency')?.value || '₹';
  const priceMin = document.getElementById('f-price-min')?.value.trim() || '';
  const priceMax = document.getElementById('f-price-max')?.value.trim() || '';
  const competitors = document.getElementById('f-competitors')?.value.trim() || '';
  const extra    = document.getElementById('f-extra')?.value.trim() || '';

  let brief = `We want to sell ${product} targeting ${audience}`;
  if (ageFrom && ageTo) brief += ` aged ${ageFrom}-${ageTo}`;
  if (location)         brief += ` in ${location}`;
  brief += `.`;
  if (name)             brief += ` Brand name is '${name}'.`;
  if (desc)             brief += ` ${desc}.`;
  if (priceMin && priceMax) brief += ` Price range ${currency}${priceMin} to ${currency}${priceMax}.`;
  if (selectedVibes.length) brief += ` We want to feel ${selectedVibes.join(', ').toLowerCase()}.`;
  if (competitors)      brief += ` Similar to ${competitors}.`;
  if (extra)            brief += ` ${extra}`;

  return brief.trim();
}

// ── Submit Form ───────────────────────────────────
async function submitForm() {
  const brief = buildBrief();
  if (!brief || brief.length < 20) {
    showToast('Please fill in your brand details first.'); return;
  }

  const payload = {
    brief,
    GROQ_API_KEY:           document.getElementById('f-groq')?.value.trim()       || '',
    TAVILY_API_KEY:         document.getElementById('f-tavily')?.value.trim()     || '',
    SHOPIFY_STORE_URL:      document.getElementById('f-shop-url')?.value.trim()   || '',
    SHOPIFY_ACCESS_TOKEN:   document.getElementById('f-shop-token')?.value.trim() || '',
  };

  // Switch to processing view
  showView('processing');
  resetProcessingView();

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok || !data.job_id) {
      throw new Error(data.error || 'Failed to start agent.');
    }
    currentJobId = data.job_id;
    listenToSSE(currentJobId);
  } catch (err) {
    addTermLine(`ERROR: ${err.message}`, 'red');
    setTermBadge('ERROR', 'error');
  }
}

// ── SSE Client ────────────────────────────────────
function listenToSSE(jobId) {
  const evtSrc = new EventSource(`/api/stream/${jobId}`);

  evtSrc.onmessage = (e) => {
    const msg = JSON.parse(e.data);

    if (msg.type === 'ping') return;

    if (msg.type === 'log') {
      handleLogMessage(msg.msg);
    }

    if (msg.type === 'done') {
      currentResult = msg.result;
      onAgentDone(msg.result);
      evtSrc.close();
    }

    if (msg.type === 'error') {
      onAgentError(msg.msg);
      evtSrc.close();
    }

    if (msg.type === 'end') {
      evtSrc.close();
    }
  };

  evtSrc.onerror = () => {
    addTermLine('Connection lost. Check if the server is running.', 'red');
    setTermBadge('DISCONNECTED', 'error');
    evtSrc.close();
  };
}

// ── Log Processing ────────────────────────────────
const nodePatterns = [
  { pattern: /Node 1.*Research/i,     node: 1, progress: 10 },
  { pattern: /Research.*searching/i,  node: 1, progress: 20 },
  { pattern: /Searching competitor/i, node: 1, progress: 25 },
  { pattern: /Searching product/i,    node: 1, progress: 30 },
  { pattern: /Searching pricing/i,    node: 1, progress: 35 },
  { pattern: /Scraping/i,             node: 1, progress: 40 },
  { pattern: /Research complete/i,    node: 1, progress: 50, done: true },
  { pattern: /Node 2.*Strategy/i,     node: 2, progress: 52 },
  { pattern: /Strategy.*building/i,   node: 2, progress: 58 },
  { pattern: /Strategy complete/i,    node: 2, progress: 65, done: true },
  { pattern: /Node 3.*Content/i,      node: 3, progress: 67 },
  { pattern: /Generating homepage/i,  node: 3, progress: 72 },
  { pattern: /Writing.*product/i,     node: 3, progress: 78 },
  { pattern: /Content complete/i,     node: 3, progress: 85, done: true },
  { pattern: /Node 4.*Shopify/i,      node: 4, progress: 87 },
  { pattern: /Creating collection/i,  node: 4, progress: 90 },
  { pattern: /Creating product/i,     node: 4, progress: 93 },
  { pattern: /Shopify.*complete/i,    node: 4, progress: 100, done: true },
];

let activeNode = 0;

function handleLogMessage(msg) {
  // Determine line style
  let cls = '';
  if (msg.includes('✓') || msg.includes('complete') || msg.includes('created')) cls = 'green';
  else if (msg.includes('Node') || msg.includes('[Node')) cls = 'gold';
  else if (msg.includes('ERROR') || msg.includes('failed') || msg.includes('✗')) cls = 'red';

  addTermLine(msg, cls);

  // Check node transitions
  for (const pat of nodePatterns) {
    if (pat.pattern.test(msg)) {
      if (pat.node !== activeNode) {
        if (activeNode > 0) setNodeStatus(activeNode, 'done');
        setNodeStatus(pat.node, 'active');
        activeNode = pat.node;
        updateSubtitle(pat.node);
      }
      if (pat.done) {
        setNodeStatus(pat.node, 'done');
        setConnectorDone(pat.node);
      }
      setProgress(pat.progress);
      break;
    }
  }
}

function updateSubtitle(node) {
  const labels = ['', 'Searching market & competitors...', 'Building brand strategy...', 'Generating store content...', 'Deploying to Shopify...'];
  const el = document.getElementById('proc-subtitle');
  if (el) el.textContent = labels[node] || '';
}

// ── Processing View Helpers ───────────────────────
function resetProcessingView() {
  activeNode = 0;
  setProgress(5);
  [1,2,3,4].forEach(n => {
    const node = document.getElementById('proc-node-' + n);
    if (node) {
      node.classList.remove('active', 'done', 'error');
      node.querySelector('.pn-status').textContent = 'Waiting...';
    }
  });
  [1,2,3].forEach(n => {
    const conn = document.getElementById('pnc-' + n);
    if (conn) conn.classList.remove('done');
  });
  const body = document.getElementById('term-body');
  if (body) body.innerHTML = '<div class="term-line dim">Agent starting...</div>';
  setTermBadge('● RUNNING', 'running');
  document.getElementById('proc-subtitle').textContent = 'Initialising agent pipeline...';
}

function setProgress(pct) {
  const bar = document.getElementById('proc-progress-fill');
  if (bar) bar.style.width = pct + '%';
}

function setNodeStatus(node, status) {
  const el = document.getElementById('proc-node-' + node);
  if (!el) return;
  el.classList.remove('active', 'done', 'error');
  el.classList.add(status);
  const statusLabels = { active: 'Running...', done: '✓ Done', error: '✗ Error' };
  el.querySelector('.pn-status').textContent = statusLabels[status] || '';
}

function setConnectorDone(node) {
  const conn = document.getElementById('pnc-' + node);
  if (conn) conn.classList.add('done');
}

function addTermLine(text, cls = '') {
  const body = document.getElementById('term-body');
  if (!body) return;
  const div = document.createElement('div');
  div.className = 'term-line' + (cls ? ' ' + cls : '');
  div.textContent = text;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;

  // Keep max ~200 lines
  const lines = body.querySelectorAll('.term-line');
  if (lines.length > 200) lines[0].remove();
}

function setTermBadge(text, cls) {
  const el = document.getElementById('term-badge');
  if (!el) return;
  el.textContent = text;
  el.className = 'term-badge ' + (cls || '');
}

// ── Agent Done ────────────────────────────────────
function onAgentDone(result) {
  setProgress(100);
  setNodeStatus(4, 'done');
  setConnectorDone(3);
  setTermBadge('✓ COMPLETE', 'done');
  addTermLine('═══ All done! Redirecting to results... ═══', 'green');
  document.getElementById('proc-subtitle').textContent = 'Store built! Preparing results...';
  document.getElementById('proc-spinner')?.remove?.();

  setTimeout(() => {
    showView('results');
    renderResults(result);
  }, 1800);
}

function onAgentError(msg) {
  setNodeStatus(activeNode || 1, 'error');
  setTermBadge('✗ ERROR', 'error');
  addTermLine('ERROR: ' + msg, 'red');
  setProgress(0);
  document.getElementById('proc-subtitle').textContent = 'An error occurred. See log above.';
}

// ── Results Rendering ─────────────────────────────
function renderResults(result) {
  const shopify = result?.shopify || {};
  const research = result?.research || {};
  const strategy = result?.strategy || {};
  const assets = result?.store_assets || {};

  // Banner
  const deployed = shopify.status === 'deployed';
  document.getElementById('rb-icon').textContent  = deployed ? '🚀' : '✅';
  document.getElementById('rb-title').textContent =
    deployed ? 'Store Deployed to Shopify!' : 'Store Assets Generated!';
  document.getElementById('rb-sub').textContent   = deployed
    ? `Live at: ${shopify.store_url || '—'}`
    : 'All assets generated. Add Shopify credentials to deploy live.';

  // OVERVIEW
  const products = assets.products || [];
  const ovGrid = document.getElementById('r-overview-grid');
  ovGrid.innerHTML = '';
  const ovItems = [
    { title: 'Brand',        value: assets.brand_name || result?.strategy?.brand_name || '—', sub: 'AI-generated brand identity' },
    { title: 'Tagline',      value: strategy.tagline || '—', sub: 'Brand positioning line' },
    { title: 'Products',     value: products.length, sub: 'Created & deployed to Shopify' },
    { title: 'Competitors',  value: (research.competitors || []).length, sub: 'Identified by research agent' },
    { title: 'Deploy Status', value: deployed ? 'Live 🟢' : 'JSON Export 📦', sub: shopify.store_url || shopify.file || '—' },
    { title: 'Pricing Tier', value: 'Premium', sub: `Entry ₹${research.pricing_analysis?.recommended_entry_price || '—'}` },
  ];
  ovItems.forEach(item => {
    const card = document.createElement('div');
    card.className = 'r-ov-card';
    card.innerHTML = `
      <div class="r-ov-card-title">${item.title}</div>
      <div class="r-ov-card-value">${item.value}</div>
      <div class="r-ov-card-sub">${item.sub}</div>`;
    ovGrid.appendChild(card);
  });

  // PRODUCTS
  const prodGrid = document.getElementById('r-products-grid');
  prodGrid.innerHTML = '';
  if (products.length === 0) {
    prodGrid.innerHTML = '<div class="r-ov-loading">No products found in output.</div>';
  } else {
    products.forEach((p, i) => {
      const badges = ['HERO', 'ENTRY', 'GIFT'];
      const card = document.createElement('div');
      card.className = 'r-prod-card';
      const tags = (p.shopify_tags || []).slice(0, 4).map(t =>
        `<span class="r-prod-tag">${t}</span>`).join('');
      const price = p.price || (p.variants && p.variants[0]?.price) || '—';
      card.innerHTML = `
        <div class="r-prod-top">
          <div class="r-prod-badge">${badges[i] || 'PRODUCT'}</div>
          <div class="r-prod-price">₹${price}</div>
        </div>
        <div class="r-prod-body">
          <div class="r-prod-name">${p.title || '—'}</div>
          <div class="r-prod-desc">${(p.description || p.subtitle || '').slice(0, 180)}${(p.description || '').length > 180 ? '...' : ''}</div>
          <div class="r-prod-tags">${tags}</div>
        </div>`;
      prodGrid.appendChild(card);
    });
  }

  // RESEARCH
  const resDiv = document.getElementById('r-research-content');
  resDiv.innerHTML = '';
  const competitors = research.competitors || [];
  if (competitors.length) {
    let html = `<div class="r-research-section">
      <div class="r-sec-title">Competitors Identified (${competitors.length})</div>
      <div class="r-comp-list">`;
    competitors.slice(0,6).forEach((c, i) => {
      html += `<div class="r-comp-item">
        <div class="r-comp-rank">${i+1}</div>
        <div>
          <div class="r-comp-name">${c.name || '—'}</div>
          <div class="r-comp-range">${c.price_range || ''}</div>
          <div class="r-comp-pos">${(c.positioning || '').slice(0, 100)}</div>
        </div>
      </div>`;
    });
    html += `</div></div>`;
    resDiv.innerHTML += html;
  }
  const scents = (research.product_trends?.top_scents || []);
  if (scents.length) {
    resDiv.innerHTML += `<div class="r-research-section">
      <div class="r-sec-title">Top Trending Scents</div>
      <div class="r-trend-tags">${scents.map(s => `<span class="r-trend-tag">${s}</span>`).join('')}</div>
    </div>`;
  }
  const pricing = research.pricing_analysis || {};
  if (pricing.recommended_entry_price) {
    resDiv.innerHTML += `<div class="r-research-section">
      <div class="r-sec-title">Pricing Recommendation</div>
      <div style="display:flex;gap:1rem;flex-wrap:wrap">
        <div class="r-ov-card" style="flex:1;min-width:150px">
          <div class="r-ov-card-title">Entry</div>
          <div class="r-ov-card-value">₹${pricing.recommended_entry_price}</div>
        </div>
        <div class="r-ov-card" style="flex:1;min-width:150px">
          <div class="r-ov-card-title">Hero</div>
          <div class="r-ov-card-value">₹${pricing.recommended_hero_price || '—'}</div>
        </div>
        <div class="r-ov-card" style="flex:1;min-width:150px">
          <div class="r-ov-card-title">Gift Set</div>
          <div class="r-ov-card-value">₹${pricing.recommended_gift_price || '—'}</div>
        </div>
      </div>
      <p style="font-size:0.8rem;color:var(--muted);margin-top:0.75rem">${pricing.launch_strategy || ''}</p>
    </div>`;
  }

  // STRATEGY
  const stratDiv = document.getElementById('r-strategy-content');
  stratDiv.innerHTML = '';
  const palette = strategy.color_palette || {};
  if (Object.keys(palette).length) {
    const colors = [
      { hex: palette.primary,    name: 'Primary' },
      { hex: palette.secondary,  name: 'Gold' },
      { hex: palette.accent,     name: 'Accent' },
      { hex: palette.background, name: 'Background', light: true },
      { hex: palette.muted,      name: 'Muted', light: true },
    ].filter(c => c.hex);

    stratDiv.innerHTML += `<div class="r-research-section">
      <div class="r-sec-title">Color Palette — ${palette.palette_name || ''}</div>
      <div class="r-palette">
        ${colors.map(c => `
          <div class="r-pal-swatch${c.light ? ' light' : ''}" style="background:${c.hex}">
            <div class="r-pal-hex">${c.hex}</div>
            <div class="r-pal-name">${c.name}</div>
          </div>`).join('')}
      </div>
    </div>`;
  }
  const typo = strategy.typography || {};
  if (typo.display) {
    stratDiv.innerHTML += `<div class="r-research-section">
      <div class="r-sec-title">Typography</div>
      <div style="display:flex;gap:1rem;flex-wrap:wrap">
        <div class="r-ov-card" style="flex:1">
          <div class="r-ov-card-title">Display</div>
          <div class="r-ov-card-value" style="font-family:'Cormorant Garamond',serif;font-style:italic">${typo.display.name}</div>
          <div class="r-ov-card-sub">${typo.display.use || ''}</div>
        </div>
        <div class="r-ov-card" style="flex:1">
          <div class="r-ov-card-title">Body</div>
          <div class="r-ov-card-value">${typo.body?.name || '—'}</div>
          <div class="r-ov-card-sub">${typo.body?.use || ''}</div>
        </div>
      </div>
    </div>`;
  }
  const persona = strategy.target_persona || {};
  if (persona.name) {
    stratDiv.innerHTML += `<div class="r-research-section">
      <div class="r-sec-title">Target Persona</div>
      <div class="r-ov-card">
        <div class="r-ov-card-value">${persona.name}, ${persona.age_range}</div>
        <div class="r-ov-card-sub" style="margin-top:0.4rem">${persona.lifestyle || ''}</div>
        <div class="r-ov-card-sub" style="margin-top:0.4rem;color:var(--gold)">"${persona.desires || ''}"</div>
      </div>
    </div>`;
  }
}

// ── Tab Switching ─────────────────────────────────
function switchResultTab(btn) {
  document.querySelectorAll('.rtab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.rtab-content').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  const tab = document.getElementById(btn.dataset.tab);
  if (tab) tab.classList.add('active');
}

// ── Toast Notification ────────────────────────────
function showToast(msg) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.style.cssText = `
      position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%) translateY(20px);
      background: var(--card2, #201D17); border: 1px solid rgba(201,165,90,0.3);
      color: var(--gold, #C9A55A); padding: 0.75rem 1.5rem; border-radius: 4px;
      font-size: 0.82rem; z-index: 9999; opacity: 0;
      transition: all 0.3s ease; pointer-events: none;
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = '1';
  toast.style.transform = 'translateX(-50%) translateY(0)';
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(-50%) translateY(20px)';
  }, 3000);
}

// ── Nav Scroll Effect ─────────────────────────────
window.addEventListener('scroll', () => {
  document.getElementById('navbar').style.boxShadow =
    window.scrollY > 20 ? '0 4px 40px rgba(0,0,0,0.4)' : '';
}, { passive: true });

// ── Init ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updatePreview();
});
