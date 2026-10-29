#!/usr/bin/env python3
"""Build tokens/llm/token-catalog.json from the REAL token files (R10).

    python3 extraction/build_token_catalog.py           # (re)write the catalog
    python3 extraction/build_token_catalog.py --check   # exit 1 if the committed catalog differs from a fresh build

Every `$value` leaf of tokens/00-foundation, 10-semantic, 20-component and 30-layout becomes one catalog entry
{category, layer, file, type, value}; semantic entries also carry the value their reference resolves to in each
theme of tokens/themes/. Nothing is typed by hand, so the catalog cannot drift from the token files without
--check (run by verify_all.py, check `token_catalog`) failing. Works standalone (no sibling source needed).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tokens", "llm", "token-catalog.json")
LAYERS = ("00-foundation", "10-semantic", "20-component", "30-layout")
# category of a token = its file for foundation tokens (typography split by top-level group), the layer otherwise
FOUNDATION_CATEGORY = {"color.json": "color", "spacing.json": "spacing", "radius.json": "radius", "elevation.json": "elevation",
                       "icon-size.json": "iconSize", "breakpoint.json": "breakpoint", "motion.json": "motion"}
TYPO_CATEGORY = {"font.family": "fontFamily", "font.weight": "fontWeight", "type": "typography"}


def leaves(d, pre=""):
    for k, v in d.items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict) and "$value" in v:
            yield pre + k, v
        elif isinstance(v, dict):
            yield from leaves(v, pre + k + ".")


def build(root=ROOT):
    tokens = {}
    for layer in LAYERS:
        d = os.path.join(root, "tokens", layer)
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                doc = json.load(f)
            for tid, leaf in leaves(doc):
                if layer == "00-foundation":
                    cat = FOUNDATION_CATEGORY.get(fn) or next(c for p, c in TYPO_CATEGORY.items() if tid == p or tid.startswith(p + "."))
                else:
                    cat = {"10-semantic": "semantic", "20-component": "component", "30-layout": "layout"}[layer]
                if tid in tokens:
                    raise SystemExit(f"duplicate token id {tid}")
                tokens[tid] = {"category": cat, "layer": layer, "file": f"tokens/{layer}/{fn}", "type": leaf.get("$type"), "value": leaf["$value"]}
    themes = {}
    td = os.path.join(root, "tokens", "themes")
    for fn in sorted(os.listdir(td)):
        if fn.endswith(".json"):
            with open(os.path.join(td, fn), encoding="utf-8") as f:
                th = json.load(f)
            themes[th["theme"]] = {"file": f"tokens/themes/{fn}", "isDefault": th.get("isDefault", False)}
            for tid, r in th["resolves"].items():
                if tid in tokens:
                    tokens[tid].setdefault("resolvedIn", {})[th["theme"]] = r["value"]
    cats = {}
    for tid, t in tokens.items():
        cats.setdefault(t["category"], []).append(tid)
    return {
        "catalogVersion": "2.0.0",
        "generatedBy": "extraction/build_token_catalog.py (verify_all.py re-runs it with --check)",
        "description": "Every approved token id. PageSpec `tokens` slots may reference only ids listed here, in the categories tokens/llm/token-policy.json allows for that slot; values come straight from the token files.",
        "themes": themes,
        "categories": {k: sorted(v) for k, v in sorted(cats.items())},
        "tokens": dict(sorted(tokens.items())),
    }


def main(argv):
    cat = build()
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            cur = json.load(f)
        if cur != cat:
            print(f"DRIFT: token-catalog.json differs from a fresh build in {[k for k in cat if cur.get(k) != cat[k]]}")
            return 1
        print(f"token catalog up to date ({len(cat['tokens'])} tokens)")
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(cat, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote tokens/llm/token-catalog.json: {len(cat['tokens'])} tokens in {len(cat['categories'])} categories")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
