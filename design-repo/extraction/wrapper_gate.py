#!/usr/bin/env python3
"""Whole-page-wrapper quality gate (R9). Called by verify_all.py (check `wrapper_gate`); also runnable alone.

    python3 extraction/wrapper_gate.py

Input: extraction/measured-values.json `sectionHeights` (measured on the BUILT clone at 1440px with
extraction/measure_sections.mjs) and extraction/wrapper-whitelist.json.
Rules (thresholds pinned HERE in code, not read from JSON):
  * a HERO section taller than 1800px -> warn; taller than 3000px -> error unless whitelisted.
  * one in-flow section holding > 50% of its page height -> warn; > 60% -> error unless whitelisted.
    Pages with fewer than 3 in-flow non-SHELL sections are skipped; SHELL sections (header, footer,
    subfooter) are excluded; sticky/fixed elements recorded with inFlow:false take no page height.
  * every template must have a measurement and every required node a measured (non-null) height -> else error.
  * a measurement at any viewport other than 1440 -> error.
  * whitelist entries need reviewedBy, a justification of 30+ chars and maxHeightPx above the measured height;
    stale entries (no gate hit) and over-cap entries fail; an agent reviewer must say
    "agent attestation, not a human sign-off". A whitelisted hit still warns.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWPORT = 1440
HERO_WARN_PX = 1800
HERO_ERROR_PX = 3000
SHARE_WARN = 0.50
SHARE_ERROR = 0.60
MIN_INFLOW_SECTIONS = 3
AGENT_ATTESTATION = "agent attestation, not a human sign-off"


def J(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return json.load(f)


def sections_meta(root):
    out = {}
    d = os.path.join(root, "sections")
    for fn in os.listdir(d):
        if fn.endswith(".json"):
            c = J(root, os.path.join("sections", fn))
            out[c["id"]] = c
    return out


def run(root=ROOT, measured=None, whitelist=None, templates=None, sections=None):
    measured = measured if measured is not None else J(root, "extraction/measured-values.json")
    whitelist = whitelist if whitelist is not None else J(root, "extraction/wrapper-whitelist.json")
    templates = templates if templates is not None else J(root, "templates/templates.json")
    sections = sections if sections is not None else sections_meta(root)
    errors, warns = [], []
    sh = measured.get("sectionHeights")
    if not isinstance(sh, dict):
        return ["sectionHeights missing from extraction/measured-values.json"], warns
    if sh.get("viewport") != VIEWPORT:
        errors.append(f"sectionHeights measured at viewport {sh.get('viewport')}, gate requires {VIEWPORT}")
    pages = sh.get("templates", {})
    entries = whitelist.get("entries", [])
    wl = {(e.get("template"), e.get("section")): e for e in entries}
    used = set()
    for e in entries:
        key = f"{e.get('template')}/{e.get('section')}"
        rb = e.get("reviewedBy", "")
        if not rb:
            errors.append(f"whitelist {key}: reviewedBy missing")
        elif "agent" in rb.lower() and AGENT_ATTESTATION not in rb:
            errors.append(f"whitelist {key}: agent reviewer must state '{AGENT_ATTESTATION}'")
        if len(e.get("justification", "")) < 30:
            errors.append(f"whitelist {key}: justification must be 30+ characters")
    cat = lambda sid: sections.get(sid, {}).get("semantic", {}).get("category")
    for t in templates["templates"]:
        tid = t["id"]
        m = pages.get(tid)
        if m is None:
            errors.append(f"template {tid}: no sectionHeights measurement")
            continue
        rows = m.get("sections", [])
        ids = [s["section"] for s in rows]
        for n in t["nodes"]:
            if n["required"] and n["section"] not in ids:
                errors.append(f"template {tid}: required node {n['section']} has no measured height")
        for s in rows:
            if s.get("height") is None:
                errors.append(f"template {tid}: {s['section']} measurement is missing (null)")
            if s["section"] not in sections:
                errors.append(f"template {tid}: measured section {s['section']} has no contract")
        page_h = m.get("pageHeight") or 0
        if not page_h:
            errors.append(f"template {tid}: pageHeight missing")
        inflow = [s for s in rows if s.get("height") is not None and s.get("inFlow", True) and cat(s["section"]) != "SHELL"]
        for s in rows:
            if s.get("height") is None:
                continue
            key = (tid, s["section"])
            entry = wl.get(key)
            if cat(s["section"]) == "HERO" and s["height"] > HERO_WARN_PX:
                if s["height"] > HERO_ERROR_PX and not entry:
                    errors.append(f"{tid}/{s['section']}: HERO {s['height']}px > {HERO_ERROR_PX}px")
                else:
                    warns.append(f"{tid}/{s['section']}: HERO {s['height']}px > {HERO_WARN_PX}px" + (" (whitelisted)" if entry else ""))
                if entry:
                    used.add(key)
            if len(inflow) >= MIN_INFLOW_SECTIONS and s in inflow and page_h:
                share = s["height"] / page_h
                if share > SHARE_WARN:
                    if share > SHARE_ERROR and not entry:
                        errors.append(f"{tid}/{s['section']}: holds {share:.0%} of the page (> {SHARE_ERROR:.0%})")
                    else:
                        warns.append(f"{tid}/{s['section']}: holds {share:.0%} of the page (> {SHARE_WARN:.0%})" + (" (whitelisted)" if entry else ""))
                    if entry:
                        used.add(key)
            if entry and s["height"] > entry.get("maxHeightPx", 0):
                errors.append(f"whitelist {tid}/{s['section']}: measured {s['height']}px exceeds maxHeightPx {entry.get('maxHeightPx')}")
    for key in set(wl) - used:
        errors.append(f"whitelist {key[0]}/{key[1]}: stale entry (no gate hit in the current measurements)")
    return errors, warns


def main():
    errors, warns = run()
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"wrapper gate: {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
