#!/usr/bin/env python3
"""Semantic validator for Equator design-repo PageSpecs.

Enforces what JSON Schema (draft-07) cannot express:
  * the declared `template` is cross-referenced against that template's real
    node list in templates/templates.json (TEMPLATE_SEQUENCE)
  * route <-> template binding from templates/routes.json
  * every rule in compatibility/graph.json, at the severity the graph declares
  * per-instance maxWords (x-maxWords annotations in the section contracts)
  * asset-role generation policies, plus PINNED values for the
    compliance-critical roles (a membership-in-enum check alone cannot catch a
    role silently switched to a different-but-valid policy)
  * PINNED_AVAILABILITY (clone-only | generation-safe | blocked-for-generation)
    per asset role, cross-checked against assets/asset-roles.json
  * retrieval eligibility pins (RETRIEVAL_INELIGIBLE) for runtime / utility UI
  * the consequences of `mode` (MODE_RULES): in generation mode every Equator
    brand, person, customer, copy shingle, claim, URL, embed and asset found in
    schema/leakage-patterns.json is rejected (GENERATION_MODE_*); in clone mode
    real refs must be real (CLONE_MODE_UNKNOWN_SOURCE)
  * token references (TOKEN_RULES) against tokens/llm/token-catalog.json and
    tokens/llm/token-policy.json
Detection is string-based on normalised text (schema/textnorm.py); no human has
reviewed the patterns, and paraphrase evades it.

Usage:
    python3 schema/semantic_validate.py [pagespec.json ...]
    (defaults to every schema/examples/*.pagespec.json)
Exit code 0 = no errors (warnings allowed), 1 = at least one error.

The repo root is derived from __file__, never hardcoded, so the package works
wherever it is extracted.
"""
import hashlib
import json
import os
import re
import sys

from jsonschema import Draft7Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textnorm import normalize, shingles  # noqa: E402

# --------------------------------------------------------------------------
# Pinned values. These are a second, independent source of truth on purpose:
# assets/asset-roles.json can be edited to another valid policy and still pass
# an enum check; it cannot pass these.
# --------------------------------------------------------------------------
PINNED_ASSET_POLICIES = {
    "team-portrait": "placeholder-only",        # real employees' likenesses
    "team-halftone": "placeholder-only",        # derived likenesses
    "merger-logo": "must-not-reproduce",        # real third-party trademarks
    "member-logo": "must-not-reproduce",        # real third-party trademarks
    "brand-wordmark": "must-not-reproduce",     # the company's trademark
    "brand-lottie-splash": "must-not-reproduce",  # proprietary brand animation
    "brand-lottie-value": "must-not-reproduce",
    "brand-lottie-footer": "must-not-reproduce",
    "funding-emblem": "omit",                   # PRR/EU emblem: false funding claim
    "project-sheet-pdf": "omit",                # proprietary document
    # generation-safe substitutes: pinned so a substitute cannot be loosened to accept real media
    "placeholder-brand-mark": "placeholder-only",
    "user-supplied-asset": "operator-supplied",
    "generated-illustration": "may-generate-new",
    "generated-ambient-video": "may-generate-new",
    "placeholder-screenshot": "placeholder-only",
    "fictional-avatar": "may-generate-new",
    "placeholder-company-logo": "placeholder-only",
    "placeholder-url": "placeholder-only",
    "original-copy": "may-generate-new",
}
# Availability per role, pinned independently of assets/asset-roles.json (verify_all.py holds an identical copy
# and checks both against each other and against the registry).
PINNED_AVAILABILITY = {
    "brand-wordmark": "clone-only",
    "brand-lottie-splash": "clone-only",
    "brand-lottie-value": "clone-only",
    "brand-lottie-footer": "clone-only",
    "ambient-video": "clone-only",
    "merger-logo": "clone-only",
    "member-logo": "clone-only",
    "project-photo": "clone-only",
    "team-portrait": "clone-only",
    "team-halftone": "clone-only",
    "funding-emblem": "blocked-for-generation",
    "project-sheet-pdf": "blocked-for-generation",
    "placeholder-brand-mark": "generation-safe",
    "user-supplied-asset": "generation-safe",
    "generated-illustration": "generation-safe",
    "generated-ambient-video": "generation-safe",
    "placeholder-screenshot": "generation-safe",
    "fictional-avatar": "generation-safe",
    "placeholder-company-logo": "generation-safe",
    "placeholder-url": "generation-safe",
    "original-copy": "generation-safe",
}
AVAILABILITY_VALUES = ("clone-only", "generation-safe", "blocked-for-generation")
# Retrieval eligibility (R8): runtime / utility UI is never a retrieval exemplar. Pinned here and in verify_all.py.
RETRIEVAL_INELIGIBLE = {"chrome.splash"}
RUNTIME_UI_RX = re.compile(r"cookie|consent|modal|dialog|drawer|popup|overlay|preload|splash|toast|tooltip|lightbox|banner")
RESERVED_HOST_SUFFIXES = (".example", ".invalid")
# keys whose values are closed vocabulary, not page content (never scanned for leakage)
NON_CONTENT_KEYS = {"type", "variant", "motion", "assetRole", "headingStyle", "tokens", "anchorId", "anchor", "retrievalEligible"}
PINNED_LICENCES = {"font.national-2": "licence-required"}
VALID_POLICIES = ("may-generate-new", "placeholder-only", "must-not-reproduce", "omit", "operator-supplied")

