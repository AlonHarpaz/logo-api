#!/usr/bin/env python3
"""Build a static domain -> logo index from gilbarbara/logos. Stdlib only."""
import json
import os
import re
import shutil
import sys
import time
import urllib.request
from urllib.parse import urlparse

# Upstream pinned to a commit of gilbarbara/logos. See README for how to bump.
UPSTREAM_SHA = "dafdf2df1334b2327497bfff40111aff0713c992"
RAW = "https://raw.githubusercontent.com/gilbarbara/logos/" + UPSTREAM_SHA + "/"
LOGOS_JSON = RAW + "logos.json"
SVG_BASE = RAW + "logos/"
SAFE_FILE = re.compile(r"^[A-Za-z0-9._-]+\.svg$")
SAFE_DOMAIN = re.compile(r"^[a-z0-9.-]+$")
RETRIES = 3
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "cache", UPSTREAM_SHA[:12])
DIST = os.path.join(ROOT, "dist")
DIST_TMP = os.path.join(ROOT, "dist.tmp")
BLOCKLIST = os.path.join(ROOT, "blocklist.txt")
DELAY = 0.05
NAME_OVERRIDES = {"vercel.com": "Vercel", "openai.com": "OpenAI"}
ROOT_SVG = re.compile(r"<svg\b[^>]*>", re.I | re.S)
COMMENT = re.compile(r"<!--.*?(?:-->|\Z)", re.S)
ATTR = r"""(?:\s|^)%s\s*=\s*(?:"([^"]*)"|'([^']*)')"""


def normalize_domain(host):
    """Lowercase, strip trailing dot and leading www."""
    host = (host or "").strip().lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def valid_domain(dom):
    return bool(SAFE_DOMAIN.match(dom)) and not dom.startswith(".") and ".." not in dom


def safe_filename(name):
    return isinstance(name, str) and bool(SAFE_FILE.match(name)) and name not in (".svg", "..svg")


def domain_from_url(url):
    """Normalized hostname of url, or empty string if none or unparsable."""
    if not url or not isinstance(url, str):
        return ""
    try:
        host = urlparse(url.strip()).hostname or ""
    except ValueError:
        return ""
    return normalize_domain(host)


def _attr(tag, name):
    m = re.search(ATTR % name, tag, re.I)
    return (m.group(1) if m.group(1) is not None else m.group(2)) if m else None


def normalize_svg(data):
    """Strip width/height from the root <svg> tag; keep or synthesize viewBox. bytes -> bytes."""
    text = data.decode("utf-8")
    m = None
    for cand in ROOT_SVG.finditer(text):
        if not any(c.start() < cand.start() < c.end() for c in COMMENT.finditer(text)):
            m = cand
            break
    if not m:
        return data
    tag = m.group(0)
    new = tag
    if _attr(tag, "viewBox") is None:
        nums = []
        for k in ("width", "height"):
            v = _attr(tag, k)
            mm = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*(?:px)?\s*", v or "")
            nums.append(mm.group(1) if mm else None)
        if all(nums):
            new = new[:-1].rstrip("/").rstrip() + ' viewBox="0 0 %s %s"' % tuple(nums) + ("/>" if tag.endswith("/>") else ">")
    for k in ("width", "height"):
        new = re.sub(r"\s+%s\s*=\s*(?:\"[^\"]*\"|'[^']*')" % k, "", new, flags=re.I)
    return (text[:m.start()] + new + text[m.end():]).encode("utf-8")


def apply_overrides(entries, overrides=None):
    overrides = NAME_OVERRIDES if overrides is None else overrides
    for e in entries:
        if e["domain"] in overrides:
            e["name"] = overrides[e["domain"]]
    return entries


def load_blocklist(path):
    out = set()
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                out.add(normalize_domain(line))
    return out


def pick_files(files):
    """Return (wordmark, icon). Wordmark: first file without -icon. Icon: first -icon file, else wordmark."""
    word = next((f for f in files if "-icon" not in f), None)
    icon = next((f for f in files if "-icon" in f), None)
    if word is None:
        word = icon
    if icon is None:
        icon = word
    return word, icon


