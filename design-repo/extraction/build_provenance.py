#!/usr/bin/env python3
"""Write the closed `source` provenance object of every section contract from the REAL clone source (R7).

    python3 extraction/build_provenance.py           # (re)write `source` into sections/*.json
    python3 extraction/build_provenance.py --check   # exit 1 if any contract's `source` differs from a fresh build

`source` = {id, tag, file, lines}: what DOM element / component implements the section, traceable to a line
range in the real file. `semantic` = {id, category} is the AI-facing taxonomy and is NOT derived from wrapper or
class names. Each range is found by searching the real file for the opening and closing needles below, so a
moved component changes the range instead of silently going stale. verify_all.py (check `provenance`) re-reads
every range and requires `<tag` on the first cited line.
Needs the sibling source project; without it --check prints a notice and exits 0.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(ROOT)

# section id -> (source id, tag, file, opening needle, closing needle or None for a one-line element)
TABLE = {
    "chrome.splash": ("Splash>section.splash", "section", "src/components/Splash.jsx", "<section className={`splash", "</section>"),
    "chrome.header": ("Header>div.headerCont>header", "div", "src/components/Header.jsx", '<div className="headerCont noselect">', "</header>"),
    "hero.title": ("Title>section.titleSection", "section", "src/components/Title.jsx", '<section className="titleSection"', "</section>"),
    "narrative.story-reveal": ("Story>section#our-story", "section", "src/components/Story.jsx", '<section className="story" id="our-story"', "</section>"),
    "values.sticky-stack": ("Values>section#what-we-stand-for", "section", "src/components/Values.jsx", '<section className="values" id="what-we-stand-for"', "</section>"),
    "capabilities.accordion": ("Capabilities>section#capabilities", "section", "src/components/Capabilities.jsx", '<section className="capabilities" id="capabilities"', "</section>"),
    "work.carousel-marquee": ("OurWork>section#our-work", "section", "src/components/OurWork.jsx", '<section className="partners noselect" id="our-work"', "</section>"),
    "team.roster": ("Team>section#team", "section", "src/components/Team.jsx", '<section className="team" id="team"', "</section>"),
    "conversion.cta-video": ("Cta>section.ctaSection", "section", "src/components/Cta.jsx", '<section className="ctaSection"', "</section>"),
    "chrome.footer": ("Footer>footer", "footer", "src/components/Footer.jsx", "<footer ref={ref}>", "</footer>"),
    "chrome.subfooter": ("Subfooter>div.subfooter", "div", "src/components/Footer.jsx", '<div className="subfooter">', "</div>\n  )"),
    "content.legal-header": ("PrivacyPolicy>article>h1", "h1", "src/pages/PrivacyPolicy.jsx", '<h1 className="text-headline1">', None),
    "content.legal-section": ("privacyBody>p>strong|h2 (heading-bounded run)", "p", "src/lib/privacyBody.js", "<p><strong>1. Data collection", None),
    "content.not-found": ("NotFound>main", "main", "src/pages/NotFound.jsx", '<main className="min-h-screen', "</main>"),
}


def locate(rel, start, end):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    a = next(i for i, l in enumerate(lines, 1) if start in l)
    if end is None:
        return f"{a}"
    off = sum(len(l) + 1 for l in lines[: a - 1])
    j = text.index(end, off)
    b = text.count("\n", 0, j) + 1
    return f"{a}-{b}" if b > a else f"{a}"


def build():
    out = {}
    for sid, (src_id, tag, rel, start, end) in TABLE.items():
        out[sid] = {"id": src_id, "tag": tag, "file": rel, "lines": locate(rel, start, end)}
    return out


def main(argv):
    if not os.path.isfile(os.path.join(SRC, "src", "App.jsx")):
        print("source project absent: provenance not rebuilt")
        return 0
    fresh = build()
    sd = os.path.join(ROOT, "sections")
    drift = []
    for fn in sorted(os.listdir(sd)):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(sd, fn)
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        want = fresh.get(d["id"])
        if want is None:
            drift.append(f"{d['id']}: no provenance row in build_provenance.TABLE")
            continue
        if "--check" in argv:
            if d.get("source") != want:
                drift.append(f"{d['id']}: source {d.get('source')} != fresh {want}")
            continue
        d["source"] = want
        keys = list(d)
        ordered = {}
        for k in keys:
            ordered[k] = d[k]
            if k == "semantic":
                ordered["source"] = want
        ordered["source"] = want
        with open(p, "w", encoding="utf-8") as f:
            json.dump(ordered, f, indent=2, ensure_ascii=False)
            f.write("\n")
    for sid in sorted(set(fresh) - {json.load(open(os.path.join(sd, f)))["id"] for f in os.listdir(sd) if f.endswith(".json")}):
        drift.append(f"{sid}: provenance row for a section with no contract")
    if drift:
        print("DRIFT: " + "; ".join(drift))
        return 1
    print("provenance up to date" if "--check" in argv else f"wrote source provenance for {len(fresh)} contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
