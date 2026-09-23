/**
 * EduHub AI — Autonomous Theme & Micro-Interactions Engine (2026)
 * File: static/js/theme-engine.js
 * Features:
 * 1. Zero-FOUC Synchronous Theme Initialization.
 * 2. Seamless Day / Night Toggle with localStorage & prefers-color-scheme.
 * 3. Haptic Web Audio Feedback (5ms soft earcon).
 * 4. Keyboard Shortcut: Alt + T.
 * 5. Touch-friendly Mega-Menu controller.
 */

(function() {
    'use strict';

    // 1. SYNCHRONOUS EARLY INITIALIZATION (ANTI-FOUC)
    function applyInitialTheme() {
        try {
            const saved = localStorage.getItem('eduhub_theme');
            let theme = saved;
            if (!theme) {
                const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
                theme = prefersDark ? 'dark' : 'light';
            }
            if (theme === 'light') {
                document.documentElement.classList.add('light');
                document.documentElement.classList.remove('dark');
            } else {
                document.documentElement.classList.add('dark');
                document.documentElement.classList.remove('light');
            }
        } catch (e) {
            // Fallback default
            document.documentElement.classList.add('dark');
        }
    }
    applyInitialTheme();

    // 2. TACTILE WEB AUDIO EARCON (MICRO-CLICK)
    let audioCtx = null;
    function playTactileClick() {
        try {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            if (!audioCtx) audioCtx = new AudioContext();
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            const now = audioCtx.currentTime;

            osc.type = 'sine';
            osc.frequency.setValueAtTime(600, now);
            osc.frequency.exponentialRampToValueAtTime(850, now + 0.03);

            gain.gain.setValueAtTime(0.04, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start(now);
            osc.stop(now + 0.04);
        } catch (e) {
            // Audio blocked or unsupported
        }
    }

    // 3. MASTER THEME TOGGLE
    window.toggleTheme = function() {
        playTactileClick();
        const isCurrentlyLight = document.documentElement.classList.contains('light');
        const nextTheme = isCurrentlyLight ? 'dark' : 'light';

        if (nextTheme === 'light') {
            document.documentElement.classList.add('light');
            document.documentElement.classList.remove('dark');
        } else {
            document.documentElement.classList.add('dark');
            document.documentElement.classList.remove('light');
        }

        try {
            localStorage.setItem('eduhub_theme', nextTheme);
        } catch (e) {}

        updateToggleButtons(nextTheme);
    };

    function updateToggleButtons(currentTheme) {
        const btns = document.querySelectorAll('.theme-toggle-btn');
        btns.forEach(btn => {
            const iconSpan = btn.querySelector('.theme-icon');
            if (currentTheme === 'light') {
                btn.title = 'Switch to Night Mode (Alt+T)';
                btn.setAttribute('aria-label', 'Switch to Night Mode');
                if (iconSpan) iconSpan.innerHTML = '🌙';
            } else {
                btn.title = 'Switch to Day Mode (Alt+T)';
                btn.setAttribute('aria-label', 'Switch to Day Mode');
                if (iconSpan) iconSpan.innerHTML = '☀️';
            }
        });
    }

    // 4. TOP ANNOUNCEMENT BANNER DISMISSAL
    window.closeAnnouncementBanner = function() {
        const b = document.getElementById('trending-banner') || document.getElementById('unified-top-banner');
        if (b) {
            b.style.transition = 'all 0.25s ease';
            b.style.opacity = '0';
            b.style.transform = 'translateY(-100%)';
            setTimeout(() => { b.style.display = 'none'; }, 260);
        }
    };

    // 5. DOM READY BINDINGS
    document.addEventListener('DOMContentLoaded', () => {
        const current = document.documentElement.classList.contains('light') ? 'light' : 'dark';
        updateToggleButtons(current);

        // System theme change listener
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
                if (!localStorage.getItem('eduhub_theme')) {
                    const sysTheme = e.matches ? 'dark' : 'light';
                    if (sysTheme === 'light') {
                        document.documentElement.classList.add('light');
                        document.documentElement.classList.remove('dark');
                    } else {
                        document.documentElement.classList.add('dark');
                        document.documentElement.classList.remove('light');
                    }
                    updateToggleButtons(sysTheme);
                }
            });
        }

        // Keyboard Shortcut: Alt + T
        document.addEventListener('keydown', e => {
            if (e.altKey && (e.key === 't' || e.key === 'T' || e.key === 'е' || e.key === 'Е')) {
                e.preventDefault();
                window.toggleTheme();
            }
        });

        // Touch Mega-Menu toggle for mobile
        const megaTrigger = document.querySelector('.mega-menu-trigger');
        const megaDropdown = document.querySelector('.mega-menu-dropdown');
        if (megaTrigger && megaDropdown) {
            megaTrigger.addEventListener('click', (e) => {
                if (window.innerWidth < 1024) {
                    megaDropdown.classList.toggle('is-open');
                }
            });
            document.addEventListener('click', (e) => {
                if (!megaTrigger.contains(e.target)) {
                    megaDropdown.classList.remove('is-open');
                }
            });
        }
    });

})();