# Structured exceptions for SURFACE_RHYTHM. verify_all.py checks each pair is
# also written in compatibility/graph.json's prose, so the two cannot diverge.
SURFACE_EXCEPTIONS = {
    ("chrome.splash", "hero.title"),
    ("capabilities.accordion", "work.carousel-marquee"),
    ("chrome.footer", "chrome.subfooter"),
}
MAX_SCROLL_STAGE_RUN = 2
STORY_REVEAL_MAX = 60
AMBIENT_VIDEO_MAX = 2


class Issue:
    def __init__(self, code, severity, path, message):
        self.code, self.severity, self.path, self.message = code, severity, path, message

    def __repr__(self):
        return f"{self.severity.upper():5} {self.code:30} {self.path}: {self.message}"


def _load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_context(root=ROOT):
    sec_dir = os.path.join(root, "sections")
    sections = {}
    for fn in sorted(os.listdir(sec_dir)):
        if fn.endswith(".json"):
            d = _load(os.path.join(sec_dir, fn))
            sections[d["id"]] = d
    return {
        "root": root,
        "schema": _load(os.path.join(root, "schema", "pagespec.schema.json")),
        "templates": {t["id"]: t for t in _load(os.path.join(root, "templates", "templates.json"))["templates"]},
        "routes": _load(os.path.join(root, "templates", "routes.json"))["routes"],
        "graph": {r["id"]: r for r in _load(os.path.join(root, "compatibility", "graph.json"))["rules"]},
        "sections": sections,
        "assets": _load(os.path.join(root, "assets", "asset-roles.json")),
        "leakage": _load(os.path.join(root, "schema", "leakage-patterns.json")),
        "catalog": _load(os.path.join(root, "tokens", "llm", "token-catalog.json")),
        "tokenPolicy": _load(os.path.join(root, "tokens", "llm", "token-policy.json")),
        "manifest": _load(os.path.join(root, "registry.manifest.json")),
    }


def count_words(text):
    return len(re.findall(r"\S+", text))


# --------------------------------------------------------------------------
# Repo-integrity: pinned asset policies and licences
# --------------------------------------------------------------------------
def check_pins(ctx):
    out = []
    roles = ctx["assets"].get("roles", {})
    for role, expected in PINNED_ASSET_POLICIES.items():
        r = roles.get(role)
        if r is None:
            out.append(Issue("ASSET_ROLE_PIN", "error", f"assets.roles.{role}", "pinned role missing from asset-roles.json"))
            continue
        if r.get("generationPolicy") != expected:
            out.append(Issue("ASSET_ROLE_PIN", "error", f"assets.roles.{role}.generationPolicy",
                             f"pinned to '{expected}', found '{r.get('generationPolicy')}'"))
        if r.get("pinned") is not True:
            out.append(Issue("ASSET_ROLE_PIN", "error", f"assets.roles.{role}.pinned", "pinned role must carry pinned: true"))
    for role, r in roles.items():
        if r.get("generationPolicy") not in VALID_POLICIES:
            out.append(Issue("ASSET_ROLE_PIN", "error", f"assets.roles.{role}.generationPolicy", f"not a valid policy: {r.get('generationPolicy')}"))
        if r.get("pinned") is True and role not in PINNED_ASSET_POLICIES:
            out.append(Issue("ASSET_ROLE_PIN", "error", f"assets.roles.{role}.pinned", "marked pinned in the registry but has no pin in semantic_validate.py"))
    for role, expected in PINNED_AVAILABILITY.items():
        r = roles.get(role)
        if r is None:
            out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}", "role with pinned availability missing from asset-roles.json"))
            continue
        if r.get("availability") != expected:
            out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}.availability", f"pinned to '{expected}', found '{r.get('availability')}'"))
    for role, r in roles.items():
        if role not in PINNED_AVAILABILITY:
            out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}", "role has no PINNED_AVAILABILITY entry in semantic_validate.py"))
        if r.get("availability") not in AVAILABILITY_VALUES:
            out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}.availability", f"not a valid availability: {r.get('availability')}"))
        subs = r.get("generationSafeSubstitutes")
        if not isinstance(subs, list) or not isinstance(r.get("generatedModeGuidance"), str) or len(r.get("generatedModeGuidance", "")) < 20:
            out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}", "generationSafeSubstitutes (list) and generatedModeGuidance (20+ chars) required"))
            continue
        if r.get("availability") != "generation-safe" and not subs:
            out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}.generationSafeSubstitutes", "a non-generation-safe role needs at least one substitute"))
        for s in subs:
            if PINNED_AVAILABILITY.get(s) != "generation-safe":
                out.append(Issue("ASSET_AVAILABILITY_PIN", "error", f"assets.roles.{role}.generationSafeSubstitutes", f"substitute '{s}' is not a pinned generation-safe role"))
    for sid, sec in ctx["sections"].items():
        want = sid not in RETRIEVAL_INELIGIBLE
        got = sec.get("retrievalEligible")
        if got is not want:
            out.append(Issue("RETRIEVAL_ELIGIBILITY_PIN", "error", f"sections.{sid}.retrievalEligible", f"pinned to {want}, found {got!r}"))
        if got is False and len(sec.get("retrievalReason", "")) < 30:
            out.append(Issue("RETRIEVAL_ELIGIBILITY_PIN", "error", f"sections.{sid}.retrievalReason", "an ineligible section needs a 30+ character reason"))
        if RUNTIME_UI_RX.search(sid + " " + sec.get("name", "").lower()) and sid not in RETRIEVAL_INELIGIBLE:
            out.append(Issue("RETRIEVAL_ELIGIBILITY_PIN", "error", f"sections.{sid}", "id/name looks like runtime UI but is not in RETRIEVAL_INELIGIBLE"))
    lic = ctx["assets"].get("licensedResources", {})
    for res, expected in PINNED_LICENCES.items():
        got = lic.get(res, {}).get("licence")
        if got != expected:
            out.append(Issue("ASSET_ROLE_PIN", "error", f"assets.licensedResources.{res}.licence", f"pinned to '{expected}', found '{got}'"))
    return out


