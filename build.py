#!/usr/bin/env python3
"""Build a static domain -> logo index from gilbarbara/logos and simple-icons. Stdlib only."""
import copy
import json
import os
import re
import shutil
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
import urllib.request
from urllib.parse import urlparse

# Upstream pinned to a commit of gilbarbara/logos. See README for how to bump.
UPSTREAM_SHA = "dafdf2df1334b2327497bfff40111aff0713c992"
RAW = "https://raw.githubusercontent.com/gilbarbara/logos/" + UPSTREAM_SHA + "/"
LOGOS_JSON = RAW + "logos.json"
SVG_BASE = RAW + "logos/"
# Second source, pinned to a commit of simple-icons/simple-icons. gilbarbara wins on conflict.
SI_SHA = "c71c69e3a27e4436936b831c72643e6513b9f49b"
SI_RAW = "https://raw.githubusercontent.com/simple-icons/simple-icons/" + SI_SHA + "/"
SI_JSON = SI_RAW + "data/simple-icons.json"
SI_SLUGS = SI_RAW + "slugs.md"
SI_ICONS = SI_RAW + "icons/"
# A simple-icons source URL on one of these hosts (or a subdomain) says nothing about the brand's domain.
CODE_WIKI_HOSTS = frozenset([
    "github.com", "githubusercontent.com", "github.io", "gitlab.com", "gitlab.io", "codeberg.org",
    "sourceforge.net", "sourceforge.io", "bitbucket.org", "wikimedia.org", "wikipedia.org",
    "wikidata.org", "npmjs.com", "pypi.org", "crates.io", "rubygems.org", "packagist.org",
    "archive.org", "gitea.com", "sr.ht",
])
HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")
SLUG_ROW = re.compile(r"^\|\s*`(.+?)`\s*\|\s*`([^`]+)`\s*\|\s*$")
SAFE_FILE = re.compile(r"^[A-Za-z0-9._-]+\.svg$")
SAFE_DOMAIN = re.compile(r"^[a-z0-9.-]+$")
RETRIES = 3
ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_ROOT = os.environ.get("LOGOAPI_CACHE") or os.path.join(ROOT, "cache")
CACHE = os.path.join(CACHE_ROOT, UPSTREAM_SHA[:12])
SI_CACHE = os.path.join(CACHE_ROOT, "si-" + SI_SHA[:12])
WORKERS = 8
DIST = os.path.join(ROOT, "dist")
DIST_TMP = os.path.join(ROOT, "dist.tmp")
BLOCKLIST = os.path.join(ROOT, "blocklist.txt")
DELAY = 0.05
EXTRAS = os.path.join(ROOT, "extras")
NAME_OVERRIDES = {"vercel.com": "Vercel", "openai.com": "OpenAI", "sencha.com": "Sencha", "apache.org": "Apache"}
# Domains where the gilbarbara logo is wrong; the simple-icons candidate wins instead.
PREFER_SIMPLE_ICONS = {"elastic.co"}
# alias domain -> target domain whose entry and SVGs it copies.
DOMAIN_ALIASES = {
    "ionic.io": "ionicframework.com",
    "amazon.co.uk": "amazon.com",
    "aboutamazon.com": "amazon.com",
    "woocommerce.com": "woothemes.com",
    "woo.com": "woothemes.com",
}
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


def _root_match(text):
    for cand in ROOT_SVG.finditer(text):
        if not any(c.start() < cand.start() < c.end() for c in COMMENT.finditer(text)):
            return cand
    return None


def inject_fill(data, hexcolor):
    """Set fill="#<hex>" on the root <svg> tag (replacing any existing root fill). bytes -> bytes."""
    text = data.decode("utf-8")
    m = _root_match(text)
    if not m or not HEX_RE.match(hexcolor or ""):
        return data
    tag = re.sub(r"\s+fill\s*=\s*(?:\"[^\"]*\"|'[^']*')", "", m.group(0), flags=re.I)
    end = "/>" if tag.endswith("/>") else ">"
    tag = tag[:-len(end)].rstrip() + ' fill="#%s"' % hexcolor.upper() + end
    return (text[:m.start()] + tag + text[m.end():]).encode("utf-8")


