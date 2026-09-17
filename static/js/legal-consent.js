/**
 * EduHub AI — Trust & Legal Micro-Consent Layer
 * Features:
 * 1. Floating Cookie & Legal Consent Bar with localStorage persistence.
 * 2. Mandatory Pre-Checkout Legal Consent Gate (Interactive Checkbox Modal) ensuring 100% indisputable consent before payment.
 * 3. Contextual checkout micro-consent captions across all pricing cards and CTA buttons.
 * 4. Multi-language parity across 4 locales (EN, RU, UZ, ES).
 */

const EduHubLegal = (function() {
    const COOKIE_CONSENT_KEY = 'cookie_consent';
    const CHECKOUT_CONSENT_KEY = 'checkout_legal_confirmed';

    let pendingCheckoutElement = null;

    const DICTIONARY = {
        en: {
            cookie_msg: "We use cookies for security and personalization. By continuing to use EduHub AI, you agree to our <a href='/terms' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Terms of Service</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Privacy Policy</a>, and <a href='/refund' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Refund Policy</a>.",
            cookie_btn: "Accept & Continue",
            micro_consent: "By clicking, you agree to the <a href='/terms' target='_blank' class='underline text-slate-300 hover:text-white'>Terms of Service</a> and our <a href='/refund' target='_blank' class='underline text-slate-300 hover:text-white'>14-day money-back guarantee</a>. Cancel anytime in 1 click.",
            modal_badge: "Legal Confirmation & Consumer Assurance",
            modal_title: "Review Order & 14-Day Refund Guarantee",
            modal_b1: "<strong>14-Day 100% Guarantee:</strong> Full refund if requested within 14 days via 1-click AI portal at /support or mohim.mohimbegim@gmail.com.",
            modal_b2: "<strong>Fee-Protected Transparency:</strong> Voluntary card refunds returned net of non-recoverable payment gateway fees (~5%), or receive +120% instant wallet credit bonus.",
            modal_b3: "<strong>Subscription Management:</strong> Cancel recurring billing anytime in 1 click from your dashboard with zero penalty.",
            modal_chk: "I have read and agree to the <a href='/terms' target='_blank' class='underline text-blue-400 font-semibold'>Terms of Service</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 font-semibold'>Privacy Policy</a>, and <a href='/refund' target='_blank' class='underline text-blue-400 font-semibold'>Refund Policy</a>.",
            modal_confirm: "Confirm & Proceed to Secure Checkout →",
            modal_cancel: "Cancel & Return to Site",
            modal_warn: "⚠️ Please check the box to confirm you accept the refund terms before proceeding."
        },
        ru: {
            cookie_msg: "Мы используем cookies для безопасности и персонализации. Продолжая использовать EduHub AI, вы соглашаетесь с <a href='/terms' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Условиями обслуживания</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Политикой конфиденциальности</a> и <a href='/refund' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Политикой возвратов</a>.",
            cookie_btn: "Принять и продолжить",
            micro_consent: "Нажимая кнопку, вы принимаете <a href='/terms' target='_blank' class='underline text-slate-300 hover:text-white'>Условия оферты</a> и <a href='/refund' target='_blank' class='underline text-slate-300 hover:text-white'>14-дневную гарантию возврата</a>. Отмена подписки в 1 клик в любое время.",
            modal_badge: "Правовое подтверждение и защита покупателя",
            modal_title: "Подтверждение условий заказа и 14-дневной гарантии возврата",
            modal_b1: "<strong>14-дневная 100% гарантия возврата:</strong> Полный возврат при обращении в течение 14 дней в 1 клик на /support или через mohim.mohimbegim@gmail.com.",
            modal_b2: "<strong>Прозрачные условия:</strong> При добровольном возврате на карту возвращается сумма за вычетом комиссии эквайринга (~5%), либо начисляется 120% на баланс.",
            modal_b3: "<strong>Управление подпиской:</strong> Автопродление можно отключить в любое время в 1 клик в личном кабинете без каких-либо комиссий.",
            modal_chk: "Я прочитал и безоговорочно принимаю <a href='/terms' target='_blank' class='underline text-blue-400 font-semibold'>Условия обслуживания</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 font-semibold'>Политику конфиденциальности</a> и <a href='/refund' target='_blank' class='underline text-blue-400 font-semibold'>Политику возвратов</a>.",
            modal_confirm: "Подтверждаю и перейти к безопасной оплате →",
            modal_cancel: "Отмена и вернуться на сайт",
            modal_warn: "⚠️ Пожалуйста, отметьте галочку согласия с условиями возврата для продолжения."
        },
        uz: {
            cookie_msg: "Xavfsizlik va shaxsiylashtirish uchun cookies fayllaridan foydalanamiz. EduHub AI dan foydalanishni davom ettirish orqali siz <a href='/terms' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Xizmat ko\'rsatish shartlari</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Maxfiylik siyosati</a> va <a href='/refund' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Qaytarish siyosati</a>ga rozilik bildirasiz.",
            cookie_btn: "Qabul qilish va davom etish",
            micro_consent: "Tugmani bosish orqali siz <a href='/terms' target='_blank' class='underline text-slate-300 hover:text-white'>Ommaviy oferta shartlari</a> va <a href='/refund' target='_blank' class='underline text-slate-300 hover:text-white'>14 kunlik to\'lovni qaytarish kafolati</a>ni qabul qilasiz. Obunani istalgan vaqtda 1 bosishda bekor qilish mumkin.",
            modal_badge: "Huquqiy tasdiqlash va xaridor himoyasi",
            modal_title: "Buyurtma shartlari va 14 kunlik qaytarish kafolatini tasdiqlash",
            modal_b1: "<strong>14 kunlik 100% kafolat:</strong> 14 kun ichida murojaat qilinganda /support portalida 1 bosishda to\'liq qaytariladi.",
            modal_b2: "<strong>Shaffof hisob-kitob:</strong> Kartaga ixtiyoriy qaytarishda bank ekvayring xarajatlari (~5%) chegiriladi yoki balansga 120% bonus beriladi.",
            modal_b3: "<strong>Obunani boshqarish:</strong> Obunani istalgan vaqtda shaxsiy kabinetda jarimalarsiz 1 bosishda bekor qilish mumkin.",
            modal_chk: "Men <a href='/terms' target='_blank' class='underline text-blue-400 font-semibold'>Xizmat ko\'rsatish shartlari</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 font-semibold'>Maxfiylik siyosati</a> va <a href='/refund' target='_blank' class='underline text-blue-400 font-semibold'>Qaytarish siyosati</a> bilan tanishdim va roziman.",
            modal_confirm: "Tasdiqlayman va xavfsiz to\'lovga o\'tish →",
            modal_cancel: "Bekor qilish va saytga qaytish",
            modal_warn: "⚠️ Davom etish uchun to\'lovni qaytarish shartlariga rozilik bildirish katakchasini belgilang."
        },
        es: {
            cookie_msg: "Utilizamos cookies para seguridad y personalización. Al continuar utilizando EduHub AI, aceptas nuestros <a href='/terms' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Términos de servicio</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Política de privacidad</a> y <a href='/refund' target='_blank' class='underline text-blue-400 hover:text-blue-300 font-medium'>Política de reembolsos</a>.",
            cookie_btn: "Aceptar y continuar",
            micro_consent: "Al hacer clic, aceptas los <a href='/terms' target='_blank' class='underline text-slate-300 hover:text-white'>Términos del servicio</a> y nuestra <a href='/refund' target='_blank' class='underline text-slate-300 hover:text-white'>garantía de reembolso de 14 días</a>. Cancela en cualquier momento con 1 clic.",
            modal_badge: "Confirmación Legal y Protección del Comprador",
            modal_title: "Confirmación de Pedido y Garantía de Reembolso de 14 Días",
            modal_b1: "<strong>Garantía de 14 Días 100%:</strong> Reembolso íntegro solicitándolo en los primeros 14 días mediante el portal /support o en mohim.mohimbegim@gmail.com.",
            modal_b2: "<strong>Transparencia de Costos:</strong> Reversión voluntaria a tarjeta deduciendo gastos no recuperables de pasarela (~5%), o +120% en saldo monedero.",
            modal_b3: "<strong>Gestión de Suscripción:</strong> Cancela la renovación automática en cualquier momento con 1 clic desde tu panel sin penalizaciones.",
            modal_chk: "He leído y acepto expresamente los <a href='/terms' target='_blank' class='underline text-blue-400 font-semibold'>Términos de servicio</a>, <a href='/privacy' target='_blank' class='underline text-blue-400 font-semibold'>Política de privacidad</a> y <a href='/refund' target='_blank' class='underline text-blue-400 font-semibold'>Política de reembolsos</a>.",
            modal_confirm: "Confirmar y Proceder al Pago Seguro →",
            modal_cancel: "Cancelar y Volver al Sitio",
            modal_warn: "⚠️ Por favor, marca la casilla de aceptación de las condiciones de reembolso para continuar."
        }
    };

    function getLocale() {
        return localStorage.getItem('eduhub_lang') || document.documentElement.lang || 'ru';
    }

    // 1. Floating Cookie & Legal Consent Bar
    function initCookieBar() {
        if (localStorage.getItem(COOKIE_CONSENT_KEY) === 'true') {
            return;
        }

        let bar = document.getElementById('cookie-consent-bar');
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'cookie-consent-bar';
            bar.className = 'fixed bottom-4 sm:bottom-6 right-4 sm:right-6 z-50 p-4 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-2xl shadow-2xl transition-all duration-500 transform translate-y-6 opacity-0 pointer-events-auto max-w-sm';
            bar.innerHTML = `
                <div class="flex items-start gap-3">
                    <span class="text-xl shrink-0">🛡️</span>
                    <div class="space-y-2 flex-grow">
                        <p id="cookie-consent-msg" class="text-xs text-slate-300 leading-relaxed"></p>
                        <button id="cookie-consent-btn" onclick="EduHubLegal.acceptCookieConsent()" class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-xs px-4 py-2 rounded-xl shadow-lg shadow-blue-500/20 transition cursor-pointer whitespace-nowrap text-center">
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(bar);
        }

        renderCookieBarContent();

        setTimeout(() => {
            bar.classList.remove('translate-y-6', 'opacity-0');
            bar.classList.add('translate-y-0', 'opacity-100');
        }, 400);
    }

    function renderCookieBarContent() {
        const lang = getLocale();
        const dict = DICTIONARY[lang] || DICTIONARY.ru;
        const msgEl = document.getElementById('cookie-consent-msg');
        const btnEl = document.getElementById('cookie-consent-btn');
        if (msgEl) msgEl.innerHTML = dict.cookie_msg;
        if (btnEl) btnEl.textContent = dict.cookie_btn;
    }

    function acceptCookieConsent() {
        localStorage.setItem(COOKIE_CONSENT_KEY, 'true');
        const bar = document.getElementById('cookie-consent-bar');
        if (bar) {
            bar.classList.remove('translate-y-0', 'opacity-100');
            bar.classList.add('translate-y-full', 'opacity-0');
            setTimeout(() => bar.remove(), 500);
        }
    }

    // 2. Pre-Checkout Interactive Consent Modal Gate
    function initPreCheckoutModal() {
        if (document.getElementById('pre-checkout-legal-modal')) return;

        const modal = document.createElement('div');
        modal.id = 'pre-checkout-legal-modal';
        modal.className = 'fixed inset-0 z-50 hidden items-center justify-center p-4 bg-black/80 backdrop-blur-md transition-all duration-300';
        modal.innerHTML = `
            <div class="relative w-full max-w-lg bg-slate-900 border border-blue-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-blue-500/15 text-left overflow-hidden">
                <button onclick="EduHubLegal.closeCheckoutModal()" class="absolute top-4 right-4 text-slate-400 hover:text-white text-xl p-2 transition">✕</button>
                
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 text-xs font-bold uppercase mb-3" id="pcm-badge">
                </div>
                
                <h3 class="text-xl sm:text-2xl font-extrabold text-white mb-2" id="pcm-title"></h3>
                
                <div class="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2.5 mb-5 text-xs text-slate-300 leading-relaxed">
                    <div class="flex items-start gap-2.5">
                        <span class="text-emerald-400 font-bold shrink-0">🛡️</span>
                        <div id="pcm-b1"></div>
                    </div>
                    <div class="flex items-start gap-2.5">
                        <span class="text-blue-400 font-bold shrink-0">💳</span>
                        <div id="pcm-b2"></div>
                    </div>
                    <div class="flex items-start gap-2.5">
                        <span class="text-indigo-400 font-bold shrink-0">⚖️</span>
                        <div id="pcm-b3"></div>
                    </div>
                </div>

                <!-- Mandatory Interactive Checkbox -->
                <div class="mb-4">
                    <label id="pcm-checkbox-container" class="flex items-start gap-3 p-3.5 bg-slate-950/60 border border-slate-700 hover:border-slate-500 rounded-xl cursor-pointer transition">
                        <input type="checkbox" id="pre-checkout-checkbox" class="w-4 h-4 mt-0.5 rounded text-blue-600 focus:ring-blue-500 border-slate-700 bg-slate-900 cursor-pointer shrink-0">
                        <span class="text-xs text-slate-200 leading-snug" id="pcm-chk-text"></span>
                    </label>
                    <div id="pcm-warning" class="hidden text-[11px] text-rose-400 mt-2 font-medium"></div>
                </div>

                <!-- Action Button -->
                <button id="pcm-confirm-btn" onclick="EduHubLegal.confirmCheckoutConsent()" class="w-full py-3.5 rounded-xl font-bold text-xs sm:text-sm text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-xl shadow-blue-500/25 transition transform hover:-translate-y-0.5 cursor-pointer text-center mb-3">
                </button>

                <div class="text-center">
                    <button onclick="EduHubLegal.closeCheckoutModal()" class="text-xs text-slate-500 hover:text-slate-300 transition" id="pcm-cancel-btn">
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    function renderCheckoutModalContent() {
        const lang = getLocale();
        const dict = DICTIONARY[lang] || DICTIONARY.ru;

        const badge = document.getElementById('pcm-badge');
        const title = document.getElementById('pcm-title');
        const b1 = document.getElementById('pcm-b1');
        const b2 = document.getElementById('pcm-b2');
        const b3 = document.getElementById('pcm-b3');
        const chkText = document.getElementById('pcm-chk-text');
        const confirmBtn = document.getElementById('pcm-confirm-btn');
        const cancelBtn = document.getElementById('pcm-cancel-btn');
        const warning = document.getElementById('pcm-warning');

        if (badge) badge.textContent = `🛡️ ${dict.modal_badge}`;
        if (title) title.textContent = dict.modal_title;
        if (b1) b1.innerHTML = dict.modal_b1;
        if (b2) b2.innerHTML = dict.modal_b2;
        if (b3) b3.innerHTML = dict.modal_b3;
        if (chkText) chkText.innerHTML = dict.modal_chk;
        if (confirmBtn) confirmBtn.textContent = dict.modal_confirm;
        if (cancelBtn) cancelBtn.textContent = dict.modal_cancel;
        if (warning) warning.textContent = dict.modal_warn;
    }

    function openCheckoutModal(targetEl) {
        initPreCheckoutModal();
        renderCheckoutModalContent();

        pendingCheckoutElement = targetEl;
        const modal = document.getElementById('pre-checkout-legal-modal');
        const chk = document.getElementById('pre-checkout-checkbox');
        const warning = document.getElementById('pcm-warning');
        const chkBox = document.getElementById('pcm-checkbox-container');

        if (chk) chk.checked = false;
        if (warning) warning.classList.add('hidden');
        if (chkBox) {
            chkBox.classList.remove('border-rose-500', 'bg-rose-950/20');
            chkBox.classList.add('border-slate-700');
        }

        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    function closeCheckoutModal() {
        const modal = document.getElementById('pre-checkout-legal-modal');
        if (modal) {
            modal.classList.remove('flex');
            modal.classList.add('hidden');
        }
        pendingCheckoutElement = null;
    }

    function confirmCheckoutConsent() {
        const chk = document.getElementById('pre-checkout-checkbox');
        const warning = document.getElementById('pcm-warning');
        const chkBox = document.getElementById('pcm-checkbox-container');

        if (!chk || !chk.checked) {
            if (warning) warning.classList.remove('hidden');
            if (chkBox) {
                chkBox.classList.remove('border-slate-700');
                chkBox.classList.add('border-rose-500', 'bg-rose-950/20');
            }
            return;
        }

        // Store verifiable consent in sessionStorage
        sessionStorage.setItem(CHECKOUT_CONSENT_KEY, 'true');
        sessionStorage.setItem('checkout_consent_timestamp', new Date().toISOString());

        // Close modal
        closeCheckoutModal();

        // Proceed with original checkout action
        if (pendingCheckoutElement) {
            const el = pendingCheckoutElement;
            const href = el.getAttribute('href');
            if (href && href.startsWith('http')) {
                let targetUrl = href;
                try {
                    const u = new URL(href);
                    let uid = localStorage.getItem('eduhub_user_id');
                    if (!uid) {
                        uid = 'usr_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now().toString(36);
                        localStorage.setItem('eduhub_user_id', uid);
                    }
                    u.searchParams.set('checkout[custom][user_id]', uid);
                    const email = localStorage.getItem('eduhub_user_email') || localStorage.getItem('user_email');
                    if (email && email.includes('@')) {
                        u.searchParams.set('checkout[email]', email.trim().toLowerCase());
                    }
                    targetUrl = u.toString();
                } catch(e) {}

                if (!targetUrl || targetUrl.startsWith('#') || targetUrl.includes('#checkout')) {
                    window.location.href = '/#pricing';
                } else {
                    window.open(targetUrl, '_blank', 'noopener,noreferrer');
                }
            } else if (typeof el.click === 'function') {
                el.click();
            }
        }
    }

    // 3. Checkout Click Interceptor (Catches all checkout buttons)
    function setupCheckoutInterceptors() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest('a.checkout-trigger-btn, button.checkout-trigger-btn, a[href*="#checkout"], a[href*="/checkout"]');
            if (!btn) return;

            // If already confirmed in this session, let it pass directly
            if (sessionStorage.getItem(CHECKOUT_CONSENT_KEY) === 'true') {
                return;
            }

            // Stop immediate checkout until explicit consent modal is confirmed
            e.preventDefault();
            e.stopPropagation();

            openCheckoutModal(btn);
        }, true); // Capture phase to intercept before checkout
    }

    // 4. Update Micro-Consent Captions
    function updateMicroConsent() {
        const lang = getLocale();
        const dict = DICTIONARY[lang] || DICTIONARY.ru;
        document.querySelectorAll('.checkout-micro-consent').forEach(el => {
            el.innerHTML = dict.micro_consent;
        });
    }

    function onLanguageChanged() {
        renderCookieBarContent();
        renderCheckoutModalContent();
        updateMicroConsent();
    }

    // Bootstrap
    function init() {
        initCookieBar();
        initPreCheckoutModal();
        setupCheckoutInterceptors();
        updateMicroConsent();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Connect to global language switcher
    const origSetLocale = window.setLocale;
    if (typeof origSetLocale === 'function') {
        window.setLocale = function(locale) {
            origSetLocale(locale);
            onLanguageChanged();
        };
    }

    return {
        acceptCookieConsent,
        closeCheckoutModal,
        confirmCheckoutConsent,
        openCheckoutModal,
        onLanguageChanged,
        updateMicroConsent
    };
})();

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EduHubLegal;
}