# --------------------------------------------------------------------------
# Graph rules. Each returns a list of (path, message). Severity comes from
# compatibility/graph.json; the second tuple element is the expected severity,
# which verify_all.py compares against the graph so the two cannot drift.
# --------------------------------------------------------------------------
def _types(spec):
    return [n["type"] for n in spec["nodes"]]


def r_template_sequence(spec, ctx):
    out = []
    tn = ctx["templates"][spec["template"]]["nodes"]
    nodes = spec["nodes"]
    j, seen = 0, set()
    for i, n in enumerate(nodes):
        k = j
        while k < len(tn) and tn[k]["section"] != n["type"]:
            k += 1
        if k == len(tn):
            earlier = [m for m, x in enumerate(tn) if x["section"] == n["type"]]
            if not earlier:
                msg = f"'{n['type']}' is not part of {spec['template']}"
            elif earlier[0] in seen and not tn[earlier[0]]["repeatable"]:
                msg = f"duplicate non-repeatable '{n['type']}'"
            else:
                msg = f"'{n['type']}' is out of order for {spec['template']}"
            out.append((f"nodes[{i}]", msg))
            continue
        for m in range(j, k):
            if tn[m]["required"] and m not in seen:
                out.append((f"nodes[{i}]", f"required '{tn[m]['section']}' missing before '{n['type']}'"))
        seen.add(k)
        want = tn[k].get("variant")
        if want and n.get("variant") != want:
            out.append((f"nodes[{i}].variant", f"{spec['template']} requires variant '{want}', got '{n.get('variant')}'"))
        j = k if tn[k]["repeatable"] else k + 1
    for m in range(j, len(tn)):
        if tn[m]["required"] and m not in seen:
            out.append(("nodes", f"required '{tn[m]['section']}' missing at end of {spec['template']}"))
    return out


def r_route_template_binding(spec, ctx):
    out = []
    route, tpl = spec["route"], spec["template"]
    reg = {r["path"]: r["template"] for r in ctx["routes"]}
    if route in reg and reg[route] != tpl:
        out.append(("route", f"route '{route}' is bound to {reg[route]}, not {tpl}"))
    pol = ctx["templates"][tpl]["routePolicy"]
    if pol["kind"] == "exact" and route != pol["route"]:
        out.append(("route", f"{tpl} is only valid at '{pol['route']}'"))
    elif pol["kind"] == "catch-all" and route != "*":
        out.append(("route", f"{tpl} is only valid as the catch-all route '*'"))
    elif pol["kind"] == "registered-or-new" and route in ("/", "*"):
        out.append(("route", f"{tpl} cannot occupy '{route}'"))
    return out


