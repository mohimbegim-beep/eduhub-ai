/**
 * EduHub AI — Enhanced Academic Document Renderer
 * Features:
 * 1. Responsive scrollable HTML tables (overflow-x: auto) with Tailwind styling.
 * 2. Mermaid.js integration for automatic SVG flowcharts, mindmaps, and sequence diagrams.
 * 3. KaTeX integration for high-performance LaTeX formulas (fractions, integrals, matrices, physics).
 */

(function () {
  // Initialize Mermaid with dark theme
  if (window.mermaid) {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
          darkMode: true,
          background: '#090d16',
          primaryColor: '#3b82f6',
          primaryTextColor: '#f8fafc',
          primaryBorderColor: '#1d4ed8',
          lineColor: '#60a5fa',
          secondaryColor: '#6366f1',
          tertiaryColor: '#1e293b'
        },
        securityLevel: 'loose',
        fontFamily: 'inherit'
      });
    } catch (err) {
      console.warn('[DOC RENDERER] Mermaid init warning:', err);
    }
  }

  // Setup Custom Marked Renderer for Tables and Mermaid
  let markedRenderer = null;
  if (window.marked && window.marked.Renderer) {
    markedRenderer = new marked.Renderer();

    // 1. Responsive Scrollable Tables (overflow-x: auto)
    markedRenderer.table = function (header, body) {
      return `
        <div class="table-responsive-container overflow-x-auto my-5 rounded-2xl border border-slate-800 bg-slate-900/90 shadow-xl">
          <table class="min-w-full divide-y divide-slate-800 text-xs text-left text-slate-200">
            <thead class="bg-slate-800/90 text-slate-100 uppercase tracking-wider font-semibold">
              ${header}
            </thead>
            <tbody class="divide-y divide-slate-800/50 font-mono text-[11px] sm:text-xs">
              ${body}
            </tbody>
          </table>
        </div>
      `;
    };

    markedRenderer.tablerow = function (content) {
      return `<tr class="hover:bg-slate-800/40 transition duration-150">${content}</tr>`;
    };

    markedRenderer.tablecell = function (content, flags) {
      const type = flags.header ? 'th' : 'td';
      const align = flags.align ? ` text-${flags.align}` : '';
      return `<${type} class="px-4 py-3${align}">${content}</${type}>`;
    };

    // 2. Mermaid Diagram Code Blocks
    markedRenderer.code = function (code, infostring) {
      const lang = (infostring || '').match(/\S*/)[0].toLowerCase();
      if (lang === 'mermaid') {
        const id = 'mermaid-' + Math.random().toString(36).substring(2, 9);
        return `
          <div class="mermaid-block-wrapper my-6 overflow-x-auto rounded-2xl border border-indigo-900/60 bg-slate-900/80 p-5 shadow-2xl flex flex-col items-center">
            <span class="text-[10px] font-bold uppercase tracking-wider text-indigo-400 self-start mb-2 px-2.5 py-0.5 rounded-full bg-indigo-950/80 border border-indigo-800/60">
              📊 Mermaid Flowchart / Mindmap
            </span>
            <div id="${id}" class="mermaid w-full flex justify-center">${code}</div>
          </div>
        `;
      }
      return `
        <div class="code-block-wrapper my-4 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-200">
          <pre><code>${code}</code></pre>
        </div>
      `;
    };

    // Typography styling for lists & headings
    markedRenderer.heading = function (text, level) {
      const sizes = {
        1: "text-xl sm:text-2xl font-black text-white mt-6 mb-3 border-b border-slate-800 pb-2",
        2: "text-lg sm:text-xl font-bold text-blue-300 mt-5 mb-2.5",
        3: "text-base font-semibold text-indigo-300 mt-4 mb-2",
        4: "text-sm font-semibold text-slate-200 mt-3 mb-1.5"
      };
      const cls = sizes[level] || sizes[4];
      return `<h${level} class="${cls}">${text}</h${level}>`;
    };

    markedRenderer.list = function (body, ordered) {
      const type = ordered ? 'ol' : 'ul';
      const cls = ordered ? 'list-decimal pl-5 space-y-1.5 my-3 text-xs text-slate-300' : 'list-disc pl-5 space-y-1.5 my-3 text-xs text-slate-300';
      return `<${type} class="${cls}">${body}</${type}>`;
    };

    markedRenderer.blockquote = function (quote) {
      return `<blockquote class="border-l-4 border-blue-500 bg-blue-950/20 px-4 py-3 my-4 rounded-r-xl text-xs text-blue-200 italic">${quote}</blockquote>`;
    };

    window.marked.setOptions({
      renderer: markedRenderer,
      gfm: true,
      breaks: true
    });
  }

  /**
   * Primary Render Function
   * @param {string} text - Raw Markdown / LaTeX / Mermaid text
   * @param {HTMLElement} targetEl - Container element
   */
  window.renderAcademicDocument = function (text, targetEl) {
    if (!targetEl) return;
    if (!text) {
      targetEl.innerHTML = '';
      return;
    }

    // Step 1: Render Markdown if Marked is present, otherwise safe fallback
    if (window.marked && typeof window.marked.parse === 'function') {
      try {
        targetEl.innerHTML = window.marked.parse(text);
      } catch (err) {
        console.warn('[DOC RENDERER] Marked parse error:', err);
        targetEl.textContent = text;
      }
    } else {
      // Basic fallback
      targetEl.textContent = text;
    }

    // Step 2: Render LaTeX formulas via KaTeX auto-render
    if (window.renderMathInElement) {
      try {
        window.renderMathInElement(targetEl, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '\\[', right: '\\]', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\(', right: '\\)', display: false }
          ],
          throwOnError: false,
          errorColor: '#f43f5e'
        });
      } catch (err) {
        console.warn('[DOC RENDERER] KaTeX math rendering error:', err);
      }
    }

    // Step 3: Render Mermaid diagrams
    if (window.mermaid && targetEl.querySelectorAll('.mermaid').length > 0) {
      try {
        window.mermaid.run({
          nodes: targetEl.querySelectorAll('.mermaid')
        });
      } catch (err) {
        console.warn('[DOC RENDERER] Mermaid run error:', err);
      }
    }
  };
})();