def build_entries(items, blocked):
    """Return (entries, skipped_blocked, duplicates, no_domain). Deterministic: input order, first wins."""
    entries, seen = [], set()
    skipped, dups, nodom = [], [], []
    for it in items:
        dom = domain_from_url(it.get("url", ""))
        files = it.get("files")
        if not dom or not files or not isinstance(files, list):
            nodom.append(it.get("name"))
            continue
        if not valid_domain(dom):
            print("invalid domain skipped: %r (%s)" % (dom, it.get("name")))
            nodom.append(it.get("name"))
            continue
        bad = [f for f in files if not safe_filename(f)]
        if bad:
            print("unsafe filename skipped: %r (%s)" % (bad, it.get("name")))
            nodom.append(it.get("name"))
            continue
        if dom in blocked:
            skipped.append(dom)
            continue
        if dom in seen:
            dups.append((dom, it.get("name")))
            continue
        word, icon = pick_files(it["files"])
        if word is None:
            nodom.append(it.get("name"))
            continue
        seen.add(dom)
        entries.append({
            "domain": dom,
            "name": it.get("name"),
            "slug": it.get("shortname"),
            "files": {"wordmark": word, "icon": icon},
            "source": it.get("url"),
        })
    entries.sort(key=lambda e: e["domain"])
    return entries, skipped, dups, nodom


def fetch(url):
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "logo-api-build/0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(0.5 * (2 ** attempt))
    raise last


def cached(fname):
    """Return path of cached file, downloading if missing or empty. None on failure."""
    if not safe_filename(fname):
        return None
    path = os.path.join(CACHE, fname)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    try:
        data = fetch(SVG_BASE + fname)
        if not data:
            raise ValueError("empty download")
    except Exception as e:
        print("download failed: %s (%s)" % (fname, e), file=sys.stderr)
        return None
    os.makedirs(CACHE, exist_ok=True)
    part = path + ".part"
    with open(part, "wb") as f:
        f.write(data)
    os.replace(part, path)
    time.sleep(DELAY)
    return path


def main():
    items = json.loads(fetch(LOGOS_JSON).decode("utf-8"))
    entries, skipped, dups, nodom = build_entries(items, load_blocklist(BLOCKLIST))
    for dom, name in dups:
        print("duplicate domain %s ignored: %s" % (dom, name))
    shutil.rmtree(DIST_TMP, ignore_errors=True)
    os.makedirs(os.path.join(DIST_TMP, "icon"))
    written, failures, index = 0, 0, []
    for e in entries:
        w = cached(e["files"]["wordmark"])
        i = w if e["files"]["icon"] == e["files"]["wordmark"] else cached(e["files"]["icon"])
        if w is None or i is None:
            failures += 1
            continue
        for src, dst in ((w, os.path.join(DIST_TMP, e["domain"] + ".svg")),
                         (i, os.path.join(DIST_TMP, "icon", e["domain"] + ".svg"))):
            with open(src, "rb") as f:
                raw = f.read()
            with open(dst, "wb") as f:
                f.write(normalize_svg(raw))
        index.append(e)
        written += 1
    print("domains written: %d" % written)
    print("skipped (blocklist): %d" % len(skipped))
    print("skipped (invalid/no domain/files): %d" % len(nodom))
    print("duplicates ignored: %d" % len(dups))
    print("download failures: %d" % failures)
    if failures:
        shutil.rmtree(DIST_TMP, ignore_errors=True)
        print("build failed, dist/ left untouched", file=sys.stderr)
        sys.exit(1)
    apply_overrides(index)
    with open(os.path.join(DIST_TMP, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    old = DIST + ".old"
    shutil.rmtree(old, ignore_errors=True)
    if os.path.exists(DIST):
        os.rename(DIST, old)
    os.rename(DIST_TMP, DIST)
    shutil.rmtree(old, ignore_errors=True)


if __name__ == "__main__":
    main()
