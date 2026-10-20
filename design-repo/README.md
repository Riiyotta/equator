# Equator design-repo

A machine-validated PageSpec system extracted from the Equator clone (a pixel replica of
https://equatorcompany.com/, The Equator Company). It tells a generator what it may use, how
sections may be combined, and how they behave across content and breakpoints, without
inventing colours, copy budgets, structure or assets.

**Status: `design-review-pending`, `productionApproved: false`.** The source is the live site of a
real company. Do not publish this package, and do not make a repository holding it public.

## Source

| | |
|---|---|
| Original | Nuxt 3 / Vue 3, Locomotive Scroll v5 (Lenis 1.1.9), dotlottie-web 0.54.1, vue3-carousel, marquee3k |
| Clone (measured) | React ^18.3.1, Vite ^5.4.10, Tailwind ^3.4.14, lenis ^1.3.27, @lottiefiles/dotlottie-web ^0.81.0 (from `package.json`) |
| Evidence | clone `src/`, `tailwind.config.cjs`, `CLONE_SPEC.md`, the saved original CSS bundles, Playwright QA dumps in `.playwright-mcp/` |

The source project is **not a git repository**. If it becomes one, add `design-repo.zip` to
`.gitignore` and never commit the zip next to this folder (two disagreeing copies).

## Layout

```
design-repo/
  README.md  CHANGELOG.md  registry.manifest.json
  tokens/00-foundation/   color, typography, radius, spacing, breakpoint, elevation, icon-size, motion
  tokens/10-semantic/     intent roles referencing foundation tokens
  tokens/20-component/    component-scoped values
  tokens/30-layout/       grid and measures
  tokens/themes/light.json   the only theme (the original has no dark mode)
  tokens/llm/             component-allowlist.json, token-catalog.json, token-policy.json
  primitives/  components/  sections/      one JSON contract each
  templates/templates.json  templates/routes.json
  compatibility/graph.json  rhythm/position rules with severity
  assets/asset-roles.json   closed asset-role vocabulary + generation policies + pins
  schema/pagespec.schema.json  schema/example.pagespec.json  schema/semantic_validate.py
  schema/tests/adversarial_test.py
  extraction/measured-values.json  extraction/verify_all.py  extraction/prove_drift.py
```

## Counts (recomputed from disk; `verify_all.py` fails if this table drifts)

| count | value |
|---|---|
| `tokens` | 114 |
| `primitives` | 12 |
| `components` | 8 |
| `sections` | 13 |
| `templates` | 3 |
| `routes` | 3 |
| `assetRoles` | 12 |
| `graphRules` | 19 |
| `adversarialMutations` | 66 |
| `adversarialControls` | 5 |
| `citations` | 247 |

Token count = `$value` leaves in `00-foundation`, `10-semantic`, `20-component`, `30-layout`.

## Templates and routes

| Route | Template | Nodes | Evidence |
|---|---|---|---|
| `/` | `template.home` | splash, header(home), title, story, values, capabilities, work, team, CTA, footer, subfooter? | measured |
| `/privacy-policy` | `template.legal-prose` | header(legal), legal-prose, footer, subfooter? | measured |
| `*` (any other path) | `template.not-found` | not-found | **inferred-unmeasured** |

Nav anchors (`/#our-story` and so on) are sections of `/`, not routes. `?` = optional.
Template nodes are structured `{section, required, repeatable, variant?}` objects.

## Run

```
python3 schema/semantic_validate.py [spec.json ...]   # schema + semantic rules; exit 1 on errors
python3 schema/tests/adversarial_test.py              # 66 mutations rejected, 5 controls pass
python3 extraction/verify_all.py                      # 19 checks, includes the adversarial suite
python3 extraction/prove_drift.py                     # injects a defect per check, proves each fails
```

Requires Python 3 with `jsonschema` (tested with 4.25.1). All scripts derive their root from
`__file__`, so the folder works wherever it is unpacked. When the sibling source tree is absent,
citation checks downgrade to WARN instead of failing.

## What is enforced

* **Schema (draft-07):** closed template and node-type enums, `additionalProperties:false` at
  every level, one closed if/then branch per section type, closed motion object
  `{pattern, trigger, reducedMotionFallback}` with const-locked values per section, closed
  `assetRole` enum per media field, `assetRef` restricted to `placeholder:` / `generated:` ids,
  hrefs restricted to placeholders or relative paths.
* **Semantic validator:** the declared `template` is matched against that template's real node
  list; route/template binding; all 19 graph rules at their declared severity (error or warn);
  per-instance `maxWords`; asset generation policies; pinned values for the compliance-critical
  roles (`team-portrait`, `team-halftone`, `merger-logo`, `member-logo`, `brand-wordmark`, the three
  brand Lottie roles, `funding-emblem`, `project-sheet-pdf`) and the font licence.
* **verify_all.py:** allowlistVersion 1.0.0 parity, allowlist parity, manifest + README counts,
  citation range and quoted-content validity, absolute-path scan, entry points inside the
  package, schema/contract parity, graph/validator parity, route coverage, theme resolution,
  token catalog/policy key parity, asset-role closure and pins, structured 768 responsive entries, evidence-level pins, status
  flags, framework-version drift against `../package.json`.

## Real-company constraints (load-bearing)

* Asset roles and policies (`assets/asset-roles.json`): real employees' portraits and halftones
  are `placeholder-only`; merger/member logos, the wordmark and the brand Lotties are
  `must-not-reproduce`; the PRR/EU funding emblem and the project-sheet PDF are `omit`;
  project photos and ambient video are `may-generate-new` (never the real files, no identifiable
  people, clients or sites).
* National 2 (Klim Type Foundry) is **licence-required**; generated output uses the fallback stack
  unless the deployer holds a licence.
* The example uses real headings and short labels only. Team names, client names and the
  privacy-policy text are not reproduced. Contracts describe fields and budgets, not prose.
* CTA links go to a live Mailchimp endpoint and the company LinkedIn on the source: the schema
  allows only placeholder or relative hrefs.

## Inferred / unmeasured

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
