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
  * MODE / TOKEN cases: generation-mode leakage of every category (brand, person,
    customer, copy, claim, URL, embed, asset; with homoglyph / zero-width /
    curly-quote / diacritic evasions) and every TOKEN_* rule; clone-mode controls
    prove real Equator content still validates (and that it really IS real content).
  * REPO_CASES: mutate a registry file (asset roles, section contracts) in a
    scratch copy of the repo to a DIFFERENT-BUT-VALID value and prove the pinned
    check (asset policy, availability, retrieval eligibility) rejects it.
  * GATE_CASES: extraction/wrapper_gate.py on mutated measurements / whitelist.
Finally asserts every graph rule, mode rule and token rule is exercised.

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

sys.path.insert(0, os.path.join(ROOT, "extraction"))
import wrapper_gate as wg  # noqa: E402

CTX = sv.load_context(ROOT)
EXDIR = os.path.join(ROOT, "schema", "examples")
EXAMPLES = {}
for _fn in sorted(os.listdir(EXDIR)):
    if _fn.endswith(".pagespec.json"):
        with open(os.path.join(EXDIR, _fn), encoding="utf-8") as f:
            EXAMPLES[_fn[: -len(".pagespec.json")]] = json.load(f)
EXAMPLE = EXAMPLES["home.clone"]


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
    return {"pageSpecVersion": "2.0.0", "mode": "clone", "template": tid, "route": route,
            "meta": {"title": "Control page", "description": "Generic control synthesised from the template."}, "nodes": nodes}


CONTROLS = {f"example:{k}": v for k, v in EXAMPLES.items()}
for tid in CTX["templates"]:
    CONTROLS[f"control:{tid}"] = build_control(tid)


def base(name):
    if name == "example":
        return copy.deepcopy(EXAMPLE)
    if name in EXAMPLES:
        return copy.deepcopy(EXAMPLES[name])
    return copy.deepcopy(CONTROLS[f"control:{name}"])


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
    ("schema:extra-top-level-field", "example", m(lambda s: s.__setitem__("layoutOverride", "dark")), "SCHEMA"),
    ("schema:missing-mode", "example", m(lambda s: s.pop("mode")), "SCHEMA"),
    ("schema:mode-not-in-enum", "example", m(lambda s: s.__setitem__("mode", "reference")), "SCHEMA"),
    ("schema:old-pagespec-version", "example", m(lambda s: s.__setitem__("pageSpecVersion", "1.0.0")), "SCHEMA"),
    ("schema:invented-token-slot", "home.generated", m(lambda s: node(s, "hero.title").__setitem__("tokens", {"shadow": "z.header"})), "SCHEMA"),
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
    ("runtime:maxwords-legal-part-heading", "template.legal-prose", m(lambda s: node(s, "content.legal-section")["content"].__setitem__("heading", words(9))), "MAX_WORDS"),
    ("runtime:maxwords-legal-paragraph", "template.legal-prose", m(lambda s: node(s, "content.legal-section")["content"]["paragraphs"].append(words(91))), "MAX_WORDS"),
    ("struct:legal-section-before-header", "legal.clone", m(lambda s: swap(s, "content.legal-header", "content.legal-section")), "TEMPLATE_SEQUENCE"),
    ("struct:legal-without-sections", "legal.clone", m(lambda s: s.__setitem__("nodes", [n for n in s["nodes"] if n["type"] != "content.legal-section"])), "TEMPLATE_SEQUENCE"),
    ("struct:legal-thirteen-parts", "legal.clone", m(lambda s: [s["nodes"].insert(2, copy.deepcopy(node(s, "content.legal-section"))) for _ in range(11)]), "ONE_PER_PAGE"),
    # ---- asset policy (schema-valid refs that break the role's policy)
    ("asset:omit-role-present-funding-emblem", "example", m(lambda s: node(s, "chrome.subfooter")["content"].__setitem__("emblem", {"assetRole": "funding-emblem", "assetRef": "placeholder:emblem"})), "ASSET_POLICY"),
    ("asset:omit-role-present-project-pdf", "example", m(lambda s: node(s, "chrome.subfooter")["content"].__setitem__("projectSheet", {"label": "Project sheet", "document": {"assetRole": "project-sheet-pdf", "assetRef": "placeholder:sheet"}})), "ASSET_POLICY"),
    ("asset:generated-likeness-of-employee", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRef", "generated:portrait-1")), "ASSET_POLICY"),
    ("asset:generated-halftone-likeness", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["halftone"].__setitem__("assetRef", "generated:halftone-1")), "ASSET_POLICY"),
    ("asset:recreated-brand-lottie", "example", m(lambda s: node(s, "values.sticky-stack")["content"]["panels"][0]["animation"].__setitem__("assetRef", "generated:value-animation")), "ASSET_POLICY"),
    ("asset:recreated-member-logo", "example", m(lambda s: node(s, "work.carousel-marquee")["content"]["memberLogos"][0].__setitem__("assetRef", "generated:member-logo-1")), "ASSET_POLICY"),
    ("asset:recreated-wordmark", "example", m(lambda s: node(s, "chrome.header")["content"]["logo"].__setitem__("assetRef", "generated:wordmark")), "ASSET_POLICY"),
    ("asset:clone-source-ref-not-a-real-file", "example", m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRef", "source:/team/invented-person")), "ASSET_POLICY"),
    ("asset:generation-safe-role-with-source-file", "home.generated", m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRef", "source:/team/rita-campos")), "ASSET_POLICY"),
    ("asset:user-ref-on-generated-role", "home.generated", m(lambda s: node(s, "hero.title")["content"]["backgroundVideo"].__setitem__("assetRef", "user:my-video")), "ASSET_POLICY"),
    ("clone:invented-external-url", "example", m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("primaryHref", "https://equator-signup-invented.com/join")), "CLONE_MODE_UNKNOWN_SOURCE"),
    ("clone:invented-email", "example", m(lambda s: node(s, "chrome.footer")["content"].__setitem__("email", "mailto:sales@invented-domain.com")), "CLONE_MODE_UNKNOWN_SOURCE"),
]

