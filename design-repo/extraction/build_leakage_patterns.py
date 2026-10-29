#!/usr/bin/env python3
"""Build schema/leakage-patterns.json: the GENERATION_MODE_* pattern registry, derived from the REAL clone source.

    python3 extraction/build_leakage_patterns.py           # (re)write schema/leakage-patterns.json
    python3 extraction/build_leakage_patterns.py --check   # exit 1 if the committed registry differs from a fresh build

Every pattern carries file:line evidence found by searching the real file (src/, index.html, CLONE_SPEC.md,
ASSET_MANIFEST.md, public/). Source copy is stored only as hashed 5-word shingles (sha256, first 16 hex) of
normalised text (schema/textnorm.py: NFKC, zero-width removal, homoglyph/quote/dash folding, diacritics stripped,
lower-case), so the registry never republishes the copy itself.
Needs the sibling source project; without it --check prints a notice and exits 0 (the committed registry is used).
No human has reviewed these patterns; detection is string-based and can be evaded by paraphrase, translation or
text rendered inside images.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "schema"))
from textnorm import normalize, shingles  # noqa: E402

OUT = os.path.join(ROOT, "schema", "leakage-patterns.json")
CONTENT = "src/lib/content.js"


def read(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        return f.read().split("\n")


def ev(rel, needle):
    for i, l in enumerate(read(rel), 1):
        if needle in l:
            return {"cite": f"{rel}:{i}", "anchor": needle}
    raise KeyError(f"{needle!r} not found in {rel}")


def rx_name(n):
    return r"\b" + r"\s+".join(re.escape(p) for p in normalize(n).split()) + r"\b"


def build():
    brand = [
        {"id": "equator", "regex": r"\bequator\b", "evidence": [ev("index.html", "<title>The Equator Company</title>")],
         "note": "the brand name; also blocks the ordinary word 'equator' in generation mode (accepted false positive)"},
        {"id": "equator-spaced", "regex": r"\be[\s._*-]{1,2}q[\s._*-]{1,2}u[\s._*-]{1,2}a[\s._*-]{1,2}t[\s._*-]{1,2}o[\s._*-]{1,2}r\b",
         "evidence": [ev("index.html", "<title>The Equator Company</title>")], "note": "letter-separated spelling (E.Q.U.A.T.O.R)"},
        {"id": "equatorcompany", "regex": r"(the)?equator[\s_-]?company", "evidence": [ev("index.html", 'href="http://equatorcompany.com"')]},
        {"id": "s317", "regex": r"\bs\s?317\b", "evidence": [ev("src/lib/privacyBody.js", "owned by S317 Consulting, LDA.")],
         "note": "S317 Consulting, LDA. is the legal entity that owns the site (privacy policy) and one of the four merged companies"},
    ]

    persons, seen = [], set()
    for i, l in enumerate(read(CONTENT), 1):
        m = re.match(r"\s*\['([^']+)', '([a-z-]+)', '[^']*', 'https://www\.linkedin\.com", l)
        if m:
            name, slug = m.group(1), m.group(2)
            for n, kind in ((name, "employee-name"), (slug.replace("-", " "), "employee-slug-name")):
                k = normalize(n)
                if k not in seen:
                    seen.add(k)
                    persons.append({"name": k, "regex": rx_name(n), "kind": kind, "evidence": [{"cite": f"{CONTENT}:{i}", "anchor": f"'{name}'"}]})
            persons.append({"name": slug, "regex": r"\b" + re.escape(slug) + r"\b", "kind": "employee-asset-slug",
                            "evidence": [{"cite": f"{CONTENT}:{i}", "anchor": f"'{slug}'"}]})

    customers = []
    for i, l in enumerate(read(CONTENT), 1):
        m = re.search(r"alt: '([^']+)', href: 'https://", l)
        if m:
            customers.append({"name": normalize(m.group(1)), "regex": rx_name(m.group(1)), "kind": "merged-company", "evidence": [{"cite": f"{CONTENT}:{i}", "anchor": f"alt: '{m.group(1)}'"}]})
    for needle, rx, kind in [
        ("Mamaland", r"\bmamaland\b", "client"), ("Mota-Engil", r"\bmota[\s-]?engil\b", "client"), ("E-Redes", r"\be[\s-]?redes\b", "client"),
        ("We support EDP", r"\bedp\b", "client"), ("Effizency", r"\beffizency\b", "client-platform"), ("SONAE MC", r"\bsonae\b", "client"),
        ("Missão Continente", r"\bmissao continente\b", "client-programme"), ("Dallas Airport", r"\bdallas airport\b", "client-asset"),
        ("Lisbon General Drainage Plan", r"\blisbon general drainage plan\b", "client-project"), ("Luanda Water Master Plan", r"\bluanda water master plan\b", "client-project"),
    ]:
        customers.append({"name": normalize(needle.replace("We support ", "")), "regex": rx, "kind": kind, "evidence": [ev(CONTENT, needle)]})
    customers.append({"name": "studio cronica", "regex": r"\bstudio[\s-]?cronica\b", "kind": "design-credit", "evidence": [ev("src/components/Footer.jsx", "Studio Cronica")]})

    claims = [
        {"id": "45-years", "regex": r"\b45\s*\+?\s*years\b", "evidence": [ev("src/components/Footer.jsx", "45 years of experience")]},
        {"id": "550000-hectare", "regex": r"\b550[,. ]?000[\s-]*hectares?\b", "evidence": [ev(CONTENT, "550,000-hectare")]},
        {"id": "900000-people", "regex": r"\b900[,. ]?000 people\b", "evidence": [ev(CONTENT, "900,000 people")]},
        {"id": "european-excellence-award", "regex": r"\beuropean excellence award\b", "evidence": [ev(CONTENT, "European Excellence Award")]},
        {"id": "prr-funding", "regex": r"\b(prr|recuperar\s?portugal|republica portuguesa)\b", "evidence": [ev("src/components/Footer.jsx", "https://recuperarportugal.gov.pt/"), ev("CLONE_SPEC.md", "PRR / República Portuguesa / EU funding strip")],
         "note": "public-funding claim (PRR / Recuperar Portugal / EU strip): must never be implied in generation mode"},
        {"id": "full-service-esg-offer", "regex": r"\bfull[\s-]service esg offer\b", "evidence": [ev(CONTENT, "full-service ESG offer")]},
    ]

    domains, emails = [], []
    url_files = ["index.html"] + [os.path.join(dp, f).replace(SRC + os.sep, "") for dp, _, fs in os.walk(os.path.join(SRC, "src")) for f in fs if f.endswith((".js", ".jsx"))]
    for rel in sorted(url_files):
        for i, l in enumerate(read(rel), 1):
            for m in re.finditer(r"https?://([a-z0-9.-]+)", l):
                host = m.group(1).removeprefix("www.")
                if host == "w3.org" or host in {d["domain"] for d in domains}:
                    continue
                domains.append({"domain": host, "evidence": [{"cite": f"{rel}:{i}", "anchor": m.group(0)}]})
            for m in re.finditer(r"(?:mailto:)?([a-z0-9._-]+@[a-z0-9.-]+\.[a-z]+)", l):
                if m.group(1) not in {e["email"] for e in emails}:
                    emails.append({"email": m.group(1), "evidence": [{"cite": f"{rel}:{i}", "anchor": m.group(1)}]})
    domains.append({"domain": "theequatorcompany.com", "evidence": [ev("src/lib/privacyBody.js", "www.theequatorcompany.com")]})

    embeds = [
        {"id": "960b9490730a", "kind": "mailchimp-signup-form", "evidence": [ev("src/components/Cta.jsx", "https://mailchi.mp/960b9490730a/website-signup")]},
        {"id": "website-signup", "kind": "mailchimp-signup-form-slug", "evidence": [ev("src/components/Cta.jsx", "https://mailchi.mp/960b9490730a/website-signup")]},
        {"id": "DhKJrr1GrcZ6ptwT7", "kind": "google-maps-place-link", "evidence": [ev("src/components/Footer.jsx", "https://maps.app.goo.gl/DhKJrr1GrcZ6ptwT7")]},
    ]

    assets = []
    pub = os.path.join(SRC, "public")
    for dp, _, fs in os.walk(pub):
        for f in sorted(fs):
            rel = os.path.relpath(os.path.join(dp, f), SRC)
            stem = os.path.splitext(f)[0]
            if f in ("site.webmanifest",) or stem.startswith(("favicon", "apple-touch", "web-app-manifest")):
                continue
            if os.path.relpath(dp, pub).startswith(("team", "assets")):
                continue  # team files are covered by persons (employee-asset-slug); public/assets is the saved-original mirror
            assets.append({"file": "/" + os.path.relpath(os.path.join(dp, f), pub), "evidence": [{"cite": rel, "anchor": "file present in public/"}]})
    asset_stems = sorted({os.path.splitext(os.path.basename(a["file"]))[0].lower() for a in assets} - {"logo1", "logo2", "logo3", "logo4", "logo5", "logo6", "logo7", "logo8", "logo9", "slide1", "slide2", "slide3", "slide4", "slide5", "global", "footer", "difference", "curiosity", "grounded", "sustainability", "mono"} | {"navbar"})

    texts = []
    lit = re.compile(r"'([^'\n]{12,})'|\"([^\"\n]{12,})\"|`([^`\n]{12,})`|>([^<>{}\n]{12,})<")

    def is_copy(s):
        w = s.split()
        if len(w) < 5 or "${" in s:
            return False
        if any((":" in x and not x.endswith(":")) or "[" in x or "=" in x or "/" in x or x.startswith(("#", ".", "--")) for x in w):
            return False
        if sum(1 for x in w if "-" in x.strip("-")) / len(w) >= 0.4:
            return False
        return sum(1 for x in w if re.fullmatch(r"[A-Za-zÀ-ÿ’'.,!?:;()-]{2,}", x)) >= 4

    files = sorted(os.path.relpath(os.path.join(dp, f), SRC) for dp, _, fs in os.walk(os.path.join(SRC, "src")) for f in fs if f.endswith((".js", ".jsx")) and f != "privacyBody.js")
    for r in files + ["index.html"]:
        lines = read(r)
        for i, l in enumerate(lines, 1):
            if l.strip().startswith(("//", "/*", "*", "{/*")):
                continue
            for m in lit.finditer(l):
                s = next(g for g in m.groups() if g)
                if is_copy(s):
                    texts.append((r, i, s))
        whole = "\n".join(lines)
        for m in re.finditer(r">\s*([^<>{}]{12,}?)\s*<", whole):
            s = re.sub(r"\s+", " ", m.group(1)).strip()
            if "\n" in m.group(1) and is_copy(s):
                texts.append((r, whole.count("\n", 0, m.start()) + 1, s))
    pb = "src/lib/privacyBody.js"
    body = json.loads(read(pb)[1].split("export default ", 1)[1])
    for m in re.finditer(r"<(p|h2)[^>]*>(.*?)</\1>", body, re.S):
        s = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if len(s.split()) >= 5:
            texts.append((pb, 2, s))
    for i, l in enumerate(read("CLONE_SPEC.md"), 1):
        for m in re.finditer(r"[\"“]([^\"“”\n]{20,})[\"”]", l):
            if is_copy(m.group(1)):
                texts.append(("CLONE_SPEC.md", i, m.group(1)))
    hashes, per_file = set(), {}
    for r, i, s in texts:
        for sh in shingles(s, 5):
            hashes.add(hashlib.sha256(sh.encode()).hexdigest()[:16])
        pf = per_file.setdefault(r, {"file": r, "strings": 0, "firstLine": i, "lastLine": i})
        pf["strings"] += 1
        pf["firstLine"], pf["lastLine"] = min(pf["firstLine"], i), max(pf["lastLine"], i)
    return {
        "registryVersion": "1.0.0",
        "generatedBy": "extraction/build_leakage_patterns.py (verify_all.py re-runs it with --check when the source project is present)",
        "humanReviewed": False,
        "caveat": "No human has reviewed these patterns. Matching is string-based on normalised text: paraphrase, translation or text inside images evade it. A pass means 'no known Equator string found', not proof of originality.",
        "normalization": "schema/textnorm.py: NFKC; zero-width and soft-hyphen removed; Cyrillic/Greek look-alikes folded to Latin; curly quotes -> straight; dash variants -> '-'; diacritics stripped; lower-case; whitespace collapsed.",
        "brand": brand,
        "persons": persons,
        "customers": customers,
        "claims": claims,
        "domains": domains,
        "emails": emails,
        "embeds": embeds,
        "assets": {"files": assets, "distinctiveStems": asset_stems,
                   "note": "files: every real public/ file (team portraits are matched through persons); distinctiveStems: file stems matched as whole tokens in any string or asset id. Generic stems (logo1, slide1, global, footer ...) are matched only as full file names."},
        "copyShingles": {"n": 5, "hash": "sha256 hex[:16] of the space-joined normalised 5-word window (punctuation stripped)",
                         "sources": sorted(per_file.values(), key=lambda x: x["file"]), "count": len(hashes), "hashes": sorted(hashes)},
    }


def main(argv):
    if not os.path.isfile(os.path.join(SRC, "src", "App.jsx")):
        print("source project absent: leakage patterns not rebuilt (committed registry is used)")
        return 0
    reg = build()
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            cur = json.load(f)
        if cur != reg:
            print(f"DRIFT: schema/leakage-patterns.json differs from a fresh build in {[k for k in reg if cur.get(k) != reg[k]]}")
            return 1
        print("leakage patterns up to date")
        return 0
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"wrote schema/leakage-patterns.json: {len(reg['brand'])} brand, {len(reg['persons'])} persons, {len(reg['customers'])} customers, "
          f"{len(reg['claims'])} claims, {len(reg['domains'])} domains, {len(reg['embeds'])} embeds, {len(reg['assets']['files'])} asset files, {reg['copyShingles']['count']} shingles")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
