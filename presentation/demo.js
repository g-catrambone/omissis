/* The demo slide: recorded runs of the pipeline, replayed from demo-data.js.
   Nothing here calls a model: every masked text and reply was produced by `omissis`
   in replay mode from results/cache and exported once (export_demo.py).

   Four steps, driven by the clicker (hidden fragments) or by clicking the track:
   1 detect and mask: the values flip into surrogates one by one while the vault fills;
   2 send: the reply of the cloud model streams in, as it was recorded;
   3 restore: the surrogates flip back to the real values; a log of every outcome;
   4 a calculation request that the feasibility check refuses.
   Hovering a value, a surrogate or a vault row links all three. */
(function () {
  const D = window.DEMO;
  const SCENARIO = {
    iban_change: 'IBAN change', card_dispute: 'Card dispute', account_closure: 'Closure',
    sick_leave: 'Sick leave', transfer_request: 'Transfer',
  };
  const STEPS = [
    { t: 'Detect & mask', where: 'local' },
    { t: 'Send to the cloud', where: 'cloud' },
    { t: 'Restore', where: 'local' },
    { t: 'A request we refuse', where: 'local' },
  ];
  const WHERE = { local: 'This machine', cloud: 'Cloud model' };
  const CLS = { direct: 'direct identifier', quasi: 'quasi-identifier', special: 'special category' };
  const PH = /^\[[A-Z]+(?:_[A-Z]+)*_\d+(?:_[MF])?\]$/;
  const PH_G = /\[[A-Z]+(?:_[A-Z]+)*_\d+(?:_[MF])?\]/g;
  const PRINT = /print-pdf/.test(window.location.search);

  const state = { fx: 'fx-bank-02', det: 'D4', strat: 'R1', step: 1 };
  let root = null;
  let ticket = 0; // bumped on every render: running animations check it and stop

  const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const md = (html) => html.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
  const fixture = () => D.fixtures.find((f) => f.id === state.fx);
  const run = () => fixture().runs[`${state.det}+${state.strat}`];
  const $ = (sel) => root.querySelector(sel);

  /* ---------- alignment: which text each surrogate stands for ---------- */

  /* original text and masked text, walked together along the detected spans */
  function alignOriginal(f, r) {
    const t = f.text, m = r.masked;
    const sp = [...r.spans].sort((a, b) => a.start - b.start);
    const surs = [...new Set(r.disclosure.map((d) => d.surrogate))].sort((a, b) => b.length - a.length);
    const out = [];
    let po = 0, pm = 0;
    for (let i = 0; i < sp.length; i++) {
      const x = sp[i];
      if (x.start < po) return null;
      const seg = t.slice(po, x.start);
      if (m.slice(pm, pm + seg.length) !== seg) return null;
      if (seg) out.push({ plain: seg });
      pm += seg.length;
      let hit = surs.find((s) => m.startsWith(s, pm));
      if (!hit) {
        // a form of a surrogate (an R2 surname alone): up to the next original text
        const last = i + 1 === sp.length;
        const next = t.slice(x.end, last ? t.length : sp[i + 1].start);
        const idx = next ? m.indexOf(next, pm) : last ? m.length : -1;
        if (idx <= pm) return null;
        hit = m.slice(pm, idx);
      }
      const d = r.disclosure.find((e) => e.surrogate === hit) || r.disclosure.find((e) => e.surrogate.includes(hit) && e.type === x.type);
      out.push({ v: t.slice(x.start, x.end), p: hit, cls: x.cls, type: x.type, source: x.source, key: d ? d.surrogate : hit });
      pm += hit.length;
      po = x.end;
    }
    if (t.slice(po) !== m.slice(pm)) return null;
    if (t.slice(po)) out.push({ plain: t.slice(po) });
    return out;
  }

  /* the reply as it came back and the restored reply, walked together */
  function alignReply(r) {
    const raw = r.raw_reply, res = r.restored;
    const byS = Object.fromEntries(r.disclosure.map((d) => [d.surrogate, d]));
    const all = [...new Set([...Object.keys(byS), ...(raw.match(PH_G) || [])])].sort((a, b) => b.length - a.length);
    const pieces = [];
    if (all.length) {
      const re = new RegExp(all.map(reEsc).join('|'), 'g');
      let pos = 0, m;
      while ((m = re.exec(raw))) {
        if (m.index > pos) pieces.push({ plain: raw.slice(pos, m.index) });
        pieces.push({ p: m[0] });
        pos = m.index + m[0].length;
      }
      if (pos < raw.length) pieces.push({ plain: raw.slice(pos) });
    } else pieces.push({ plain: raw });
    let pr = 0;
    for (let i = 0; i < pieces.length; i++) {
      const pc = pieces[i];
      if (pc.plain !== undefined) {
        if (!res.startsWith(pc.plain, pr)) return null;
        pr += pc.plain.length;
        continue;
      }
      const d = byS[pc.p], nxt = pieces[i + 1];
      let end;
      if (!nxt) end = res.length;
      else if (nxt.plain !== undefined) end = res.indexOf(nxt.plain, pr);
      else {
        const guess = d ? d.value : pc.p;
        end = res.startsWith(guess, pr) ? pr + guess.length : res.startsWith(pc.p, pr) ? pr + pc.p.length : -1;
      }
      if (end < pr) return null;
      pc.v = res.slice(pr, end);
      pr = end;
      pc.cls = d ? d.cls : 'direct';
      pc.type = d ? d.type : null;
      pc.source = d ? d.source : null;
      pc.key = d ? d.surrogate : pc.p;
      pc.bad = !d || pc.v === pc.p;
    }
    return pr === res.length ? pieces : null;
  }

  /* fallback when the model rewrote a surrogate (an R2 first name alone, an amount in
     another format) and restoration matched it after normalising: diff the reply
     against the restored reply; each changed stretch is one restored value */
  function alignDiff(r) {
    const a = r.raw_reply, b = r.restored, K = 10, MAX = 200;
    const isW = (c) => !!c && /[\p{L}\p{N}]/u.test(c);
    const pieces = [];
    let i = 0, j = 0, plain = '';
    while (i < a.length || j < b.length) {
      if (i < a.length && j < b.length && a[i] === b[j]) { plain += a[i]; i++; j++; continue; }
      let back = 0; // start the stretch at the beginning of the word
      while (back < plain.length && isW(plain[plain.length - back - 1])) back++;
      const i0 = i - back, j0 = j - back;
      plain = plain.slice(0, plain.length - back);
      let found = null;
      for (let i2 = i; i2 <= a.length && i2 - i <= MAX; i2++) {
        const anchor = a.slice(i2, i2 + K);
        if (!anchor) { found = [a.length, b.length]; break; }
        const j2 = b.indexOf(anchor, j);
        if (j2 >= 0 && j2 - j <= MAX) { found = [i2, j2]; break; }
      }
      if (!found) return null;
      let [i2, j2] = found;
      while (i2 < a.length && j2 < b.length && a[i2] === b[j2] && isW(a[i2]) && isW(a[i2 - 1])) { i2++; j2++; }
      if (plain) pieces.push({ plain });
      plain = '';
      pieces.push({ p: a.slice(i0, i2), v: b.slice(j0, j2) });
      i = i2;
      j = j2;
    }
    if (plain) pieces.push({ plain });
    if (pieces.map((x) => (x.plain !== undefined ? x.plain : x.p)).join('') !== a) return null;
    if (pieces.map((x) => (x.plain !== undefined ? x.plain : x.v)).join('') !== b) return null;
    // describe each changed stretch; placeholders left unchanged in the plain text are
    // the ones restoration reported (made up by the model, or not resolved)
    const out = [];
    for (const x of pieces) {
      if (x.plain === undefined) {
        const d = r.disclosure.find((e) => e.surrogate === x.p || x.p.includes(e.surrogate) || e.surrogate.includes(x.p.trim()))
          || r.disclosure.find((e) => e.value && (x.v.includes(e.value) || e.value.includes(x.v.trim())));
        out.push({ ...x, cls: d ? d.cls : 'quasi', type: d ? d.type : null, source: d ? d.source : null, key: d ? d.surrogate : x.p, bad: false });
        continue;
      }
      let pos = 0, m;
      const re = new RegExp(PH_G.source, 'g');
      while ((m = re.exec(x.plain))) {
        if (m.index > pos) out.push({ plain: x.plain.slice(pos, m.index) });
        out.push({ p: m[0], v: m[0], cls: 'direct', type: null, source: null, key: m[0], bad: true });
        pos = m.index + m[0].length;
      }
      if (pos < x.plain.length) out.push({ plain: x.plain.slice(pos) });
    }
    return out;
  }

  /* ---------- rendering ---------- */

  function tokens(pieces, masked, isReply) {
    let i = 0;
    const html = pieces.map((x) => {
      if (x.plain !== undefined) return esc(x.plain);
      const kind = x.bad ? 'bad' : PH.test(x.p) ? 'ph' : 'fake';
      return `<span class="tk ${x.cls} ${kind}${masked ? ' on' : ''}" data-k="${esc(x.key)}" data-i="${i++}"`
        + ` data-type="${esc(x.type || '')}" data-src="${esc(x.source || '')}" data-v="${esc(x.v)}" data-p="${esc(x.p)}">`
        + `<span class="v">${esc(x.v)}</span><span class="p">${esc(x.p)}</span></span>`;
    }).join('');
    return isReply ? md(html) : html;
  }

  function counts(r) {
    const c = { direct: 0, quasi: 0, special: 0 };
    for (const d of r.disclosure) c[d.cls] = (c[d.cls] || 0) + 1;
    return `<span class="chip direct">${c.direct} direct</span><span class="chip quasi">${c.quasi} quasi</span><span class="chip special">${c.special} special</span>`;
  }

  function panel(where, title, body, foot, toggle) {
    return `<div class="dm-panel ${where}">
      <div class="dm-head"><span class="ttl">${title}</span><span class="where ${where}">${WHERE[where]}</span>${toggle || ''}</div>
      <div class="dm-body">${body}</div>${foot ? `<div class="dm-foot">${foot}</div>` : ''}</div>`;
  }
  function side(where, title, body, foot) {
    return `<div class="dm-panel side ${where}">
      <div class="dm-head"><span class="ttl">${title}</span></div>
      <div class="dm-sbody">${body}</div>${foot ? `<div class="dm-foot">${foot}</div>` : ''}</div>`;
  }
  const toggle = (a, b) => `<div class="dm-toggle"><button data-view="a">${a}</button><button data-view="b">${b}</button></div>`;

  function vault(r, shown) {
    const seen = new Set();
    return `<div class="vault">${r.disclosure.filter((d) => !seen.has(d.surrogate) && seen.add(d.surrogate)).map((d) =>
      `<div class="vr ${d.cls}${shown ? ' in' : ''}" data-k="${esc(d.surrogate)}" data-type="${esc(d.type)}" data-src="${esc(d.source)}" data-v="${esc(d.value)}" data-p="${esc(d.surrogate)}">`
      + `<span class="vp ${PH.test(d.surrogate) ? 'ph' : 'fake'}">${esc(d.surrogate)}</span><span class="ar">⇄</span><span class="vv">${esc(d.value)}</span></div>`).join('')}</div>`;
  }

  function stepOne(f, r) {
    const pieces = alignOriginal(f, r);
    const body = pieces ? tokens(pieces, false, false) : esc(f.text);
    const main = panel('local', `Your email · ${esc(f.id)} <span class="syn">synthetic</span>`, body,
      `<span>${counts(r)}</span><span class="push">Nothing has left this machine yet.</span>`, toggle('Original', 'As it will be sent'));
    const n = new Set(r.disclosure.map((d) => d.surrogate)).size;
    const aside = side('local', 'The vault', `<p class="dm-note">Each value and the surrogate that replaces it. Kept in memory on this machine, erased after the reply.</p>${vault(r, false)}`,
      `<span><b class="cnt">0</b> of ${n} values replaced</span>`);
    return main + aside;
  }

  function stepTwo(f, r) {
    const pieces = alignReply(r) || alignDiff(r);
    const body = pieces ? tokens(pieces, true, true) : md(esc(r.raw_reply));
    const used = new Set((pieces || []).filter((x) => x.p && !x.bad).map((x) => x.key)).size;
    const madeUp = (pieces || []).filter((x) => x.p && x.bad).length;
    const n = new Set(r.disclosure.map((d) => d.surrogate)).size;
    const main = panel('cloud', 'The reply, as it came back', body, '<span>Replayed from the recorded run: nothing is called live.</span>');
    const aside = side('cloud', 'What crossed to the cloud',
      `<p class="dm-lbl">The request, sent with the masked email</p><p class="req">“${esc(D.task)}”</p>
       <div class="nums">
         <div><b data-n="${n}">0</b><span>values the cloud model never saw</span></div>
         <div><b data-n="${used}">0</b><span>surrogates its reply uses</span></div>
         <div class="${madeUp ? 'warn' : ''}"><b data-n="${madeUp}">0</b><span>placeholders it made up</span></div>
       </div>`,
      '<span>Hosted model, temperature 0.</span>');
    return main + aside;
  }

  function stepThree(f, r) {
    const pieces = alignReply(r) || alignDiff(r);
    const body = pieces ? tokens(pieces, true, true) : md(esc(r.restored));
    const ok = r.fully_restored;
    const main = panel('local', 'The reply, with the real values put back', body,
      `<span class="verdict ${ok ? 'yes' : 'no'}">${ok ? 'fully restored' : 'not fully restored'}</span><span>exact, then normalised, then fuzzy matching; never a guess</span>`,
      toggle('As received', 'Restored'));
    const byS = Object.fromEntries(r.disclosure.map((d) => [d.surrogate, d]));
    const bad = r.events.filter((e) => e.outcome === 'hallucinated_token' || e.outcome === 'altered_unresolved');
    const restored = r.events.filter((e) => e.outcome === 'restored');
    const dropped = r.events.filter((e) => e.outcome === 'dropped');
    const row = (icon, cls, k, txt) => `<div class="lg ${cls}" data-k="${esc(k)}"><span class="ic">${icon}</span><span>${txt}</span></div>`;
    const log = [
      ...bad.map((e) => row('!', 'bad', e.surrogate, e.outcome === 'hallucinated_token'
        ? `<code>${esc(e.surrogate)}</code> made up by the model: reported, not guessed`
        : `<code>${esc(e.found_as || e.surrogate)}</code> altered by the model and not resolved: reported`)),
      ...restored.map((e) => row('✓', 'ok', e.surrogate, `<code>${esc(e.surrogate)}</code> → ${esc(byS[e.surrogate] ? byS[e.surrogate].value : '')}`)),
      dropped.length ? row('–', 'mute', '', `${dropped.length} not used by the reply: ${dropped.map((e) => `<code>${esc(e.surrogate)}</code>`).join(' ')}`) : '',
    ].join('');
    const aside = side('local', 'Restoration log', `<div class="log">${log}</div>`,
      `<span>${restored.length} put back · ${bad.length} reported · ${dropped.length} unused</span>`);
    return main + aside;
  }

  function stepFour(f, r) {
    const blocked = f.calc_blocked[state.det] || {};
    const kinds = Object.entries(blocked).map(([t, n]) => `${n} ${t}`).join(', ');
    const pieces = alignOriginal(f, r);
    const body = `<span class="req-bubble">“${esc(D.calc_task)}”</span>\n\n` + (pieces ? tokens(pieces, true, false) : esc(r.masked));
    const main = panel('local', 'A new request on the same email', body, '<span>The check reads the request before anything is sent.</span>');
    const verdict = kinds
      ? `<div class="refusal"><p class="stop"><strong>Not sent.</strong> The request asks for a calculation on values the cloud model would not see (${esc(kinds)}).</p>
         <p class="small">With placeholders it would have no numbers; with fakes it would compute a plausible, wrong total that cannot be restored. Only a local answer is right.</p>
         <p class="tiny">A heuristic, not evaluated: a fixed list of Italian cues.</p></div>`
      : `<div class="refusal"><p class="go"><strong>Sent.</strong> With ${esc(state.det)} no amount, date or age is masked in this email, so the cloud model sees the real numbers.</p>
         <p class="tiny">The check protects only what is masked: here the privacy cost is the detector's.</p></div>`;
    return main + side(kinds ? 'local' : 'cloud', kinds ? 'Feasibility check: refused' : 'Feasibility check: passed', verdict);
  }

  function render() {
    if (!root) return;
    const my = ++ticket;
    const f = fixture(), r = run();
    const opt = (key, val, label) => `<button class="opt ${state[key] === val ? 'on' : ''}" data-k="${key}" data-v="${val}">${label}</button>`;
    $('.dm-bar').innerHTML =
      `<div class="dm-group"><span class="dm-gl">Email</span>${D.fixtures.map((x) => opt('fx', x.id, SCENARIO[x.scenario] || x.id)).join('')}</div>
       <div class="dm-group"><span class="dm-gl">Detector</span>${D.detectors.map((d) => opt('det', d, d)).join('')}</div>
       <div class="dm-group"><span class="dm-gl">Surrogates</span>${opt('strat', 'R1', 'Placeholders')}${opt('strat', 'R2', 'Fakes')}</div>`;
    $('.dm-track').innerHTML = STEPS.map((s, i) => {
      const st = state.step === i + 1 ? 'on' : state.step > i + 1 ? 'done' : '';
      return `<div class="dm-step ${st} ${s.where}" data-step="${i + 1}"><span class="n">${state.step > i + 1 ? '✓' : i + 1}</span><span class="tx"><span class="t">${s.t}</span><span class="w">${WHERE[s.where]}</span></span></div>`;
    }).join('') + '<button class="dm-replay" title="Play this step again">↻ Replay</button>';
    $('.dm-stage').innerHTML = [stepOne, stepTwo, stepThree, stepFour][state.step - 1](f, r);
    animate(my);
  }

  /* ---------- animation ---------- */

  const wait = (ms) => new Promise((res) => setTimeout(res, ms));
  const alive = (my) => my === ticket;

  function setView(view) {
    // view 'a' or 'b' of the toggle; tokens follow it at once
    const tg = root.querySelector('.dm-toggle');
    if (!tg) return;
    tg.querySelectorAll('button').forEach((b) => b.classList.toggle('on', b.dataset.view === view));
    const masked = state.step === 1 ? view === 'b' : view === 'a';
    root.querySelectorAll('.dm-body .tk').forEach((t) => t.classList.toggle('on', masked));
    if (state.step === 1) {
      root.querySelectorAll('.vr').forEach((v) => v.classList.toggle('in', masked));
      updateCount();
    }
  }

  function updateCount() {
    const c = root.querySelector('.cnt');
    if (c) c.textContent = root.querySelectorAll('.vr.in').length;
  }

  function flash(el) {
    el.classList.remove('flip');
    void el.offsetWidth;
    el.classList.add('flip');
  }

  async function flipAll(my, toMasked) {
    const toks = [...root.querySelectorAll('.dm-body .tk')];
    const gap = Math.max(45, Math.min(130, 1900 / Math.max(1, toks.length)));
    for (const t of toks) {
      if (!alive(my)) return;
      t.classList.toggle('on', toMasked);
      flash(t);
      if (toMasked) {
        const v = root.querySelector(`.vr[data-k="${CSS.escape(t.dataset.k)}"]`);
        if (v && !v.classList.contains('in')) { v.classList.add('in'); updateCount(); }
      }
      await wait(gap);
    }
  }

  async function stream(my) {
    const body = root.querySelector('.dm-body');
    body.classList.add('stream');
    const total = body.clientHeight + 90, dur = 1700, t0 = performance.now();
    await new Promise((res) => {
      const tick = (now) => {
        if (!alive(my)) return res();
        const k = Math.min(1, (now - t0) / dur);
        body.style.setProperty('--p', `${Math.round(k * total)}px`);
        if (k < 1) requestAnimationFrame(tick); else res();
      };
      requestAnimationFrame(tick);
    });
    if (alive(my)) body.classList.remove('stream');
  }

  async function countUp(my) {
    const nums = [...root.querySelectorAll('.nums b')];
    for (let s = 1; s <= 12; s++) {
      if (!alive(my)) return;
      nums.forEach((b) => { b.textContent = Math.round((Number(b.dataset.n) * s) / 12); });
      await wait(40);
    }
  }

  async function animate(my) {
    const s = state.step;
    if (s === 1) {
      if (PRINT) return setView('b');
      setView('a');
      await wait(800);
      if (!alive(my)) return;
      root.querySelector('.dm-toggle button[data-view="b"]').classList.add('on');
      root.querySelector('.dm-toggle button[data-view="a"]').classList.remove('on');
      await flipAll(my, true);
    } else if (s === 2) {
      if (PRINT) return root.querySelectorAll('.nums b').forEach((b) => { b.textContent = b.dataset.n; });
      countUp(my);
      await stream(my);
    } else if (s === 3) {
      if (PRINT) return setView('b');
      setView('a');
      await wait(700);
      if (!alive(my)) return;
      root.querySelector('.dm-toggle button[data-view="b"]').classList.add('on');
      root.querySelector('.dm-toggle button[data-view="a"]').classList.remove('on');
      await flipAll(my, false);
    }
  }

  /* ---------- linking and tooltip ---------- */

  function tipFor(el) {
    const tip = $('.dm-tip');
    const { type, src, v, p } = el.dataset;
    const kls = [...el.classList].find((c) => CLS[c]);
    const head = el.classList.contains('bad') && !type
      ? 'Made up by the model: no value to restore'
      : `${esc(type)} · ${CLS[kls] || ''}${src ? ` · found by ${esc(src)}` : ''}`;
    tip.innerHTML = `${head}${v && p && v !== p ? `<br><b>${esc(v)}</b> ⇄ <code>${esc(p)}</code>` : ''}`;
    const rr = root.getBoundingClientRect(), er = el.getBoundingClientRect();
    const scale = rr.width / root.offsetWidth || 1;
    let x = (er.left - rr.left) / scale, y = (er.bottom - rr.top) / scale + 6;
    tip.classList.add('show');
    const w = tip.offsetWidth;
    if (x + w > root.offsetWidth) x = root.offsetWidth - w;
    if (y + tip.offsetHeight > root.offsetHeight) y = (er.top - rr.top) / scale - tip.offsetHeight - 6;
    tip.style.left = `${Math.max(0, x)}px`;
    tip.style.top = `${y}px`;
  }

  function hover(e) {
    const el = e.target.closest('.tk, .vr, .lg');
    root.querySelectorAll('.hl').forEach((x) => x.classList.remove('hl'));
    if (!el || !el.dataset.k) { $('.dm-tip').classList.remove('show'); return; }
    root.querySelectorAll(`[data-k="${CSS.escape(el.dataset.k)}"]`).forEach((x) => x.classList.add('hl'));
    if (el.classList.contains('lg')) { $('.dm-tip').classList.remove('show'); return; }
    tipFor(el);
  }

  /* ---------- wiring ---------- */

  function setStep(n) {
    state.step = n;
    // keep reveal's fragments in step with the track (fragment i shows step i + 2)
    if (window.Reveal && Reveal.getCurrentSlide() && Reveal.getCurrentSlide().id === 'demo') Reveal.navigateFragment(n - 2);
    render();
  }

  function init() {
    root = document.querySelector('#demo .demo');
    if (!root || !D) return;
    root.innerHTML = '<div class="dm-bar"></div><div class="dm-track"></div><div class="dm-stage"></div><div class="dm-tip"></div>';
    root.addEventListener('click', (e) => {
      const b = e.target.closest('button.opt');
      if (b) { state[b.dataset.k] = b.dataset.v; render(); return; }
      const tg = e.target.closest('.dm-toggle button');
      if (tg) { ticket++; setView(tg.dataset.view); return; }
      if (e.target.closest('.dm-replay')) { render(); return; }
      const st = e.target.closest('.dm-step');
      if (st) setStep(Number(st.dataset.step));
    });
    root.addEventListener('mouseover', hover);
    root.addEventListener('mouseleave', () => { $('.dm-tip').classList.remove('show'); root.querySelectorAll('.hl').forEach((x) => x.classList.remove('hl')); });
    const slide = document.getElementById('demo');
    const visibleSteps = () => slide.querySelectorAll('.fragment.step.visible').length + 1;
    const sync = () => { if (state.step !== visibleSteps()) { state.step = visibleSteps(); render(); } };
    Reveal.on('fragmentshown', sync);
    Reveal.on('fragmenthidden', sync);
    // entering the slide plays the current step from the start
    Reveal.on('slidechanged', (e) => { if (e.currentSlide.id === 'demo') { state.step = visibleSteps(); render(); } });
    // the deck may open on a later step (a link with a fragment index): read it now
    state.step = visibleSteps();
    render();
  }

  /* for checking the alignment of every run: OmissisDemo.check() */
  function check() {
    const out = { original: 0, reply: 0, failed: [] };
    for (const f of D.fixtures) for (const [k, r] of Object.entries(f.runs)) {
      if (alignOriginal(f, r)) out.original++; else out.failed.push(`${f.id} ${k} original`);
      if (alignReply(r) || alignDiff(r)) out.reply++; else out.failed.push(`${f.id} ${k} reply`);
    }
    return out;
  }

  window.OmissisDemo = { init, state, render, check };
})();
