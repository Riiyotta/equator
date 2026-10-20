# Changelog

## 1.0.0 (2026-10-20): initial build

Built from scratch against the Equator clone (React 18.3 / Vite 5.4 / Tailwind 3.4) and its
evidence: `src/`, `tailwind.config.cjs`, `CLONE_SPEC.md`, the saved original CSS bundles and the
Playwright QA dumps. allowlistVersion 1.0.0.

Added
- 114 tokens (foundation colour/typography/radius/spacing/breakpoint/elevation/icon-size/motion,
  semantic, component, layout) and the single `light` theme. Colours are exactly the 13 values in
  the original CSS histogram; elevation is z-index only (0 box-shadow declarations).
- 12 primitives, 8 components, 13 section contracts with `maxWords` budgets, closed motion with
  const-locked `reducedMotionFallback`, structured 768 responsive entries and cited evidence.
- 3 templates (home, legal-prose, not-found) with structured nodes; 3 routes mapped 1:1.
- 19 graph rules with severity, each enforced by `schema/semantic_validate.py`.
- 12 asset roles with generation policies; 10 roles plus the National 2 licence are pinned.
- 66 adversarial mutations and 5 controls. 10 of the mutations target the pins: 7 switch a pinned role to a different but valid policy, 1 un-pins a role, 1 marks a role pinned with no pin in code, 1 changes the font licence.
- `extraction/verify_all.py` (19 checks) and `extraction/prove_drift.py`, which proves each check
  fails on an injected defect.

Recorded, not normalised
- QA-measured corrections that supersede CLONE_SPEC.md (values initial opacity 0, carousel clamp).
- NotFound is inferred-unmeasured.
- Accessibility parity defects are kept as source-site behaviour.