def normalize_svg(data):
    """Strip width/height from the root <svg> tag; keep or synthesize viewBox. bytes -> bytes."""
    text = data.decode("utf-8")
    m = _root_match(text)
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
    """Set curated names. Extras entries keep their own name from SOURCES.md."""
    overrides = NAME_OVERRIDES if overrides is None else overrides
    for e in entries:
        if e.get("origin") != "extras" and e["domain"] in overrides:
            e["name"] = overrides[e["domain"]]
    return entries


def drop_preferred_si(entries, prefer=None):
    """Drop gilbarbara entries for domains that should use simple-icons."""
    prefer = PREFER_SIMPLE_ICONS if prefer is None else prefer
    return [e for e in entries if e["domain"] not in prefer]


def missing_preferred(si_entries, prefer=None):
    """Sorted PREFER_SIMPLE_ICONS domains that simple-icons did not produce."""
    prefer = PREFER_SIMPLE_ICONS if prefer is None else prefer
    return sorted(prefer - {e["domain"] for e in si_entries})


def apply_aliases(index, dist_dir, aliases=None):
    """Make each alias domain a copy of its target's entry and SVGs."""
    aliases = DOMAIN_ALIASES if aliases is None else aliases
    by = {e["domain"]: e for e in index}
    for alias, target in aliases.items():
        t = by.get(target)
        if t is None:
            print("warning: alias %s skipped, target %s missing" % (alias, target))
            continue
        index[:] = [e for e in index if e["domain"] != alias]
        new = copy.deepcopy(t)
        new["domain"] = alias
        index.append(new)
        for sub in ("", "icon"):
            src = os.path.join(dist_dir, sub, target + ".svg")
            dst = os.path.join(dist_dir, sub, alias + ".svg")
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copyfile(src, dst)
    index.sort(key=lambda e: e["domain"])
    return index


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


def alnum(text):
    """Lowercase, alphanumerics only."""
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def pick_root(dom, cands):
    """Pick the item that best names the domain, exact matches only. cands keep input order.

    The shortname or slugified name equals the first label (google.com -> google) or the
    labels reversed without the TLD (cloud.google.com -> googlecloud); else the first.
    """
    labels = dom.split(".")[:-1] or dom.split(".")
    wanted = {alnum(labels[0]), alnum("".join(reversed(labels)))} - {""}
    for it in cands:
        if wanted & {alnum(it.get("shortname")), alnum(it.get("name"))}:
            return it
    return cands[0]


def build_entries(items, blocked):
    """Return (entries, skipped_blocked, duplicates, no_domain). Deterministic.

    When several items share a domain, the one named after the domain's first label wins
    (see pick_root); otherwise the first in input order.
    """
    groups, order = {}, []
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
        if pick_files(files)[0] is None:
            nodom.append(it.get("name"))
            continue
        if dom not in groups:
            groups[dom] = []
            order.append(dom)
        groups[dom].append(it)
    entries = []
    for dom in order:
        cands = groups[dom]
        it = pick_root(dom, cands)
        for other in cands:
            if other is not it:
                dups.append((dom, other.get("name")))
        word, icon = pick_files(it["files"])
        entries.append({
            "domain": dom,
            "name": it.get("name"),
            "slug": it.get("shortname"),
            "files": {"wordmark": word, "icon": icon},
            "source": it.get("url"),
            "origin": "gilbarbara",
        })
    entries.sort(key=lambda e: e["domain"])
    return entries, skipped, dups, nodom


def is_code_host(host):
    """True for code, package and wiki hosts (and their subdomains)."""
    return any(host == h or host.endswith("." + h) for h in CODE_WIKI_HOSTS)


def parse_slugs(text):
    """Map brand title -> ordered list of slugs from the simple-icons slugs.md table."""
    out = {}
    for line in text.splitlines():
        m = SLUG_ROW.match(line)
        if m:
            out.setdefault(m.group(1).replace("\\|", "|"), []).append(m.group(2))
    return out