def r_new_route_notice(spec, ctx):
    pol = ctx["templates"][spec["template"]]["routePolicy"]
    reg = {r["path"] for r in ctx["routes"]}
    if pol["kind"] == "registered-or-new" and spec["route"] not in reg and spec["route"] not in ("/", "*"):
        return [("route", f"'{spec['route']}' is a new route with no measured counterpart")]
    return []


def r_splash_first_home_only(spec, ctx):
    out = []
    for i, t in enumerate(_types(spec)):
        if t == "chrome.splash":
            if spec["template"] != "template.home":
                out.append((f"nodes[{i}]", "chrome.splash is home-only"))
            if i != 0:
                out.append((f"nodes[{i}]", "chrome.splash must be node 0"))
    return out


def r_header_position(spec, ctx):
    types = _types(spec)
    idx = [i for i, t in enumerate(types) if t == "chrome.header"]
    if spec["template"] == "template.not-found":
        return [(f"nodes[{i}]", "template.not-found renders no header") for i in idx]
    if len(idx) != 1:
        return [("nodes", f"chrome.header must appear exactly once (found {len(idx)})")]
    i = idx[0]
    if "chrome.splash" in types:
        if i == 0 or types[i - 1] != "chrome.splash":
            return [(f"nodes[{i}]", "chrome.header must immediately follow chrome.splash")]
    elif i != 0:
        return [(f"nodes[{i}]", "chrome.header must be the first node when there is no splash")]
    return []


def r_one_hero(spec, ctx):
    n = _types(spec).count("hero.title")
    return [("nodes", f"{n} hero.title nodes; at most one allowed")] if n > 1 else []


def r_cta_before_footer(spec, ctx):
    types = _types(spec)
    return [(f"nodes[{i}]", "conversion.cta-video must be immediately followed by chrome.footer")
            for i, t in enumerate(types)
            if t == "conversion.cta-video" and (i + 1 >= len(types) or types[i + 1] != "chrome.footer")]


def r_footer_subfooter_tail(spec, ctx):
    out = []
    types = _types(spec)
    for i, t in enumerate(types):
        if t == "chrome.footer":
            rest = types[i + 1:]
            if rest not in ([], ["chrome.subfooter"]):
                out.append((f"nodes[{i}]", f"chrome.footer may only be followed by chrome.subfooter, found {rest}"))
        if t == "chrome.subfooter" and i != len(types) - 1:
            out.append((f"nodes[{i}]", "chrome.subfooter must be the last node"))
    return out


def r_one_per_page(spec, ctx):
    out = []
    types = _types(spec)
    for t in sorted(set(types)):
        mx = ctx["sections"][t]["constraints"].get("maxPerPage")
        if mx is not None and types.count(t) > mx:
            out.append(("nodes", f"'{t}' appears {types.count(t)} times; maxPerPage {mx}"))
    return out


def r_max_scroll_stages(spec, ctx):
    run, start = 0, 0
    for i, t in enumerate(_types(spec)):
        if ctx["sections"][t].get("scrollStage"):
            if run == 0:
                start = i
            run += 1
            if run == MAX_SCROLL_STAGE_RUN + 1:
                return [(f"nodes[{start}..{i}]", f"more than {MAX_SCROLL_STAGE_RUN} consecutive scroll-driven sections")]
        else:
            run = 0
    return []


def r_surface_rhythm(spec, ctx):
    out = []
    painted = [(i, t, ctx["sections"][t]["surface"]) for i, t in enumerate(_types(spec))
               if ctx["sections"][t]["surface"] != "transparent"]
    for (i, a, sa), (k, b, sb) in zip(painted, painted[1:]):
        if sa == sb and (a, b) not in SURFACE_EXCEPTIONS:
            out.append((f"nodes[{i}]->nodes[{k}]", f"'{a}' and '{b}' share surface '{sa}'"))
    return out


def r_nav_anchors(spec, ctx):
    out = []
    page_anchors = {n["anchorId"] for n in spec["nodes"] if "anchorId" in n}
    home_anchors = {ctx["sections"][x["section"]]["anchor"] for x in ctx["templates"]["template.home"]["nodes"]
                    if ctx["sections"][x["section"]].get("anchor")}
    for i, n in enumerate(spec["nodes"]):
        if n["type"] != "chrome.header":
            continue
        valid = page_anchors if n.get("variant") == "home" else home_anchors
        for j, item in enumerate(n["content"]["navItems"]):
            if item["anchor"] not in valid:
                out.append((f"nodes[{i}].content.navItems[{j}].anchor", f"'{item['anchor']}' does not resolve to a section anchor"))
    return out


def r_anchor_unique(spec, ctx):
    ids = [n["anchorId"] for n in spec["nodes"] if "anchorId" in n]
    dup = sorted({a for a in ids if ids.count(a) > 1})
    return [("nodes", f"duplicate anchorId '{a}'") for a in dup]


