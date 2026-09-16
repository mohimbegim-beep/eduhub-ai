/**
 * EduHub AI — PWA Install & Lifecycle Manager
 * Handles Service Worker registration, Android/Chrome Install Prompt, and iOS Safari Guide.
 */

(function () {
  let deferredPrompt = null;

  // Register Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/static/sw.js')
        .then((reg) => console.log('[PWA] ServiceWorker registered:', reg.scope))
        .catch((err) => console.warn('[PWA] ServiceWorker registration warning:', err));
    });
  }

  // Intercept beforeinstallprompt for Android / Desktop Chrome
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showPwaBanner();
  });

  function isIos() {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test(userAgent);
  }

  function isInStandaloneMode() {
    return ('standalone' in window.navigator && window.navigator.standalone) ||
           window.matchMedia('(display-mode: standalone)').matches;
  }

  function showPwaBanner() {
    if (isInStandaloneMode()) return;
    if (sessionStorage.getItem('eduhub_pwa_dismissed')) return;

    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
      banner.classList.remove('hidden');
      banner.classList.add('flex');
    }
  }

  window.EduHubPWA = {
    triggerInstall: function () {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            console.log('[PWA] User accepted install prompt');
            this.dismissBanner();
          }
          deferredPrompt = null;
        });
      } else if (isIos()) {
        // Show iOS Safari instruction modal
        const iosModal = document.getElementById('pwa-ios-modal');
        if (iosModal) {
          iosModal.classList.remove('hidden');
          iosModal.classList.add('flex');
        } else {
          alert("To install on iOS: Tap the Share button below, then select 'Add to Home Screen' (+).");
        }
      } else {
        alert("To install: Click your browser menu (⋮ or ⋯) and select 'Install app' or 'Add to Home Screen'.");
      }
    },

    dismissBanner: function () {
      const banner = document.getElementById('pwa-install-banner');
      if (banner) {
        banner.classList.add('hidden');
        banner.classList.remove('flex');
      }
      sessionStorage.setItem('eduhub_pwa_dismissed', 'true');
    },

    closeIosModal: function () {
      const iosModal = document.getElementById('pwa-ios-modal');
      if (iosModal) {
        iosModal.classList.add('hidden');
        iosModal.classList.remove('flex');
      }
    }
  };

  // Check on DOM ready if iOS not standalone
  document.addEventListener('DOMContentLoaded', () => {
    if (isIos() && !isInStandaloneMode() && !sessionStorage.getItem('eduhub_pwa_dismissed')) {
      // Show install banner on iOS after a brief delay
      setTimeout(showPwaBanner, 5000);
    }
  });
})();