G = "home.generated"
HDR = lambda s: node(s, "capabilities.accordion")["content"]  # noqa: E731
CASES += [
    # ---- generation-mode leakage: brand (with evasions)
    ("gen:brand-in-heading", G, m(lambda s: HDR(s).__setitem__("heading", "Why choose Equator")), "GENERATION_MODE_BRAND"),
    ("gen:brand-letter-spaced", G, m(lambda s: HDR(s).__setitem__("heading", "Why choose E.Q.U.A.T.O.R")), "GENERATION_MODE_BRAND"),
    ("gen:brand-homoglyph", G, m(lambda s: HDR(s).__setitem__("heading", "Why choose \u0415quator")), "GENERATION_MODE_BRAND"),
    ("gen:brand-zero-width", G, m(lambda s: HDR(s).__setitem__("heading", "Why choose Equa\u200btor")), "GENERATION_MODE_BRAND"),
    ("gen:brand-legal-entity", G, m(lambda s: node(s, "chrome.footer")["content"].__setitem__("copyrightHolder", "S317 Consulting")), "GENERATION_MODE_BRAND"),
    ("gen:brand-in-meta-title", "not-found.generated", m(lambda s: s["meta"].__setitem__("title", "The Equator Company")), "GENERATION_MODE_BRAND"),
    ("gen:brand-in-asset-id", G, m(lambda s: node(s, "chrome.header")["content"]["logo"].__setitem__("assetRef", "placeholder:equator-wordmark")), "GENERATION_MODE_BRAND"),
    # ---- person
    ("gen:real-employee-name", G, m(lambda s: node(s, "team.roster")["content"]["members"][0].__setitem__("name", "Rita Campos")), "GENERATION_MODE_PERSON"),
    ("gen:real-employee-no-diacritics", G, m(lambda s: node(s, "team.roster")["content"]["members"][1].__setitem__("name", "Antonio Monteiro")), "GENERATION_MODE_PERSON"),
    ("gen:real-employee-with-diacritics", G, m(lambda s: node(s, "team.roster")["content"]["members"][1].__setitem__("name", "Cl\u00e1udia Tapadas")), "GENERATION_MODE_PERSON"),
    ("gen:real-employee-slug-asset", G, m(lambda s: node(s, "team.roster")["content"]["members"][0]["portrait"].__setitem__("assetRef", "generated:jose-palma")), "GENERATION_MODE_PERSON"),
    # ---- customer / partner
    ("gen:real-client-in-slide", G, m(lambda s: node(s, "work.carousel-marquee")["content"]["slides"][0].__setitem__("text", "A forest programme delivered with Mota-Engil.")), "GENERATION_MODE_CUSTOMER"),
    ("gen:real-merged-company-label", G, m(lambda s: node(s, "narrative.story-reveal")["content"]["mergerLogos"][1].__setitem__("label", "Sair da Casca")), "GENERATION_MODE_CUSTOMER"),
    ("gen:real-design-credit", G, m(lambda s: node(s, "chrome.footer")["content"].__setitem__("creditLine", "Design by Studio Cronica")), "GENERATION_MODE_CUSTOMER"),
    # ---- copy (hashed shingles, with curly quotes / case changes)
    ("gen:source-heading-copy", G, m(lambda s: node(s, "work.carousel-marquee")["content"].__setitem__("heading", "Trusted by those driving change")), "GENERATION_MODE_COPY"),
    ("gen:source-copy-curly-quotes", G, m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("heading", "LET\u2019S BUILD THE INFRASTRUCTURE of change")), "GENERATION_MODE_COPY"),
    ("gen:source-legal-text", "legal.generated", m(lambda s: node(s, "content.legal-section")["content"]["paragraphs"].__setitem__(0, "The data collected data is exclusively for the use of our studio.")), "GENERATION_MODE_COPY"),
    # ---- claims
    ("gen:claim-45-years", G, m(lambda s: node(s, "team.roster")["content"].__setitem__("heading", "Over 45 years on site")), "GENERATION_MODE_CLAIM"),
    ("gen:claim-public-funding", G, m(lambda s: node(s, "chrome.footer")["content"].__setitem__("blurb", "Co-funded by Recuperar Portugal.")), "GENERATION_MODE_CLAIM"),
    ("gen:claim-award", G, m(lambda s: node(s, "work.carousel-marquee")["content"]["slides"][2].__setitem__("text", "Winner of the European Excellence Award.")), "GENERATION_MODE_CLAIM"),
    # ---- URLs
    ("gen:source-domain-href", G, m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("secondaryHref", "https://equatorcompany.com/")), "GENERATION_MODE_URL"),
    ("gen:real-linkedin-profile", G, m(lambda s: node(s, "team.roster")["content"]["members"][0].__setitem__("profileUrl", "https://www.linkedin.com/in/someone/")), "GENERATION_MODE_URL"),
    ("gen:non-reserved-host", G, m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("primaryHref", "https://northwind.com/newsletter")), "GENERATION_MODE_URL"),
    ("gen:source-email", G, m(lambda s: node(s, "chrome.footer")["content"].__setitem__("email", "mailto:info@equatorcompany.com")), "GENERATION_MODE_URL"),
    ("gen:domain-in-copy", G, m(lambda s: node(s, "chrome.footer")["content"].__setitem__("addressLine", "See www.theequatorcompany.com")), "GENERATION_MODE_URL"),
    # ---- embeds
    ("gen:mailchimp-signup-form", G, m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("primaryHref", "https://mailchi.mp/960b9490730a/website-signup")), "GENERATION_MODE_EMBED"),
    ("gen:google-maps-place", G, m(lambda s: node(s, "conversion.cta-video")["content"].__setitem__("secondaryHref", "https://maps.app.goo.gl/DhKJrr1GrcZ6ptwT7")), "GENERATION_MODE_EMBED"),
    # ---- assets / proprietary media
    ("gen:source-file-ref", G, m(lambda s: node(s, "hero.title")["content"].__setitem__("backgroundVideo", {"assetRole": "ambient-video", "assetRef": "source:/bird_low.mp4"})), "GENERATION_MODE_ASSET"),
    ("gen:clone-only-role-placeholder", G, m(lambda s: node(s, "team.roster")["content"]["members"][0].__setitem__("portrait", {"assetRole": "team-portrait", "assetRef": "placeholder:portrait-1"})), "GENERATION_MODE_ASSET"),
    ("gen:real-wordmark-role", G, m(lambda s: node(s, "chrome.header")["content"].__setitem__("logo", {"assetRole": "brand-wordmark", "assetRef": "placeholder:wordmark"})), "GENERATION_MODE_ASSET"),
    ("gen:real-member-logo-role", G, m(lambda s: node(s, "work.carousel-marquee")["content"]["memberLogos"].__setitem__(0, {"assetRole": "member-logo", "assetRef": "placeholder:member-logo-1"})), "GENERATION_MODE_ASSET"),
    ("gen:blocked-funding-emblem", G, m(lambda s: node(s, "chrome.subfooter").__setitem__("content", {"emblem": {"assetRole": "funding-emblem", "assetRef": "source:/mono.svg"}})), "GENERATION_MODE_ASSET"),
    ("gen:real-asset-stem-as-id", G, m(lambda s: node(s, "conversion.cta-video")["content"]["backgroundVideo"].__setitem__("assetRef", "generated:cloud-low")), "GENERATION_MODE_ASSET"),
    ("gen:real-file-name-in-alt", G, m(lambda s: node(s, "narrative.story-reveal")["content"]["mergerLogos"][0]["logo"].__setitem__("alt", "logo_engidro.png")), "GENERATION_MODE_ASSET"),
    ("gen:real-lottie-file", G, m(lambda s: node(s, "values.sticky-stack")["content"]["panels"][0]["animation"].__setitem__("alt", "plays sustainability.lottie")), "GENERATION_MODE_ASSET"),
    # ---- tokens
    ("token:unknown", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("surface", "surface.brand")), "TOKEN_UNKNOWN"),
    ("token:raw-hex", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("surface", "#ff9d69")), "TOKEN_RAW_COLOR"),
    ("token:raw-rgba", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("text", "rgba(62,32,2,.7)")), "TOKEN_RAW_COLOR"),
    ("token:arbitrary-px", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("spacingY", "150px")), "TOKEN_ARBITRARY_SPACING"),
    ("token:arbitrary-calc", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("gap", "calc(100% - 64px)")), "TOKEN_ARBITRARY_SPACING"),
    ("token:unsupported-font", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("fontFamily", "Inter")), "TOKEN_FONT_UNSUPPORTED"),
    ("token:foundation-colour-as-surface", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("surface", "color.coral")), "TOKEN_SLOT_MISMATCH"),
    ("token:text-role-as-surface", G, m(lambda s: node(s, "hero.title")["tokens"].__setitem__("surface", "text.primary")), "TOKEN_SLOT_MISMATCH"),
    ("token:unvalidated-theme", G, m(lambda s: s.__setitem__("theme", "dark")), "TOKEN_THEME_COMBINATION"),
    # ---- retrieval eligibility at node level
    ("retrieval:splash-node-flipped-eligible", "example", m(lambda s: node(s, "chrome.splash").__setitem__("retrievalEligible", True)), "RETRIEVAL_ELIGIBILITY_PIN"),
    ("retrieval:content-node-marked-ineligible", "example", m(lambda s: node(s, "capabilities.accordion").__setitem__("retrievalEligible", False)), "RETRIEVAL_ELIGIBILITY_PIN"),
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