def si_slug(item, slugs, explicit=frozenset()):
    """Explicit slug, else the one table slug for the title that no item claims explicitly."""
    if item.get("slug"):
        return item["slug"]
    left = [s for s in slugs.get(item.get("title"), []) if s not in explicit]
    return left[0] if len(left) == 1 else None


def build_si_entries(items, slugs, blocked, taken, prefer=None):
    """Return (entries, stats) for simple-icons. `taken` = domains already served (gilbarbara wins).

    Drops code/wiki hosts, hosts shared by several icons, custom licenses, blocklisted
    and conflicting domains, and icons without a usable slug or hex. Sorted by domain.
    For domains in `prefer` (PREFER_SIMPLE_ICONS) a shared host is resolved with pick_root.
    """
    prefer = PREFER_SIMPLE_ICONS if prefer is None else prefer
    stats = {"no_domain": 0, "code_host": 0, "ambiguous": 0, "custom_license": 0,
             "blocked": 0, "conflict": 0, "invalid": 0}
    explicit = {it["slug"] for it in items if it.get("slug")}
    cands = []
    for it in items:
        dom = domain_from_url(it.get("source", ""))
        if not dom or not valid_domain(dom):
            stats["no_domain"] += 1
        elif is_code_host(dom):
            stats["code_host"] += 1
        else:
            cands.append((dom, it))
    for dom in prefer:
        group = [it for d, it in cands if d == dom]
        if len(group) > 1:
            root = pick_root(dom, [{"name": it.get("title"), "shortname": it.get("slug"), "_it": it} for it in group])["_it"]
            cands = [(d, it) for d, it in cands if d != dom or it is root]
    counts = {}
    for dom, _ in cands:
        counts[dom] = counts.get(dom, 0) + 1
    entries = []
    for dom, it in cands:
        lic = (it.get("license") or {}).get("type")
        slug = si_slug(it, slugs, explicit)
        if counts[dom] > 1:
            stats["ambiguous"] += 1
        elif lic == "custom":
            stats["custom_license"] += 1
        elif dom in blocked:
            stats["blocked"] += 1
        elif dom in taken:
            stats["conflict"] += 1
        elif not slug or not safe_filename(slug + ".svg") or not HEX_RE.match(it.get("hex") or ""):
            stats["invalid"] += 1
        else:
            e = {
                "domain": dom,
                "name": it.get("title"),
                "slug": slug,
                "files": {"wordmark": slug + ".svg", "icon": slug + ".svg"},
                "source": it.get("source"),
                "origin": "simple-icons",
                "hex": it["hex"].upper(),
            }
            if lic:
                e["license"] = lic
            entries.append(e)
    entries.sort(key=lambda e: e["domain"])
    return entries, stats


def extras_domain(fname):
    """('example.com', 'wordmark'|'icon') for extras file names, else None."""
    if not safe_filename(fname):
        return None
    stem = fname[:-4]
    kind = "wordmark"
    if stem.endswith("-icon"):
        stem, kind = stem[:-5], "icon"
    dom = normalize_domain(stem)
    if dom != stem or not valid_domain(dom):
        return None
    return dom, kind


def load_extras_names(path):
    """Map domain -> brand name from the Name column (2nd) of the extras/SOURCES.md table."""
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
            if len(cells) >= 2 and cells[1] and cells[0] not in ("Domain", "---") and valid_domain(cells[0]):
                out[cells[0]] = cells[1]
    return out


def build_extras_entries(names, blocked, brand_names=None):
    """Return (entries, skipped). `names` = file names found in extras/.

    Curated: these win over both upstreams. Same safe-name, domain and blocklist
    checks as upstream. A missing wordmark or icon falls back to the other one.
    """
    brand_names = brand_names or {}
    found, skipped = {}, []
    for fname in sorted(names):
        if not fname.endswith(".svg"):
            continue
        parsed = extras_domain(fname)
        if parsed is None:
            print("unsafe extras filename skipped: %r" % fname)
            skipped.append(fname)
            continue
        dom, kind = parsed
        if dom in blocked:
            skipped.append(fname)
            continue
        found.setdefault(dom, {})[kind] = fname
    entries = []
    for dom in sorted(found):
        word, icon = pick_files(
            [f for f in (found[dom].get("wordmark"), found[dom].get("icon")) if f])
        entries.append({
            "domain": dom,
            "name": brand_names.get(dom) or dom.split(".")[0].title(),
            "slug": dom,
            "files": {"wordmark": word, "icon": icon},
            "source": "https://github.com/AlonHarpaz/logo-api/blob/main/extras/SOURCES.md",
            "origin": "extras",
        })
    return entries, skipped


