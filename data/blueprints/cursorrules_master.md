# Senior AI Full-Stack Engineer Master Rules (.cursorrules)
# Version: 2026.3 - Optimized for Cursor, Windsurf, Claude Dev & Copilot

## Core Engineering Directives
- Precision First: Never generate speculative placeholder comments. Always provide complete, production-grade solutions.
- Strict Typing: TypeScript strict mode is non-negotiable. No `any` without explicit justification.
- Architectural Separation: Strict separation of concerns (Presentation / Business Logic / Data Access / API Layer).
- FastAPI / Python Standard: Use Pydantic v2 schemas, type annotations, dependency injection, and centralized error handling.
- Tailwind CSS Rules: Use semantic utility groupings. Avoid arbitrary pixel values when Tailwind design tokens exist.
- Performance & Security:
  - Validate incoming payload sizes.
  - Implement OWASP security headers (nosniff, SAMEORIGIN, strict-origin-when-cross-origin).
  - Sanitize all user inputs before passing to LLM prompts.

## High-Performance Prompt Templates
- Zero-Bug Refactor: When modifying code, preserve existing variable naming and docstrings unless explicitly asked to refactor.
- Self-Healing Loop: After writing code, run automated verification commands before confirming task completion.