def r_story_reveal(spec, ctx):
    out = []
    for i, n in enumerate(spec["nodes"]):
        if n["type"] != "narrative.story-reveal":
            continue
        c = n["content"]
        units = count_words(c["intro"]) + len(c["mergerLogos"]) + sum(count_words(s["text"]) for s in c["statements"])
        if units > STORY_REVEAL_MAX:
            out.append((f"nodes[{i}].content", f"{units} reveal units > {STORY_REVEAL_MAX}: trailing words would never reveal"))
        for j, s in enumerate(c["statements"]):
            if "emphasisFromWord" in s and s["emphasisFromWord"] >= count_words(s["text"]):
                out.append((f"nodes[{i}].content.statements[{j}].emphasisFromWord", "index beyond the statement's word count"))
    return out


def r_values_five(spec, ctx):
    return [(f"nodes[{i}].content.panels", f"{len(n['content']['panels'])} panels; exactly 5 required")
            for i, n in enumerate(spec["nodes"])
            if n["type"] == "values.sticky-stack" and len(n["content"]["panels"]) != 5]


def r_header_variant_match(spec, ctx):
    out = []
    variants = ctx["sections"]["chrome.header"]["motion"]["variants"]
    for i, n in enumerate(spec["nodes"]):
        if n["type"] == "chrome.header":
            want = variants[n["variant"]]["pattern"]
            if n["motion"]["pattern"] != want:
                out.append((f"nodes[{i}].motion.pattern", f"variant '{n['variant']}' requires pattern '{want}'"))
    return out