def mutate_role(role, value, key="generationPolicy"):
    def f(d):
        d["roles"][role][key] = value
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


def sec_set(key, value):
    def f(d):
        d[key] = value
    return f


AR = "assets/asset-roles.json"
# (id, file, mutate, expected code). Different-but-VALID values only: exactly what an enum-membership check misses.
REPO_CASES = [
    ("pin:team-portrait->may-generate-new", AR, mutate_role("team-portrait", "may-generate-new"), "ASSET_ROLE_PIN"),
    ("pin:team-halftone->must-not-reproduce", AR, mutate_role("team-halftone", "must-not-reproduce"), "ASSET_ROLE_PIN"),
    ("pin:merger-logo->placeholder-only", AR, mutate_role("merger-logo", "placeholder-only"), "ASSET_ROLE_PIN"),
    ("pin:member-logo->may-generate-new", AR, mutate_role("member-logo", "may-generate-new"), "ASSET_ROLE_PIN"),
    ("pin:brand-lottie-value->may-generate-new", AR, mutate_role("brand-lottie-value", "may-generate-new"), "ASSET_ROLE_PIN"),
    ("pin:funding-emblem->placeholder-only", AR, mutate_role("funding-emblem", "placeholder-only"), "ASSET_ROLE_PIN"),
    ("pin:project-sheet-pdf->placeholder-only", AR, mutate_role("project-sheet-pdf", "placeholder-only"), "ASSET_ROLE_PIN"),
    ("pin:fictional-avatar->operator-supplied", AR, mutate_role("fictional-avatar", "operator-supplied"), "ASSET_ROLE_PIN"),
    ("pin:team-halftone-unpinned", AR, unpin("team-halftone"), "ASSET_ROLE_PIN"),
    ("pin:unpinned-role-marked-pinned-without-code-pin", AR, pin_flag("project-photo"), "ASSET_ROLE_PIN"),
    ("pin:font-licence->not-required", AR, licence("not-required"), "ASSET_ROLE_PIN"),
    ("availability:team-portrait->generation-safe", AR, mutate_role("team-portrait", "generation-safe", "availability"), "ASSET_AVAILABILITY_PIN"),
    ("availability:brand-wordmark->generation-safe", AR, mutate_role("brand-wordmark", "generation-safe", "availability"), "ASSET_AVAILABILITY_PIN"),
    ("availability:funding-emblem->clone-only", AR, mutate_role("funding-emblem", "clone-only", "availability"), "ASSET_AVAILABILITY_PIN"),
    ("availability:placeholder-url->clone-only", AR, mutate_role("placeholder-url", "clone-only", "availability"), "ASSET_AVAILABILITY_PIN"),
    ("availability:substitute-is-clone-only", AR, mutate_role("member-logo", ["merger-logo"], "generationSafeSubstitutes"), "ASSET_AVAILABILITY_PIN"),
    ("availability:clone-only-role-without-substitute", AR, mutate_role("project-photo", [], "generationSafeSubstitutes"), "ASSET_AVAILABILITY_PIN"),
    ("retrieval:splash-contract-flipped-eligible", "sections/chrome.splash.json", sec_set("retrievalEligible", True), "RETRIEVAL_ELIGIBILITY_PIN"),
    ("retrieval:hero-contract-marked-ineligible", "sections/hero.title.json", sec_set("retrievalEligible", False), "RETRIEVAL_ELIGIBILITY_PIN"),
    ("retrieval:ineligible-reason-too-short", "sections/chrome.splash.json", sec_set("retrievalReason", "intro"), "RETRIEVAL_ELIGIBILITY_PIN"),
    ("retrieval:runtime-ui-named-section-unpinned", "sections/content.not-found.json", sec_set("name", "Cookie consent banner"), "RETRIEVAL_ELIGIBILITY_PIN"),
]


