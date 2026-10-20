#!/usr/bin/env python3
"""Prove that every verify_all.py check actually catches drift.

For each check, copy design-repo/ into a fresh temp folder, inject one defect,
run that copy's own extraction/verify_all.py and require (a) a non-zero exit
and (b) a FAIL line for the targeted check. Clean copies must pass, both
standalone (no sibling source: citations WARN) and, when the real source tree
is available next to this package, with the source symlinked in.

Citation drift is proven twice: against a synthetic fixture file created in the
temp parent (works even in a standalone copy) and, when the real source is
present, against real cited files.

Exit 0 only if every injection is caught and every clean control passes.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REAL_PARENT = os.path.dirname(ROOT)
MARKERS = ("src/App.jsx", "CLONE_SPEC.md", "package.json")
SOURCE_AVAILABLE = all(os.path.exists(os.path.join(REAL_PARENT, m)) for m in MARKERS)


def jedit(repo, rel, fn):
    p = os.path.join(repo, rel)
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    fn(d)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)


def tedit(repo, rel, fn):
    p = os.path.join(repo, rel)
    with open(p, encoding="utf-8") as f:
        t = f.read()
    t2 = fn(t)
    assert t2 != t, f"injection into {rel} changed nothing"
    with open(p, "w", encoding="utf-8") as f:
        f.write(t2)


def fresh(with_source):
    tmp = tempfile.mkdtemp(prefix="equator-drift-")
    repo = os.path.join(tmp, "design-repo")
    shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns("__pycache__"))
    if with_source:
        for entry in os.listdir(REAL_PARENT):
            if entry not in ("design-repo", "design-repo.zip"):
                os.symlink(os.path.join(REAL_PARENT, entry), os.path.join(tmp, entry))
    return tmp, repo


def verify(repo, adversarial=False):
    cmd = [sys.executable, os.path.join(repo, "extraction", "verify_all.py")]
    if not adversarial:
        cmd.append("--skip-adversarial")
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


# ---------------------------------------------------------------- injections
def inj_phantom_section(repo, parent):
    jedit(repo, "tokens/llm/component-allowlist.json", lambda d: d["sections"].append("hero.phantom"))

def inj_orphan_primitive(repo, parent):
    jedit(repo, "tokens/llm/component-allowlist.json", lambda d: d["primitives"].remove("primitive.pill"))

def inj_allowlist_version(repo, parent):
    jedit(repo, "tokens/llm/component-allowlist.json", lambda d: d.__setitem__("allowlistVersion", "1.0.1"))

def inj_readme_version(repo, parent):
    tedit(repo, "README.md", lambda t: t.replace("allowlistVersion 1.0.0", "allowlistVersion 1.0.1"))

def inj_manifest_count(repo, parent):
    jedit(repo, "registry.manifest.json", lambda d: d["counts"].__setitem__("sections", 14))

def inj_readme_count(repo, parent):
    tedit(repo, "README.md", lambda t: t.replace("| `routes` | 3 |", "| `routes` | 4 |"))

def _add_cite(repo, cite):
    jedit(repo, "extraction/measured-values.json", lambda d: d["entries"].append({"id": "injected", "claim": "x", "evidenceLevel": "measured", "evidence": [cite]}))

def _fixture(parent):
    os.makedirs(os.path.join(parent, "fixture"), exist_ok=True)
    with open(os.path.join(parent, "fixture", "sample.css"), "w") as f:
        f.write(".a { color: red; }\n.b { color: blue; }\n.c { color: green; }\n")

def inj_cite_range_synthetic(repo, parent):
    _fixture(parent)
    _add_cite(repo, {"path": "fixture/sample.css", "lines": "5-9", "quote": "color"})

def inj_cite_quote_synthetic(repo, parent):
    _fixture(parent)
    _add_cite(repo, {"path": "fixture/sample.css", "lines": "1", "quote": "color: blue"})

def inj_cite_range_real(repo, parent):
    def f(d):
        e = next(x for x in d["entries"] if x["id"] == "lazy-fade")
        e["evidence"][0]["lines"] = "9000-9001"
    jedit(repo, "extraction/measured-values.json", f)

def inj_cite_wrong_content_real(repo, parent):
    # in range, wrong lines: shift the values-opacity citation by one line in the QA dump
    def f(d):
        e = next(x for x in d["entries"] if x["id"] == "values-initial-opacity")
        e["evidence"][0]["lines"] = "84"
    jedit(repo, "extraction/measured-values.json", f)

def inj_cite_missing_file_real(repo, parent):
    _add_cite(repo, {"path": "src/components/DoesNotExist.jsx", "lines": "1", "quote": "x"})

def inj_absolute_path(repo, parent):
    tedit(repo, "README.md", lambda t: t + "\nSee /" + "Users/someone/V3/equator/CLONE_SPEC.md\n")

def inj_entrypoint_outside(repo, parent):
    jedit(repo, "registry.manifest.json", lambda d: d["entryPoints"].__setitem__("spec", "../CLONE_SPEC.md"))

def inj_schema_contract(repo, parent):
    jedit(repo, "sections/hero.title.json", lambda d: d["content"]["properties"].__setitem__("eyebrow", {"type": "string", "x-maxWords": 3}))

def inj_graph_rule_added(repo, parent):
    jedit(repo, "compatibility/graph.json", lambda d: d["rules"].append({"id": "NO_DOUBLE_CTA", "severity": "error", "description": "x", "exceptions": [], "evidence": []}))

def inj_graph_severity(repo, parent):
    jedit(repo, "compatibility/graph.json", lambda d: next(r for r in d["rules"] if r["id"] == "MAX_WORDS").__setitem__("severity", "warn"))

def inj_graph_exception_prose(repo, parent):
    jedit(repo, "compatibility/graph.json", lambda d: next(r for r in d["rules"] if r["id"] == "SURFACE_RHYTHM")["exceptions"].pop())

def inj_duplicate_route(repo, parent):
    jedit(repo, "templates/routes.json", lambda d: d["routes"].append({"path": "/privacy-policy", "template": "template.not-found", "evidenceLevel": "measured", "evidence": []}))

def inj_theme_ref(repo, parent):
    jedit(repo, "tokens/10-semantic/semantic.json", lambda d: d["text"]["primary"].__setitem__("$value", "{color.ink}"))

def inj_catalog_phantom(repo, parent):
    jedit(repo, "tokens/llm/token-catalog.json", lambda d: d["semantic"].append("text.phantom"))

def inj_policy_key(repo, parent):
    def f(d):
        d["rawValueRestrictions"]["shadow"] = d["rawValueRestrictions"].pop("motion")
    jedit(repo, "tokens/llm/token-policy.json", f)

def inj_asset_pin(repo, parent):
    jedit(repo, "assets/asset-roles.json", lambda d: d["roles"]["team-portrait"].__setitem__("generationPolicy", "may-generate-new"))

def inj_evidence_laundering(repo, parent):
    jedit(repo, "templates/templates.json", lambda d: next(t for t in d["templates"] if t["id"] == "template.not-found").__setitem__("evidenceLevel", "measured"))

def inj_responsive(repo, parent):
    jedit(repo, "sections/hero.title.json", lambda d: d["responsive"].__setitem__("changes", []))

def inj_example_maxwords(repo, parent):
    jedit(repo, "schema/example.pagespec.json", lambda d: d["nodes"][2]["content"].__setitem__("subtitle", " ".join(["word"] * 30)))

def inj_example_schema(repo, parent):
    jedit(repo, "schema/example.pagespec.json", lambda d: d["nodes"][2]["motion"].__setitem__("inventedAnimation", "parallax"))

def inj_status(repo, parent):
    jedit(repo, "registry.manifest.json", lambda d: d.__setitem__("productionApproved", True))

def inj_framework(repo, parent):
    def f(d):
        d["sourceProject"]["framework"]["react"] = "^19.0.0"
    jedit(repo, "registry.manifest.json", f)
    jedit(repo, "extraction/measured-values.json", f)

def inj_validator_neutered(repo, parent):
    tedit(repo, "schema/semantic_validate.py", lambda t: t.replace(
        'n = _types(spec).count("hero.title")', 'n = min(1, _types(spec).count("hero.title"))'))


# (name, target check, inject, needs real source, run adversarial suite)
INJECTIONS = [
    ("phantom allowlist section", "allowlist_parity", inj_phantom_section, False, False),
    ("orphan primitive contract", "allowlist_parity", inj_orphan_primitive, False, False),
    ("allowlistVersion bumped in allowlist only", "allowlist_version_parity", inj_allowlist_version, False, False),
    ("README states a stale allowlistVersion", "allowlist_version_parity", inj_readme_version, False, False),
    ("manifest count wrong", "manifest_counts", inj_manifest_count, False, False),
    ("README counts table wrong", "manifest_counts", inj_readme_count, False, False),
    ("citation range past EOF (synthetic file)", "citations", inj_cite_range_synthetic, False, False),
    ("citation quote not in cited line (synthetic)", "citations", inj_cite_quote_synthetic, False, False),
    ("citation range past EOF (real source)", "citations", inj_cite_range_real, True, False),
    ("citation in range but wrong lines (real source)", "citations", inj_cite_wrong_content_real, True, False),
    ("citation to a missing file (real source)", "citations", inj_cite_missing_file_real, True, False),
    ("absolute machine path in README", "absolute_paths", inj_absolute_path, False, False),
    ("entry point outside the package", "entrypoints", inj_entrypoint_outside, False, False),
    ("contract field not in schema", "schema_contract_parity", inj_schema_contract, False, False),
    ("graph rule with no validator", "graph_validator_parity", inj_graph_rule_added, False, False),
    ("graph severity drift", "graph_validator_parity", inj_graph_severity, False, False),
    ("graph exception prose dropped", "graph_validator_parity", inj_graph_exception_prose, False, False),
    ("route assigned twice", "template_route_coverage", inj_duplicate_route, False, False),
    ("semantic token unresolvable", "theme_resolution", inj_theme_ref, False, False),
    ("catalog lists a token that does not exist", "token_catalog", inj_catalog_phantom, False, False),
    ("policy category not a real catalog key", "token_catalog", inj_policy_key, False, False),
    ("pinned role -> different valid policy", "asset_roles", inj_asset_pin, False, False),
    ("not-found evidence laundered to measured", "evidence_levels", inj_evidence_laundering, False, False),
    ("768 responsive entry removed", "responsive_768", inj_responsive, False, False),
    ("example maxWords overflow", "semantic_example", inj_example_maxwords, False, False),
    ("example invented motion field", "schema_example", inj_example_schema, False, False),
    ("productionApproved flipped", "status_flags", inj_status, False, False),
    ("framework version drift vs package.json", "framework_versions", inj_framework, True, False),
    ("validator rule neutered", "adversarial_suite", inj_validator_neutered, False, True),
]


def main():
    rows, failures = [], 0
    controls = [("clean copy, standalone (no sibling source)", False)]
    if SOURCE_AVAILABLE:
        controls.append(("clean copy, real source symlinked", True))
    for label, with_src in controls:
        tmp, repo = fresh(with_src)
        try:
            code, out = verify(repo, adversarial=True)
            ok = code == 0
            rows.append(("CONTROL", label, "passes" if ok else "FAILED:\n" + out))
            failures += not ok
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    for name, check, inject, needs_src, adv in INJECTIONS:
        if needs_src and not SOURCE_AVAILABLE:
            rows.append(("SKIP", f"{check}: {name}", "real source tree not present"))
            continue
        tmp, repo = fresh(needs_src)
        try:
            inject(repo, tmp)
            code, out = verify(repo, adversarial=adv)
            line = next((l for l in out.splitlines() if l.startswith("FAIL") and l.split()[1] == check), None)
            ok = code != 0 and line is not None
            rows.append(("CAUGHT" if ok else "MISSED", f"{check}: {name}", (line[len("FAIL "):].strip()[:110] if line else out[-300:])))
            failures += not ok
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    for kind, name, detail in rows:
        print(f"{kind:8} {name:70} {detail}")
    caught = sum(1 for r in rows if r[0] == "CAUGHT")
    skipped = sum(1 for r in rows if r[0] == "SKIP")
    print(f"\n{caught}/{len(INJECTIONS)} injections caught, {skipped} skipped, {len(controls)} clean control(s), {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
