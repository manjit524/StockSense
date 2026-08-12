(function () {
  var navToggle = document.getElementById('vwNavToggle');
  var navLinks = document.getElementById('vwNavLinks');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });
  }

  var filterButtons = document.querySelectorAll('.vw-filter-btn');
  var assetCards = document.querySelectorAll('.vw-asset-card');
  filterButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterButtons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var category = btn.dataset.category;
      assetCards.forEach(function (card) {
        var show = category === 'all' || card.dataset.category === category;
        card.style.display = show ? '' : 'none';
      });
    });
  });

  var newsletterForm = document.getElementById('vwNewsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = document.getElementById('vwNewsletterNote');
      if (note) note.classList.add('visible');
    });
  }
})();
