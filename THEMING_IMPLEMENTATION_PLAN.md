# Theming Implementation Plan

Status: Draft

Purpose
-------
This document describes a practical, low-risk plan to implement consistent theming across the Countdown Calendar app (Ionic + Vue frontend). It covers variables, tokens, light/dark modes, component theming, accessibility considerations, testing, migration steps, and an implementation checklist for PR reviewers.

Scope
-----
- Frontend only: `frontend/` (Vue + Ionic). Backend changes are out of scope.
- Implement design tokens and CSS variables, wire into Ionic theming, and provide a runtime theme switch (light/dark) and scoped component token usage.
- Migrate existing visual styles to use tokens where practical.

Contract (short)
-----------------
- Inputs: existing `frontend/src/theme/variables.css`, component styles, design token suggestions from UI/UX.
- Outputs: a well-documented `THEMING_IMPLEMENTATION_PLAN.md`, updated `frontend/src/theme/variables.css`, a small `theme` composable to toggle themes, updated components consuming tokens, tests and a PR checklist.
- Error modes: missing tokens, platform inconsistencies (iOS/Android webview), and contrast/accessibility failures.

High-level approach
-------------------
1. Create a clear set of design tokens (colors, spacing, radii, typography) expressed as CSS custom properties in `frontend/src/theme/variables.css`.
2. Map tokens to Ionic CSS variables where applicable (Ionic provides many variables the components read). Override Ionic defaults in `variables.css`.
3. Implement light/dark sets using a root-level data attribute or class (e.g., `:root[data-theme="light"]` / `:root[data-theme="dark"]`) so switching is a single attribute toggle.
4. Provide a tiny `useTheme` composable that reads/saves user preference (localStorage + prefers-color-scheme fallback) and toggles the root attribute.
5. Migrate components incrementally to read CSS variables instead of hard-coded values. Prefer variables over inline styles.
6. Add visual and accessibility tests and a PR checklist so reviewers ensure tokens are used.

Design tokens (suggested)
------------------------
- Colors
  - --cc-bg (app background)
  - --cc-surface (cards, surfaces)
  - --cc-primary
  - --cc-primary-contrast (text on primary)
  - --cc-secondary
  - --cc-accent
  - --cc-success
  - --cc-warning
  - --cc-danger
  - --cc-text (primary text)
  - --cc-text-muted
  - --cc-border
  - --cc-skeleton (skeleton loaders)

- Semantic roles
  - --cc-bg-elev-1, --cc-bg-elev-2 (elevations for surfaces)

- Typography
  - --cc-font-family
  - --cc-font-size-base
  - --cc-font-scale-step-1 .. -3

- Spacing & radii
  - --cc-space-xs, --cc-space-sm, --cc-space-md, --cc-space-lg
  - --cc-radius-sm, --cc-radius-md, --cc-radius-lg

How to organize `variables.css`
-------------------------------
- Keep a `:root` block with default (light) tokens, and a `[data-theme="dark"]` block for dark overrides.
- Also override Ionic variables near the top (for example: `--ion-color-primary`, `--ion-background-color`, etc.) by mapping them to our tokens so Ionic components inherit the look.
- Example structure (conceptual):
  - Section: Ionic variable mappings
  - Section: Design tokens (colors/typography/spacing)
  - Section: Theme overrides (dark)

Theme switching
---------------
- Add a composable `frontend/src/composables/useTheme.ts` (or `.js`) with these responsibilities:
  - read initial theme preference (localStorage -> prefers-color-scheme -> default 'light')
  - apply `data-theme` attribute on `document.documentElement`
  - expose `toggleTheme()` and `setTheme(theme)` helpers
  - persist choice to localStorage

Migration strategy (incremental)
------------------------------
1. Start by introducing tokens and Ionic mappings only (no component changes). This gives an immediate global theme effect.
2. Add the `useTheme` composable and a small UI control (Settings > Theme) to let users toggle.
3. Identify the highest-value components (calendar tile, header, buttons) and update styles to use tokens.
4. Create a small list of components to migrate per PR (2–4 components per PR).

Testing & accessibility
-----------------------
- Visual checks: manual review of main screens in both light/dark.
- Automated tests: Add snapshot tests for components that changed and a small visual regression run in CI (if available).
- Accessibility: Ensure color contrast >= 4.5:1 for body text and 3:1 for large text. Use an axe check or similar in CI for changed pages.

Developer ergonomics
--------------------
- Document token usage in `frontend/README.md` or a new `frontend/THEMING_README.md` with examples:
  - Use `var(--cc-primary)` in components, or prefer Ionic mapping where the component is an Ionic component.
- Keep token names semantic rather than descriptive where possible (use `--cc-primary` instead of `--cc-blue-500`), to avoid meaning-locked tokens.

PR checklist (for theming PRs)
-----------------------------
- [ ] Variables added/updated in `frontend/src/theme/variables.css`.
- [ ] Ionic variables mapped where appropriate.
- [ ] No hard-coded color/spacing left in updated components — tokens used.
- [ ] Dark mode verified locally and screenshots attached (if visual review required).
- [ ] Accessibility contrast checks passed for changed views.
- [ ] Unit/snapshot tests updated or added for changed components.
- [ ] Brief note in PR description describing token changes and migration scope.

Rollback & fallback
-------------------
- If a token change causes major regressions, revert the variables file and open small follow-up PRs to fix component mismatches.
- Keep a short migration log in the PR template when renaming or removing tokens.

Estimated timeline (small team)
------------------------------
- Week 0 (1–2 days): Prepare tokens, update `variables.css`, map Ionic variables.
- Week 1: Add `useTheme` composable + UI toggle; smoke test major screens.
- Weeks 2–4: Incremental component migrations (1–2 PRs per week), tests, and accessibility checks.

Notes and follow-ups
--------------------
- Decide final token palette with the designer (if available). This plan takes a pragmatic approach so devs can start migration without blocking on pixel-perfect color choices.
- Optionally introduce a small script to validate tokens are referenced in components to aid future cleanup.

Contact
-------
If anything here is incorrect or you have a prior version of the deleted file, paste it into an issue or here and I will restore the canonical content exactly.

---
Generated as a draft to restore the accidentally-deleted file; refine as needed.
