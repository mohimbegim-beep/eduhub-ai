/**
 * EduHub AI — Omni-Channel Viral Engine
 * Features:
 * 1. 1-Click WhatsApp Share (with formatted text & URL for LatAm, US, EU)
 * 2. 1-Click Telegram Share (with localized preview for CIS, Central Asia)
 * 3. Native Web Share API (navigator.share for Instagram, iMessage, Discord, Reddit)
 * 4. HTML5 Canvas Stories Badge Generator (Creates high-res downloadable Instagram/Telegram Stories image)
 */

(function () {
  const EduHubShare = {
    getBaseUrl: function () {
      return window.location.origin + window.location.pathname;
    },

    getShareUrl: function () {
      const ref = localStorage.getItem('eduhub_ref_id') || 'student_' + Math.random().toString(36).substring(2, 7);
      const url = new URL(this.getBaseUrl());
      url.searchParams.set('ref', ref);
      return url.toString();
    },

    getLocalizedText: function (customTitle) {
      const lang = document.documentElement.lang || 'en';
      const title = customTitle || (window.t ? window.t('share_default_title') : 'Check out EduHub AI');
      
      if (lang === 'ru') {
        return `🔥 Я использую EduHub AI для учебы и экзаменов (IELTS, математика, конспекты с ИИ по методу Сократа). Попробуй бесплатно:`;
      } else if (lang === 'uz') {
        return `🔥 Men o'qish va imtihonlar (IELTS, matematika va konspektlar) uchun EduHub AI-dan foydalanmoqdaman. Bepul sinab ko'ring:`;
      } else if (lang === 'es') {
        return `🔥 Estoy usando EduHub AI para preparar exámenes (IELTS, matemáticas y ensayos con IA socrática). Pruébalo gratis aquí:`;
      } else {
        return `🔥 I'm using EduHub AI to ace my exams (IELTS essays, STEM homework, and Socratic AI tutor). Try it free here:`;
      }
    },

    // 1. WhatsApp Share
    shareToWhatsApp: function (customTitle) {
      const text = encodeURIComponent(this.getLocalizedText(customTitle) + ' ' + this.getShareUrl());
      window.open(`https://api.whatsapp.com/send?text=${text}`, '_blank');
    },

    // 2. Telegram Share
    shareToTelegram: function (customTitle) {
      const url = encodeURIComponent(this.getShareUrl());
      const text = encodeURIComponent(this.getLocalizedText(customTitle));
      window.open(`https://t.me/share/url?url=${url}&text=${text}`, '_blank');
    },

    // 3. Native Web Share API
    shareNative: async function (title, text) {
      const shareData = {
        title: title || 'EduHub AI — Academic Super-Copilot',
        text: text || this.getLocalizedText(title),
        url: this.getShareUrl()
      };

      if (navigator.share) {
        try {
          await navigator.share(shareData);
          console.log('[SHARE] Native share completed');
        } catch (err) {
          if (err.name !== 'AbortError') {
            this.copyLink();
          }
        }
      } else {
        this.copyLink();
      }
    },

    // 4. Copy Referral Link
    copyLink: function () {
      const url = this.getShareUrl();
      if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(() => {
          this.showToast((window.t ? window.t('share_copied') : 'Referral link copied to clipboard! 📋'));
        });
      } else {
        prompt('Copy your link:', url);
      }
    },

    // 5. Generate Instagram / Telegram Stories Badge via HTML5 Canvas
    generateStoriesCard: function (scoreText, categoryName) {
      const canvas = document.createElement('canvas');
      canvas.width = 1080;
      canvas.height = 1920;
      const ctx = canvas.getContext('2d');

      // Background Gradient
      const grad = ctx.createLinearGradient(0, 0, 1080, 1920);
      grad.addColorStop(0, '#030712');
      grad.addColorStop(0.5, '#0f172a');
      grad.addColorStop(1, '#020617');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 1080, 1920);

      // Accent Glowing Circles
      ctx.beginPath();
      ctx.arc(200, 300, 250, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
      ctx.fill();

      ctx.beginPath();
      ctx.arc(880, 1500, 300, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(245, 158, 11, 0.12)';
      ctx.fill();

      // Card Container
      ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.4)';
      ctx.lineWidth = 4;
      this.roundRect(ctx, 100, 360, 880, 1200, 48);
      ctx.fill();
      ctx.stroke();

      // EduHub AI Brand Header
      ctx.fillStyle = '#60a5fa';
      ctx.font = 'bold 44px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('🎓 EDUHUB AI • ACADEMIC VERIFIED', 540, 490);

      // Score / Achievement Headline
      ctx.fillStyle = '#f8fafc';
      ctx.font = '900 84px sans-serif';
      ctx.fillText(scoreText || 'Estimated Band 8.0', 540, 680);

      // Category / Rubric Badge
      ctx.fillStyle = '#f59e0b';
      ctx.font = '600 48px sans-serif';
      ctx.fillText(categoryName || 'Cambridge Examiner Scoring', 540, 780);

      // Divider Line
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.8)';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(200, 860);
      ctx.lineTo(880, 860);
      ctx.stroke();

      // Features checkmarks
      ctx.font = '500 38px sans-serif';
      ctx.fillStyle = '#94a3b8';
      ctx.textAlign = 'left';
      ctx.fillText('✓ Task Achievement & Socratic Scaffolding', 240, 970);
      ctx.fillText('✓ High-Yield Academic Vocabulary (Anki-Ready)', 240, 1070);
      ctx.fillText('✓ 100% Verified Cambridge Official Rubric', 240, 1170);
      ctx.fillText('✓ 24/7 Socrates AI Academic Copilot', 240, 1270);

      // CTA Box
      ctx.fillStyle = '#2563eb';
      this.roundRect(ctx, 200, 1370, 680, 110, 28);
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 42px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Test Your Essay Free → eduhub.ai', 540, 1440);

      // Footer
      ctx.fillStyle = '#64748b';
      ctx.font = '400 32px sans-serif';
      ctx.fillText('Scan & Share with #EduHubAI', 540, 1680);

      // Download / Open
      const dataUrl = canvas.toDataURL('image/png');
      const win = window.open();
      if (win) {
        win.document.write(`<img src="${dataUrl}" style="max-width:100%; height:auto;" alt="Stories Badge"><p style="color:#333; font-family:sans-serif; text-align:center;">Long-press or right-click to save and share to Stories!</p>`);
      } else {
        const link = document.createElement('a');
        link.download = 'EduHub_Achievement_Stories.png';
        link.href = dataUrl;
        link.click();
      }
    },

    roundRect: function (ctx, x, y, width, height, radius) {
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
    },

    showToast: function (msg) {
      let toast = document.getElementById('share-toast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'share-toast';
        toast.className = 'fixed top-6 right-6 z-50 bg-blue-600 text-white font-bold text-xs px-4 py-2.5 rounded-xl shadow-xl transition-all duration-300 transform translate-y-0 opacity-100';
        document.body.appendChild(toast);
      }
      toast.textContent = msg;
      toast.classList.remove('hidden');
      setTimeout(() => {
        toast.classList.add('hidden');
      }, 3000);
    }
  };

  window.EduHubShare = EduHubShare;
})();