NAME_SUFFIXES = ("docs", "doc", "blog", "press", "brand", "branding", "wiki", "about", "help",
                 "assets", "styleguide", "handbook", "foundation")
THIRD_PARTY_HOSTS = frozenset([
    "github.io", "frontify.com", "widencollective.com", "netlify.app", "js.org", "pages.dev",
    "vercel.app", "readthedocs.io", "webflow.io", "zendesk.com", "workspaceair.com",
])


def same_brand_name(a, b):
    """Normalized names match, or one is the other plus a suffix word like docs or blog."""
    a, b = alnum(a), alnum(b)
    if not a or not b:
        return False
    if a == b:
        return True
    return any(a == b + x or b == a + x for x in NAME_SUFFIXES)


def is_third_party(host):
    return any(host == h or host.endswith("." + h) for h in THIRD_PARTY_HOSTS)


def collapse_entries(entries):
    """Return (kept, dropped). dropped = [(domain, kept_domain, reason)], sorted by domain.

    Drops a subdomain entry when a parent-domain entry has the same brand name, and a
    third-party-hosted entry when a brand-domain entry has the same name. Different-name
    subdomains (home.google.com) and sole third-party entries stay.
    """
    entries = sorted(entries, key=lambda e: e["domain"])
    doms = {e["domain"]: e for e in entries}
    dropped = {}
    for e in entries:
        d = e["domain"]
        if e.get("origin") == "extras":
            continue
        parts = d.split(".")
        for i in range(1, len(parts) - 1):
            parent = ".".join(parts[i:])
            p = doms.get(parent)
            if p is not None and same_brand_name(e.get("name"), p.get("name")):
                dropped[d] = (parent, "subdomain")
                break
    for e in entries:
        d = e["domain"]
        if d in dropped or e.get("origin") == "extras" or not is_third_party(d):
            continue
        for p in entries:
            pd = p["domain"]
            if pd != d and not is_third_party(pd) and pd not in dropped \
                    and alnum(p.get("name")) == alnum(e.get("name")):
                dropped[d] = (pd, "third-party host")
                break
    kept = [e for e in entries if e["domain"] not in dropped]
    return kept, sorted((d, v[0], v[1]) for d, v in dropped.items())


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


def cached(fname, base=None, cache_dir=None):
    """Return path of cached file, downloading if missing or empty. None on failure."""
    base = SVG_BASE if base is None else base
    cache_dir = CACHE if cache_dir is None else cache_dir
    if not safe_filename(fname):
        return None
    path = os.path.join(cache_dir, fname)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    try:
        data = fetch(base + fname)
        if not data:
            raise ValueError("empty download")
    except Exception as e:
        print("download failed: %s (%s)" % (fname, e), file=sys.stderr)
        return None
    os.makedirs(cache_dir, exist_ok=True)
    fd, part = tempfile.mkstemp(dir=cache_dir, prefix=fname + ".", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(part, path)
    except BaseException:
        try:
            os.remove(part)
        except OSError:
            pass
        raise
    time.sleep(DELAY)
    return path


def prefetch(jobs, workers=WORKERS):
    """Download missing files in parallel. jobs: (fname, base, cache_dir) tuples; duplicates are dropped."""
    unique = list(dict.fromkeys(jobs))
    if not unique:
        return 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(lambda j: cached(j[0], j[1], j[2]), unique))
    return len(unique)


