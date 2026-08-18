(function () {
  // Generic tab switcher — powers both the login/signup tabs and the
  // Markets page tabs (any .auth-tab/.market-tab + matching .auth-panel/.market-panel)
  function wireTabs(tabSelector, panelSelector, activeClass) {
    var tabs = document.querySelectorAll(tabSelector);
    var panels = document.querySelectorAll(panelSelector);
    tabs.forEach(function (btn) {
      btn.addEventListener('click', function () {
        tabs.forEach(function (b) { b.classList.remove(activeClass); });
        panels.forEach(function (p) { p.classList.remove(activeClass); });
        btn.classList.add(activeClass);
        var target = document.getElementById(btn.dataset.target);
        if (target) target.classList.add(activeClass);
      });
    });
  }

  wireTabs('.auth-tab', '.auth-panel', 'active');
  wireTabs('.market-tab', '.market-panel', 'active');

  // Demo forms (login/signup/contact) have no backend wired up — show a
  // friendly inline note instead of silently doing nothing on submit.
  var demoForms = document.querySelectorAll('[data-demo-form]');
  demoForms.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.querySelector('.form-note');
      if (note) note.classList.add('visible');
    });
  });

  // --------------------------------------------------------------------
  // LIVE PRICE POLLING — any element with data-symbol gets its
  // .live-price-value / .live-change-value / .live-arrow contents updated
  // on a timer by calling /api/live-quotes.
  // --------------------------------------------------------------------
  var POLL_INTERVAL_MS = 15000;

  function collectSymbols() {
    var symbols = new Set();
    document.querySelectorAll('[data-symbol]').forEach(function (el) {
      var s = el.getAttribute('data-symbol');
      if (s) symbols.add(s);
    });
    return Array.from(symbols);
  }

  function applyQuotes(quotes) {
    var now = new Date();
    var timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    document.querySelectorAll('[data-symbol]').forEach(function (el) {
      var symbol = el.getAttribute('data-symbol');
      var q = quotes[symbol];
      if (!q) return;

      var priceEl = el.querySelector('.live-price-value');
      if (priceEl) priceEl.textContent = q.price.toFixed(2);

      var changeEl = el.querySelector('.live-change-value');
      if (changeEl) changeEl.textContent = Math.abs(q.change).toFixed(2);

      var arrowEl = el.querySelector('.live-arrow');
      if (arrowEl) arrowEl.textContent = q.change >= 0 ? '▲' : '▼';

      var isUp = q.change >= 0;
      el.classList.toggle('trend-up', isUp);
      el.classList.toggle('trend-down', !isUp);
      el.classList.toggle('up', isUp);
      el.classList.toggle('down', !isUp);

      el.classList.add('live-flash');
      setTimeout(function () { el.classList.remove('live-flash'); }, 700);
    });

    document.querySelectorAll('.live-updated-time').forEach(function (el) {
      el.textContent = timeStr;
    });
  }

  function pollLiveQuotes() {
    var symbols = collectSymbols();
    if (symbols.length === 0) return;

    fetch('/api/live-quotes?tickers=' + encodeURIComponent(symbols.join(',')))
      .then(function (res) { return res.json(); })
      .then(applyQuotes)
      .catch(function () { /* silent — the next poll will retry */ });
  }

  if (document.querySelector('[data-symbol]')) {
    pollLiveQuotes();
    setInterval(pollLiveQuotes, POLL_INTERVAL_MS);
  }

  // --------------------------------------------------------------------
  // TICKER AUTOCOMPLETE — Reports page symbol search
  // --------------------------------------------------------------------
  var searchInput = document.getElementById('ticker-search');
  var dropdown = document.getElementById('ticker-dropdown');
  var symbolField = document.getElementById('ticker-symbol');
  var exchangeField = document.getElementById('ticker-exchange');
  var searchDebounce = null;

  if (searchInput && dropdown) {
    searchInput.addEventListener('input', function () {
      var q = searchInput.value.trim();
      clearTimeout(searchDebounce);
      if (q.length < 1) { dropdown.innerHTML = ''; dropdown.classList.remove('open'); return; }

      searchDebounce = setTimeout(function () {
        fetch('/api/search-tickers?q=' + encodeURIComponent(q))
          .then(function (r) { return r.json(); })
          .then(function (results) {
            dropdown.innerHTML = '';
            if (!results.length) { dropdown.classList.remove('open'); return; }
            results.forEach(function (r) {
              var item = document.createElement('div');
              item.className = 'autocomplete-item';
              item.textContent = r.label + ' · ' + r.exchange;
              item.addEventListener('click', function () {
                searchInput.value = r.symbol;
                symbolField.value = r.symbol;
                exchangeField.value = r.exchange;
                dropdown.innerHTML = '';
                dropdown.classList.remove('open');
              });
              dropdown.appendChild(item);
            });
            dropdown.classList.add('open');
          })
          .catch(function () {});
      }, 250);
    });

    document.addEventListener('click', function (e) {
      if (!dropdown.contains(e.target) && e.target !== searchInput) {
        dropdown.classList.remove('open');
      }
    });
  }

  // Fallback: if the user types a symbol and hits Generate without ever
  // clicking a dropdown suggestion, the hidden symbol/exchange fields would
  // otherwise stay empty and the form would silently submit nothing. Fill
  // them from the typed text right before submit.
  var reportForm = document.getElementById('report-form');
  if (reportForm && searchInput && symbolField) {
    reportForm.addEventListener('submit', function (e) {
      if (!symbolField.value.trim() && searchInput.value.trim()) {
        symbolField.value = searchInput.value.trim().toUpperCase();
        if (exchangeField && !exchangeField.value) {
          exchangeField.value = 'NSE';
        }
      }
      if (!symbolField.value.trim()) {
        e.preventDefault();
        searchInput.focus();
        searchInput.style.borderColor = 'var(--risk-high)';
      }
    });
  }

  // --------------------------------------------------------------------
  // TABLE SEARCH FILTER — Markets page ETF / Mutual Fund search boxes.
  // Client-side row filtering for tables already on the page (ETFs);
  // for Mutual Funds it also queries the search API since the full
  // ~40k-scheme directory isn't all rendered up front.
  // --------------------------------------------------------------------
  function wireLocalTableFilter(inputId, tableBodyId) {
    var input = document.getElementById(inputId);
    var tbody = document.getElementById(tableBodyId);
    if (!input || !tbody) return;
    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      Array.from(tbody.rows).forEach(function (row) {
        row.style.display = row.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
      });
    });
  }

  wireLocalTableFilter('etf-search', 'etf-table-body');

  var mfSearchInput = document.getElementById('mf-search');
  var mfTableBody = document.getElementById('mf-table-body');
  var mfSearchDebounce = null;

  if (mfSearchInput && mfTableBody) {
    mfSearchInput.addEventListener('input', function () {
      var q = mfSearchInput.value.trim();
      clearTimeout(mfSearchDebounce);
      mfSearchDebounce = setTimeout(function () {
        if (q.length < 2) return; // let the default 100 keep showing for short queries
        fetch('/api/mutual-funds/search?q=' + encodeURIComponent(q))
          .then(function (r) { return r.json(); })
          .then(function (results) {
            mfTableBody.innerHTML = '';
            if (!results.length) {
              mfTableBody.innerHTML = '<tr><td colspan="3">No matching funds found.</td></tr>';
              return;
            }
            results.forEach(function (f) {
              var tr = document.createElement('tr');
              var navText = f.nav !== null ? '₹' + f.nav.toFixed(4) : '—';
              tr.innerHTML = '<td>' + f.name + '</td><td class="mono">' + navText + '</td><td class="mono">' + f.date + '</td>';
              mfTableBody.appendChild(tr);
            });
          })
          .catch(function () {});
      }, 350);
    });
  }

  // --------------------------------------------------------------------
  // THEME SWITCHER (Ultra-Smooth Aurora Circular Bloom Transition)
  // --------------------------------------------------------------------
  var themeToggleBtn = document.getElementById('themeToggleBtn');

  function getPreferredTheme() {
    var saved = localStorage.getItem('theme');
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function (e) {
      var current = document.documentElement.getAttribute('data-theme') || getPreferredTheme();
      var next = (current === 'light') ? 'dark' : 'light';

      // Visual button ripple feedback
      themeToggleBtn.classList.add('theme-pulsing');
      setTimeout(function () { themeToggleBtn.classList.remove('theme-pulsing'); }, 750);

      // Check if browser supports document.startViewTransition for circular aurora wipe
      if (document.startViewTransition) {
        var rect = themeToggleBtn.getBoundingClientRect();
        var x = e.clientX || (rect.left + rect.width / 2);
        var y = e.clientY || (rect.top + rect.height / 2);
        var endRadius = Math.hypot(
          Math.max(x, window.innerWidth - x),
          Math.max(y, window.innerHeight - y)
        );

        var transition = document.startViewTransition(function () {
          applyTheme(next);
        });

        transition.ready.then(function () {
          var clipPath = [
            'circle(0px at ' + x + 'px ' + y + 'px)',
            'circle(' + endRadius + 'px at ' + x + 'px ' + y + 'px)'
          ];
          document.documentElement.animate(
            {
              clipPath: clipPath
            },
            {
              duration: 720,
              easing: 'cubic-bezier(0.16, 1, 0.3, 1)',
              pseudoElement: '::view-transition-new(root)'
            }
          );
        });
      } else {
        // Fallback smooth transition
        applyTheme(next);
      }
    });
  }

  // Listen to system preference changes if user hasn't explicitly set preference
  try {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      if (!localStorage.getItem('theme')) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  } catch (e) {}
})();
