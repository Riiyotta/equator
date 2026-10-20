#!/usr/bin/env python3
"""Adversarial suite for the Equator design-repo.

Proves every rule rejects a bad instance, and that real structures pass:
  * CONTROLS: the bundled example plus one generic control synthesised per
    template from templates.json + each section's own fixtures (a new template
    is covered automatically, with no new control code), plus a warn-only
    control showing that warn-severity rules do not fail a page.
  * CASES: PageSpec mutations. Each names the rule code that MUST fire, so a
    case cannot pass by tripping some unrelated check.
  * RULE_CASES: direct calls into a rule function for rules the schema layer
    already shields (defence in depth must still work on its own).
  * REPO_CASES: mutate assets/asset-roles.json in a scratch copy of the repo to
    a DIFFERENT-BUT-VALID value and prove the pinned-value check rejects it.
Finally asserts every graph rule id is exercised by at least one case.

Exit 0 only if every mutation is rejected and every control passes.
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "schema"))
import semantic_validate as sv  # noqa: E402

CTX = sv.load_context(ROOT)
with open(os.path.join(ROOT, "schema", "example.pagespec.json"), encoding="utf-8") as f:
    EXAMPLE = json.load(f)


def build_control(tid):
    t = CTX["templates"][tid]
    pol = t["routePolicy"]
    route = {"exact": pol.get("route"), "catch-all": "*"}.get(pol["kind"]) or pol["registered"][0]
    nodes = []
    for tn in t["nodes"]:
        if not tn["required"]:
            continue
        sec = CTX["sections"][tn["section"]]
        fx = copy.deepcopy(sec["fixtures"][tn.get("variant") or "default"])
        node = {"type": sec["id"]}
        if "variant" in fx:
            node["variant"] = fx["variant"]
            m = sec["motion"]["variants"][fx["variant"]]
        else:
            m = sec["motion"]
        if sec.get("anchor"):
            node["anchorId"] = sec["anchor"]
        node["content"] = fx["content"]
        node["motion"] = {k: m[k] for k in ("pattern", "trigger", "reducedMotionFallback")}
        nodes.append(node)
    return {"pageSpecVersion": "1.0.0", "template": tid, "route": route,
            "meta": {"title": "Control page", "description": "Generic control synthesised from the template."}, "nodes": nodes}


CONTROLS = {"example": EXAMPLE}
for tid in CTX["templates"]:
    CONTROLS[f"control:{tid}"] = build_control(tid)


def base(name):
    return copy.deepcopy(EXAMPLE if name == "example" else CONTROLS[f"control:{name}"])


def ix(spec, t):
    return next(i for i, n in enumerate(spec["nodes"]) if n["type"] == t)


def node(spec, t):
    return spec["nodes"][ix(spec, t)]


def words(n):
    return " ".join(["word"] * n)


def swap(spec, a, b):
    i, j = ix(spec, a), ix(spec, b)
    spec["nodes"][i], spec["nodes"][j] = spec["nodes"][j], spec["nodes"][i]


def move_after(spec, t, after):
    n = spec["nodes"].pop(ix(spec, t))
    spec["nodes"].insert(ix(spec, after) + 1, n)


def m(fn):
    return fn


# (id, base, mutate(spec), expected rule code)
CASES = [
    # ---- schema layer
    ("schema:bad-template-enum", "example", m(lambda s: s.__setitem__("template", "template.blog")), "SCHEMA"),
    ("schema:invented-node-type", "example", m(lambda s: s["nodes"][2].__setitem__("type", "hero.video-banner")), "SCHEMA"),
    ("schema:missing-motion", "example", m(lambda s: node(s, "narrative.story-reveal").pop("motion")), "SCHEMA"),
    ("schema:missing-reducedMotionFallback", "example", m(lambda s: node(s, "narrative.story-reveal")["motion"].pop("reducedMotionFallback")), "SCHEMA"),
    ("schema:story-fallback-not-const", "example", m(lambda s: node(s, "narrative.story-reveal")["motion"].__setitem__("reducedMotionFallback", "fade-in")), "SCHEMA"),
    ("schema:values-fallback-borrowed-from-story", "example", m(lambda s: node(s, "values.sticky-stack")["motion"].__setitem__("reducedMotionFallback", "all-words-visible")), "SCHEMA"),
    ("schema:marquee-pattern-swapped", "example", m(lambda s: node(s, "work.carousel-marquee")["motion"].__setitem__("pattern", "accordion-expand-120ms")), "SCHEMA"),
    ("schema:invented-motion-field", "example", m(lambda s: node(s, "values.sticky-stack")["motion"].__setitem__("inventedAnimation", "parallax")), "SCHEMA"),
    ("schema:invented-content-field", "example", m(lambda s: node(s, "capabilities.accordion")["content"]["cards"][0].__setitem__("icon", "star")), "SCHEMA"),
    ("schema:values-four-panels", "example", m(lambda s: node(s, "values.sticky-stack")["content"]["panels"].pop()), "SCHEMA"),
    ("schema:invented-asset-role", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRole", "stock-photo")), "SCHEMA"),
    ("schema:role-not-allowed-for-field", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRole", "project-photo")), "SCHEMA"),
    ("schema:real-logo-file-path", "example", m(lambda s: node(s, "narrative.story-reveal")["content"]["mergerLogos"][0]["logo"].__setitem__("assetRef", "/logo_s317.png")), "SCHEMA"),
    ("schema:header-variant-invalid", "example", m(lambda s: node(s, "chrome.header").__setitem__("variant", "mobile")), "SCHEMA"),
    ("schema:extra-top-level-field", "example", m(lambda s: s.__setitem__("theme", "dark")), "SCHEMA"),
    ("schema:live-signup-endpoint", "example", m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("primaryHref", "https://mailchi.mp/x/website-signup")), "SCHEMA"),
    ("schema:real-profile-url", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0].__setitem__("profileUrl", "https://www.linkedin.com/in/someone/")), "SCHEMA"),
    ("schema:missing-anchorId", "example", m(lambda s: node(s, "values.sticky-stack").pop("anchorId")), "SCHEMA"),
    ("schema:not-found-wrong-code", "template.not-found", m(lambda s: s["nodes"][0]["content"].__setitem__("code", "500")), "SCHEMA"),
    # ---- structural / template linkage
    ("struct:template-mismatch-declared-legal", "example", m(lambda s: (s.__setitem__("template", "template.legal-prose"), s.__setitem__("route", "/privacy-policy"))), "TEMPLATE_SEQUENCE"),
    ("struct:removed-mandatory-values", "example", m(lambda s: s["nodes"].pop(ix(s, "values.sticky-stack"))), "TEMPLATE_SEQUENCE"),
    ("struct:duplicate-hero", "example", m(lambda s: s["nodes"].insert(ix(s, "hero.title") + 1, copy.deepcopy(node(s, "hero.title")))), "ONE_HERO"),
    ("struct:duplicate-capabilities", "example", m(lambda s: s["nodes"].insert(ix(s, "capabilities.accordion") + 1, dict(copy.deepcopy(node(s, "capabilities.accordion")), anchorId="capabilities-2"))), "ONE_PER_PAGE"),
    ("struct:footer-before-cta", "example", m(lambda s: swap(s, "conversion.cta-video", "chrome.footer")), "CTA_IMMEDIATELY_BEFORE_FOOTER"),
    ("struct:subfooter-not-last", "example", m(lambda s: swap(s, "chrome.footer", "chrome.subfooter")), "FOOTER_SUBFOOTER_TAIL"),
    ("struct:splash-not-first", "example", m(lambda s: swap(s, "chrome.splash", "chrome.header")), "SPLASH_FIRST_HOME_ONLY"),
    ("struct:splash-on-legal-page", "template.legal-prose", m(lambda s: s["nodes"].insert(0, copy.deepcopy(node(EXAMPLE, "chrome.splash")))), "SPLASH_FIRST_HOME_ONLY"),
    ("struct:header-on-not-found", "template.not-found", m(lambda s: s["nodes"].insert(0, copy.deepcopy(node(CONTROLS["control:template.legal-prose"], "chrome.header")))), "HEADER_POSITION"),
    ("struct:legal-header-variant-on-home", "example", m(lambda s: node(s, "chrome.header").update(variant="legal", motion={"pattern": "menu-slide-200ms", "trigger": "click", "reducedMotionFallback": "menu-instant-toggle"})), "TEMPLATE_SEQUENCE"),
    ("struct:header-motion-mismatch-variant", "example", m(lambda s: node(s, "chrome.header").update(motion={"pattern": "menu-slide-200ms", "trigger": "click", "reducedMotionFallback": "menu-instant-toggle"})), "HEADER_VARIANT_MATCH"),
    ("struct:three-consecutive-scroll-stages", "example", m(lambda s: move_after(s, "team.roster", "values.sticky-stack")), "MAX_CONSECUTIVE_SCROLL_STAGES"),
    ("struct:nav-anchor-unresolved", "example", m(lambda s: node(s, "chrome.header")["content"]["navItems"][0].__setitem__("anchor", "about-us")), "NAV_ANCHORS_RESOLVE"),
    ("struct:legal-nav-anchor-unresolved", "template.legal-prose", m(lambda s: s["nodes"][0]["content"]["navItems"][0].__setitem__("anchor", "about-us")), "NAV_ANCHORS_RESOLVE"),
    ("struct:duplicate-anchorId", "example", m(lambda s: node(s, "capabilities.accordion").__setitem__("anchorId", "our-story")), "ANCHOR_UNIQUE"),
    # ---- routes
    ("route:home-at-privacy-route", "example", m(lambda s: s.__setitem__("route", "/privacy-policy")), "ROUTE_TEMPLATE_BINDING"),
    ("route:not-found-at-root", "template.not-found", m(lambda s: s.__setitem__("route", "/")), "ROUTE_TEMPLATE_BINDING"),
    ("route:registered-route-wrong-template", "template.not-found", m(lambda s: s.__setitem__("route", "/privacy-policy")), "ROUTE_TEMPLATE_BINDING"),
    ("route:legal-at-catch-all", "template.legal-prose", m(lambda s: s.__setitem__("route", "*")), "ROUTE_TEMPLATE_BINDING"),
    # ---- content budgets / story
    ("runtime:story-reveal-over-60", "example", m(lambda s: node(s, "narrative.story-reveal")["content"].__setitem__("statements", [{"text": words(12), "indent": False} for _ in range(4)])), "STORY_REVEAL_BUDGET"),
    ("runtime:story-emphasis-out-of-range", "example", m(lambda s: node(s, "narrative.story-reveal")["content"]["statements"][3].__setitem__("emphasisFromWord", 11)), "STORY_REVEAL_BUDGET"),
    ("runtime:maxwords-title-subtitle", "example", m(lambda s: node(s, "hero.title")["content"].__setitem__("subtitle", words(25))), "MAX_WORDS"),
    ("runtime:maxwords-capability-card", "example", m(lambda s: node(s, "capabilities.accordion")["content"]["cards"][4].__setitem__("text", words(40))), "MAX_WORDS"),
    ("runtime:maxwords-slide-text", "example", m(lambda s: node(s, "work.carousel-marquee")["content"]["slides"][0].__setitem__("text", words(73))), "MAX_WORDS"),
    ("runtime:maxwords-meta-title", "example", m(lambda s: s["meta"].__setitem__("title", words(10))), "MAX_WORDS"),
    ("runtime:maxwords-legal-subheading-by-kind", "template.legal-prose", m(lambda s: s["nodes"][1]["content"]["blocks"].append({"kind": "subheading", "text": words(12)})), "MAX_WORDS"),
    # ---- asset policy (schema-valid refs that break the role's policy)
    ("asset:omit-role-present-funding-emblem", "example", m(lambda s: node(s, "chrome.subfooter")["content"].__setitem__("emblem", {"assetRole": "funding-emblem", "assetRef": "placeholder:emblem"})), "ASSET_POLICY"),
    ("asset:omit-role-present-project-pdf", "example", m(lambda s: node(s, "chrome.subfooter")["content"].__setitem__("projectSheet", {"label": "Project sheet", "document": {"assetRole": "project-sheet-pdf", "assetRef": "placeholder:sheet"}})), "ASSET_POLICY"),
    ("asset:generated-likeness-of-employee", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRef", "generated:portrait-1")), "ASSET_POLICY"),
    ("asset:generated-halftone-likeness", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["halftone"].__setitem__("assetRef", "generated:halftone-1")), "ASSET_POLICY"),
    ("asset:recreated-brand-lottie", "example", m(lambda s: node(s, "values.sticky-stack")["content"]["panels"][0]["animation"].__setitem__("assetRef", "generated:value-animation")), "ASSET_POLICY"),
    ("asset:recreated-member-logo", "example", m(lambda s: node(s, "work.carousel-marquee")["content"]["memberLogos"][0].__setitem__("assetRef", "generated:member-logo-1")), "ASSET_POLICY"),
    ("asset:recreated-wordmark", "example", m(lambda s: node(s, "chrome.header")["content"]["logo"].__setitem__("assetRef", "generated:wordmark")), "ASSET_POLICY"),
]


def partial(*types):
    return {"nodes": [{"type": t, "content": {}, "motion": {}} for t in types]}


# Direct rule-function checks for rules the schema shields (id, rule, spec, expected severity)
RULE_CASES = [
    ("rule:values-three-panels", "VALUES_FIVE_PANELS", {"nodes": [{"type": "values.sticky-stack", "content": {"panels": [{}, {}, {}]}, "motion": {}}]}),
    ("rule:three-ambient-videos", "AMBIENT_VIDEO_BUDGET", {"nodes": [{"type": "hero.title", "content": {"v": [{"assetRole": "ambient-video", "assetRef": "placeholder:a"}] * 3}}]}),
    ("rule:surface-repeat-oat", "SURFACE_RHYTHM", partial("narrative.story-reveal", "capabilities.accordion")),
    ("rule:one-hero-direct", "ONE_HERO", partial("hero.title", "hero.title")),
]


def mutate_role(role, value):
    def f(d):
        d["roles"][role]["generationPolicy"] = value
    return f


def unpin(role):
    def f(d):
        d["roles"][role]["pinned"] = False
    return f


def pin_flag(role):
    def f(d):
        d["roles"][role]["pinned"] = True
    return f


def licence(value):
    def f(d):
        d["licensedResources"]["font.national-2"]["licence"] = value
    return f


# Different-but-VALID values only: exactly what an enum-membership check misses.
REPO_CASES = [
    ("pin:team-portrait->may-generate-new", mutate_role("team-portrait", "may-generate-new")),
    ("pin:team-halftone->must-not-reproduce", mutate_role("team-halftone", "must-not-reproduce")),
    ("pin:merger-logo->placeholder-only", mutate_role("merger-logo", "placeholder-only")),
    ("pin:member-logo->may-generate-new", mutate_role("member-logo", "may-generate-new")),
    ("pin:brand-lottie-value->may-generate-new", mutate_role("brand-lottie-value", "may-generate-new")),
    ("pin:funding-emblem->placeholder-only", mutate_role("funding-emblem", "placeholder-only")),
    ("pin:project-sheet-pdf->placeholder-only", mutate_role("project-sheet-pdf", "placeholder-only")),
    ("pin:team-halftone-unpinned", unpin("team-halftone")),
    ("pin:unpinned-role-marked-pinned-without-code-pin", pin_flag("project-photo")),
    ("pin:font-licence->not-required", licence("not-required")),
]


def run():
    failures, rows = [], []
    covered = set()

    # Real structures must be clean: no errors AND no warnings. Zero warnings proves the
    # SURFACE_RHYTHM exceptions cover every real adjacency (the rule itself is proven to fire below).
    for name, spec in CONTROLS.items():
        iss = sv.validate(spec, ctx=CTX)
        ok = not iss
        rows.append(("CONTROL", name, "pass (0 errors, 0 warnings)" if ok else f"FAIL {iss[:3]}"))
        if not ok:
            failures.append(name)

    warn_ctrl = base("template.legal-prose")
    warn_ctrl["route"] = "/terms"
    iss = sv.validate(warn_ctrl, ctx=CTX)
    ok = not [i for i in iss if i.severity == "error"] and any(i.code == "NEW_ROUTE_NOTICE" and i.severity == "warn" for i in iss)
    rows.append(("CONTROL", "warn-only:legal-at-new-route", "pass (warning only)" if ok else f"FAIL {iss}"))
    covered.add("NEW_ROUTE_NOTICE")
    if not ok:
        failures.append("warn-only")

    for cid, b, fn, expected in CASES:
        spec = base(b)
        fn(spec)
        iss = sv.validate(spec, ctx=CTX)
        codes = {i.code for i in iss if i.severity == "error"}
        ok = expected in codes
        covered.add(expected)
        rows.append(("REJECT" if ok else "MISSED", cid, f"{expected} fired" if ok else f"expected {expected}, got {sorted(codes) or 'no errors'}"))
        if not ok:
            failures.append(cid)

    for cid, rid, spec in RULE_CASES:
        hits = sv.GRAPH_RULES[rid][1](spec, CTX)
        ok = bool(hits)
        covered.add(rid)
        rows.append(("REJECT" if ok else "MISSED", cid, f"{rid} fired ({CTX['graph'][rid]['severity']})" if ok else f"{rid} silent"))
        if not ok:
            failures.append(cid)

    for cid, mutate in REPO_CASES:
        tmp = tempfile.mkdtemp(prefix="equator-pin-")
        try:
            repo = os.path.join(tmp, "design-repo")
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            p = os.path.join(repo, "assets", "asset-roles.json")
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            mutate(d)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f)
            iss = sv.validate(copy.deepcopy(EXAMPLE), root=repo)
            ok = any(i.code == "ASSET_ROLE_PIN" for i in iss)
            rows.append(("REJECT" if ok else "MISSED", cid, "ASSET_ROLE_PIN fired" if ok else "pin check silent"))
            if not ok:
                failures.append(cid)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    missing = sorted(set(CTX["graph"]) - covered)
    rows.append(("COVERAGE", "every graph rule exercised", "ok" if not missing else f"UNCOVERED {missing}"))
    if missing:
        failures.append("coverage")

    for kind, name, detail in rows:
        print(f"{kind:8} {name:48} {detail}")
    n_mut = len(CASES) + len(RULE_CASES) + len(REPO_CASES)
    n_ctrl = len(CONTROLS) + 1
    print(f"\n{n_mut} mutations, {n_ctrl} controls, {len(failures)} failure(s)")
    return 1 if failures else 0


TOTAL_CASES = len(CASES) + len(RULE_CASES) + len(REPO_CASES) + len(CONTROLS) + 1

if __name__ == "__main__":
    sys.exit(run())
