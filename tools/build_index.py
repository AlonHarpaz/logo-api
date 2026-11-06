#!/usr/bin/env python3
"""Build index.json (domain and ticker -> logos/<file>.svg) for files in logos/.

Usage: python3 tools/build_index.py <catalog index.json> [logos dir] [out]

The catalog file is a list of entries with domain, files, origin and optional
ticker. Only entries whose file already exists in logos/ are written; anything
else is left out. Stdlib only.
"""
import json, os, sys

def main():
    cat = sys.argv[1]
    logos = sys.argv[2] if len(sys.argv) > 2 else "logos"
    out = sys.argv[3] if len(sys.argv) > 3 else "index.json"
    have = set(os.listdir(logos))
    domains, tickers = {}, {}
    for e in json.load(open(cat)):
        if e.get("origin") != "gilbarbara":
            continue  # same file name in another source can be a different drawing
        f = e.get("files", {})
        name = f.get("icon") or f.get("wordmark")
        if name not in have or not e.get("domain"):
            continue
        domains.setdefault(e["domain"].lower(), "logos/" + name)
        t = e.get("ticker")
        if t:
            tickers.setdefault(str(t).upper(), "logos/" + name)
    data = {"domains": dict(sorted(domains.items())), "tickers": dict(sorted(tickers.items()))}
    with open(out, "w") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(len(domains), "domains,", len(tickers), "tickers")

main()