def _gate_measured():
    with open(os.path.join(ROOT, "extraction", "measured-values.json"), encoding="utf-8") as f:
        return json.load(f)


def _gate_set(tid, sid, h, page=None):
    def f(mv, wl):
        row = next(s for s in mv["sectionHeights"]["templates"][tid]["sections"] if s["section"] == sid)
        row["height"] = h
        if page:
            mv["sectionHeights"]["templates"][tid]["pageHeight"] = page
    return f


def _wl(entry):
    def f(mv, wl):
        wl["entries"].append(entry)
    return f


AGENT = "agent attestation, not a human sign-off"
# (id, mutate(measured, whitelist), expect "error" or "warn", substring)
GATE_CASES = [
    ("gate:hero-1900-warns", _gate_set("template.home", "hero.title", 1900), "warn", "HERO 1900"),
    ("gate:hero-3100-errors", _gate_set("template.home", "hero.title", 3100), "error", "HERO 3100"),
    ("gate:majority-section-55-warns", _gate_set("template.home", "values.sticky-stack", 9000, 16500), "warn", "holds"),
    ("gate:majority-section-80-errors", _gate_set("template.legal-prose", "content.legal-header", 3476.4, 4423), "error", "holds"),
    ("gate:missing-measurement", lambda mv, wl: mv["sectionHeights"]["templates"].pop("template.not-found"), "error", "no sectionHeights"),
    ("gate:null-height", _gate_set("template.home", "team.roster", None), "error", "missing (null)"),
    ("gate:wrong-viewport", lambda mv, wl: mv["sectionHeights"].__setitem__("viewport", 1280), "error", "viewport 1280"),
    ("gate:whitelist-no-justification", _wl({"template": "template.home", "section": "values.sticky-stack", "maxHeightPx": 4000, "reviewedBy": AGENT, "justification": "ok"}), "error", "justification"),
    ("gate:whitelist-agent-without-attestation", _wl({"template": "template.home", "section": "values.sticky-stack", "maxHeightPx": 4000, "reviewedBy": "review agent", "justification": "x" * 40}), "error", "must state"),
    ("gate:whitelist-stale", _wl({"template": "template.home", "section": "values.sticky-stack", "maxHeightPx": 4000, "reviewedBy": AGENT, "justification": "x" * 40}), "error", "stale"),
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

    for cid, rel, mutate, code in REPO_CASES:
        tmp = tempfile.mkdtemp(prefix="equator-pin-")
        try:
            repo = os.path.join(tmp, "design-repo")
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
            p = os.path.join(repo, rel)
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            mutate(d)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f)
            iss = sv.validate(copy.deepcopy(EXAMPLE), root=repo)
            ok = any(i.code == code for i in iss)
            covered.add(code)
            rows.append(("REJECT" if ok else "MISSED", cid, f"{code} fired" if ok else f"{code} silent"))
            if not ok:
                failures.append(cid)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    base_err, base_warn = wg.run(ROOT)
    ok = not base_err and not base_warn
    rows.append(("CONTROL", "wrapper-gate:real-measurements", "pass (0 errors, 0 warnings)" if ok else f"FAIL {base_err + base_warn}"))
    if not ok:
        failures.append("wrapper-gate-control")
    for cid, mutate, kind, needle in GATE_CASES:
        mv = _gate_measured()
        wl = {"entries": []}
        mutate(mv, wl)
        err, warn = wg.run(ROOT, measured=mv, whitelist=wl)
        bucket = err if kind == "error" else warn
        ok = any(needle in x for x in bucket) and (kind == "error" or not err)
        rows.append(("REJECT" if ok else "MISSED", cid, f"{kind}: {next((x for x in bucket if needle in x), '')[:70]}" if ok else f"expected {kind} with '{needle}', got errors={err} warns={warn}"))
        if not ok:
            failures.append(cid)

    # clone mode must really contain real Equator content (otherwise the clone control proves nothing)
    for name in ("home.clone", "legal.clone"):
        gen = copy.deepcopy(EXAMPLES[name])
        gen["mode"] = "generation"
        codes = {i.code for i in sv.validate(gen, ctx=CTX) if i.severity == "error"}
        need = {"GENERATION_MODE_BRAND", "GENERATION_MODE_COPY"} | ({"GENERATION_MODE_PERSON", "GENERATION_MODE_ASSET", "GENERATION_MODE_URL"} if name == "home.clone" else set())
        ok = need <= codes
        rows.append(("CONTROL", f"clone-has-real-content:{name}", f"same spec as generation trips {sorted(need)}" if ok else f"FAIL only {sorted(codes)}"))
        if not ok:
            failures.append(f"clone-real:{name}")
    # warn-only control: licensed font in generation mode warns, never errors
    wc = base("home.generated")
    node(wc, "hero.title")["tokens"]["fontFamily"] = "font.family.national"
    iss = sv.validate(wc, ctx=CTX)
    ok = not [i for i in iss if i.severity == "error"] and any(i.code == "TOKEN_FONT_LICENCE" for i in iss)
    covered.add("TOKEN_FONT_LICENCE")
    rows.append(("CONTROL", "warn-only:generation-licensed-font", "pass (warning only)" if ok else f"FAIL {iss}"))
    if not ok:
        failures.append("warn-only-font")

    missing = sorted((set(CTX["graph"]) | set(sv.MODE_RULES) | set(sv.TOKEN_RULES)) - covered)
    rows.append(("COVERAGE", "every graph/mode/token rule exercised", "ok" if not missing else f"UNCOVERED {missing}"))
    if missing:
        failures.append("coverage")

    for kind, name, detail in rows:
        print(f"{kind:8} {name:48} {detail}")
    n_mut = N_MUTATIONS
    n_ctrl = N_CONTROLS
    print(f"\n{n_mut} mutations, {n_ctrl} controls, {len(failures)} failure(s)")
    return 1 if failures else 0


N_MUTATIONS = len(CASES) + len(RULE_CASES) + len(REPO_CASES) + len(GATE_CASES)
N_CONTROLS = len(CONTROLS) + 1 + 1 + 2 + 1  # examples+synthesised, warn-only route, gate control, 2 clone-real, warn-only font
TOTAL_CASES = N_MUTATIONS + N_CONTROLS

if __name__ == "__main__":
    sys.exit(run())
