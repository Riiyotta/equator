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

Usage:
    python3 schema/semantic_validate.py [pagespec.json ...]
    (defaults to schema/example.pagespec.json)
Exit code 0 = no errors (warnings allowed), 1 = at least one error.

The repo root is derived from __file__, never hardcoded, so the package works
wherever it is extracted.
"""
import json
import os
import re
import sys

from jsonschema import Draft7Validator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
}
PINNED_LICENCES = {"font.national-2": "licence-required"}
VALID_POLICIES = ("may-generate-new", "placeholder-only", "must-not-reproduce", "omit")

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
        policy = role["generationPolicy"]
        if policy == "omit":
            out.append((path, f"assetRole '{m['assetRole']}' has policy 'omit': the field must be absent"))
            continue
        pattern = pols[policy]["assetRefPattern"]
        if not re.match(pattern, m["assetRef"]):
            out.append((path, f"assetRef '{m['assetRef']}' violates policy '{policy}' (needs {pattern})"))
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
    return issues


def main(argv):
    paths = argv[1:] or [os.path.join(ROOT, "schema", "example.pagespec.json")]
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
