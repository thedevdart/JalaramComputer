(function () {
  var SPLASH_KEY = 'jc_splash_seen';
  var splash = document.getElementById('jc-splash');
  if (!splash) return;

  try {
    if (sessionStorage.getItem(SPLASH_KEY) === '1') {
      splash.remove();
      return;
    }
  } catch (e) {}

  document.body.classList.add('jc-splash-active');

  function dismiss() {
    if (splash.classList.contains('is-hidden')) return;
    splash.classList.add('is-hidden');
    document.body.classList.remove('jc-splash-active');
    try { sessionStorage.setItem(SPLASH_KEY, '1'); } catch (e) {}
    setTimeout(function () {
      if (splash.parentNode) splash.parentNode.removeChild(splash);
    }, 700);
  }

  var skip = document.getElementById('jc-splash-skip');
  if (skip) skip.addEventListener('click', dismiss);

  splash.addEventListener('click', function (e) {
    if (e.target === splash || e.target.closest('.jc-splash__inner')) dismiss();
  });

  setTimeout(dismiss, 2800);
})();