def main():
    items = json.loads(fetch(LOGOS_JSON).decode("utf-8"))
    entries, skipped, dups, nodom = build_entries(items, load_blocklist(BLOCKLIST))
    entries = drop_preferred_si(entries)
    for dom, name in dups:
        print("duplicate domain %s ignored: %s" % (dom, name))
    blocked = load_blocklist(BLOCKLIST)
    si_items = json.loads(fetch(SI_JSON).decode("utf-8"))
    slugs = parse_slugs(fetch(SI_SLUGS).decode("utf-8"))
    si_entries, si_stats = build_si_entries(si_items, slugs, blocked, {e["domain"] for e in entries})
    lost = missing_preferred(si_entries)
    if lost:
        print("error: no simple-icons entry for preferred domain(s): " + ", ".join(lost), file=sys.stderr)
        print("build failed, dist/ left untouched", file=sys.stderr)
        sys.exit(1)
    extras_names = sorted(os.listdir(EXTRAS)) if os.path.isdir(EXTRAS) else []
    ex_entries, ex_skipped = build_extras_entries(extras_names, blocked, load_extras_names(os.path.join(EXTRAS, "SOURCES.md")))
    won = {e["domain"] for e in ex_entries}
    entries = [e for e in entries if e["domain"] not in won]
    si_entries = [e for e in si_entries if e["domain"] not in won]
    _, dropped = collapse_entries(entries + si_entries + ex_entries)
    for d, keep, why in dropped:
        print("collapsed %s into %s (%s)" % (d, keep, why))
    print("collapsed: %d" % len(dropped))
    gone = {d for d, _, _ in dropped}
    entries = [e for e in entries if e["domain"] not in gone]
    si_entries = [e for e in si_entries if e["domain"] not in gone]
    ex_entries = [e for e in ex_entries if e["domain"] not in gone]
    shutil.rmtree(DIST_TMP, ignore_errors=True)
    os.makedirs(os.path.join(DIST_TMP, "icon"))
    jobs = []
    for e in entries:
        jobs.append((e["files"]["wordmark"], SVG_BASE, CACHE))
        jobs.append((e["files"]["icon"], SVG_BASE, CACHE))
    for e in si_entries:
        jobs.append((e["files"]["icon"], SI_ICONS, SI_CACHE))
    print("prefetch: %d files" % prefetch(jobs))
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
    si_written = 0
    for e in si_entries:
        p = cached(e["files"]["icon"], SI_ICONS, SI_CACHE)
        if p is None:
            failures += 1
            continue
        with open(p, "rb") as f:
            data = inject_fill(normalize_svg(f.read()), e["hex"])
        for dst in (os.path.join(DIST_TMP, e["domain"] + ".svg"),
                    os.path.join(DIST_TMP, "icon", e["domain"] + ".svg")):
            with open(dst, "wb") as f:
                f.write(data)
        index.append(e)
        si_written += 1
    ex_written = 0
    for e in ex_entries:
        w = os.path.join(EXTRAS, e["files"]["wordmark"])
        i = os.path.join(EXTRAS, e["files"]["icon"])
        for src, dst in ((w, os.path.join(DIST_TMP, e["domain"] + ".svg")),
                         (i, os.path.join(DIST_TMP, "icon", e["domain"] + ".svg"))):
            with open(src, "rb") as f:
                raw = f.read()
            with open(dst, "wb") as f:
                f.write(normalize_svg(raw))
        index.append(e)
        ex_written += 1
    index.sort(key=lambda e: e["domain"])
    apply_overrides(index)
    apply_aliases(index, DIST_TMP)
    print("extras domains written: %d (skipped %d)" % (ex_written, len(ex_skipped)))
    print("domains written: %d" % written)
    print("simple-icons domains written: %d" % si_written)
    print("simple-icons skipped: " + ", ".join("%s %d" % (k, v) for k, v in sorted(si_stats.items())))
    print("skipped (blocklist): %d" % len(skipped))
    print("skipped (invalid/no domain/files): %d" % len(nodom))
    print("duplicates ignored: %d" % len(dups))
    print("download failures: %d" % failures)
    if failures:
        shutil.rmtree(DIST_TMP, ignore_errors=True)
        print("build failed, dist/ left untouched", file=sys.stderr)
        sys.exit(1)
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
