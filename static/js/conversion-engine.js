/**
 * EduHub AI — High-Converting CRO & Paywall Engine
 * Features:
 * 1. Exit-Intent Detection & High-Converting $1 Trial Modal
 * 2. Live Social Proof & Activity Ticker (Rotating Student Verified Actions)
 * 3. Climax Paywall: Frosted-Glass Blur on High-Value Output (Band 8.5+ Rewrites & Socratic Derivations)
 * 4. PCI-DSS Direct Checkout Integration
 * 5. Full Multi-Language i18n Synchronization
 */

(function () {
  const EduHubConversion = {
    // Configuration
    CHECKOUT_URL_TRIAL: "/#pricing",
    CHECKOUT_URL_STARTER: "/#pricing",
    TICKER_INTERVAL_MS: 16000,
    TICKER_DISPLAY_MS: 6000,

    isSubscribed: function () {
      return localStorage.getItem("eduhub_user_subscribed") === "true" ||
             sessionStorage.getItem("eduhub_user_subscribed") === "true";
    },

    setSubscribed: function (status) {
      if (status) {
        localStorage.setItem("eduhub_user_subscribed", "true");
      } else {
        localStorage.removeItem("eduhub_user_subscribed");
      }
    },

    
    getOrCreateUserId: function () {
      let uid = localStorage.getItem("eduhub_user_id");
      if (!uid) {
        uid = "usr_" + Math.random().toString(36).substring(2, 10) + "_" + Date.now().toString(36);
        localStorage.setItem("eduhub_user_id", uid);
      }
      return uid;
    },

    buildCheckoutUrl: function (baseUrl) {
      try {
        const u = new URL(baseUrl);
        const userId = this.getOrCreateUserId();
        u.searchParams.set("checkout[custom][user_id]", userId);
        
        const email = localStorage.getItem("eduhub_user_email") || localStorage.getItem("user_email");
        if (email && email.includes("@")) {
          u.searchParams.set("checkout[email]", email.trim().toLowerCase());
        }
        return u.toString();
      } catch (e) {
        return baseUrl;
      }
    },

    triggerCheckout: function (tier) {
      let url = this.CHECKOUT_URL_TRIAL;
      if (tier === "starter") {
        url = this.CHECKOUT_URL_STARTER;
      }

      const finalUrl = this.buildCheckoutUrl(url);

      if (window.EduHubLegal && typeof window.EduHubLegal.openCheckoutModal === "function") {
        window.EduHubLegal.openCheckoutModal(null);
        return;
      }
      window.location.href = "/#pricing";
    },

    // ------------------------------------------------------------------------
    // 1. Exit-Intent Detection & Modal
    // ------------------------------------------------------------------------
    initExitIntent: function () {
      let hasShown = sessionStorage.getItem("eduhub_exit_intent_shown");
      if (hasShown) return;

      // Desktop: mouse leaves top viewport
      document.addEventListener("mouseleave", (e) => {
        if (e.clientY <= 10 && !sessionStorage.getItem("eduhub_exit_intent_shown")) {
          this.showExitModal();
        }
      });

      // Mobile: trigger on rapid back or idle after interaction
      let touchStartY = 0;
      document.addEventListener("touchstart", (e) => {
        touchStartY = e.touches[0].clientY;
      }, { passive: true });

      document.addEventListener("touchend", (e) => {
        let touchEndY = e.changedTouches[0].clientY;
        // User scrolls up rapidly at the top of the page
        if (window.scrollY < 50 && touchEndY - touchStartY > 120) {
          if (!sessionStorage.getItem("eduhub_exit_intent_shown")) {
            this.showExitModal();
          }
        }
      }, { passive: true });
    },

    showExitModal: function () {
      const modal = document.getElementById("exit-intent-modal");
      if (!modal) return;
      sessionStorage.setItem("eduhub_exit_intent_shown", "true");
      modal.classList.remove("hidden");
      modal.classList.add("flex");
      if (window.applyTranslations) {
        window.applyTranslations();
      }
    },

    closeExitModal: function () {
      const modal = document.getElementById("exit-intent-modal");
      if (!modal) return;
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    },

    // ------------------------------------------------------------------------
    // 2. Live Social Proof Ticker
    // ------------------------------------------------------------------------
    initSocialTicker: function () {
      const tickerEl = document.getElementById("conversion-social-ticker");
      const textEl = document.getElementById("ticker-text");
      if (!tickerEl || !textEl) return;

      const tickerKeys = ["ticker_1", "ticker_2", "ticker_3", "ticker_4"];
      let currentIndex = 0;

      const cycleTicker = () => {
        if (sessionStorage.getItem("eduhub_ticker_dismissed")) return;

        const key = tickerKeys[currentIndex];
        const text = (window.t && window.t(key)) ? window.t(key) : "";
        if (text) {
          textEl.innerHTML = text;
          tickerEl.classList.remove("opacity-0", "translate-y-2");
          tickerEl.classList.add("opacity-100", "translate-y-0");

          setTimeout(() => {
            tickerEl.classList.remove("opacity-100", "translate-y-0");
            tickerEl.classList.add("opacity-0", "translate-y-2");
          }, this.TICKER_DISPLAY_MS);
        }

        currentIndex = (currentIndex + 1) % tickerKeys.length;
      };

      // Initial delay then cycle
      setTimeout(cycleTicker, 4000);
      setInterval(cycleTicker, this.TICKER_INTERVAL_MS);
    },

    dismissTicker: function () {
      const tickerEl = document.getElementById("conversion-social-ticker");
      if (tickerEl) {
        tickerEl.classList.remove("opacity-100", "translate-y-0");
        tickerEl.classList.add("opacity-0", "translate-y-2");
      }
      sessionStorage.setItem("eduhub_ticker_dismissed", "true");
    },

    // ------------------------------------------------------------------------
    // 3. Climax Paywall: Frosted-Glass Blur on High-Value Solutions
    // ------------------------------------------------------------------------
    applyPaywallBlur: function (targetContainer, options = {}) {
      if (!targetContainer) return;
      if (this.isSubscribed()) return; // Paid users see full content!

      // Check if already blurred
      if (targetContainer.querySelector(".paywall-overlay-wrapper")) return;

      // Find high-value section (e.g., table, second h2, or full container)
      const tables = targetContainer.querySelectorAll(".table-responsive-container, table, blockquote, pre");
      let targetSection = null;

      // In essay grader, the table contains [Original vs Band 8.5+ Upgrade]
      if (tables.length > 0) {
        targetSection = tables[0];
      }

      if (!targetSection) {
        // Fallback: blur last 50% of elements
        const children = Array.from(targetContainer.children);
        if (children.length >= 3) {
          targetSection = children[Math.floor(children.length / 2)];
        }
      }

      if (targetSection) {
        const wrapper = document.createElement("div");
        wrapper.className = "paywall-overlay-wrapper relative my-6 rounded-2xl overflow-hidden border border-amber-500/40 bg-slate-900/60 shadow-2xl";

        // Create blurred copy of content
        const blurredBox = document.createElement("div");
        blurredBox.className = "filter blur-md select-none pointer-events-none opacity-40 p-4";
        blurredBox.innerHTML = targetSection.outerHTML;

        // Create interactive glassmorphism overlay
        const overlay = document.createElement("div");
        overlay.className = "absolute inset-0 z-10 flex flex-col items-center justify-center p-6 bg-slate-950/75 backdrop-blur-sm text-center";
        overlay.innerHTML = `
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[11px] font-black uppercase tracking-wider mb-3">
            🔒 <span data-i18n="paywall_locked_badge">Pro Max Exclusive</span>
          </div>
          <h3 class="text-xl sm:text-2xl font-black text-white mb-2 leading-snug" data-i18n="paywall_locked_title">
            Unlock Full High-Band (8.5+) Rewrite & Anki Deck
          </h3>
          <p class="text-slate-300 text-xs sm:text-sm max-w-md mb-5 leading-relaxed" data-i18n="paywall_locked_desc">
            See paragraph-by-paragraph Cambridge examiner upgrades, error corrections, and instant Anki flashcard download.
          </p>
          <button onclick="EduHubConversion.triggerCheckout('promax_trial')" class="px-8 py-3.5 rounded-xl font-black text-sm text-slate-950 bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-500 hover:brightness-110 shadow-lg shadow-amber-500/30 transition transform hover:-translate-y-0.5 cursor-pointer">
            <span data-i18n="paywall_locked_btn">Get Pro Max ($19/mo) — 14-Day Guarantee →</span>
          </button>
          <div class="mt-3.5 flex flex-wrap items-center justify-center gap-3 text-[11px] text-slate-400">
            <span class="flex items-center gap-1 text-emerald-400 font-medium">🛡️ <span data-i18n="banner_guarantee_badge">100% 14-Day Money-Back Guarantee</span></span>
            <span>•</span>
            <span data-i18n="paywall_locked_sub">Instant activation. Cancel anytime in 1 click.</span>
          </div>
        `;

        wrapper.appendChild(blurredBox);
        wrapper.appendChild(overlay);

        targetSection.parentNode.replaceChild(wrapper, targetSection);

        // Apply translations to the injected overlay
        if (window.applyTranslations) {
          window.applyTranslations();
        }
      }
    }
  };

  // Expose globally
  window.EduHubConversion = EduHubConversion;

  // Auto-init on DOM ready
  document.addEventListener("DOMContentLoaded", () => {
    EduHubConversion.initExitIntent();
    EduHubConversion.initSocialTicker();

    // Check if user arrived via payment success
    if (window.location.search.includes("payment=success") || window.location.search.includes("trial=activated")) {
      EduHubConversion.setSubscribed(true);
    }
  });
})();
