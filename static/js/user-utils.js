/**
 * EduHub AI — Essential User Utilities
 * 1. Export actions: Copy Text, Download PDF, Export DOCX.
 * 2. Session history auto-save to localStorage with "Recent Documents" slide-over drawer.
 * 3. Streaming/animated step progress indicator during processing.
 * 4. Mobile camera direct upload trigger for homework photos.
 */

const EduHubUtils = (function () {
  const HISTORY_KEY = "eduhub_user_history_v1";

  // --------------------------------------------------------------------------
  // 1. Export Actions: Copy, PDF, DOCX
  // --------------------------------------------------------------------------
  function copyText(targetId, btnEl) {
    const el = document.getElementById(targetId);
    if (!el) return;
    const text = el.innerText || el.textContent;
    navigator.clipboard.writeText(text).then(() => {
      if (btnEl) {
        const originalHtml = btnEl.innerHTML;
        btnEl.innerHTML = `<span>✓</span> <span>${(window.t && window.t('btn_copied')) || 'Copied!'}</span>`;
        btnEl.classList.add('text-emerald-400');
        setTimeout(() => {
          btnEl.innerHTML = originalHtml;
          btnEl.classList.remove('text-emerald-400');
        }, 2000);
      }
    });
  }

  function downloadPDF(targetId, docTitle) {
    const el = document.getElementById(targetId);
    if (!el) return;
    const title = docTitle || 'EduHub_Academic_Analysis';
    const contentHtml = el.innerHTML;

    const printWin = window.open('', '_blank', 'width=850,height=900');
    if (!printWin) {
      alert("Please allow popups to download/print PDF.");
      return;
    }

    printWin.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>${title}</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
        <style>
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
            padding: 40px;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
          }
          .header {
            border-bottom: 2px solid #2563eb;
            padding-bottom: 12px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
          }
          .header h1 { font-size: 20px; color: #1e3a8a; margin: 0; }
          .header span { font-size: 11px; color: #64748b; }
          .footer {
            margin-top: 40px;
            border-top: 1px solid #e2e8f0;
            padding-top: 12px;
            font-size: 10px;
            color: #94a3b8;
            text-align: center;
          }
          table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 12px; }
          th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }
          th { background-color: #f1f5f9; font-weight: 600; }
          code, pre { font-family: monospace; background: #f8fafc; padding: 2px 4px; border-radius: 4px; font-size: 11px; }
          pre { padding: 12px; border: 1px solid #e2e8f0; overflow-x: auto; }
          blockquote { border-left: 4px solid #3b82f6; margin: 12px 0; padding-left: 12px; color: #475569; font-style: italic; }
          @media print {
            body { padding: 20px; }
            .no-print { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <h1>EduHub AI — Academic Analysis</h1>
            <span>Verified Socratic Copilot • Generated on ${new Date().toLocaleDateString()}</span>
          </div>
          <button class="no-print" onclick="window.print()" style="padding: 6px 14px; background: #2563eb; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600;">Print / Save PDF</button>
        </div>
        <div class="content">${contentHtml}</div>
        <div class="footer">
          Generated autonomously by EduHub AI (https://eduhub.ai) • Strict 18+ Safe Academic Filter • Merchant: PCI-DSS Compliant Processor
        </div>
        <script>
          setTimeout(() => { window.print(); }, 400);
        </script>
      </body>
      </html>
    `);
    printWin.document.close();
  }

  function exportDOCX(targetId, docTitle) {
    const el = document.getElementById(targetId);
    if (!el) return;
    const title = (docTitle || 'EduHub_Academic_Analysis').replace(/[^a-zA-Z0-9_-]/g, '_');
    const contentHtml = el.innerHTML;

    // Build Word-compatible HTML package (.doc)
    const docxContent = `
      <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
      <head>
        <meta charset='utf-8'>
        <title>${title}</title>
        <style>
          body { font-family: Calibri, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #111827; }
          h1 { font-size: 18pt; color: #1e3a8a; }
          h2 { font-size: 14pt; color: #1d4ed8; }
          h3 { font-size: 12pt; color: #374151; }
          table { border-collapse: collapse; width: 100%; margin: 12pt 0; }
          th, td { border: 1pt solid #9ca3af; padding: 6pt; text-align: left; }
          th { background-color: #f3f4f6; font-weight: bold; }
          p { margin: 6pt 0; }
        </style>
      </head>
      <body>
        <p style="font-size: 9pt; color: #6b7280; border-bottom: 1pt solid #d1d5db; padding-bottom: 4pt;">
          <strong>EduHub AI Academic Diagnostic</strong> | Generated on ${new Date().toLocaleString()}
        </p>
        <div>${contentHtml}</div>
        <p style="font-size: 8pt; color: #9ca3af; margin-top: 24pt; border-top: 1pt solid #e5e7eb; padding-top: 4pt;">
          EduHub AI Autonomous Platform • Confidential Student Record • Safe Content Filter
        </p>
      </body>
      </html>
    `;

    const blob = new Blob(['\ufeff', docxContent], {
      type: 'application/msword;charset=utf-8'
    });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${title}.doc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  }

  // --------------------------------------------------------------------------
  // 2. Auto-Save Session History & "Recent Documents" Slide-over Drawer
  // --------------------------------------------------------------------------
  function getHistory() {
    try {
      const data = localStorage.getItem(HISTORY_KEY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      return [];
    }
  }

  function saveHistoryItem(item) {
    try {
      const history = getHistory();
      const newItem = {
        id: 'doc_' + Date.now() + '_' + Math.random().toString(36).substring(2, 6),
        timestamp: new Date().toISOString(),
        title: item.title || 'Academic Analysis',
        type: item.type || 'general',
        preview: (item.preview || item.content || '').substring(0, 120) + '...',
        content: item.content || '',
        meta: item.meta || {}
      };
      // Prepend and limit to 25 items
      history.unshift(newItem);
      const trimmed = history.slice(0, 25);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
      updateHistoryBadge();
      renderHistoryDrawer();
      return newItem;
    } catch (e) {
      console.warn('[USER UTILS] History save error:', e);
    }
  }

  function deleteHistoryItem(id) {
    const history = getHistory().filter(item => item.id !== id);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    updateHistoryBadge();
    renderHistoryDrawer();
  }

  function clearAllHistory() {
    if (confirm("Are you sure you want to clear your local session history?")) {
      localStorage.removeItem(HISTORY_KEY);
      updateHistoryBadge();
      renderHistoryDrawer();
    }
  }

  function updateHistoryBadge() {
    const history = getHistory();
    document.querySelectorAll('[data-history-count]').forEach(el => {
      el.textContent = history.length.toString();
      if (history.length > 0) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    });
  }

  function renderHistoryDrawer() {
    const listEl = document.getElementById('history-drawer-list');
    if (!listEl) return;
    const history = getHistory();

    if (history.length === 0) {
      listEl.innerHTML = `
        <div class="text-center py-12 px-4 text-slate-500 text-xs">
          <span class="text-3xl block mb-2">📂</span>
          <p>${(window.t && window.t('recent_empty')) || 'No saved documents yet. Run an analysis to auto-save.'}</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = history.map(item => {
      const dateStr = new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      return `
        <div class="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-4 transition group">
          <div class="flex justify-between items-start gap-2 mb-1.5">
            <span class="text-[10px] font-bold uppercase tracking-wider text-blue-400 bg-blue-950/80 border border-blue-800/60 px-2 py-0.5 rounded-md">
              ${item.type}
            </span>
            <span class="text-[10px] text-slate-500">${dateStr}</span>
          </div>
          <h4 class="text-xs font-semibold text-white group-hover:text-blue-300 transition line-clamp-1 mb-1">${item.title}</h4>
          <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-3">${item.preview}</p>
          <div class="flex items-center justify-between border-t border-slate-800/80 pt-2.5">
            <button onclick="EduHubUtils.loadHistoryItem('${item.id}')" class="text-[11px] text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1 transition">
              <span>↗</span> Load Into Workspace
            </button>
            <button onclick="EduHubUtils.deleteHistoryItem('${item.id}')" class="text-[11px] text-slate-500 hover:text-rose-400 transition" title="Delete">
              ✕
            </button>
          </div>
        </div>
      `;
    }).join('');
  }

  function loadHistoryItem(id) {
    const item = getHistory().find(x => x.id === id);
    if (!item) return;

    // Check what page we are on and inject content into active workspace
    const aiInput = document.getElementById('ai-input');
    const responseDiv = document.getElementById('ai-response');
    const resultBox = document.getElementById('ai-result-box');

    const textInput = document.getElementById('text-input');
    const outputBox = document.getElementById('output-container');
    const outputText = document.getElementById('output-text');

    const assignmentInput = document.getElementById('assignment-input');

    if (aiInput && responseDiv && resultBox) {
      aiInput.value = item.title;
      resultBox.classList.remove('hidden');
      if (window.renderAcademicDocument) {
        window.renderAcademicDocument(item.content, responseDiv);
      } else {
        responseDiv.textContent = item.content;
      }
      closeHistoryDrawer();
      responseDiv.scrollIntoView({ behavior: 'smooth' });
    } else if (textInput && outputBox && outputText) {
      textInput.value = item.title;
      outputBox.classList.remove('hidden');
      if (window.renderAcademicDocument) {
        window.renderAcademicDocument(item.content, outputText);
      } else {
        outputText.textContent = item.content;
      }
      closeHistoryDrawer();
      outputBox.scrollIntoView({ behavior: 'smooth' });
    } else if (assignmentInput && outputBox && outputText) {
      assignmentInput.value = item.title;
      outputBox.classList.remove('hidden');
      if (window.renderAcademicDocument) {
        window.renderAcademicDocument(item.content, outputText);
      } else {
        outputText.textContent = item.content;
      }
      closeHistoryDrawer();
      outputBox.scrollIntoView({ behavior: 'smooth' });
    }
  }

  function openHistoryDrawer() {
    renderHistoryDrawer();
    const drawer = document.getElementById('history-drawer');
    const backdrop = document.getElementById('history-backdrop');
    if (drawer) drawer.classList.remove('translate-x-full');
    if (backdrop) backdrop.classList.remove('hidden');
  }

  function closeHistoryDrawer() {
    const drawer = document.getElementById('history-drawer');
    const backdrop = document.getElementById('history-backdrop');
    if (drawer) drawer.classList.add('translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
  }

  // --------------------------------------------------------------------------
  // 3. Streaming / Animated Step Progress Indicator
  // --------------------------------------------------------------------------
  let stepperInterval = null;

  function startStepper(containerId, customStages) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const stages = customStages || [
      { id: 1, text: (window.t && window.t('stepper_ingest')) || "📥 Ingesting & tokenizing document...", pct: 25 },
      { id: 2, text: (window.t && window.t('stepper_safety')) || "🛡️ Verifying Safe Content Filter & citations...", pct: 55 },
      { id: 3, text: (window.t && window.t('stepper_reason')) || "🧠 Socratic synthesis via Gemini 2.5 Flash...", pct: 85 },
      { id: 4, text: (window.t && window.t('stepper_finalize')) || "✨ Formatting responsive tables & formulas...", pct: 98 }
    ];

    container.classList.remove('hidden');
    container.innerHTML = `
      <div class="p-5 bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl my-4 space-y-4">
        <div class="flex justify-between items-center text-xs">
          <span id="stepper-stage-title" class="font-bold text-blue-400 flex items-center gap-2">
            <svg class="animate-spin h-3.5 w-3.5 text-blue-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
            </svg>
            <span>${stages[0].text}</span>
          </span>
          <span id="stepper-pct" class="font-mono text-slate-400 font-semibold">25%</span>
        </div>
        
        <!-- Animated Progress Bar -->
        <div class="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800/80">
          <div id="stepper-bar" class="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-500 ease-out" style="width: 25%"></div>
        </div>

        <!-- Stages Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          ${stages.map((st, i) => `
            <div id="step-pill-${i}" class="p-2 rounded-xl border border-slate-800/80 bg-slate-950/60 text-[10px] text-slate-400 flex items-center gap-1.5 transition">
              <span class="step-icon text-xs">${i === 0 ? '⏳' : '○'}</span>
              <span class="truncate">${st.text.split(' ')[1] || 'Step'}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    let currentStageIndex = 0;
    clearInterval(stepperInterval);
    stepperInterval = setInterval(() => {
      if (currentStageIndex < stages.length - 1) {
        // Mark current as done
        const prevPill = document.getElementById(`step-pill-${currentStageIndex}`);
        if (prevPill) {
          prevPill.className = "p-2 rounded-xl border border-emerald-800/60 bg-emerald-950/30 text-[10px] text-emerald-300 flex items-center gap-1.5 transition";
          const icon = prevPill.querySelector('.step-icon');
          if (icon) icon.textContent = '✓';
        }

        currentStageIndex++;
        const st = stages[currentStageIndex];
        const bar = document.getElementById('stepper-bar');
        const title = document.getElementById('stepper-stage-title');
        const pct = document.getElementById('stepper-pct');
        const curPill = document.getElementById(`step-pill-${currentStageIndex}`);

        if (bar) bar.style.width = st.pct + '%';
        if (pct) pct.textContent = st.pct + '%';
        if (title) {
          const span = title.querySelector('span');
          if (span) span.textContent = st.text;
        }
        if (curPill) {
          curPill.className = "p-2 rounded-xl border border-blue-600/70 bg-blue-950/50 text-[10px] text-blue-200 font-semibold flex items-center gap-1.5 transition";
          const icon = curPill.querySelector('.step-icon');
          if (icon) icon.textContent = '⏳';
        }
      }
    }, 1200);
  }

  function stopStepper(containerId) {
    clearInterval(stepperInterval);
    const container = document.getElementById(containerId);
    if (!container) return;
    const bar = document.getElementById('stepper-bar');
    const pct = document.getElementById('stepper-pct');
    if (bar) bar.style.width = '100%';
    if (pct) pct.textContent = '100%';
    setTimeout(() => {
      container.classList.add('hidden');
    }, 400);
  }

  // --------------------------------------------------------------------------
  // 4. Mobile Camera Direct Upload Trigger for Homework Photos
  // --------------------------------------------------------------------------
  let attachedPhotoBase64 = null;

  function initCameraTrigger(buttonId, fileInputId, previewContainerId) {
    const btn = document.getElementById(buttonId);
    const input = document.getElementById(fileInputId);
    const preview = document.getElementById(previewContainerId);

    if (!btn || !input) return;

    btn.addEventListener('click', () => {
      input.click();
    });

    input.addEventListener('change', (e) => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;

      if (!file.type.startsWith('image/')) {
        alert('Please select or photograph an image file.');
        return;
      }

      const reader = new FileReader();
      reader.onload = (loadEvt) => {
        const fullBase64 = loadEvt.target.result;
        attachedPhotoBase64 = fullBase64;

        if (preview) {
          preview.classList.remove('hidden');
          preview.innerHTML = `
            <div class="flex items-center justify-between p-3 bg-slate-950/90 border border-indigo-700/60 rounded-2xl shadow-lg">
              <div class="flex items-center gap-3">
                <img src="${fullBase64}" alt="Homework Photo" class="w-12 h-12 object-cover rounded-xl border border-indigo-500/60 shadow">
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-bold text-white">${file.name || 'Homework Photo'}</span>
                    <span class="text-[10px] bg-emerald-950 text-emerald-300 border border-emerald-700/60 px-2 py-0.5 rounded-full font-medium">📷 Camera OCR Ready</span>
                  </div>
                  <span class="text-[10px] text-slate-400">${(file.size / 1024).toFixed(1)} KB • Multi-Modal Socratic Vision</span>
                </div>
              </div>
              <button type="button" onclick="EduHubUtils.removeAttachedPhoto('${previewContainerId}', '${fileInputId}')" class="text-xs text-rose-400 hover:text-rose-300 p-2 font-bold transition" title="Remove Photo">
                ✕ Remove
              </button>
            </div>
          `;
        }
      };
      reader.readAsDataURL(file);
    });
  }

  function removeAttachedPhoto(previewContainerId, fileInputId) {
    attachedPhotoBase64 = null;
    const preview = document.getElementById(previewContainerId);
    const input = document.getElementById(fileInputId);
    if (preview) preview.classList.add('hidden');
    if (input) input.value = '';
  }

  function getAttachedPhoto() {
    return attachedPhotoBase64;
  }

  function exportAnkiDeck(cardsOrData, deckName) {
    const name = (deckName || 'EduHub_Vocabulary_Deck').replace(/[^a-zA-Z0-9_-]/g, '_');
    let tsvContent = "#separator:tab\n#html:true\n#deck:" + name + "\n#tags column:3\n";
    
    if (Array.isArray(cardsOrData)) {
      cardsOrData.forEach(card => {
        const front = (card.front || card.term || card.word || '').toString().trim().replace(/\t/g, ' ').replace(/\n/g, '<br>');
        const back = (card.back || card.definition || card.meaning || '').toString().trim().replace(/\t/g, ' ').replace(/\n/g, '<br>');
        const tags = (card.tags || card.collocation || name).toString().trim().replace(/\t/g, ' ').replace(/\s+/g, '_');
        if (front && back) {
          tsvContent += `${front}\t${back}\t${tags}\n`;
        }
      });
    } else if (typeof cardsOrData === 'string') {
      tsvContent += cardsOrData.trim() + "\n";
    }

    const blob = new Blob(['\ufeff', tsvContent], {
      type: 'text/tab-separated-values;charset=utf-8'
    });

    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${name}_anki.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
    return true;
  }

  // Auto-init badges on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    updateHistoryBadge();
  });

  return {
    copyText,
    downloadPDF,
    exportDOCX,
    exportAnkiDeck,
    getHistory,
    saveHistoryItem,
    deleteHistoryItem,
    clearAllHistory,
    updateHistoryBadge,
    renderHistoryDrawer,
    openHistoryDrawer,
    closeHistoryDrawer,
    loadHistoryItem,
    startStepper,
    stopStepper,
    initCameraTrigger,
    removeAttachedPhoto,
    getAttachedPhoto,
    openTelegramBotWithAuth,
    getActiveLocale,
    showErrorToast,
    fetchAIWithTimeout
  };

  // --------------------------------------------------------------------------
  // AI Request AbortController & Error Toast Notifications
  // --------------------------------------------------------------------------
  function showErrorToast(message, durationMs) {
    const text = message || "ИИ-модель временно перегружена. Пожалуйста, попробуйте еще раз через минуту.";
    let toast = document.getElementById("eduhub-error-toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "eduhub-error-toast";
      toast.className = "fixed top-6 right-4 sm:right-6 z-50 max-w-md bg-slate-900/95 border border-rose-500/40 text-slate-100 px-4 py-3 rounded-2xl shadow-2xl backdrop-blur-md flex items-start gap-3 transition-all duration-300 transform translate-y-0 opacity-100";
      document.body.appendChild(toast);
    }

    toast.innerHTML = `
      <div class="w-6 h-6 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center shrink-0 mt-0.5 text-xs font-black">✕</div>
      <div class="flex-grow">
        <div class="text-xs font-bold text-rose-300">Внимание</div>
        <div class="text-[11px] text-slate-300 mt-0.5 leading-snug">${text}</div>
      </div>
      <button onclick="this.parentElement.classList.add('hidden')" class="text-slate-400 hover:text-white text-xs px-1">✕</button>
    `;
    toast.classList.remove("hidden");

    if (toast._timer) clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.classList.add("hidden");
    }, durationMs || 5000);
  }

  async function fetchAIWithTimeout(url, fetchOptions, timeoutMs) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs || 20000);

    try {
      const response = await fetch(url, {
        ...(fetchOptions || {}),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.status === "error") {
        const errorMsg = data.message || "ИИ-модель временно перегружена. Пожалуйста, попробуйте еще раз через минуту.";
        return { success: false, status: "error", message: errorMsg, data };
      }
      return { success: true, status: "success", data };
    } catch (err) {
      clearTimeout(timeoutId);
      let errorMsg = "ИИ-модель временно перегружена. Пожалуйста, попробуйте еще раз через минуту.";
      if (err.name === "AbortError") {
        errorMsg = "Превышено время ожидания ответа ИИ (20 секунд). Попробуйте еще раз.";
      }
      return { success: false, status: "error", message: errorMsg, originalError: err };
    }
  }

  function getActiveLocale() {
    try {
      if (typeof window.getCurrentLocale === 'function') {
        const loc = window.getCurrentLocale();
        if (loc) return String(loc).toLowerCase();
      }
      const stored = localStorage.getItem('eduhub_locale');
      if (stored) return String(stored).toLowerCase();
    } catch (e) {}
    return 'uz';
  }

  function openTelegramBotWithAuth(e, botUsername) {
    if (e && e.preventDefault) e.preventDefault();
    const username = botUsername || 'eduhub_ielts_bot';
    let token = localStorage.getItem('eduhub_session_token') || localStorage.getItem('eduhub_user_email') || '';
    if (!token) {
      token = 'usr_' + Math.random().toString(36).substring(2, 10);
      localStorage.setItem('eduhub_session_token', token);
    }
    const cleanToken = encodeURIComponent(token.replace(/[^a-zA-Z0-9_-]/g, ''));
    const url = 'https://t.me/' + username + '?start=auth_' + cleanToken;
    window.open(url, '_blank', 'noopener,noreferrer');
  }
})();

if (typeof window !== 'undefined' && typeof EduHubUtils !== 'undefined') {
  window.getActiveLocale = EduHubUtils.getActiveLocale;
}

// Privacy-Preserving Lightweight Telemetry Beacon
(function () {
  try {
    const searchParams = new URLSearchParams(window.location.search);
    const payload = {
      path: window.location.pathname,
      referrer: document.referrer || "Direct",
      utm_source: searchParams.get("utm_source") || undefined,
      utm_medium: searchParams.get("utm_medium") || undefined,
      screen: `${window.innerWidth}x${window.innerHeight}`
    };
    if (navigator.sendBeacon) {
      navigator.sendBeacon("/api/v1/analytics/track", new Blob([JSON.stringify(payload)], { type: "application/json" }));
    } else {
      fetch("/api/v1/analytics/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        keepalive: true
      }).catch(function () {});
    }
  } catch (e) {}
})();


