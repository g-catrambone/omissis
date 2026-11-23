/* The demo slide: recorded runs of the pipeline, replayed from demo-data.js.
   Nothing here calls a model: every masked text and reply was produced by
   `omissis` in replay mode from results/cache and exported once. */
(function () {
  const D = window.DEMO;
  const LABELS = {
    iban_change: 'Bank · IBAN change', card_dispute: 'Bank · card dispute',
    account_closure: 'Bank · account closure', sick_leave: 'HR · sick leave',
    transfer_request: 'HR · transfer request',
  };
  const TYPE_CLASS = {};
  const STEPS = ['Protect', 'Send', 'Restore', 'A request we refuse'];
  const state = { fx: 'fx-bank-02', det: 'D4', strat: 'R1', step: 1 };
  let root = null;

  const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const fixture = () => D.fixtures.find((f) => f.id === state.fx);
  const run = () => fixture().runs[`${state.det}+${state.strat}`];

  for (const f of D.fixtures) for (const r of Object.values(f.runs)) {
    for (const d of r.disclosure) TYPE_CLASS[d.type] = d.cls;
    for (const s of r.spans) TYPE_CLASS[s.type] = s.cls;
  }

  /* original text with the detected spans marked by class */
  function markSpans(text, spans) {
    const sorted = [...spans].sort((a, b) => a.start - b.start);
    let out = '', pos = 0;
    for (const s of sorted) {
      if (s.start < pos) continue;
      out += esc(text.slice(pos, s.start));
      out += `<mark class="${s.cls}" title="${s.type} · ${s.source}">${esc(text.slice(s.start, s.end))}</mark>`;
      pos = s.end;
    }
    return out + esc(text.slice(pos));
  }

  /* mark every occurrence of the given strings; cls(str) gives the class */
  function markAll(text, strings, cls, title) {
    const list = [...new Set(strings.filter((s) => s && s.length > 1))].sort((a, b) => b.length - a.length);
    if (!list.length) return esc(text);
    const re = new RegExp(list.map(reEsc).join('|'), 'g');
    let out = '', pos = 0, m;
    while ((m = re.exec(text))) {
      out += esc(text.slice(pos, m.index));
      out += `<mark class="${cls(m[0])}" title="${esc(title(m[0]))}">${esc(m[0])}</mark>`;
      pos = m.index + m[0].length;
    }
    return out + esc(text.slice(pos));
  }

  const PLACEHOLDER = /^\[[A-Z]+(?:_[A-Z]+)*_\d+(?:_[MF])?\]$/;
  function markSurrogates(text, r) {
    const byS = Object.fromEntries(r.disclosure.map((d) => [d.surrogate, d]));
    // placeholders the model wrote that are not ours
    const extra = (text.match(/\[[A-Z]+(?:_[A-Z]+)*_\d+(?:_[MF])?\]/g) || []).filter((t) => !byS[t]);
    return markAll(text, [...Object.keys(byS), ...extra],
      (s) => (!byS[s] ? 'bad' : PLACEHOLDER.test(s) ? 'sur' : 'fake'),
      (s) => (byS[s] ? `${byS[s].type} · ${byS[s].source}` : 'made up by the model'));
  }

  function markRestored(text, r) {
    const orig = fixture();
    const values = {};
    for (const s of r.spans) values[orig.text.slice(s.start, s.end)] = s.cls;
    const extra = (text.match(/\[[A-Z]+(?:_[A-Z]+)*_\d+(?:_[MF])?\]/g) || []);
    for (const t of extra) values[t] = 'bad';
    return markAll(text, Object.keys(values), (s) => values[s],
      (s) => (values[s] === 'bad' ? 'placeholder left: not restored, reported' : 'restored on this machine'));
  }

  /* the model writes markdown bold: show it as bold, after the marks are placed */
  const md = (html) => html.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');

  function counts(r) {
    const c = { direct: 0, quasi: 0, special: 0 };
    for (const d of r.disclosure) c[d.cls] = (c[d.cls] || 0) + 1;
    return `<span class="chip direct">${c.direct} direct</span><span class="chip quasi">${c.quasi} quasi</span><span class="chip special">${c.special} special</span>`;
  }

  function pane(kind, title, body, foot) {
    const where = kind === 'cloud' ? 'cloud model' : 'this machine';
    return `<div class="pane ${kind}"><div class="ph"><span>${title}</span><span class="where ${kind}">${where}</span></div>
      <div class="pb">${body}</div>${foot ? `<div class="pf">${foot}</div>` : ''}</div>`;
  }

  function restoreFoot(r) {
    const bad = r.events.filter((e) => e.outcome === 'hallucinated_token' || e.outcome === 'altered_unresolved');
    const restored = r.events.filter((e) => e.outcome === 'restored').length;
    const dropped = r.events.filter((e) => e.outcome === 'dropped').length;
    let s = `<span class="verdict ${r.fully_restored ? 'yes' : 'no'}">${r.fully_restored ? 'fully restored' : 'not fully restored'}</span>`;
    s += `<span>${restored} values put back · ${dropped} not used by the reply</span>`;
    if (bad.length) s += `<span class="ink-coral">${bad.map((e) => `${esc(e.found_as || e.surrogate)}: ${e.outcome.replace('_', ' ')}`).join(' · ')}</span>`;
    return s;
  }

  function refusal() {
    const f = fixture(), r = run();
    const blocked = f.calc_blocked[state.det] || {};
    const kinds = Object.entries(blocked).map(([t, n]) => `${n} ${t}`).join(', ');
    const left = pane('local', 'The request, then the masked text',
      `<div class="refusal"><p class="req">“${esc(D.calc_task)}”</p></div>` + markSurrogates(r.masked, r));
    let body;
    if (kinds) {
      body = `<div class="refusal"><p class="stop"><strong>Not sent.</strong> The request asks for a calculation, and the text holds masked values the cloud model does not see (${esc(kinds)}).</p>
        <p class="small">With placeholders it would have no numbers; with fake values it would compute a plausible, wrong total that cannot be restored. This request can only be answered locally.</p>
        <p class="tiny">A heuristic, not evaluated: it reads the request alone, with a fixed list of Italian cues.</p></div>`;
    } else {
      body = `<div class="refusal"><p class="go"><strong>Sent.</strong> With ${state.det} no amount, date or age is masked in this text, so the cloud model sees the real numbers and nothing blocks the request.</p>
        <p class="tiny">The check protects only what is masked: the privacy cost here is the detector's.</p></div>`;
    }
    return left + pane(kinds ? 'local' : 'cloud', kinds ? 'Feasibility check' : 'Feasibility check: passed', body);
  }

  function render() {
    if (!root) return;
    const f = fixture(), r = run();
    const opt = (key, val, label) => `<button class="opt ${state[key] === val ? 'on' : ''}" data-k="${key}" data-v="${val}">${label}</button>`;
    root.querySelector('.bar').innerHTML =
      `<div class="group"><span class="gl">Email</span>${D.fixtures.map((x) => opt('fx', x.id, LABELS[x.scenario] || x.id)).join('')}</div>
       <div class="group"><span class="gl">Detector</span>${D.detectors.map((d) => opt('det', d, d)).join('')}</div>
       <div class="group"><span class="gl">Replace</span>${opt('strat', 'R1', 'R1 placeholders')}${opt('strat', 'R2', 'R2 fakes')}</div>`;
    root.querySelector('.stepper').innerHTML = STEPS.map((s, i) =>
      `<div class="st ${state.step === i + 1 ? 'on' : state.step > i + 1 ? 'done' : ''}" data-step="${i + 1}"><span class="n">${i + 1}</span>${s}</div>`).join('');

    let html;
    if (state.step === 1) {
      html = pane('local', `Your text · ${f.id} (synthetic)`, markSpans(f.text, r.spans), counts(r))
        + pane('local', 'What would be sent', markSurrogates(r.masked, r), '<span>Nothing has left this machine yet: this is the preview.</span>');
    } else if (state.step === 2) {
      html = pane('cloud', 'Sent to the cloud model', markSurrogates(r.masked, r), `<span>Request: “${esc(D.task)}”</span>`)
        + pane('cloud', 'Its reply, as it came back', md(markSurrogates(r.raw_reply, r)), '<span>The model only ever saw surrogates.</span>');
    } else if (state.step === 3) {
      html = pane('cloud', 'Reply from the cloud model', md(markSurrogates(r.raw_reply, r)), '<span>exact → normalised → fuzzy match; never a guess</span>')
        + pane('local', 'Reply with the real values restored', md(markRestored(r.restored, r)), restoreFoot(r));
    } else {
      html = refusal();
    }
    root.querySelector('.panes').innerHTML = html;
  }

  function setStep(n) {
    state.step = n;
    // keep reveal's fragments in step with the stepper (fragment i shows step i + 2)
    if (window.Reveal && Reveal.getCurrentSlide() && Reveal.getCurrentSlide().id === 'demo') {
      Reveal.navigateFragment(n - 2);
    }
    render();
  }

  function init() {
    root = document.querySelector('#demo .demo');
    if (!root || !D) return;
    root.addEventListener('click', (e) => {
      const b = e.target.closest('button.opt');
      if (b) { state[b.dataset.k] = b.dataset.v; render(); return; }
      const st = e.target.closest('.st');
      if (st) setStep(Number(st.dataset.step));
    });
    const sync = () => {
      const slide = document.getElementById('demo');
      const shown = slide.querySelectorAll('.fragment.step.visible').length;
      if (state.step !== shown + 1) { state.step = shown + 1; render(); }
    };
    Reveal.on('fragmentshown', sync);
    Reveal.on('fragmenthidden', sync);
    Reveal.on('slidechanged', (e) => { if (e.currentSlide.id === 'demo') sync(); });
    // the deck may open on a later step (link with a fragment index): read it now
    state.step = document.getElementById('demo').querySelectorAll('.fragment.step.visible').length + 1;
    render();
  }

  window.OmissisDemo = { init, state, render };
})();
