/* Charts of the deck. Every number is copied from results/test/metrics/ (scorecard of
   22 Nov 2026); the file each comes from is named next to it. */
(function () {
  const NAVY = '#1F2A44', CORAL = '#E4572E', TEAL = '#2A9D8F', MUSTARD = '#E9B44C', MUTED = '#5C6478';
  const GRID = 'rgba(31, 42, 68, 0.12)';
  const exporting = window.location.search.includes('export');

  Chart.defaults.font.family = 'Inter, Helvetica, Arial, sans-serif';
  Chart.defaults.font.size = 16;
  Chart.defaults.color = NAVY;
  Chart.defaults.borderColor = GRID;
  Chart.defaults.devicePixelRatio = 2;
  if (exporting) Chart.defaults.animation = false;

  /* draws 95% intervals: dataset.intervals[i] = {xl, xh, yl, yh} (any subset) */
  const intervals = {
    id: 'intervals',
    afterDatasetsDraw(chart) {
      const { ctx, scales } = chart;
      chart.data.datasets.forEach((ds, di) => {
        if (!ds.intervals || !chart.isDatasetVisible(di)) return;
        const meta = chart.getDatasetMeta(di);
        ctx.save();
        ctx.strokeStyle = NAVY; ctx.lineWidth = 2;
        ds.intervals.forEach((iv, i) => {
          const el = meta.data[i]; if (!el || !iv) return;
          const { x, y } = el.getProps(['x', 'y'], true);
          const cap = 6;
          const line = (x1, y1, x2, y2) => { ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); };
          const sx = scales.x, sy = scales.y;
          if (iv.xl !== undefined && sx.getPixelForValue) {
            const a = sx.getPixelForValue(iv.xl), b = sx.getPixelForValue(iv.xh);
            if (Math.abs(b - a) > 1) { line(a, y, b, y); line(a, y - cap, a, y + cap); line(b, y - cap, b, y + cap); }
          }
          if (iv.yl !== undefined) {
            const a = sy.getPixelForValue(iv.yl), b = sy.getPixelForValue(iv.yh);
            if (Math.abs(b - a) > 1) { line(x, a, x, b); line(x - cap, a, x + cap, a); line(x - cap, b, x + cap, b); }
          }
        });
        ctx.restore();
      });
    },
  };

  /* point labels next to scatter points: dataset.labels[i], dataset.labelPos[i] = [dx, dy] */
  const pointLabels = {
    id: 'pointLabels',
    afterDatasetsDraw(chart) {
      const { ctx } = chart;
      chart.data.datasets.forEach((ds, di) => {
        if (!ds.pointLabels) return;
        const meta = chart.getDatasetMeta(di);
        ctx.save();
        ctx.font = '600 15px Inter, Helvetica, sans-serif'; ctx.fillStyle = NAVY;
        ds.pointLabels.forEach((lab, i) => {
          const el = meta.data[i]; if (!el || !lab) return;
          const at = ds.labelAt && ds.labelAt[i];
          if (at) {
            // label placed in data coordinates, joined to its point by a leader line
            const lx = chart.scales.x.getPixelForValue(at.x), ly = chart.scales.y.getPixelForValue(at.y);
            ctx.strokeStyle = 'rgba(31, 42, 68, 0.45)'; ctx.lineWidth = 1.2;
            ctx.beginPath(); ctx.moveTo(el.x, el.y); ctx.lineTo(lx - 4, ly - 5); ctx.stroke();
            ctx.textAlign = 'left'; ctx.fillText(lab, lx, ly);
            return;
          }
          const [dx, dy, align] = (ds.labelPos && ds.labelPos[i]) || [10, -10, 'left'];
          ctx.textAlign = align || 'left';
          ctx.fillText(lab, el.x + dx, el.y + dy);
        });
        ctx.restore();
      });
    },
  };

  const builders = {
    /* results/test/metrics/detection.json, overlap matching, rows level=class */
    'chart-detect': (ctx) => new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['D0 rules', 'D1 Presidio', 'D2 classifier', 'D3 local LLM', 'D4 hybrid'],
        datasets: [
          { label: 'Direct identifiers', data: [0.48, 0.72, 0.48, 0.13, 0.99], backgroundColor: CORAL, borderColor: NAVY, borderWidth: 1.5 },
          { label: 'Quasi-identifiers', data: [0.13, 0.43, 0.21, 0.97, 0.97], backgroundColor: MUSTARD, borderColor: NAVY, borderWidth: 1.5 },
          { label: 'Special categories', data: [0.00, 0.00, 0.00, 0.88, 0.88], backgroundColor: TEAL, borderColor: NAVY, borderWidth: 1.5 },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top', align: 'end', labels: { boxWidth: 16, padding: 16, font: { size: 16 } } },
          tooltip: { callbacks: { label: (c) => `${c.dataset.label}: ${c.parsed.y.toFixed(2)}` } } },
        scales: {
          y: { min: 0, max: 1, ticks: { stepSize: 0.2 }, title: { display: true, text: 'Recall, test split (overlap)' } },
          x: { grid: { display: false }, ticks: { font: { size: 16, weight: 600 } } },
        },
      },
    }),

    /* x = 1 − linkage top-1 at N = 25 (linkage.json), y = T3 (utility.json), 95% intervals */
    'chart-plane': (ctx) => {
      const P = [
        { c: 'REF-none', x: 0.0, xl: 0.0, xh: 0.0, y: 0.965, yl: 0.939, yh: 0.987, col: NAVY, at: { x: 0.2, y: 0.992 } },
        { c: 'REF-oracle-direct', x: 0.022, xl: 0.0, xh: 0.065, y: 0.957, yl: 0.926, yh: 0.983, col: NAVY, at: { x: 0.2, y: 0.976 } },
        { c: 'REF-oracle', x: 0.5, xl: 0.348, xh: 0.652, y: 0.909, yl: 0.87, yh: 0.943, col: NAVY, pos: [12, 22] },
        { c: 'D1+R1', x: 0.065, xl: 0.0, xh: 0.152, y: 0.952, yl: 0.922, yh: 0.978, col: MUSTARD, at: { x: 0.2, y: 0.96 } },
        { c: 'D2+R1', x: 0.0, xl: 0.0, xh: 0.0, y: 0.948, yl: 0.913, yh: 0.974, col: MUSTARD, at: { x: 0.2, y: 0.944 } },
        { c: 'D4+R1', x: 0.413, xl: 0.261, xh: 0.565, y: 0.896, yl: 0.857, yh: 0.93, col: CORAL, pos: [-12, 22, 'right'] },
        { c: 'D4+R2', x: 0.587, xl: 0.456, xh: 0.717, y: 0.948, yl: 0.917, yh: 0.974, col: TEAL, pos: [12, -12] },
      ];
      return new Chart(ctx, {
        type: 'scatter',
        data: {
          datasets: [
            {
              label: 'configurations', data: P.map((p) => ({ x: p.x, y: p.y })),
              pointBackgroundColor: P.map((p) => p.col), pointBorderColor: NAVY, pointBorderWidth: 1.8,
              pointRadius: P.map((p) => (p.c.startsWith('REF') ? 8 : 10)),
              pointStyle: P.map((p) => (p.c.startsWith('REF') ? 'rect' : 'circle')),
              intervals: P.map((p) => ({ xl: p.xl, xh: p.xh, yl: p.yl, yh: p.yh })),
              pointLabels: P.map((p) => p.c), labelPos: P.map((p) => p.pos), labelAt: P.map((p) => p.at),
            },
            { label: 'chance (attacker guesses)', type: 'line', data: [{ x: 0.96, y: 0.84 }, { x: 0.96, y: 1.0 }],
              borderColor: CORAL, borderDash: [7, 6], borderWidth: 2.5, pointRadius: 0 },
          ],
        },
        options: {
          maintainAspectRatio: false,
          layout: { padding: { right: 10, top: 6 } },
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          scales: {
            x: { min: -0.02, max: 1.0, ticks: { stepSize: 0.2 }, title: { display: true, text: 'Privacy score = 1 − linkage top-1, 25 candidates  →  more private' } },
            y: { min: 0.84, max: 1.0, ticks: { stepSize: 0.04 }, title: { display: true, text: 'T3 extraction score  →  more useful' } },
          },
        },
        plugins: [intervals, pointLabels],
      });
    },

    /* linkage top-1 at N = 25 with 95% intervals: linkage.json */
    'chart-linkage': (ctx) => {
      const L = [
        ['REF-none', 1.0, 1.0, 1.0, NAVY], ['D2+R1', 1.0, 1.0, 1.0, MUSTARD], ['REF-oracle-direct', 0.978, 0.935, 1.0, NAVY],
        ['D1+R1', 0.935, 0.848, 1.0, MUSTARD], ['D4+R1', 0.587, 0.435, 0.739, CORAL], ['REF-oracle', 0.5, 0.348, 0.652, NAVY],
        ['D4+R2', 0.413, 0.283, 0.543, TEAL],
      ];
      return new Chart(ctx, {
        type: 'bar',
        data: {
          labels: L.map((l) => l[0]),
          datasets: [
            { label: 'linkage top-1', data: L.map((l) => l[1]), backgroundColor: L.map((l) => l[4]), borderColor: NAVY, borderWidth: 1.5,
              intervals: L.map((l) => ({ xl: l[2], xh: l[3] })) },
          ],
        },
        options: {
          indexAxis: 'y', maintainAspectRatio: false, layout: { padding: { top: 22 } },
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          scales: {
            x: { min: 0, max: 1, ticks: { stepSize: 0.2 }, title: { display: true, text: 'Share of texts whose author the attacker names first (of 25)' } },
            y: { grid: { display: false }, ticks: { font: { size: 15, weight: 600 } } },
          },
        },
        plugins: [intervals, {
          id: 'chanceLine',
          afterDatasetsDraw(chart) {
            const { ctx, scales, chartArea } = chart;
            const x = scales.x.getPixelForValue(0.04);
            ctx.save(); ctx.strokeStyle = CORAL; ctx.lineWidth = 2.5; ctx.setLineDash([7, 6]);
            ctx.beginPath(); ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); ctx.stroke();
            ctx.setLineDash([]); ctx.fillStyle = '#B8401D'; ctx.font = '600 14px Inter, sans-serif';
            ctx.fillText('chance 0.04', x + 6, chartArea.top - 8); ctx.restore();
          },
        }],
      });
    },
  };

  /* horizontal intervals on a horizontal bar chart: x is the value axis */
  const made = {};
  function build(slide) {
    if (!slide) return;
    slide.querySelectorAll('canvas[data-chart]').forEach((cv) => {
      const id = cv.dataset.chart;
      if (made[id] || !builders[id]) return;
      made[id] = builders[id](cv.getContext('2d'));
    });
  }

  window.OmissisCharts = {
    init() {
      Reveal.on('ready', (e) => build(e.currentSlide));
      Reveal.on('slidechanged', (e) => build(e.currentSlide));
      if (exporting) document.querySelectorAll('.reveal .slides section').forEach(build);
    },
  };
})();
