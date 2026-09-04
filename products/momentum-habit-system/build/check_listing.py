#!/usr/bin/env python3
"""Validates etsy/listing.md against Etsy's field limits, so a listing is
never rejected at paste time."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(os.path.dirname(HERE), "etsy", "listing.md")
LIMITS = dict(title=140, tag=20, tags=13, description=102400)

def main():
    text = open(MD, encoding="utf-8").read()
    fails = []

    title = re.search(r"## 1\. Title.*?```\n(.*?)\n```", text, re.S)
    title = title.group(1).strip() if title else ""
    print("TITLE  %3d/%d chars" % (len(title), LIMITS["title"]))
    print("       %s" % title)
    if not title:
        fails.append("title not found")
    elif len(title) > LIMITS["title"]:
        fails.append("title is %d chars, %d over the limit"
                     % (len(title), len(title) - LIMITS["title"]))

    desc = re.search(r"## 2\. Description.*?```\n(.*?)\n```", text, re.S)
    desc = desc.group(1) if desc else ""
    print("\nDESC   %d chars, %d lines" % (len(desc), len(desc.splitlines())))
    if len(desc) > LIMITS["description"]:
        fails.append("description over limit")
    if not desc:
        fails.append("description not found")

    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|$",
                      text, re.M)
    print("\nTAGS   %d/%d" % (len(rows), LIMITS["tags"]))
    if len(rows) != LIMITS["tags"]:
        fails.append("expected %d tags, found %d" % (LIMITS["tags"], len(rows)))
    seen = set()
    for n, tag, claimed in rows:
        real = len(tag)
        flag = ""
        if real > LIMITS["tag"]:
            flag = "  <-- %d OVER LIMIT" % (real - LIMITS["tag"])
            fails.append("tag %r is %d chars" % (tag, real))
        if int(claimed) != real:
            flag += "  <-- table says %s, actually %d" % (claimed, real)
            fails.append("tag %r count wrong in table" % tag)
        if tag.lower() in seen:
            flag += "  <-- DUPLICATE"
            fails.append("duplicate tag %r" % tag)
        seen.add(tag.lower())
        if tag != tag.lower():
            fails.append("tag %r should be lowercase" % tag)
        print("  %2s  %-22s %2d%s" % (n, tag, real, flag))

    # the three shipped files must actually exist with the promised names
    dist = os.path.join(os.path.dirname(HERE), "dist")
    promised = re.findall(r"^• (Momentum-[\w.\-]+)", desc, re.M)
    print("\nFILES  %d promised in the description" % len(promised))
    for f in promised:
        ok = os.path.exists(os.path.join(dist, f))
        print("  %-42s %s" % (f, "found" if ok else "MISSING"))
        if not ok:
            fails.append("description promises %s, which is not in dist/" % f)

    print()
    if fails:
        for f in fails:
            print("FAIL: %s" % f)
        return 1
    print("listing pack is within every Etsy limit")
    return 0

if __name__ == "__main__":
    sys.exit(main())
