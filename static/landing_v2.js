/**
 * landing_v2.js
 * JavaScript engine for Desk & Ledger home page:
 *  - Hero Interactive Trading Dashboard Canvas Widget
 *  - Area / Candlestick rendering modes + Crosshair Tooltip
 *  - Main Live Market Pulse Chart (6 markets)
 *  - Risk Donut Chart animation
 *  - Watchlist filtering & Live quote polling
 */

(function () {
  'use strict';

  function qs(sel) { return document.querySelector(sel); }
  function qsa(sel) { return document.querySelectorAll(sel); }

  /* =============================================================
     HERO TRADING DASHBOARD WIDGET ENGINE
     ============================================================= */
  var widgetData = {
    nifty: {
      name: 'NIFTY 50', currency: '₹', price: '24,380.15', change: '+142.30 (+0.59%)', isUp: true,
      high: '24,412.50', low: '24,198.30', rsi: '64.2 (Bullish)', signal: 'Strong Outperform',
      pts: [24250, 24280, 24230, 24310, 24290, 24340, 24320, 24380, 24350, 24400, 24370, 24410],
      candles: [
        { o: 24250, h: 24290, l: 24240, c: 24280 },
        { o: 24280, h: 24300, l: 24220, c: 24230 },
        { o: 24230, h: 24320, l: 24220, c: 24310 },
        { o: 24310, h: 24320, l: 24280, c: 24290 },
        { o: 24290, h: 24360, l: 24280, c: 24340 },
        { o: 24340, h: 24350, l: 24300, c: 24320 },
        { o: 24320, h: 24400, l: 24310, c: 24380 },
        { o: 24380, h: 24412, l: 24350, c: 24410 }
      ]
    },
    reliance: {
      name: 'RELIANCE', currency: '₹', price: '2,948.10', change: '+36.20 (+1.24%)', isUp: true,
      high: '2,962.00', low: '2,910.50', rsi: '58.7 (Moderate Buy)', signal: 'Outperform',
      pts: [2912, 2920, 2915, 2930, 2925, 2940, 2935, 2948, 2942, 2955, 2950, 2960],
      candles: [
        { o: 2912, h: 2925, l: 2908, c: 2920 },
        { o: 2920, h: 2928, l: 2910, c: 2915 },
        { o: 2915, h: 2935, l: 2912, c: 2930 },
        { o: 2930, h: 2938, l: 2922, c: 2925 },
        { o: 2925, h: 2945, l: 2920, c: 2940 },
        { o: 2940, h: 2946, l: 2932, c: 2935 },
        { o: 2935, h: 2952, l: 2930, c: 2948 },
        { o: 2948, h: 2962, l: 2942, c: 2960 }
      ]
    },
    sp500: {
      name: 'S&P 500', currency: '$', price: '5,540.20', change: '+28.40 (+0.51%)', isUp: true,
      high: '5,548.30', low: '5,498.20', rsi: '61.4 (Bullish)', signal: 'Outperform',
      pts: [5510, 5505, 5522, 5518, 5530, 5525, 5538, 5540, 5535, 5545, 5542, 5548],
      candles: [
        { o: 5510, h: 5518, l: 5502, c: 5505 },
        { o: 5505, h: 5526, l: 5500, c: 5522 },
        { o: 5522, h: 5528, l: 5512, c: 5518 },
        { o: 5518, h: 5534, l: 5515, c: 5530 },
        { o: 5530, h: 5532, l: 5520, c: 5525 },
        { o: 5525, h: 5542, l: 5522, c: 5538 },
        { o: 5538, h: 5544, l: 5532, c: 5540 },
        { o: 5540, h: 5548, l: 5535, c: 5548 }
      ]
    },
    nvda: {
      name: 'NVIDIA', currency: '$', price: '142.66', change: '+4.72 (+3.42%)', isUp: true,
      high: '144.20', low: '137.50', rsi: '72.1 (Overbought/Strong)', signal: 'High Volatility Buy',
      pts: [138, 137.5, 139.2, 138.8, 140.5, 140, 141.8, 142.66, 142.1, 143.5, 143, 144.2],
      candles: [
        { o: 138, h: 139, l: 137, c: 137.5 },
        { o: 137.5, h: 140, l: 137, c: 139.2 },
        { o: 139.2, h: 140.2, l: 138.5, c: 138.8 },
        { o: 138.8, h: 141, l: 138.2, c: 140.5 },
        { o: 140.5, h: 141.2, l: 139.5, c: 140 },
        { o: 140, h: 142.5, l: 139.8, c: 141.8 },
        { o: 141.8, h: 143.2, l: 141.2, c: 142.66 },
        { o: 142.66, h: 144.2, l: 142, c: 144.2 }
      ]
    },
    btc: {
      name: 'BITCOIN', currency: '$', price: '64,250.00', change: '-410.00 (-0.63%)', isUp: false,
      high: '65,100.00', low: '64,100.00', rsi: '46.8 (Neutral)', signal: 'Consolidation',
      pts: [64900, 64800, 64650, 64700, 64400, 64500, 64300, 64250, 64350, 64200, 64280, 64250],
      candles: [
        { o: 64900, h: 65100, l: 64750, c: 64800 },
        { o: 64800, h: 64850, l: 64580, c: 64650 },
        { o: 64650, h: 64780, l: 64600, c: 64700 },
        { o: 64700, h: 64720, l: 64350, c: 64400 },
        { o: 64400, h: 64580, l: 64380, c: 64500 },
        { o: 64500, h: 64520, l: 64220, c: 64300 },
        { o: 64300, h: 64380, l: 64180, c: 64250 },
        { o: 64250, h: 64350, l: 64100, c: 64200 }
      ]
    }
  };

  var activeSymbol = 'nifty';
  var chartMode = 'line'; // 'line' or 'candles'
  var widgetAnimOff = 0;
  var mouseX = -1;

  var widgetCanvas = qs('#heroWidgetCanvas');
  var widgetWrap = qs('#heroWidgetCanvasWrap');
  var tooltip = qs('#heroChartTooltip');

  if (widgetCanvas && widgetWrap) {
    var wCtx = widgetCanvas.getContext('2d');

    function resizeWidgetCanvas() {
      var dpr = window.devicePixelRatio || 1;
      var rect = widgetWrap.getBoundingClientRect();
      widgetCanvas.width = rect.width * dpr;
      widgetCanvas.height = rect.height * dpr;
      wCtx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resizeWidgetCanvas);
    resizeWidgetCanvas();

    widgetWrap.addEventListener('mousemove', function (e) {
      var rect = widgetWrap.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
    });

    widgetWrap.addEventListener('mouseleave', function () {
      mouseX = -1;
      if (tooltip) tooltip.style.display = 'none';
    });

    function drawHeroWidget() {
      var w = widgetWrap.clientWidth;
      var h = widgetWrap.clientHeight;
      wCtx.clearRect(0, 0, w, h);

      var d = widgetData[activeSymbol];
      widgetAnimOff += 0.04;

      // Draw horizontal grid lines & price ticks
      wCtx.strokeStyle = 'rgba(255,255,255,0.04)';
      wCtx.lineWidth = 1;
      for (var y = 20; y < h; y += 45) {
        wCtx.beginPath(); wCtx.moveTo(0, y); wCtx.lineTo(w, y); wCtx.stroke();
      }

      if (chartMode === 'line') {
        var pts = d.pts.slice();
        pts[pts.length - 1] += Math.sin(widgetAnimOff) * (d.isUp ? 2.5 : -2.5);

        var mn = Math.min.apply(null, pts) - 10;
        var mx = Math.max.apply(null, pts) + 10;
        var rng = mx - mn || 1;

        var coords = pts.map(function (p, i) {
          return { x: (i / (pts.length - 1)) * w, y: h - 18 - ((p - mn) / rng) * (h - 36), val: p };
        });

        var lineColor = d.isUp ? '#FF7A29' : '#F87171';
        var gradColor = d.isUp ? 'rgba(255, 122, 41, 0.2)' : 'rgba(248, 93, 93, 0.2)';

        // Area Gradient
        wCtx.beginPath();
        wCtx.moveTo(coords[0].x, h);
        wCtx.lineTo(coords[0].x, coords[0].y);
        for (var i = 1; i < coords.length; i++) {
          var cp = coords[i - 1];
          var np = coords[i];
          var mpx = (cp.x + np.x) / 2;
          wCtx.bezierCurveTo(mpx, cp.y, mpx, np.y, np.x, np.y);
        }
        wCtx.lineTo(w, h);
        wCtx.closePath();

        var gradient = wCtx.createLinearGradient(0, 0, 0, h);
        gradient.addColorStop(0, gradColor);
        gradient.addColorStop(1, 'rgba(20, 16, 13, 0)');
        wCtx.fillStyle = gradient;
        wCtx.fill();

        // Stroke Path Line
        wCtx.beginPath();
        wCtx.moveTo(coords[0].x, coords[0].y);
        for (var i2 = 1; i2 < coords.length; i2++) {
          var cp2 = coords[i2 - 1];
          var np2 = coords[i2];
          var mpx2 = (cp2.x + np2.x) / 2;
          wCtx.bezierCurveTo(mpx2, cp2.y, mpx2, np2.y, np2.x, np2.y);
        }
        wCtx.strokeStyle = lineColor;
        wCtx.lineWidth = 2.5;
        wCtx.stroke();

        // Pulsing End Dot
        var lastPt = coords[coords.length - 1];
        wCtx.beginPath();
        wCtx.arc(lastPt.x - 3, lastPt.y, 4, 0, Math.PI * 2);
        wCtx.fillStyle = lineColor;
        wCtx.fill();
        wCtx.beginPath();
        wCtx.arc(lastPt.x - 3, lastPt.y, 8 + Math.sin(widgetAnimOff * 2) * 3, 0, Math.PI * 2);
        wCtx.strokeStyle = lineColor;
        wCtx.lineWidth = 1;
        wCtx.stroke();

        // Crosshair Hover Logic
        if (mouseX >= 0 && mouseX <= w) {
          // Find nearest point
          var closest = coords[0];
          var minDist = Math.abs(coords[0].x - mouseX);
          for (var k = 1; k < coords.length; k++) {
            var dist = Math.abs(coords[k].x - mouseX);
            if (dist < minDist) { minDist = dist; closest = coords[k]; }
          }

          // Vertical crosshair line
          wCtx.strokeStyle = 'rgba(255, 122, 41, 0.4)';
          wCtx.setLineDash([4, 4]);
          wCtx.beginPath();
          wCtx.moveTo(closest.x, 0);
          wCtx.lineTo(closest.x, h);
          wCtx.stroke();
          wCtx.setLineDash([]);

          // Hover point dot
          wCtx.beginPath();
          wCtx.arc(closest.x, closest.y, 5, 0, Math.PI * 2);
          wCtx.fillStyle = '#FFFFFF';
          wCtx.fill();

          // Tooltip update
          if (tooltip) {
            tooltip.style.display = 'flex';
            var ttPrice = qs('#ttPrice');
            var ttTime = qs('#ttTime');
            if (ttPrice) ttPrice.textContent = d.currency + closest.val.toLocaleString('en-US', { minimumFractionDigits: 2 });
            if (ttTime) ttTime.textContent = '15:30 IST';
          }
        }
      } else {
        // Candlestick rendering mode
        var cndls = d.candles;
        var cW = (w / cndls.length) * 0.55;
        var mnC = Math.min.apply(null, cndls.map(function (c) { return c.l; })) - 5;
        var mxC = Math.max.apply(null, cndls.map(function (c) { return c.h; })) + 5;
        var rngC = mxC - mnC || 1;

        cndls.forEach(function (c, idx) {
          var cx = (idx / (cndls.length - 1)) * (w - 60) + 30;
          var isBull = c.c >= c.o;
          var yOpen = h - 20 - ((c.o - mnC) / rngC) * (h - 40);
          var yClose = h - 20 - ((c.c - mnC) / rngC) * (h - 40);
          var yHigh = h - 20 - ((c.h - mnC) / rngC) * (h - 40);
          var yLow = h - 20 - ((c.l - mnC) / rngC) * (h - 40);

          var color = isBull ? '#34D399' : '#F87171';

          // Wick line
          wCtx.strokeStyle = color;
          wCtx.lineWidth = 1.5;
          wCtx.beginPath();
          wCtx.moveTo(cx, yHigh);
          wCtx.lineTo(cx, yLow);
          wCtx.stroke();

          // Candle body
          var topY = Math.min(yOpen, yClose);
          var bH = Math.max(Math.abs(yOpen - yClose), 3);
          wCtx.fillStyle = color;
          wCtx.fillRect(cx - cW / 2, topY, cW, bH);
        });
      }

      requestAnimationFrame(drawHeroWidget);
    }
    requestAnimationFrame(drawHeroWidget);

    // Tab buttons logic
    qsa('.w-tab').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.w-tab').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        activeSymbol = btn.getAttribute('data-symbol');
        var d = widgetData[activeSymbol];

        var nameEl = qs('#heroWName');
        var priceEl = qs('#heroWPrice');
        var changeEl = qs('#heroWChange');
        var highEl = qs('#wmHigh');
        var lowEl = qs('#wmLow');
        var rsiEl = qs('#wmRsi');

        if (nameEl && d) nameEl.textContent = d.name;
        if (priceEl && d) priceEl.textContent = d.price;
        if (changeEl && d) {
          changeEl.textContent = d.change;
          changeEl.className = 'wpr-change ' + (d.isUp ? 'up' : 'down');
        }
        if (highEl && d) highEl.textContent = d.high;
        if (lowEl && d) lowEl.textContent = d.low;
        if (rsiEl && d) rsiEl.textContent = d.rsi;
      });
    });

    // Timeframe buttons
    qsa('.tf-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.tf-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
      });
    });

    // Mode buttons (Line vs Candle)
    qsa('.cm-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.cm-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        chartMode = btn.getAttribute('data-mode');
      });
    });
  }

  /* =============================================================
     MAIN LIVE MARKET PULSE CHART (6 MARKETS)
     ============================================================= */
  var marketData = {
    nifty:  { name: 'NIFTY 50', price: '24,380.15', change: '+142.30 (+0.59%)', isUp: true,
               open: '24,238.00', high: '24,412.50', low: '24,198.30', prev: '24,237.85',
               pts: [24100, 24150, 24120, 24200, 24180, 24230, 24210, 24280, 24260, 24310, 24290, 24340, 24320, 24380] },
    sensex: { name: 'SENSEX', price: '80,210.35', change: '+482.10 (+0.60%)', isUp: true,
               open: '79,728.00', high: '80,350.20', low: '79,650.40', prev: '79,728.25',
               pts: [79500, 79600, 79550, 79720, 79680, 79800, 79780, 79900, 79860, 80000, 79960, 80100, 80080, 80210] },
    sp500:  { name: 'S&P 500', price: '5,540.20', change: '+28.40 (+0.51%)', isUp: true,
               open: '5,511.80', high: '5,548.30', low: '5,498.20', prev: '5,511.80',
               pts: [5510, 5505, 5520, 5518, 5530, 5525, 5538, 5530, 5535, 5542, 5535, 5540] },
    nasdaq: { name: 'NASDAQ 100', price: '19,820.50', change: '+110.30 (+0.56%)', isUp: true,
               open: '19,710.00', high: '19,860.20', low: '19,690.10', prev: '19,710.20',
               pts: [19700, 19680, 19720, 19700, 19750, 19740, 19780, 19760, 19800, 19790, 19820] },
    btc:    { name: 'Bitcoin / USD', price: '$64,250.00', change: '-410.00 (-0.63%)', isUp: false,
               open: '$64,660.00', high: '$65,100.00', low: '$64,100.00', prev: '$64,660.00',
               pts: [64900, 64800, 64650, 64700, 64400, 64500, 64300, 64250, 64280, 64240] },
    gold:   { name: 'Gold (USD/oz)', price: '$2,381.40', change: '+18.60 (+0.79%)', isUp: true,
               open: '$2,362.80', high: '$2,385.00', low: '$2,356.20', prev: '$2,362.80',
               pts: [2360, 2362, 2358, 2365, 2370, 2368, 2375, 2372, 2380, 2381] }
  };

  var currentMarket = 'nifty';
  var homeAnimOffset = 0;

  var homeCanvas = qs('#homeMainChart');
  if (homeCanvas) {
    var hCtx = homeCanvas.getContext('2d');

    function resizeHomeChart() {
      var dpr = window.devicePixelRatio || 1;
      var wrap = homeCanvas.parentElement;
      homeCanvas.width = wrap.clientWidth * dpr;
      homeCanvas.height = wrap.clientHeight * dpr;
      hCtx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resizeHomeChart);
    resizeHomeChart();

    function drawHomeChart() {
      var w = homeCanvas.parentElement.clientWidth;
      var h = homeCanvas.parentElement.clientHeight;
      hCtx.clearRect(0, 0, w, h);

      var d = marketData[currentMarket];
      var pts = d.pts.slice();
      homeAnimOffset += 0.04;
      pts[pts.length - 1] += Math.sin(homeAnimOffset) * (d.isUp ? 5 : -5);

      var mn = Math.min.apply(null, pts) - (pts[0] * 0.002);
      var mx = Math.max.apply(null, pts) + (pts[0] * 0.002);
      var rng = mx - mn || 1;

      // Grid
      hCtx.strokeStyle = 'rgba(255,255,255,0.03)';
      hCtx.lineWidth = 1;
      for (var gy = 0; gy < h; gy += h / 5) {
        hCtx.beginPath(); hCtx.moveTo(0, gy); hCtx.lineTo(w, gy); hCtx.stroke();
      }
      for (var gx = 0; gx < w; gx += w / 8) {
        hCtx.beginPath(); hCtx.moveTo(gx, 0); hCtx.lineTo(gx, h); hCtx.stroke();
      }

      var coords = pts.map(function (p, i) {
        return { x: (i / (pts.length - 1)) * w, y: h - 20 - ((p - mn) / rng) * (h - 40) };
      });

      var lc = d.isUp ? '#FF7A29' : '#F87171';
      var gc = d.isUp ? 'rgba(255,122,41,0.18)' : 'rgba(248,113,113,0.15)';

      // Area fill
      hCtx.beginPath();
      hCtx.moveTo(coords[0].x, h);
      hCtx.lineTo(coords[0].x, coords[0].y);
      for (var i2 = 1; i2 < coords.length; i2++) {
        var cp = coords[i2 - 1];
        var np = coords[i2];
        var mpx = (cp.x + np.x) / 2;
        hCtx.bezierCurveTo(mpx, cp.y, mpx, np.y, np.x, np.y);
      }
      hCtx.lineTo(w, h);
      hCtx.closePath();
      var areaGr = hCtx.createLinearGradient(0, 0, 0, h);
      areaGr.addColorStop(0, gc);
      areaGr.addColorStop(1, 'rgba(20,16,13,0)');
      hCtx.fillStyle = areaGr;
      hCtx.fill();

      // Line
      hCtx.beginPath();
      hCtx.moveTo(coords[0].x, coords[0].y);
      for (var i3 = 1; i3 < coords.length; i3++) {
        var cp3 = coords[i3 - 1];
        var np3 = coords[i3];
        var mpx3 = (cp3.x + np3.x) / 2;
        hCtx.bezierCurveTo(mpx3, cp3.y, mpx3, np3.y, np3.x, np3.y);
      }
      hCtx.strokeStyle = lc;
      hCtx.lineWidth = 2.5;
      hCtx.stroke();

      // Pulsing end dot
      var last = coords[coords.length - 1];
      hCtx.beginPath();
      hCtx.arc(last.x, last.y, 4.5, 0, Math.PI * 2);
      hCtx.fillStyle = lc;
      hCtx.fill();
      hCtx.beginPath();
      hCtx.arc(last.x, last.y, 9 + Math.sin(homeAnimOffset * 2) * 3, 0, Math.PI * 2);
      hCtx.strokeStyle = lc;
      hCtx.lineWidth = 1;
      hCtx.globalAlpha = 0.5;
      hCtx.stroke();
      hCtx.globalAlpha = 1;

      requestAnimationFrame(drawHomeChart);
    }
    requestAnimationFrame(drawHomeChart);

    // Tab buttons
    qsa('.hct-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        qsa('.hct-btn').forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');
        currentMarket = btn.getAttribute('data-market');
        var d = marketData[currentMarket];
        var name = qs('#homeChartName');
        var price = qs('#homeChartPrice');
        var change = qs('#homeChartChange');
        var csOpen = qs('#csOpen');
        var csHigh = qs('#csHigh');
        var csLow = qs('#csLow');
        var csPrev = qs('#csPrev');
        if (name) name.textContent = d.name;
        if (price) price.textContent = d.price;
        if (change) {
          change.textContent = d.change;
          change.className = 'hci-change ' + (d.isUp ? 'up' : 'down');
        }
        if (csOpen) csOpen.textContent = d.open;
        if (csHigh) csHigh.textContent = d.high;
        if (csLow) csLow.textContent = d.low;
        if (csPrev) csPrev.textContent = d.prev;
      });
    });
  }

  /* =============================================================
     RISK DONUT CHART
     ============================================================= */
  var donutCanvas = qs('#riskDonutChart');
  if (donutCanvas) {
    var dCtx = donutCanvas.getContext('2d');
    var donutW = donutCanvas.width;
    var donutH = donutCanvas.height;
    var donutCx = donutW / 2, donutCy = donutH / 2;
    var donutR = Math.min(donutW, donutH) * 0.44;
    var donutInner = donutR * 0.58;
    var donutAngle = 0;

    var segments = [
      { pct: 0.35, color: '#34D399', label: 'Low' },
      { pct: 0.40, color: '#FBBF24', label: 'Medium' },
      { pct: 0.25, color: '#F87171', label: 'High' }
    ];

    function drawDonut() {
      dCtx.clearRect(0, 0, donutW, donutH);
      donutAngle += 0.008;

      var start = -Math.PI / 2 + Math.sin(donutAngle * 0.3) * 0.06;
      segments.forEach(function (seg) {
        var end = start + seg.pct * Math.PI * 2;

        dCtx.beginPath();
        dCtx.arc(donutCx, donutCy, donutR, start, end);
        dCtx.arc(donutCx, donutCy, donutInner, end, start, true);
        dCtx.closePath();
        dCtx.fillStyle = seg.color;
        dCtx.fill();

        start = end;
      });

      // Center text
      dCtx.fillStyle = '#F5EFE8';
      dCtx.font = 'bold 20px "Space Grotesk", sans-serif';
      dCtx.textAlign = 'center';
      dCtx.textBaseline = 'middle';
      dCtx.fillText('Risk', donutCx, donutCy - 10);
      dCtx.font = '12px "JetBrains Mono", monospace';
      dCtx.fillStyle = '#A79A8C';
      dCtx.fillText('Allocation', donutCx, donutCy + 12);

      requestAnimationFrame(drawDonut);
    }
    requestAnimationFrame(drawDonut);
  }

  /* =============================================================
     ASSET CARD FILTER (watchlist)
     ============================================================= */
  qsa('.vw-filter-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      qsa('.vw-filter-btn').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var cat = btn.getAttribute('data-category');
      qsa('.vw-asset-card').forEach(function (card) {
        if (cat === 'all' || card.getAttribute('data-category') === cat) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  /* =============================================================
     NEWSLETTER FORM
     ============================================================= */
  var newsletterForm = qs('#vwNewsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = qs('#vwNewsletterNote');
      if (note) note.classList.add('visible');
    });
  }

  /* =============================================================
     LIVE QUOTE POLLING
     ============================================================= */
  var assetCards = qsa('.vw-asset-card[data-symbol]');
  if (assetCards.length > 0) {
    var symbols = Array.from(assetCards).map(function (c) { return c.getAttribute('data-symbol'); }).filter(Boolean);

    function refreshQuotes() {
      if (!symbols.length) return;
      fetch('/api/live-quotes?tickers=' + symbols.join(','))
        .then(function (r) { return r.json(); })
        .then(function (data) {
          assetCards.forEach(function (card) {
            var sym = card.getAttribute('data-symbol');
            if (!data[sym]) return;
            var q = data[sym];
            var priceEl = card.querySelector('.live-price-value');
            var changeEl = card.querySelector('.live-change-value');
            var arrowEl = card.querySelector('.live-arrow');
            var changeWrap = card.querySelector('.vw-asset-change');
            if (priceEl) priceEl.textContent = q.price.toLocaleString();
            if (changeEl) changeEl.textContent = q.change.toFixed(2);
            if (arrowEl) arrowEl.textContent = q.change >= 0 ? '▲' : '▼';
            if (changeWrap) {
              changeWrap.className = 'vw-asset-change ' + (q.change >= 0 ? 'up' : 'down');
            }
            card.classList.add('live-flash');
            setTimeout(function () { card.classList.remove('live-flash'); }, 700);
          });
        })
        .catch(function () {});
    }

    refreshQuotes();
    setInterval(refreshQuotes, 30000);
  }

})();
