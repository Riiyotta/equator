#!/usr/bin/env python3
"""Content hash of the files the design policy is enforced by (registry.manifest.json designPolicy.contentHash).

    python3 extraction/policy_hash.py           # print the hash
    python3 extraction/policy_hash.py --write   # store it in registry.manifest.json

hash = sha256 over, for each file in policy/design-policy.json `enforcedBy` (sorted): "<relpath>\\n" + bytes + "\\n".
verify_all.py (check `design_policy`) recomputes it and fails on mismatch, so changing any enforcing file
(validator, schema, roles, leakage patterns, graph, token policy/catalog, the policy itself) without re-binding is caught.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def compute(root=ROOT):
    with open(os.path.join(root, "policy", "design-policy.json"), encoding="utf-8") as f:
        pol = json.load(f)
    h = hashlib.sha256()
    for rel in sorted(pol["enforcedBy"]):
        h.update(rel.encode() + b"\n")
        with open(os.path.join(root, rel), "rb") as f:
            h.update(f.read())
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


def main(argv):
    value = compute()
    if "--write" in argv:
        p = os.path.join(ROOT, "registry.manifest.json")
        with open(p, encoding="utf-8") as f:
            m = json.load(f)
        m["designPolicy"]["contentHash"] = value
        with open(p, "w", encoding="utf-8") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
