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
    CHECKOUT_URL_TRIAL: "https://test.checkout.dodopayments.com/buy/pdt_0NoI6L8G7azwANaxwZU4K?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html",
    CHECKOUT_URL_STARTER: "https://test.checkout.dodopayments.com/buy/pdt_0NoI5o1C5b1146SfNmJ0G?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html",
    CHECKOUT_URL_PROMAX: "https://test.checkout.dodopayments.com/buy/pdt_0NndXfFExcWaOMFk1ATxT?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html",
    CHECKOUT_URL_SPRINT: "https://test.checkout.dodopayments.com/buy/pdt_0NoI607WU6ofbWIn6oUQQ?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html",
    CHECKOUT_URL_TUTOR: "https://test.checkout.dodopayments.com/buy/pdt_0NoI6BT0oduXyGTfKHOZC?quantity=1&redirect_url=https://eduhub-ai.onrender.com%2Fstatic%2Fpayment-success.html",
    TICKER_INTERVAL_MS: 16000,
    TICKER_DISPLAY_MS: 6000,

    // Production Live Mode Active
    isBetaMode: false,

    isSubscribed: function () {
      if (this.isBetaMode) return true;
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
        
        // Forward Google Ads / Search UTM parameters to checkout metadata
        const pageParams = new URLSearchParams(window.location.search);
        ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(key => {
          const val = pageParams.get(key);
          if (val) {
            u.searchParams.set(`checkout[custom][${key}]`, val);
          }
        });

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
      } else if (tier === "promax" || tier === "promax_trial" || tier === "pro") {
        url = this.CHECKOUT_URL_PROMAX;
      } else if (tier === "sprint" || tier === "exam_sprint") {
        url = this.CHECKOUT_URL_SPRINT;
      } else if (tier === "tutor" || tier === "tutor_creator") {
        url = this.CHECKOUT_URL_TUTOR;
      }

      const finalUrl = this.buildCheckoutUrl(url);

      if (window.EduHubLegal && typeof window.EduHubLegal.openCheckoutModal === "function") {
        const dummyLink = document.createElement("a");
        dummyLink.href = finalUrl;
        window.EduHubLegal.openCheckoutModal(dummyLink);
        return;
      }
      window.location.href = finalUrl;
    },

    // ------------------------------------------------------------------------
    // 1. Exit-Intent Detection & Modal
    // ------------------------------------------------------------------------
    initExitIntent: function () {
      if (this.isBetaMode) return;
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
    startClimaxTimer: function (timerElementId) {
      let timerEnd = sessionStorage.getItem("eduhub_paywall_timer_end");
      const now = Date.now();
      if (!timerEnd || parseInt(timerEnd, 10) <= now) {
        timerEnd = now + 15 * 60 * 1000; // 15 minutes
        sessionStorage.setItem("eduhub_paywall_timer_end", timerEnd.toString());
      } else {
        timerEnd = parseInt(timerEnd, 10);
      }

      const updateDisplay = () => {
        const el = document.getElementById(timerElementId || "paywall-timer-countdown");
        if (!el) return;
        const remaining = Math.max(0, Math.floor((timerEnd - Date.now()) / 1000));
        const mins = String(Math.floor(remaining / 60)).padStart(2, "0");
        const secs = String(remaining % 60).padStart(2, "0");
        el.textContent = `${mins}:${secs}`;
        if (remaining <= 0) {
          timerEnd = Date.now() + 5 * 60 * 1000;
          sessionStorage.setItem("eduhub_paywall_timer_end", timerEnd.toString());
        }
      };

      updateDisplay();
      if (this._climaxTimerInterval) clearInterval(this._climaxTimerInterval);
      this._climaxTimerInterval = setInterval(updateDisplay, 1000);
    },

    initExamCountdown: function () {
      const daysEl = document.getElementById("exam-timer-days");
      if (!daysEl) return;
      const hoursEl = document.getElementById("exam-timer-hours");
      const minsEl = document.getElementById("exam-timer-mins");
      const secsEl = document.getElementById("exam-timer-secs");

      // Target: Next official Saturday exam date (October 17, 2026, 09:00 UTC)
      const targetDate = new Date("2026-10-17T09:00:00Z").getTime();

      const updateExamTimer = () => {
        const now = Date.now();
        let diff = Math.max(0, Math.floor((targetDate - now) / 1000));
        if (diff <= 0) {
          diff = 14 * 24 * 3600;
        }

        const days = Math.floor(diff / (24 * 3600));
        const hours = Math.floor((diff % (24 * 3600)) / 3600);
        const mins = Math.floor((diff % 3600) / 60);
        const secs = diff % 60;

        if (daysEl) daysEl.textContent = String(days).padStart(2, "0");
        if (hoursEl) hoursEl.textContent = String(hours).padStart(2, "0");
        if (minsEl) minsEl.textContent = String(mins).padStart(2, "0");
        if (secsEl) secsEl.textContent = String(secs).padStart(2, "0");
      };

      updateExamTimer();
      setInterval(updateExamTimer, 1000);
    },

    applyPaywallBlur: function (targetContainer, options = {}) {
      if (!targetContainer) return;
      if (this.isSubscribed()) return; // Paid users see full content!

      // Check if already blurred
      if (targetContainer.querySelector(".paywall-overlay-wrapper")) return;

      const children = Array.from(targetContainer.children);
      if (children.length === 0) return;

      let climaxIndex = -1;
      // 1. Look for headings or tables with climax keywords
      for (let i = 0; i < children.length; i++) {
        const child = children[i];
        const text = (child.textContent || "").toLowerCase();
        const isHeading = /^H[1-6]$/.test(child.tagName);
        if (isHeading && (text.includes("upgrade") || text.includes("rewrite") || text.includes("model") || text.includes("band 8") || text.includes("band 9") || text.includes("anki") || text.includes("collocation") || text.includes("step 3") || text.includes("solution") || text.includes("answer"))) {
          climaxIndex = i;
          break;
        }
        if (child.classList.contains("table-responsive-container") || child.tagName === "TABLE") {
          climaxIndex = i;
          break;
        }
      }

      // 2. If no explicit keyword heading found, blur after initial 45% of elements
      if (climaxIndex === -1) {
        if (children.length > 2) {
          climaxIndex = Math.max(1, Math.floor(children.length * 0.45));
        } else {
          climaxIndex = children.length - 1;
        }
      }

      const elementsToBlur = children.slice(climaxIndex);
      if (elementsToBlur.length === 0) return;

      const wrapper = document.createElement("div");
      wrapper.className = "paywall-overlay-wrapper relative my-6 rounded-3xl overflow-hidden border border-amber-500/50 bg-slate-900/90 shadow-2xl backdrop-blur-md";

      // Create blurred copy of content
      const blurredBox = document.createElement("div");
      blurredBox.className = "filter blur-md select-none pointer-events-none opacity-25 p-6 space-y-4 max-h-[520px] overflow-hidden";
      elementsToBlur.forEach(el => {
        blurredBox.appendChild(el.cloneNode(true));
      });

      // Create interactive glassmorphism Climax overlay
      const overlay = document.createElement("div");
      overlay.className = "absolute inset-0 z-10 flex flex-col items-center justify-center p-6 sm:p-8 bg-slate-950/85 backdrop-blur-md text-center";
      overlay.innerHTML = `
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/40 text-[11px] font-black uppercase tracking-wider mb-2.5 shadow-sm">
          <span>🔥</span> <span data-i18n="paywall_locked_badge">Band 8.5+ Model Rewrite Unlock</span>
        </div>

        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-bold mb-3 shadow-inner">
          <span>⚡</span>
          <span data-i18n="paywall_timer_label">Special 15-Minute Exam Clinic Offer:</span>
          <span id="paywall-timer-countdown" class="font-mono font-black text-amber-400 tracking-wider text-sm sm:text-base">14:59</span>
        </div>

        <h3 class="text-xl sm:text-2xl font-black text-white mb-2 leading-snug tracking-tight max-w-xl" data-i18n="paywall_locked_title">
          Unlock Full High-Band (8.5+) Rewrite &amp; Anki Deck
        </h3>

        <p class="text-slate-300 text-xs sm:text-sm max-w-lg mb-4 leading-relaxed" data-i18n="paywall_locked_desc">
          See exact examiner-level sentences, paragraph-by-paragraph replacements, and download ready-to-study vocabulary decks.
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left text-xs text-slate-200 mb-5 max-w-xl mx-auto w-full">
          <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2">
            <span>✍️</span> <span data-i18n="paywall_feat_rewrite">Complete Band 8.5–9.0 Native Examiner Essay Rewrite</span>
          </div>
          <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2">
            <span>🎯</span> <span data-i18n="paywall_feat_notes">Paragraph-by-paragraph C1/C2 Lexical Upgrades</span>
          </div>
          <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2">
            <span>📥</span> <span data-i18n="paywall_feat_anki">1-Click Anki Deck Export (40+ Collocations)</span>
          </div>
          <div class="flex items-center gap-2 bg-slate-900/90 border border-slate-800 rounded-xl px-3 py-2">
            <span>🛡️</span> <span data-i18n="paywall_guarantee">14-Day Money-Back Guarantee</span>
          </div>
        </div>

        <button onclick="EduHubConversion.triggerCheckout('trial')" class="w-full sm:w-auto px-8 py-3.5 rounded-xl font-black text-sm sm:text-base text-slate-950 bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-500 hover:brightness-110 shadow-xl shadow-amber-500/30 transition transform hover:-translate-y-0.5 cursor-pointer">
          <span data-i18n="paywall_locked_btn">Unlock for Just $1.00 (3-Day Pro Pass) &rarr;</span>
        </button>

        <button type="button" onclick="EduHubConversion.openRewardedAdModal()" class="mt-2.5 text-xs text-amber-300 hover:text-amber-200 underline font-medium cursor-pointer transition flex items-center justify-center gap-1.5 mx-auto">
          <span data-i18n="paywall_watch_ad_btn">🎬 Watch 20s Sponsor Message to Preview Free</span>
        </button>

        <div class="mt-3 flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-400">
          <span class="flex items-center gap-1 text-emerald-400 font-medium">🛡️ <span data-i18n="banner_guarantee_badge">100% 14-Day Money-Back Guarantee</span></span>
          <span>•</span>
          <span data-i18n="paywall_locked_sub">Instant activation. Cancel anytime in 1 click.</span>
        </div>
        <p class="mt-2 text-[11px] text-amber-400/90 font-medium" data-i18n="paywall_social_proof">🔥 Over 1,240 students upgraded their essays to Band 7.5+ this week</p>
      `;

      wrapper.appendChild(blurredBox);
      wrapper.appendChild(overlay);

      const firstEl = elementsToBlur[0];
      firstEl.parentNode.insertBefore(wrapper, firstEl);
      elementsToBlur.forEach(el => el.remove());

      this.startClimaxTimer("paywall-timer-countdown");

      if (window.applyTranslations) {
        window.applyTranslations();
      }
    },

    openRewardedAdModal: function () {
      let modal = document.getElementById("rewarded-ad-modal");
      if (!modal) {
        modal = document.createElement("div");
        modal.id = "rewarded-ad-modal";
        modal.className = "fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md hidden";
        modal.innerHTML = `
          <div class="bg-slate-900 border border-amber-500/40 rounded-3xl max-w-lg w-full p-6 sm:p-7 shadow-2xl relative text-center">
            <button onclick="EduHubConversion.closeRewardedAdModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-lg font-bold p-1">✕</button>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30 text-[11px] font-black uppercase tracking-wider mb-3">
              <span>📢</span> <span data-i18n="sponsor_modal_title">Official Education Partner Spotlight</span>
            </div>
            <h3 class="text-lg sm:text-xl font-black text-white mb-2" data-i18n="sponsor_partner_title">
              Cambridge &amp; IELTS Official Preparation Partner
            </h3>
            <p class="text-xs text-slate-300 mb-4 leading-relaxed" data-i18n="sponsor_partner_desc">
              Book 1-on-1 intensive speaking &amp; mock test sessions with certified native British &amp; American examiners. 70% off your first diagnostic trial.
            </p>
            
            <div class="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 mb-4 text-left flex items-center gap-3.5">
              <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-600 to-amber-500 flex items-center justify-center text-2xl shrink-0">
                🇬🇧
              </div>
              <div class="flex-grow">
                <span class="text-[10px] text-amber-400 font-bold uppercase tracking-wider block" data-i18n="sponsor_card_label">Sponsored Resource</span>
                <p class="text-xs font-bold text-white">Preply &middot; Certified IELTS Examiners</p>
                <p class="text-[11px] text-slate-400" data-i18n="partner_verified_badge">Verified Academic Partner</p>
              </div>
              <a href="https://preply.com" target="_blank" rel="noopener noreferrer" class="shrink-0 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 px-3.5 py-2 rounded-xl transition" data-i18n="sponsor_partner_cta">
                Visit Partner &amp; Claim 70% Discount &rarr;
              </a>
            </div>

            <div class="bg-slate-950 border border-slate-800 rounded-xl p-3 mb-4 flex items-center justify-between text-xs">
              <div class="flex items-center gap-2 text-slate-300">
                <span>⏳</span> <span data-i18n="sponsor_timer_prefix">Reward unlock ready in:</span>
              </div>
              <span id="rewarded-ad-countdown" class="font-mono font-black text-amber-400 text-sm">20s</span>
            </div>

            <button id="rewarded-claim-btn" onclick="EduHubConversion.claimFreePreview()" disabled class="w-full py-3 rounded-xl font-bold text-xs sm:text-sm bg-slate-800 text-slate-500 cursor-not-allowed transition">
              <span data-i18n="sponsor_claim_btn">Claim Free Preview Paragraph ✓</span>
            </button>
          </div>
        `;
        document.body.appendChild(modal);
      }

      modal.classList.remove("hidden");
      modal.classList.add("flex");

      if (window.applyTranslations) {
        window.applyTranslations();
      }

      let timeLeft = 20;
      const countEl = document.getElementById("rewarded-ad-countdown");
      const claimBtn = document.getElementById("rewarded-claim-btn");
      if (claimBtn) {
        claimBtn.disabled = true;
        claimBtn.className = "w-full py-3 rounded-xl font-bold text-xs sm:text-sm bg-slate-800 text-slate-500 cursor-not-allowed transition";
      }

      if (this._rewardedTimer) clearInterval(this._rewardedTimer);
      this._rewardedTimer = setInterval(() => {
        timeLeft--;
        if (countEl) countEl.textContent = timeLeft + "s";
        if (timeLeft <= 0) {
          clearInterval(this._rewardedTimer);
          if (countEl) countEl.textContent = "Ready! ✓";
          if (claimBtn) {
            claimBtn.disabled = false;
            claimBtn.className = "w-full py-3 rounded-xl font-black text-xs sm:text-sm bg-gradient-to-r from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 hover:brightness-110 cursor-pointer transition transform hover:-translate-y-0.5";
          }
        }
      }, 1000);
    },

    closeRewardedAdModal: function () {
      const modal = document.getElementById("rewarded-ad-modal");
      if (modal) {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      }
      if (this._rewardedTimer) clearInterval(this._rewardedTimer);
    },

    claimFreePreview: function () {
      this.closeRewardedAdModal();
      const blurredBox = document.querySelector(".paywall-overlay-wrapper .filter.blur-md");
      if (blurredBox && blurredBox.children.length > 0) {
        const first = blurredBox.children[0];
        const previewBlock = document.createElement("div");
        previewBlock.className = "p-4 mb-4 rounded-2xl bg-slate-800/90 border border-emerald-500/50 text-left text-xs text-slate-200 shadow-xl";
        previewBlock.innerHTML = `
          <div class="flex items-center gap-1.5 text-emerald-400 font-bold mb-2 text-[11px] uppercase tracking-wider">
            <span>✓</span> <span data-i18n="preview_unlocked_label">Free Preview Unlocked (1 Section)</span>
          </div>
          <div>${first.innerHTML}</div>
        `;
        const wrapper = document.querySelector(".paywall-overlay-wrapper");
        if (wrapper && wrapper.parentNode) {
          wrapper.parentNode.insertBefore(previewBlock, wrapper);
        }
      }
      try {
        localStorage.setItem("eduhub_rewarded_preview_claimed", "true");
      } catch (e) {}
    },

    grantFreeAccess: function (role) {
      this.setSubscribed(true);
      try {
        localStorage.setItem("eduhub_user_tier", "pro_max");
        localStorage.setItem("eduhub_user_role", role || "founder");
      } catch (e) {}
      console.log("[EduHub VIP] Free Pro Max Lifetime Access Granted!");
      return true;
    }
  };

  // Expose globally
  window.EduHubConversion = EduHubConversion;

  // Auto-init on DOM ready
  document.addEventListener("DOMContentLoaded", () => {
    EduHubConversion.initExitIntent();
    EduHubConversion.initSocialTicker();
    EduHubConversion.initExamCountdown();

    // Check if user has VIP, Founder, or Payment Success URL flags
    const s = (window.location.search || "").toLowerCase();
    if (s.includes("payment=success") || s.includes("trial=activated") || 
        s.includes("vip=") || s.includes("access=founder") || 
        s.includes("role=founder") || s.includes("free=true") || 
        s.includes("free=1")) {
      EduHubConversion.grantFreeAccess("founder");
    }
  });
})();
