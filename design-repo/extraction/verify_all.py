#!/usr/bin/env python3
"""One-shot verification for the Equator design-repo.

Checks (each prints PASS/WARN/FAIL <name>):
  schema_example            Draft-07 meta-check of the schema + example validates with 0 errors
  semantic_example          semantic_validate.py on the example: 0 errors (incl. per-instance maxWords)
  adversarial_suite         schema/tests/adversarial_test.py exits 0 (skip with --skip-adversarial)
  allowlist_parity          allowlist ids == contract files / templates / asset roles / schema properties
  allowlist_version_parity  allowlistVersion equal in allowlist, manifest, README and CHANGELOG
  manifest_counts           manifest counts AND the README counts table recomputed from disk
  citations                 every {path, lines, quote}: range inside the real file, quote inside the range
                            (WARN, not FAIL, when the sibling source tree is absent)
  absolute_paths            no absolute machine paths anywhere in the package
  entrypoints               manifest entryPoints exist and are inside design-repo/
  schema_contract_parity    schema node branches == section contracts (content, motion consts, anchors)
  graph_validator_parity    graph.json rule ids/severities == semantic_validate.GRAPH_RULES; exception prose agrees
  template_route_coverage   every route -> exactly one template, every template has a route, nodes resolve
  theme_resolution          every semantic token resolves to a foundation token; light theme agrees
  token_catalog             token-catalog.json lists == real token leaves; token-policy keys == catalog keys
  asset_roles               registry == schema enum == field roles == allowlist; pinned values hold
  responsive_768            every section has a structured 768 entry or a cited noChangeAt768
  evidence_levels           closed evidence vocabulary; not-found pinned to inferred-unmeasured
  status_flags              design-review-pending, productionApproved false, publishRecommended false
  framework_versions        manifest framework versions == ledger (== ../package.json when present)

Drift-proof: extraction/prove_drift.py injects a defect for every check above in a scratch copy and
confirms this script fails on it, then confirms clean copies pass.

Root is derived from __file__; nothing here depends on where the folder lives.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "schema"))
sys.path.insert(0, os.path.join(ROOT, "schema", "tests"))

RESULTS = []
EVIDENCE_LEVELS = {"measured", "inferred-unmeasured"}
PINNED_EVIDENCE = {("template", "template.not-found"), ("route", "*"), ("section", "content.not-found")}
# Built by concatenation so this file never contains the literal patterns it hunts for.
ABS_PATTERNS = [re.compile(p) for p in ("/" + "Users/", "/" + "home/[a-z]", "/" + "private/tmp", "/" + "var/folders", "[A-Za-z]:" + r"\\" + r"\\?Users")]


def res(name, status, detail=""):
    RESULTS.append((name, status, detail))


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return json.load(f)


def ids_in(folder):
    out = []
    for fn in sorted(os.listdir(os.path.join(ROOT, folder))):
        if fn.endswith(".json"):
            out.append(load(os.path.join(folder, fn))["id"])
    return out


def walk_json(obj):
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            yield from walk_json(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk_json(v)


def all_json_files():
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for fn in fns:
            if fn.endswith(".json"):
                yield os.path.join(dp, fn)


def count_leaves(d):
    n = 0
    for k, v in d.items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict) and "$value" in v:
            n += 1
        elif isinstance(v, dict):
            n += count_leaves(v)
    return n


def leaf_values(d, prefix=""):
    out = {}
    for k, v in d.items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict) and "$value" in v:
            out[prefix + k] = v["$value"]
        elif isinstance(v, dict):
            out.update(leaf_values(v, prefix + k + "."))
    return out


def compute_counts():
    tokens = 0
    for layer in ("00-foundation", "10-semantic", "20-component", "30-layout"):
        d = os.path.join(ROOT, "tokens", layer)
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".json"):
                tokens += count_leaves(load(os.path.join("tokens", layer, fn)))
    import adversarial_test as at
    cites = sum(1 for p in all_json_files() for o in walk_json(json.load(open(p, encoding="utf-8")))
                if isinstance(o, dict) and {"path", "lines", "quote"} <= set(o))
    return {
        "tokens": tokens,
        "primitives": len(ids_in("primitives")),
        "components": len(ids_in("components")),
        "sections": len(ids_in("sections")),
        "templates": len(load("templates/templates.json")["templates"]),
        "routes": len(load("templates/routes.json")["routes"]),
        "assetRoles": len(load("assets/asset-roles.json")["roles"]),
        "graphRules": len(load("compatibility/graph.json")["rules"]),
        "adversarialMutations": len(at.CASES) + len(at.RULE_CASES) + len(at.REPO_CASES),
        "adversarialControls": len(at.CONTROLS) + 1,
        "citations": cites,
    }


# ------------------------------------------------------------------ checks
def check_schema_example():
    from jsonschema import Draft7Validator
    schema = load("schema/pagespec.schema.json")
    Draft7Validator.check_schema(schema)
    errs = list(Draft7Validator(schema).iter_errors(load("schema/example.pagespec.json")))
    res("schema_example", "FAIL" if errs else "PASS", f"{len(errs)} error(s)" + (f": {errs[0].message[:120]}" if errs else ""))


def check_semantic_example():
    import semantic_validate as sv
    iss = sv.validate(load("schema/example.pagespec.json"), root=ROOT)
    errs = [i for i in iss if i.severity == "error"]
    res("semantic_example", "FAIL" if errs else "PASS", f"{len(errs)} error(s), {len(iss) - len(errs)} warning(s)" + (f": {errs[0]}" if errs else ""))


def check_adversarial():
    p = subprocess.run([sys.executable, os.path.join(ROOT, "schema", "tests", "adversarial_test.py")], capture_output=True, text=True)
    last = (p.stdout.strip().splitlines() or ["(no output)"])[-1]
    res("adversarial_suite", "PASS" if p.returncode == 0 else "FAIL", last)


def check_allowlist_parity():
    al = load("tokens/llm/component-allowlist.json")
    schema = load("schema/pagespec.schema.json")
    props = set()
    for br in schema["definitions"]["node"]["allOf"]:
        props |= set(br["then"]["properties"])
    motion = set()
    for br in schema["definitions"]["node"]["allOf"]:
        motion |= set(br["then"]["properties"]["motion"]["properties"])
    pairs = {
        "sections": (al["sections"], ids_in("sections")),
        "primitives": (al["primitives"], ids_in("primitives")),
        "components": (al["components"], ids_in("components")),
        "templates": (al["templates"], [t["id"] for t in load("templates/templates.json")["templates"]]),
        "assetRoles": (al["assetRoles"], list(load("assets/asset-roles.json")["roles"])),
        "nodeProperties": (al["nodeProperties"], props),
        "motionProperties": (al["motionProperties"], motion),
        "pageProperties": (al["pageProperties"], schema["properties"]),
    }
    bad = []
    for k, (a, b) in pairs.items():
        a, b = set(a), set(b)
        if a - b:
            bad.append(f"{k}: phantom {sorted(a - b)}")
        if b - a:
            bad.append(f"{k}: orphan {sorted(b - a)}")
    res("allowlist_parity", "FAIL" if bad else "PASS", "; ".join(bad) or f"{sum(len(v[0]) for v in pairs.values())} ids matched across {len(pairs)} groups")


def check_allowlist_version():
    v = load("tokens/llm/component-allowlist.json")["allowlistVersion"]
    m = load("registry.manifest.json")["allowlistVersion"]
    bad = []
    if v != m:
        bad.append(f"manifest {m} != allowlist {v}")
    for doc in ("README.md", "CHANGELOG.md"):
        with open(os.path.join(ROOT, doc), encoding="utf-8") as f:
            text = f.read()
        found = set(re.findall(r"allowlistVersion\W+(\d+\.\d+\.\d+)", text))
        if found != {v}:
            bad.append(f"{doc} states {sorted(found) or 'nothing'}, allowlist is {v}")
    res("allowlist_version_parity", "FAIL" if bad else "PASS", "; ".join(bad) or f"allowlistVersion {v} everywhere")


def check_counts():
    real = compute_counts()
    stated = load("registry.manifest.json")["counts"]
    bad = [f"manifest {k}={stated.get(k)} real={v}" for k, v in real.items() if stated.get(k) != v]
    bad += [f"manifest has unknown count '{k}'" for k in stated if k not in real]
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        table = dict(re.findall(r"^\|\s*`?(\w+)`?\s*\|\s*(\d+)\s*\|", f.read(), re.M))
    for k, v in real.items():
        if k not in table:
            bad.append(f"README counts table missing '{k}'")
        elif int(table[k]) != v:
            bad.append(f"README {k}={table[k]} real={v}")
    res("manifest_counts", "FAIL" if bad else "PASS", "; ".join(bad) or ", ".join(f"{k}={v}" for k, v in real.items()))


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def check_citations():
    mv = load("extraction/measured-values.json")
    markers = mv["sourceProject"]["markerFiles"]
    source_present = all(os.path.exists(os.path.join(PARENT, m)) for m in markers)
    bad, absent, ok = [], 0, 0
    cache = {}
    for p in all_json_files():
        rel = os.path.relpath(p, ROOT)
        with open(p, encoding="utf-8") as f:
            doc = json.load(f)
        for o in walk_json(doc):
            if not (isinstance(o, dict) and {"path", "lines", "quote"} <= set(o)):
                continue
            path, lines, quote = o["path"], str(o["lines"]), o["quote"]
            where = f"{rel} -> {path}:{lines}"
            if os.path.isabs(path) or ".." in path.split("/"):
                bad.append(f"{where}: path must be relative to the project folder")
                continue
            m = re.fullmatch(r"(\d+)(?:-(\d+))?", lines)
            if not m:
                bad.append(f"{where}: malformed line range")
                continue
            a, b = int(m.group(1)), int(m.group(2) or m.group(1))
            full = os.path.join(PARENT, path)
            if not os.path.isfile(full):
                if source_present:
                    bad.append(f"{where}: file not found although the source tree is present")
                else:
                    absent += 1
                continue
            if full not in cache:
                with open(full, encoding="utf-8", errors="replace") as f:
                    cache[full] = f.read().split("\n")
                if cache[full] and cache[full][-1] == "":
                    cache[full].pop()
            src = cache[full]
            if a < 1 or b < a or b > len(src):
                bad.append(f"{where}: range outside file length {len(src)}")
                continue
            if norm(quote) not in norm(" ".join(src[a - 1:b])):
                bad.append(f"{where}: quote {quote[:60]!r} not found in the cited lines")
                continue
            ok += 1
    if bad:
        res("citations", "FAIL", f"{len(bad)} bad: " + " | ".join(bad[:5]))
    elif absent:
        res("citations", "WARN", f"{ok} verified, {absent} unverifiable: sibling source tree absent (standalone copy)")
    else:
        res("citations", "PASS", f"{ok} citations: range and quoted content verified")


def check_absolute_paths():
    hits = []
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d != "__pycache__"]
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                with open(p, encoding="utf-8") as f:
                    for n, line in enumerate(f, 1):
                        if any(rx.search(line) for rx in ABS_PATTERNS):
                            hits.append(f"{os.path.relpath(p, ROOT)}:{n}")
            except UnicodeDecodeError:
                continue
    res("absolute_paths", "FAIL" if hits else "PASS", ", ".join(hits[:10]) or "no absolute machine paths")


def check_entrypoints():
    ep = load("registry.manifest.json")["entryPoints"]
    bad = []
    for k, rel in ep.items():
        if os.path.isabs(rel) or ".." in rel.replace("\\", "/").split("/"):
            bad.append(f"{k}: '{rel}' points outside design-repo/")
        elif not os.path.isfile(os.path.join(ROOT, rel)):
            bad.append(f"{k}: '{rel}' does not exist")
    res("entrypoints", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(ep)} entry points, all inside the package")


def check_schema_contract_parity():
    schema = load("schema/pagespec.schema.json")
    branches = {br["if"]["properties"]["type"]["const"]: br["then"] for br in schema["definitions"]["node"]["allOf"]}
    bad = []
    secs = {i: load(f"sections/{i}.json") for i in ids_in("sections")}
    if set(branches) != set(secs):
        bad.append(f"schema branches {sorted(set(branches) ^ set(secs))} differ from contracts")
    if set(schema["definitions"]["node"]["properties"]["type"]["enum"]) != set(secs):
        bad.append("node type enum != contracts")
    for sid, s in secs.items():
        br = branches.get(sid)
        if not br:
            continue
        if br["properties"]["content"] != s["content"]:
            bad.append(f"{sid}: content schema differs from contract")
        mp = br["properties"]["motion"]
        if mp.get("additionalProperties") is not False:
            bad.append(f"{sid}: motion object is not closed")
        if "variants" in s["motion"]:
            want = sorted(v["pattern"] for v in s["motion"]["variants"].values())
            if sorted(mp["properties"]["pattern"]["enum"]) != want:
                bad.append(f"{sid}: motion pattern enum differs from contract variants")
            for cond in mp.get("allOf", []):
                pat = cond["if"]["properties"]["pattern"]["const"]
                v = next(v for v in s["motion"]["variants"].values() if v["pattern"] == pat)
                if cond["then"]["properties"]["reducedMotionFallback"]["const"] != v["reducedMotionFallback"]:
                    bad.append(f"{sid}: fallback const for {pat} differs")
        else:
            for k in ("pattern", "trigger", "reducedMotionFallback"):
                if mp["properties"][k].get("const") != s["motion"][k]:
                    bad.append(f"{sid}: motion.{k} const differs from contract")
        if bool(s.get("anchor")) != ("anchorId" in br["properties"]):
            bad.append(f"{sid}: anchorId presence differs from contract")
    res("schema_contract_parity", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(secs)} section branches match their contracts")


def check_graph_validator_parity():
    import semantic_validate as sv
    graph = {r["id"]: r for r in load("compatibility/graph.json")["rules"]}
    bad = []
    if set(graph) != set(sv.GRAPH_RULES):
        bad.append(f"graph-only {sorted(set(graph) - set(sv.GRAPH_RULES))}, validator-only {sorted(set(sv.GRAPH_RULES) - set(graph))}")
    for rid, (sev, _fn) in sv.GRAPH_RULES.items():
        if rid in graph and graph[rid]["severity"] != sev:
            bad.append(f"{rid}: graph says {graph[rid]['severity']}, validator expects {sev}")
        if rid in graph and graph[rid]["severity"] not in ("error", "warn"):
            bad.append(f"{rid}: invalid severity")
    sr = graph.get("SURFACE_RHYTHM", {})
    prose = " ".join(sr.get("exceptions", []))
    for a, b in sorted(sv.SURFACE_EXCEPTIONS):
        if f"{a} -> {b}" not in prose:
            bad.append(f"SURFACE_RHYTHM exception {a} -> {b} enforced but not documented")
    if len(sr.get("exceptions", [])) != len(sv.SURFACE_EXCEPTIONS):
        bad.append("SURFACE_RHYTHM exception count differs between graph and validator")
    for rid, const in (("MAX_CONSECUTIVE_SCROLL_STAGES", sv.MAX_SCROLL_STAGE_RUN), ("STORY_REVEAL_BUDGET", sv.STORY_REVEAL_MAX), ("AMBIENT_VIDEO_BUDGET", sv.AMBIENT_VIDEO_MAX)):
        if rid in graph and not re.search(rf"\b{const}\b", graph[rid]["description"]):
            bad.append(f"{rid}: validator limit {const} not stated in graph description")
    res("graph_validator_parity", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(graph)} rules: ids, severities and limits agree")


def check_template_route_coverage():
    tpls = {t["id"]: t for t in load("templates/templates.json")["templates"]}
    routes = load("templates/routes.json")["routes"]
    secs = {i: load(f"sections/{i}.json") for i in ids_in("sections")}
    bad = []
    paths = [r["path"] for r in routes]
    dup = sorted({p for p in paths if paths.count(p) > 1})
    if dup:
        bad.append(f"routes assigned more than once: {dup}")
    for r in routes:
        if r["template"] not in tpls:
            bad.append(f"route {r['path']} -> unknown template {r['template']}")
    for tid, t in tpls.items():
        bound = [r["path"] for r in routes if r["template"] == tid]
        if not bound:
            bad.append(f"{tid} has no route")
        pol = t["routePolicy"]
        if pol["kind"] == "exact" and bound != [pol["route"]]:
            bad.append(f"{tid}: exact route {pol['route']} but bound to {bound}")
        if pol["kind"] == "catch-all" and bound != ["*"]:
            bad.append(f"{tid}: catch-all but bound to {bound}")
        if pol["kind"] == "registered-or-new" and sorted(bound) != sorted(pol["registered"]):
            bad.append(f"{tid}: registered {pol['registered']} but bound to {bound}")
        for n in t["nodes"]:
            if not {"section", "required", "repeatable"} <= set(n):
                bad.append(f"{tid}: node is not a structured object {n}")
                continue
            s = secs.get(n["section"])
            if s is None:
                bad.append(f"{tid}: unknown section {n['section']}")
            elif n.get("variant") and n["variant"] not in (s.get("variants") or []):
                bad.append(f"{tid}: variant {n['variant']} not in {n['section']}")
            elif s["constraints"].get("templates") and tid not in s["constraints"]["templates"]:
                bad.append(f"{tid}: {n['section']} is restricted to {s['constraints']['templates']}")
    res("template_route_coverage", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(routes)} routes -> {len(tpls)} templates, 1:1 coverage")


def check_theme_resolution():
    found = leaf_values(load("tokens/00-foundation/color.json"))
    sem = leaf_values(load("tokens/10-semantic/semantic.json"))
    theme = load("tokens/themes/light.json")["resolves"]
    bad = []
    for k, v in sem.items():
        m = re.fullmatch(r"\{(color\.[a-z-]+)\}", str(v))
        if not m:
            bad.append(f"{k}: raw value {v!r} (must reference a foundation token)")
        elif m.group(1) not in found:
            bad.append(f"{k}: {v} does not resolve")
        elif theme.get(k, {}).get("value") != found[m.group(1)]:
            bad.append(f"{k}: light theme resolves to {theme.get(k)}, foundation is {found[m.group(1)]}")
    extra = set(theme) - set(sem)
    if extra:
        bad.append(f"light theme has unknown keys {sorted(extra)}")
    res("theme_resolution", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(sem)} semantic tokens resolve in theme 'light'")


def check_token_catalog():
    cat = load("tokens/llm/token-catalog.json")
    pol = load("tokens/llm/token-policy.json")
    motion = load("tokens/00-foundation/motion.json")
    real = {
        "semantic": leaf_values(load("tokens/10-semantic/semantic.json")),
        "component": leaf_values(load("tokens/20-component/component.json")),
        "layout": leaf_values(load("tokens/30-layout/layout.json")),
        "typography": leaf_values(load("tokens/00-foundation/typography.json")["type"]),
        "breakpoint": leaf_values(load("tokens/00-foundation/breakpoint.json")["breakpoint"]),
        "motion": {**{"duration." + k: 1 for k in leaf_values(motion["duration"])}, **{"easing." + k: 1 for k in leaf_values(motion["easing"])}},
    }
    bad = []
    for k, leaves in real.items():
        listed = set(cat.get(k, []))
        if listed - set(leaves):
            bad.append(f"catalog.{k} phantom {sorted(listed - set(leaves))}")
        if set(leaves) - listed:
            bad.append(f"catalog.{k} missing {sorted(set(leaves) - listed)}")
    cat_keys = {k for k in cat if k not in ("catalogVersion", "description")}
    pol_keys = set(pol["rawValueRestrictions"])
    if pol_keys != cat_keys:
        bad.append(f"policy categories {sorted(pol_keys ^ cat_keys)} do not match catalog keys")
    res("token_catalog", "FAIL" if bad else "PASS", "; ".join(bad) or f"{sum(len(v) for v in real.values())} catalog entries resolve; policy keys == catalog keys")


def check_asset_roles():
    import semantic_validate as sv
    reg = load("assets/asset-roles.json")
    schema = load("schema/pagespec.schema.json")
    al = load("tokens/llm/component-allowlist.json")
    field_roles = set()
    for i in ids_in("sections"):
        for o in walk_json(load(f"sections/{i}.json")["content"]):
            if isinstance(o, dict) and "assetRole" in o.get("properties", {}):
                field_roles |= set(o["properties"]["assetRole"]["enum"])
    roles = set(reg["roles"])
    bad = []
    if roles != set(schema["definitions"]["assetRole"]["enum"]):
        bad.append("registry != schema assetRole enum")
    if roles != field_roles:
        bad.append(f"registry vs fields: unused {sorted(roles - field_roles)}, unregistered {sorted(field_roles - roles)}")
    if roles != set(al["assetRoles"]):
        bad.append("registry != allowlist")
    for name, r in reg["roles"].items():
        if r["generationPolicy"] not in reg["generationPolicies"]:
            bad.append(f"{name}: unknown policy {r['generationPolicy']}")
    pins = sv.check_pins(sv.load_context(ROOT))
    bad += [f"{i.path}: {i.message}" for i in pins]
    res("asset_roles", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(roles)} roles closed and wired; {len(sv.PINNED_ASSET_POLICIES)} pinned policies + {len(sv.PINNED_LICENCES)} licence hold")


def check_responsive():
    bad = []
    for i in ids_in("sections"):
        r = load(f"sections/{i}.json").get("responsive") or {}
        if r.get("primaryBreakpoint") != 768:
            bad.append(f"{i}: primaryBreakpoint must be 768")
        has768 = any(c.get("maxWidth") == 768 for c in r.get("changes", []))
        no = r.get("noChangeAt768")
        if not has768 and not (no and no.get("reason") and no.get("evidence")):
            bad.append(f"{i}: no 768 change and no cited noChangeAt768")
        for c in r.get("changes", []):
            if not {"maxWidth", "aspect", "desktop", "mobile", "evidence"} <= set(c):
                bad.append(f"{i}: unstructured responsive change")
    res("responsive_768", "FAIL" if bad else "PASS", "; ".join(bad) or "every section has a structured, cited 768 entry")


def check_evidence_levels():
    bad = []
    items = [("template", t["id"], t["evidenceLevel"]) for t in load("templates/templates.json")["templates"]]
    items += [("route", r["path"], r["evidenceLevel"]) for r in load("templates/routes.json")["routes"]]
    items += [("section", i, load(f"sections/{i}.json")["evidenceLevel"]) for i in ids_in("sections")]
    for kind, key, lvl in items:
        if lvl not in EVIDENCE_LEVELS:
            bad.append(f"{kind} {key}: unknown evidence level {lvl}")
        if (kind, key) in PINNED_EVIDENCE and lvl != "inferred-unmeasured":
            bad.append(f"{kind} {key}: must stay inferred-unmeasured (never measured against the original), found {lvl}")
    res("evidence_levels", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(items)} evidence levels valid; not-found stays inferred-unmeasured")


def check_status():
    m = load("registry.manifest.json")
    bad = []
    if m.get("status") != "design-review-pending":
        bad.append(f"status {m.get('status')}")
    if m.get("productionApproved") is not False:
        bad.append("productionApproved must be false")
    if m.get("publishRecommended") is not False:
        bad.append("publishRecommended must be false")
    res("status_flags", "FAIL" if bad else "PASS", "; ".join(bad) or "design-review-pending, not production-approved, publishing not recommended")


def check_framework():
    m = load("registry.manifest.json")["sourceProject"]["framework"]
    led = load("extraction/measured-values.json")["sourceProject"]["framework"]
    bad = [] if m == led else [f"manifest {m} != ledger {led}"]
    pkg_path = os.path.join(PARENT, "package.json")
    if os.path.isfile(pkg_path):
        with open(pkg_path, encoding="utf-8") as f:
            pkg = json.load(f)
        deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        for k, v in m.items():
            if deps.get(k) != v:
                bad.append(f"{k}: manifest {v}, package.json {deps.get(k)}")
        res("framework_versions", "FAIL" if bad else "PASS", "; ".join(bad) or f"{len(m)} versions match ../package.json")
    else:
        res("framework_versions", "FAIL" if bad else "WARN", "; ".join(bad) or "manifest == ledger; ../package.json absent, live drift not checkable")


def main(argv):
    checks = [check_schema_example, check_semantic_example, check_allowlist_parity, check_allowlist_version, check_counts,
              check_citations, check_absolute_paths, check_entrypoints, check_schema_contract_parity, check_graph_validator_parity,
              check_template_route_coverage, check_theme_resolution, check_token_catalog, check_asset_roles, check_responsive, check_evidence_levels,
              check_status, check_framework]
    if "--print-counts" in argv:
        print(json.dumps(compute_counts(), indent=2))
        return 0
    if "--skip-adversarial" not in argv:
        checks.insert(2, check_adversarial)
    for c in checks:
        try:
            c()
        except Exception as e:  # a crashing check is a failing check
            res(c.__name__.replace("check_", ""), "FAIL", f"crashed: {type(e).__name__}: {e}")
    for name, status, detail in RESULTS:
        print(f"{status:4} {name:26} {detail}")
    n_fail = sum(1 for r in RESULTS if r[1] == "FAIL")
    n_warn = sum(1 for r in RESULTS if r[1] == "WARN")
    print(f"\n{len(RESULTS)} checks: {len(RESULTS) - n_fail - n_warn} pass, {n_warn} warn, {n_fail} fail")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