def _media(obj, path):
    if isinstance(obj, dict):
        if "assetRole" in obj:
            yield path, obj
        for k, v in obj.items():
            yield from _media(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _media(v, f"{path}[{i}]")


def r_ambient_video(spec, ctx):
    n = sum(1 for _, m in _media(spec["nodes"], "nodes") if m["assetRole"] == "ambient-video")
    return [("nodes", f"{n} ambient videos; budget {AMBIENT_VIDEO_MAX}")] if n > AMBIENT_VIDEO_MAX else []


def r_asset_policy(spec, ctx):
    out = []
    roles = ctx["assets"]["roles"]
    pols = ctx["assets"]["generationPolicies"]
    for path, m in _media(spec["nodes"], "nodes"):
        role = roles.get(m["assetRole"])
        if role is None:
            out.append((path, f"unknown assetRole '{m['assetRole']}'"))
            continue
        ref = m["assetRef"]
        if ref.startswith("source:"):
            if spec.get("mode") == "clone" and ref[len("source:"):] not in role.get("sourceFiles", []):
                out.append((path, f"'{ref}' is not one of the real sourceFiles of role '{m['assetRole']}'"))
            if role.get("availability") == "generation-safe":
                out.append((path, f"generation-safe role '{m['assetRole']}' never carries a real source: file"))
            continue  # generation mode: GENERATION_MODE_ASSET reports it
        policy = role["generationPolicy"]
        if policy == "omit":
            out.append((path, f"assetRole '{m['assetRole']}' has policy 'omit': only the real file (clone mode) or nothing"))
            continue
        pattern = pols[policy]["assetRefPattern"]
        if not re.match(pattern, ref):
            out.append((path, f"assetRef '{ref}' violates policy '{policy}' (needs {pattern})"))
    return out


def _walk_words(inst, sch, path, out):
    if isinstance(inst, str) and "x-maxWords" in sch:
        wc = count_words(inst)
        if wc > sch["x-maxWords"]:
            out.append((path, f"{wc} words > maxWords {sch['x-maxWords']}"))
    elif isinstance(inst, dict):
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                _walk_words(v, props[k], f"{path}.{k}", out)
    elif isinstance(inst, list) and isinstance(sch.get("items"), dict):
        for i, v in enumerate(inst):
            _walk_words(v, sch["items"], f"{path}[{i}]", out)


def r_max_words(spec, ctx):
    out = []
    _walk_words(spec["meta"], ctx["schema"]["properties"]["meta"], "meta", out)
    for i, n in enumerate(spec["nodes"]):
        sec = ctx["sections"][n["type"]]
        _walk_words(n["content"], sec["content"], f"nodes[{i}].content", out)
        by_kind = sec["constraints"].get("maxWordsByKind")
        if by_kind:
            for j, b in enumerate(n["content"].get("blocks", [])):
                lim = by_kind.get(b["kind"])
                if lim is not None and count_words(b["text"]) > lim:
                    out.append((f"nodes[{i}].content.blocks[{j}].text", f"{count_words(b['text'])} words > maxWords {lim} for kind '{b['kind']}'"))
    return out


GRAPH_RULES = {
    "TEMPLATE_SEQUENCE": ("error", r_template_sequence),
    "ROUTE_TEMPLATE_BINDING": ("error", r_route_template_binding),
    "NEW_ROUTE_NOTICE": ("warn", r_new_route_notice),
    "SPLASH_FIRST_HOME_ONLY": ("error", r_splash_first_home_only),
    "HEADER_POSITION": ("error", r_header_position),
    "ONE_HERO": ("error", r_one_hero),
    "CTA_IMMEDIATELY_BEFORE_FOOTER": ("error", r_cta_before_footer),
    "FOOTER_SUBFOOTER_TAIL": ("error", r_footer_subfooter_tail),
    "ONE_PER_PAGE": ("error", r_one_per_page),
    "MAX_CONSECUTIVE_SCROLL_STAGES": ("error", r_max_scroll_stages),
    "SURFACE_RHYTHM": ("warn", r_surface_rhythm),
    "NAV_ANCHORS_RESOLVE": ("error", r_nav_anchors),
    "ANCHOR_UNIQUE": ("error", r_anchor_unique),
    "STORY_REVEAL_BUDGET": ("error", r_story_reveal),
    "VALUES_FIVE_PANELS": ("error", r_values_five),
    "HEADER_VARIANT_MATCH": ("error", r_header_variant_match),
    "AMBIENT_VIDEO_BUDGET": ("warn", r_ambient_video),
    "ASSET_POLICY": ("error", r_asset_policy),
    "MAX_WORDS": ("error", r_max_words),
}


# --------------------------------------------------------------------------
# Mode rules (R1/R2). Severity is fixed here; they are not composition rules, so
# they live outside compatibility/graph.json (documented in policy/design-policy.json).
# --------------------------------------------------------------------------
def _strings(obj, path, key=None):
    if isinstance(obj, str):
        yield path, key, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in NON_CONTENT_KEYS:
                continue
            yield from _strings(v, f"{path}.{k}", k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _strings(v, f"{path}[{i}]", key)


def page_strings(spec):
    yield from _strings(spec.get("meta", {}), "meta")
    for i, n in enumerate(spec.get("nodes", [])):
        yield from _strings(n, f"nodes[{i}]")


URL_RX = re.compile(r"(?:https?:)?//([a-z0-9.-]+)|mailto:[^@\s]+@([a-z0-9.-]+)|\b[a-z0-9._-]+@([a-z0-9.-]+\.[a-z]+)")
DOMAIN_RX = re.compile(r"\b((?:[a-z0-9-]+\.)+[a-z]{2,})\b")


def _hosts(s):
    for m in URL_RX.finditer(s):
        h = next(g for g in m.groups() if g)
        yield h.removeprefix("www.")


def _host_is(host, domain):
    return host == domain or host.endswith("." + domain)


def _reserved(host):
    return host.endswith(RESERVED_HOST_SUFFIXES) or host.rstrip(".") in ("example", "invalid")


def _regex_hits(rows, s, label_key):
    for r in rows:
        if re.search(r["regex"], s):
            yield r.get(label_key) or r.get("id")


def m_brand(spec, ctx):
    L = ctx["leakage"]
    return [(p, f"Equator brand '{h}' in generation mode") for p, _k, s in page_strings(spec) for h in _regex_hits(L["brand"], normalize(s), "id")]


def m_person(spec, ctx):
    L = ctx["leakage"]
    out = []
    for p, _k, s in page_strings(spec):
        for h in _regex_hits(L["persons"], normalize(s), "name"):
            out.append((p, f"real Equator team member '{h}' in generation mode"))
    return out


def m_customer(spec, ctx):
    L = ctx["leakage"]
    return [(p, f"real Equator partner/client '{h}' in generation mode") for p, _k, s in page_strings(spec) for h in _regex_hits(L["customers"], normalize(s), "name")]


def m_claim(spec, ctx):
    L = ctx["leakage"]
    return [(p, f"Equator claim '{h}' in generation mode") for p, _k, s in page_strings(spec) for h in _regex_hits(L["claims"], normalize(s), "id")]


def m_copy(spec, ctx):
    H = ctx.setdefault("_shingles", set(ctx["leakage"]["copyShingles"]["hashes"]))
    n = ctx["leakage"]["copyShingles"]["n"]
    out = []
    for p, k, s in page_strings(spec):
        if k in ("assetRef",) or s.startswith(("placeholder:", "generated:", "user:", "source:", "/", "#", "http", "mailto:")):
            continue
        hit = [sh for sh in shingles(s, n) if hashlib.sha256(sh.encode()).hexdigest()[:16] in H]
        if hit:
            out.append((p, f"{len(hit)} 5-word shingle(s) match Equator copy, e.g. '{hit[0]}'"))
    return out


def m_url(spec, ctx):
    L = ctx["leakage"]
    doms = [d["domain"] for d in L["domains"]]
    emails = [e["email"] for e in L["emails"]]
    out = []
    for p, _k, s in page_strings(spec):
        ns = normalize(s)
        for host in _hosts(ns):
            if not _reserved(host):
                out.append((p, f"absolute link host '{host}' in generation mode: use placeholder:, relative, or a .example/.invalid host"))
        for m in DOMAIN_RX.finditer(ns):
            if any(_host_is(m.group(1).removeprefix("www."), d) for d in doms):
                out.append((p, f"Equator source domain '{m.group(1)}' in generation mode"))
        for e in emails:
            if e in ns:
                out.append((p, f"Equator email '{e}' in generation mode"))
    return out


def m_embed(spec, ctx):
    L = ctx["leakage"]
    out = []
    for p, _k, s in page_strings(spec):
        ns = normalize(s)
        for e in L["embeds"]:
            if e["id"].lower() in ns:
                out.append((p, f"Equator {e['kind']} id '{e['id']}' in generation mode"))
        for host in _hosts(ns):
            if any(_host_is(host, d) for d in ("mailchi.mp", "maps.app.goo.gl", "list-manage.com")):
                out.append((p, f"third-party embed endpoint '{host}' in generation mode"))
    return out


def m_asset(spec, ctx):
    L = ctx["leakage"]
    roles = ctx["assets"]["roles"]
    files = {os.path.basename(f["file"]).lower() for f in L["assets"]["files"]}
    stems = [s.replace("_", "-") for s in L["assets"]["distinctiveStems"]]
    out = []
    for path, m in _media(spec["nodes"], "nodes"):
        role = roles.get(m["assetRole"], {})
        if role.get("availability") != "generation-safe":
            out.append((path, f"assetRole '{m['assetRole']}' is {role.get('availability')}; use one of {role.get('generationSafeSubstitutes')}"))
        if m["assetRef"].startswith("source:"):
            out.append((path, f"real Equator file '{m['assetRef']}' in generation mode"))
    for p, _k, s in page_strings(spec):
        ns = normalize(s).replace("_", "-")
        for f in files:
            if f.replace("_", "-") in ns:
                out.append((p, f"real Equator asset file '{f}' referenced in generation mode"))
        for st in stems:
            if re.search(r"(?<![a-z0-9])" + re.escape(st) + r"(?![a-z0-9])", ns):
                out.append((p, f"real Equator asset identifier '{st}' in generation mode"))
    return out


def m_clone_source(spec, ctx):
    """Clone mode may reuse real refs, but they must BE real: unknown absolute hosts/emails are invented, not cloned."""
    L = ctx["leakage"]
    doms = [d["domain"] for d in L["domains"]]
    emails = {e["email"] for e in L["emails"]}
    out = []
    for p, k, s in page_strings(spec):
        ns = normalize(s)
        if not (ns.startswith(("http", "mailto:", "//"))):
            continue
        for host in _hosts(ns):
            if not _reserved(host) and not any(_host_is(host, d) for d in doms):
                out.append((p, f"'{host}' is neither an Equator source domain nor a reserved .example/.invalid host"))
        if ns.startswith("mailto:") and ns[len("mailto:"):] not in emails and not _reserved(ns.rsplit("@", 1)[-1]):
            out.append((p, f"'{s}' is not a real Equator email"))
    return out


MODE_RULES = {
    "GENERATION_MODE_BRAND": ("generation", "error", m_brand),
    "GENERATION_MODE_PERSON": ("generation", "error", m_person),
    "GENERATION_MODE_CUSTOMER": ("generation", "error", m_customer),
    "GENERATION_MODE_COPY": ("generation", "error", m_copy),
    "GENERATION_MODE_CLAIM": ("generation", "error", m_claim),
    "GENERATION_MODE_URL": ("generation", "error", m_url),
    "GENERATION_MODE_EMBED": ("generation", "error", m_embed),
    "GENERATION_MODE_ASSET": ("generation", "error", m_asset),
    "CLONE_MODE_UNKNOWN_SOURCE": ("clone", "error", m_clone_source),
}


# --------------------------------------------------------------------------
# Token rules (R10): node `tokens` slots against the catalog and policy.
# --------------------------------------------------------------------------
RAW_COLOR_RX = re.compile(r"^\s*(#[0-9a-f]{3,8}|(rgb|rgba|hsl|hsla)\s*\()", re.I)
RAW_LENGTH_RX = re.compile(r"^\s*(-?\d+(\.\d+)?\s*(px|rem|em|%|vh|vw|svh|pt)?|calc\(.*\))\s*$", re.I)


def token_issues(spec, ctx):
    cat = ctx["catalog"]["tokens"]
    slots = ctx["tokenPolicy"]["slots"]
    validated = ctx["manifest"].get("schemaValidatedThemes", [])
    theme = spec.get("theme", ctx["manifest"].get("defaultTheme"))
    out = []
    if theme not in validated:
        out.append(("TOKEN_THEME_COMBINATION", "error", "theme", f"theme '{theme}' is not schema-validated (validated: {validated})"))
    for i, n in enumerate(spec["nodes"]):
        for slot, val in (n.get("tokens") or {}).items():
            path = f"nodes[{i}].tokens.{slot}"
            pol = slots.get(slot)
            if RAW_COLOR_RX.search(val):
                out.append(("TOKEN_RAW_COLOR", "error", path, f"raw colour '{val}': use a catalog token id"))
                continue
            if RAW_LENGTH_RX.search(val):
                out.append(("TOKEN_ARBITRARY_SPACING", "error", path, f"raw length '{val}': use a spacing/radius token id"))
                continue
            if slot == "fontFamily" and (val not in cat or cat[val]["category"] != "fontFamily"):
                out.append(("TOKEN_FONT_UNSUPPORTED", "error", path, f"'{val}' is not a supported font token ({ctx['catalog']['categories'].get('fontFamily')})"))
                continue
            if val not in cat:
                out.append(("TOKEN_UNKNOWN", "error", path, f"'{val}' is not in tokens/llm/token-catalog.json"))
                continue
            t = cat[val]
            if pol is None or t["category"] not in pol["categories"] or not val.startswith(tuple(pol["idPrefixes"])):
                out.append(("TOKEN_SLOT_MISMATCH", "error", path, f"'{val}' ({t['category']}) is not allowed in slot '{slot}'"))
                continue
            if t["category"] == "semantic" and theme not in t.get("resolvedIn", {}):
                out.append(("TOKEN_THEME_COMBINATION", "error", path, f"'{val}' is not resolved by theme '{theme}'"))
            if slot == "fontFamily" and val == "font.family.national" and spec.get("mode") == "generation":
                out.append(("TOKEN_FONT_LICENCE", "warn", path, "National 2 is licence-required: a deployer without a Klim licence gets the fallback stack"))
    return out


TOKEN_RULES = ("TOKEN_UNKNOWN", "TOKEN_RAW_COLOR", "TOKEN_ARBITRARY_SPACING", "TOKEN_FONT_UNSUPPORTED", "TOKEN_SLOT_MISMATCH", "TOKEN_THEME_COMBINATION", "TOKEN_FONT_LICENCE")


def r_node_retrieval(spec, ctx):
    out = []
    for i, n in enumerate(spec["nodes"]):
        if "retrievalEligible" in n:
            want = n["type"] not in RETRIEVAL_INELIGIBLE
            if n["retrievalEligible"] is not want:
                out.append(("RETRIEVAL_ELIGIBILITY_PIN", "error", f"nodes[{i}].retrievalEligible", f"'{n['type']}' is pinned to retrievalEligible {want}"))
    return out


def validate(spec, root=ROOT, ctx=None):
    ctx = ctx or load_context(root)
    issues = check_pins(ctx)
    schema_errors = sorted(Draft7Validator(ctx["schema"]).iter_errors(spec), key=lambda e: list(e.absolute_path))
    if schema_errors:
        return issues + [Issue("SCHEMA", "error", "/".join(str(p) for p in e.absolute_path) or "(root)", e.message[:300])
                         for e in schema_errors]
    for rid, (_expected, fn) in GRAPH_RULES.items():
        rule = ctx["graph"].get(rid)
        if rule is None:
            issues.append(Issue("GRAPH_RULE_MISSING", "error", "compatibility/graph.json", f"{rid} enforced here but not declared in the graph"))
            continue
        for path, msg in fn(spec, ctx):
            issues.append(Issue(rid, rule["severity"], path, msg))
    for rid, (mode, sev, fn) in MODE_RULES.items():
        if spec["mode"] == mode:
            seen = set()
            for path, msg in fn(spec, ctx):
                if (path, msg) not in seen:
                    seen.add((path, msg))
                    issues.append(Issue(rid, sev, path, msg))
    for code, sev, path, msg in token_issues(spec, ctx) + r_node_retrieval(spec, ctx):
        issues.append(Issue(code, sev, path, msg))
    return issues


def main(argv):
    paths = argv[1:] or sorted(os.path.join(ROOT, "schema", "examples", f) for f in os.listdir(os.path.join(ROOT, "schema", "examples")) if f.endswith(".json"))
    ctx = load_context(ROOT)
    failed = False
    for p in paths:
        with open(p, encoding="utf-8") as f:
            spec = json.load(f)
        issues = validate(spec, ctx=ctx)
        errors = [i for i in issues if i.severity == "error"]
        warns = [i for i in issues if i.severity != "error"]
        print(f"{os.path.basename(p)}: {len(errors)} error(s), {len(warns)} warning(s)")
        for i in issues:
            print("  ", i)
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
