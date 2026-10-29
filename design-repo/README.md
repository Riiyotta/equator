# Equator design-repo

A machine-validated PageSpec system extracted from the Equator clone (a pixel replica of
https://equatorcompany.com/, The Equator Company). It tells a generator what it may use, how
sections may be combined, and how they behave across content and breakpoints, without
inventing colours, copy budgets, structure or assets.

Repository 2.0.0, pageSpecVersion 2.0.0, allowlistVersion 2.0.0.

**Status: `design-review-pending`, `productionApproved: false`.** The source is the live site of a
real company. Do not publish this package, and do not make a repository holding it public.

## Source

| | |
|---|---|
| Original | Nuxt 3 / Vue 3, Locomotive Scroll v5 (Lenis 1.1.9), dotlottie-web 0.54.1, vue3-carousel, marquee3k |
| Clone (measured) | React ^18.3.1, Vite ^5.4.10, Tailwind ^3.4.14, lenis ^1.3.27, @lottiefiles/dotlottie-web ^0.81.0 (from `package.json`) |
| Evidence | clone `src/`, `tailwind.config.cjs`, `CLONE_SPEC.md`, the saved original CSS bundles, Playwright QA dumps in `.playwright-mcp/` |

The source project is a git repository. `design-repo.zip` is listed in `.gitignore` and is never
committed next to this folder (two disagreeing copies).

## Layout

```
design-repo/
  README.md  CHANGELOG.md  registry.manifest.json
  policy/design-policy.json   non-SaaS common-policy binding (N0 Common Composition IR 0.5)
  tokens/00-foundation/   color, typography, radius, spacing, breakpoint, elevation, icon-size, motion
  tokens/10-semantic/     intent roles referencing foundation tokens
  tokens/20-component/    component-scoped values
  tokens/30-layout/       grid and measures
  tokens/themes/light.json   the only theme (the original has no dark mode)
  tokens/llm/             component-allowlist.json, token-catalog.json (generated), token-policy.json
  primitives/  components/  sections/      one JSON contract each
  templates/templates.json  templates/routes.json
  compatibility/graph.json  rhythm/position rules with severity
  assets/asset-roles.json   closed asset-role vocabulary: availability, substitutes, policies, pins
  schema/pagespec.schema.json  schema/section-contract.schema.json  schema/semantic_validate.py
  schema/textnorm.py  schema/leakage-patterns.json (generated)  schema/examples/*.pagespec.json
  schema/tests/adversarial_test.py
  extraction/measured-values.json  extraction/verify_all.py  extraction/prove_drift.py
  extraction/wrapper_gate.py  extraction/wrapper-whitelist.json  extraction/measure_sections.mjs
  extraction/build_leakage_patterns.py  extraction/build_provenance.py  extraction/build_token_catalog.py
  extraction/policy_hash.py
```

## Counts (recomputed from disk; `verify_all.py` fails if this table drifts)

| count | value |
|---|---|
| `tokens` | 114 |
| `primitives` | 12 |
| `components` | 8 |
| `sections` | 14 |
| `templates` | 3 |
| `routes` | 3 |
| `assetRoles` | 21 |
| `graphRules` | 19 |
| `modeRules` | 9 |
| `tokenRules` | 7 |
| `examples` | 6 |
| `adversarialMutations` | 144 |
| `adversarialControls` | 14 |
| `citations` | 253 |

Token count = `$value` leaves in `00-foundation`, `10-semantic`, `20-component`, `30-layout`.

## Modes (pageSpecVersion 2.0.0)

Every PageSpec carries a required, closed `mode`:

* `clone`: faithful reconstruction of the Equator site. Real copy, names and files may be used:
  `assetRef: "source:<path>"` must name one of the role's real `sourceFiles`, absolute links must be
  real Equator source domains/emails (`CLONE_MODE_UNKNOWN_SOURCE`, `ASSET_POLICY`).
* `generation`: a new page for another organisation. `semantic_validate.py` rejects, each with its own
  rule: `GENERATION_MODE_BRAND` (Equator / The Equator Company / S317 and spelling variants),
  `_PERSON` (15 employees, names and asset slugs), `_CUSTOMER` (merged companies, clients, programmes,
  design credit), `_COPY` (hashed 5-word shingles of the real copy), `_CLAIM` (45 years, project
  statistics, award, PRR / public-funding claim), `_URL` (source domains/emails and any non
  `.example` / `.invalid` absolute host), `_EMBED` (Mailchimp form, Google Maps place link) and
  `_ASSET` (clone-only / blocked roles, `source:` refs, real file names and stems).

Patterns live in `schema/leakage-patterns.json`, built by `extraction/build_leakage_patterns.py` from
`src/`, `index.html`, `CLONE_SPEC.md` and `public/` with file:line evidence; `verify_all.py` re-runs the
build with `--check` when the source tree is present. Strings are normalised first (`schema/textnorm.py`:
NFKC, zero-width removal, homoglyph / curly-quote / dash folding, diacritics stripped). **No human has
reviewed these patterns, and detection is string-based**: paraphrase, translation or text inside images
evade it. A pass means "no known Equator string found", not proof of originality. There are no product
screenshots in the source, so there is no separate screenshot rule; slide photography is covered by
`GENERATION_MODE_ASSET`.

Examples, one clone + one generation-mode (file label `generated`) per template family: `schema/examples/{home,legal,not-found}.{clone,generated}.pagespec.json`.
The generation examples use a fictional brand (Northwind Field Partners), fictional people, placeholder /
generated / operator-supplied assets and `.example` URLs.

## Asset availability

Every role in `assets/asset-roles.json` has a closed `availability` (`clone-only`, `generation-safe`,
`blocked-for-generation`), `generationSafeSubstitutes` and `generatedModeGuidance`. The 10 real-media roles
are clone-only, the PRR emblem and project-sheet PDF are blocked-for-generation, and 9 generation-safe
roles were added: placeholder-brand-mark, user-supplied-asset, generated-illustration,
generated-ambient-video, placeholder-screenshot, fictional-avatar, placeholder-company-logo,
placeholder-url (`.example` / `.invalid` only) and original-copy. A real logo or wordmark is never
`must-reuse-exact` in generation mode. Availability is pinned in code twice (`PINNED_AVAILABILITY` in
`schema/semantic_validate.py` and `extraction/verify_all.py`) and both are cross-checked against the registry.

## Sections, provenance, retrieval, wrapper gate

* Every contract has closed `source {id, tag, file, lines}` (generated by `extraction/build_provenance.py`
  from the real files; `verify_all.py` re-reads each range and requires `<tag` on its first line) and
  `semantic {id, category}` (the AI-facing taxonomy). The closed `schema/section-contract.schema.json`
  validates every contract.
* `retrievalEligible` is a closed boolean on every contract. `chrome.splash` (preloader-style brand intro,
  no content) is `false` with a reason; this is pinned in both validators and the allowlist.
* The former whole-article `content.legal-prose` measured 3476px of the 4423px privacy page (79%). It is
  now `content.legal-header` + one `content.legal-section` per real heading (8 on `/privacy-policy`).
* `extraction/wrapper_gate.py` (thresholds pinned in code: HERO 1800 warn / 3000 error, single-section
  share 50% warn / 60% error, 1440px only) runs inside `verify_all.py` on `sectionHeights` measured from the
  built clone with `extraction/measure_sections.mjs` (`npx vite build --outDir <scratch>`,
  `npx vite preview --port 5732`, Playwright through `NODE_PATH`). Result: 0 errors, 0 warnings; the
  whitelist is empty. Largest shares: values 27% of home, Data Treatment part 26% of the legal page.

## Tokens

`tokens/llm/token-catalog.json` is generated from the token files (`extraction/build_token_catalog.py`,
checked by `verify_all.py`). A node may carry an optional `tokens` object with closed slots (surface, text,
accent, headingType, bodyType, spacingY, gap, radius, fontFamily); `tokens/llm/token-policy.json` says which
catalog categories each slot accepts. Rules: `TOKEN_UNKNOWN`, `TOKEN_RAW_COLOR`, `TOKEN_ARBITRARY_SPACING`,
`TOKEN_FONT_UNSUPPORTED`, `TOKEN_SLOT_MISMATCH`, `TOKEN_THEME_COMBINATION` (errors), `TOKEN_FONT_LICENCE` (warning).

## Design policy

The clone is a sustainability / ESG consultancy site (no pricing, app, login, dashboard, demo or
integrations; evidence in `policy/design-policy.json`), so it is **not** bound to
`n0-saas-design-constraints-common`. The manifest has `category: professional-services` and binds
`policy/design-policy.json` (`n0-professional-services-consultancy-web` 1.0.0, commonIrVersion 0.5,
hard-and-soft). `contentHash` covers the files that enforce the policy and is recomputed by `verify_all.py`.
The classification is agent attestation, not a human sign-off: `policyDecision` is
`defined-pending-architecture-review`.

## Templates and routes

| Route | Template | Nodes | Evidence |
|---|---|---|---|
| `/` | `template.home` | splash, header(home), title, story, values, capabilities, work, team, CTA, footer, subfooter? | measured |
| `/privacy-policy` | `template.legal-prose` | header(legal), legal-header, legal-section+, footer, subfooter? | measured |
| `*` (any other path) | `template.not-found` | not-found | **inferred-unmeasured** |

Routes come from the clone's router (`src/App.jsx`: `/`, `/privacy-policy`, everything else NotFound).
Nav anchors (`/#our-story` and so on) are sections of `/`, not routes. `?` optional, `+` repeatable.

## Run

```
python3 schema/semantic_validate.py [spec.json ...]   # schema + semantic rules on every example by default
python3 schema/tests/adversarial_test.py              # 144 mutations rejected, 14 controls pass
python3 extraction/verify_all.py                      # all checks, includes the adversarial suite
python3 extraction/prove_drift.py [--scratch DIR]     # injects a defect per check, proves each fails
python3 extraction/wrapper_gate.py                    # R9 gate alone
```

Requires Python 3 with `jsonschema`. All scripts derive their root from `__file__`, so the folder works
wherever it is unpacked. Without the sibling source tree, citation, provenance and leakage-rebuild checks
downgrade to WARN instead of failing.

## What is enforced

* **Schema (draft-07):** required closed `mode`, closed template and node-type enums,
  `additionalProperties:false` at every level, one closed if/then branch per section type, closed motion
  object with const-locked values, closed `assetRole` enum per media field, closed `tokens` slots.
* **Semantic validator:** template node-list cross-check, route binding, the 19 graph rules at their declared
  severity, per-instance `maxWords`, asset policies, policy / availability / licence / retrieval pins, the 9
  mode rules and the 7 token rules.
* **verify_all.py:** examples per family and mode, closed contracts, provenance ranges, retrieval pins,
  leakage registry freshness, wrapper gate, design-policy binding and hash, allowlist and version parity,
  manifest + README counts, citations, absolute paths, entry points, schema/contract and graph/validator
  parity, route coverage, theme resolution, token catalog freshness, asset roles + pins + real sourceFiles,
  responsive entries, evidence levels, status flags, framework versions.

## Real-company constraints (load-bearing)

* Asset roles and policies (`assets/asset-roles.json`): real employees' portraits and halftones
  are `placeholder-only`; merger/member logos, the wordmark and the brand Lotties are
  `must-not-reproduce`; the PRR/EU funding emblem and the project-sheet PDF are `omit`;
  project photos and ambient video are `may-generate-new` (never the real files, no identifiable
  people, clients or sites).
* National 2 (Klim Type Foundry) is **licence-required**; generated output uses the fallback stack
  unless the deployer holds a licence.
* Clone examples deliberately contain real content (headings, three team members, real file refs, the
  privacy preamble and two parts) to prove clone mode accepts it. Generation examples contain none.
  Contracts describe fields and budgets, not prose.
* CTA links go to a live Mailchimp endpoint and the company LinkedIn on the source. Clone mode may
  carry them; generation mode allows only placeholder:, relative or `.example` / `.invalid` links.

## Inferred / unmeasured / not reviewed

* No human reviewed the leakage patterns, the non-SaaS classification or the splash retrieval decision
  (agent attestation, not a human sign-off).
* Visual parity of the clone against the live site was not re-measured in this revision. Only section
  heights of the built clone at 1440px were measured.

* `template.not-found`, route `*`, `content.not-found`: NotFound.jsx was added after QA and was
  never compared with the original's Nuxt 404; its styling is approximate. Pinned by verify_all.
* Every `reducedMotionFallback`: prescriptive. Neither the clone nor the original CSS has a
  `prefers-reduced-motion` rule.
* Copy budgets above the measured instance (capability cards 2-12, slides 2-6, member logos
  3-12, team members 1-20) are inferred ranges; the measured counts are 9, 5, 9 and 15.
* Lottie/video artwork (canvas and video pixels) was never measured.
* The accessibility snapshot showing cards and names as `generic[cursor=pointer]` does not record
  whether it captured the original or the clone.

## Known parity defects (kept as source-site behaviour)

* Capability accordion cards and team names are divs with `onClick` only: no role, not
  focusable, no key handling (`sections/capabilities.accordion.json`, `sections/team.roster.json`).
* The hamburger has `aria-label="Menu"` but no `aria-expanded`.
* The mobile-menu body scroll lock persists when resizing past 768 while the menu is open.

New builds should use button semantics and `aria-expanded`. That is a recommendation, not a
description of the source.

## Where the source contradicts CLONE_SPEC.md

* CLONE_SPEC 7.2 notes that the original's values-panel opacity starts at 0, but recommends
  initialising it to 1 "for the same visual result". The QA pass rejected that: the original
  measures `op:0` at load (`orig-1440.txt.n:85`), and the clone keeps 0 and drives opacity with an
  IntersectionObserver (rootMargin 100%) plus scroll progress, snapped to 0/1 on exit. This repo
  follows the measured behaviour, not the recommendation.
* CLONE_SPEC 9 gives the carousel transform as `-index*(slideW+20)` with no clamp. The QA dump
  shows it stopping at -1890px at 1440 (`orig-state-1440.txt.n:44-47`), and the clone clamps to
  track width minus viewport width.
* CLONE_SPEC 0 lists only two routes; the clone also renders a NotFound page for every other
  path (spec silent, unmeasured).

## Packaging

Build the zip with the CLI only, last, after every check passes:
`zip -rX design-repo.zip design-repo -x "*.DS_Store" "__MACOSX/*" "*/__pycache__/*"`.
`unzip -l design-repo.zip | grep -ic "__MACOSX\|\.DS_Store"` must print 0, and
`find design-repo -type f -newer design-repo.zip` must print nothing.
