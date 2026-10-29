# Changelog

## 2.0.0 (2026-10-29): baseline revision (R1-R14), clone|generation modes, non-SaaS policy binding

allowlistVersion 2.0.0. pageSpecVersion 2.0.0 (breaking: `mode` is required).

Verified first (Situation B): baseline audit at the start reported 7 pass / 14 fail (R1-R4, R7, R8 + contract
schema, R9 gate + heights). Re-checked against the clone: routes are still exactly `/`, `/privacy-policy` and the
NotFound catch-all (`src/App.jsx`); the old README's "not a git repository" claim was stale (the project is a git
repo; `design-repo.zip` is in `.gitignore`); `prove_drift.py` had no `--scratch` option.

Added
- `mode: clone | generation` (required). 9 mode rules: GENERATION_MODE_BRAND / _PERSON / _CUSTOMER / _COPY /
  _CLAIM / _URL / _EMBED / _ASSET and CLONE_MODE_UNKNOWN_SOURCE. Patterns in `schema/leakage-patterns.json`,
  built from the real source by `extraction/build_leakage_patterns.py` (file:line evidence, copy as hashed
  5-word shingles, NFKC / zero-width / homoglyph / quote / dash / diacritic normalisation in `schema/textnorm.py`).
  No human has reviewed the patterns; detection is string-based.
- Asset availability (clone-only / generation-safe / blocked-for-generation), `generationSafeSubstitutes`,
  `generatedModeGuidance` and real `sourceFiles` on every role; 9 generation-safe roles; availability pinned in
  both validators. Media fields accept their substitutes; `assetRef` gains `user:` and (clone only) `source:`.
- Six examples in `schema/examples/` (clone + generation for home, legal, not-found). The old
  `schema/example.pagespec.json` became `home.clone.pagespec.json` with real refs.
- R7 `source` / `semantic` on every contract (`extraction/build_provenance.py`), closed
  `schema/section-contract.schema.json`; R8 `retrievalEligible` (splash false), pinned in both validators and the
  allowlist; R9 `extraction/wrapper_gate.py` + `wrapper-whitelist.json` (empty) + `measure_sections.mjs`, with
  `sectionHeights` measured from the built clone at 1440px.
- Token catalog generated from the token files (`extraction/build_token_catalog.py`); token policy slots and 7
  TOKEN_* rules; optional per-node `tokens` and page `theme`.
- `policy/design-policy.json` (non-SaaS, professional-services; notBoundTo n0-saas-design-constraints-common),
  manifest `category` + `designPolicy` with a recomputed contentHash (`extraction/policy_hash.py`).
- verify_all checks: mode_examples, section_contracts, provenance, retrieval_eligibility, leakage_patterns,
  wrapper_gate, design_policy; prove_drift `--scratch DIR` and new injections.

Changed
- R6: `content.legal-prose` (whole article, 3476px = 79% of the page) replaced by `content.legal-header` +
  repeatable `content.legal-section` (one per real heading; 8 measured).
- Adversarial suite: 66 mutations / 5 controls -> see the README counts table.

Not done / caveats
- Visual parity against the live site was not re-measured. The non-SaaS classification, the splash
  retrieval decision and the leakage patterns are agent attestation, not a human sign-off.
- The root `ia.json` (outside this package) still models the privacy article as one section; it was not edited.

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
