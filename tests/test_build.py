import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import build


class DomainTests(unittest.TestCase):
    def test_strips_www_and_path(self):
        self.assertEqual(build.domain_from_url("https://www.Example.com/a/b"), "example.com")

    def test_keeps_subdomain(self):
        self.assertEqual(build.domain_from_url("https://docs.example.com/"), "docs.example.com")

    def test_empty(self):
        self.assertEqual(build.domain_from_url(""), "")
        self.assertEqual(build.domain_from_url(None), "")


class BlocklistTests(unittest.TestCase):
    def test_load_ignores_comments(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("# header\nFoo.com\n\nwww.bar.com # note\n")
        try:
            self.assertEqual(build.load_blocklist(f.name), {"foo.com", "bar.com"})
        finally:
            os.unlink(f.name)

    def test_missing_file(self):
        self.assertEqual(build.load_blocklist("/nonexistent/x.txt"), set())

    def test_blocked_skipped(self):
        items = [{"name": "A", "shortname": "a", "url": "https://a.com", "files": ["a.svg"]}]
        entries, skipped, _, _ = build.build_entries(items, {"a.com"})
        self.assertEqual(entries, [])
        self.assertEqual(skipped, ["a.com"])


class PickTests(unittest.TestCase):
    def test_both(self):
        self.assertEqual(build.pick_files(["a-icon.svg", "a.svg", "a-icon-2.svg"]), ("a.svg", "a-icon.svg"))

    def test_no_icon(self):
        self.assertEqual(build.pick_files(["a.svg", "a-b.svg"]), ("a.svg", "a.svg"))

    def test_only_icon(self):
        self.assertEqual(build.pick_files(["a-icon.svg"]), ("a-icon.svg", "a-icon.svg"))


class DuplicateTests(unittest.TestCase):
    def test_first_wins(self):
        items = [
            {"name": "One", "shortname": "one", "url": "https://www.x.com", "files": ["one.svg"]},
            {"name": "Two", "shortname": "two", "url": "https://x.com/y", "files": ["two.svg"]},
        ]
        entries, _, dups, _ = build.build_entries(items, set())
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "One")
        self.assertEqual(dups, [("x.com", "Two")])

    def test_deterministic_sorted(self):
        items = [
            {"name": "B", "shortname": "b", "url": "https://b.com", "files": ["b.svg"]},
            {"name": "A", "shortname": "a", "url": "https://a.com", "files": ["a.svg"]},
        ]
        e1 = build.build_entries(items, set())[0]
        e2 = build.build_entries(list(reversed(items)), set())[0]
        self.assertEqual(e1, e2)
        self.assertEqual([e["domain"] for e in e1], ["a.com", "b.com"])


class SafetyTests(unittest.TestCase):
    def test_safe_filename(self):
        for ok in ["a.svg", "a-icon.svg", "A_b.1.svg"]:
            self.assertTrue(build.safe_filename(ok), ok)
        for bad in ["../a.svg", "a/b.svg", "a.png", "", "/etc/x.svg", "a b.svg", "..\\a.svg", None]:
            self.assertFalse(build.safe_filename(bad), bad)

    def test_unsafe_file_entry_skipped(self):
        items = [{"name": "E", "shortname": "e", "url": "https://e.com", "files": ["../x.svg"]},
                 {"name": "F", "shortname": "f", "url": "https://f.com", "files": ["f.svg"]}]
        entries, _, _, nodom = build.build_entries(items, set())
        self.assertEqual([e["domain"] for e in entries], ["f.com"])
        self.assertEqual(nodom, ["E"])

    def test_valid_domain(self):
        self.assertTrue(build.valid_domain("a-b.example.com"))
        for bad in [".a.com", "a..com", "a_b.com", "a/b.com", "a b.com"]:
            self.assertFalse(build.valid_domain(bad), bad)

    def test_malformed_bracket_host_no_abort(self):
        self.assertEqual(build.domain_from_url("http://[bad"), "")
        items = [{"name": "X", "shortname": "x", "url": "http://[bad", "files": ["x.svg"]}]
        entries, _, _, nodom = build.build_entries(items, set())
        self.assertEqual(entries, [])
        self.assertEqual(nodom, ["X"])

    def test_invalid_domain_entry_skipped(self):
        items = [{"name": "U", "shortname": "u", "url": "https://a_b.com", "files": ["u.svg"]}]
        self.assertEqual(build.build_entries(items, set())[0], [])


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.old = (build.CACHE, build.fetch, build.DELAY)
        build.CACHE = self.tmp
        build.DELAY = 0

    def tearDown(self):
        build.CACHE, build.fetch, build.DELAY = self.old
        import shutil
        shutil.rmtree(self.tmp)

    def test_empty_cache_file_redownloaded(self):
        open(os.path.join(self.tmp, "a.svg"), "w").close()
        build.fetch = lambda url: b"<svg/>"
        p = build.cached("a.svg")
        self.assertEqual(open(p, "rb").read(), b"<svg/>")
        self.assertFalse(os.path.exists(p + ".part"))

    def test_good_cache_used(self):
        with open(os.path.join(self.tmp, "a.svg"), "wb") as f:
            f.write(b"x")
        def boom(url):
            raise AssertionError("should not fetch")
        build.fetch = boom
        self.assertIsNotNone(build.cached("a.svg"))

    def test_failure_leaves_no_file(self):
        def boom(url):
            raise OSError("down")
        build.fetch = boom
        self.assertIsNone(build.cached("a.svg"))
        self.assertEqual(os.listdir(self.tmp), [])

    def test_empty_download_not_cached(self):
        build.fetch = lambda url: b""
        self.assertIsNone(build.cached("a.svg"))
        self.assertEqual(os.listdir(self.tmp), [])


class BlocklistNormTests(unittest.TestCase):
    def test_normalized(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("WWW.Foo.COM.\nBar.com.\n")
        try:
            self.assertEqual(build.load_blocklist(f.name), {"foo.com", "bar.com"})
        finally:
            os.unlink(f.name)


class NormalizeTests(unittest.TestCase):
    def n(self, s):
        return build.normalize_svg(s.encode()).decode()

    def test_strips_size_keeps_viewbox(self):
        out = self.n('<?xml version="1.0"?><svg xmlns="x" width="100" height="50px" viewBox="0 0 10 5"><rect width="3" height="4"/></svg>')
        self.assertIn('<svg xmlns="x" viewBox="0 0 10 5">', out)
        self.assertIn('<rect width="3" height="4"/>', out)

    def test_adds_viewbox(self):
        out = self.n("<svg width='24' height='12.5' xmlns='x'><path/></svg>")
        self.assertIn('viewBox="0 0 24 12.5"', out)
        self.assertNotIn("width='24'", out)

    def test_no_size_no_viewbox_untouched(self):
        s = '<svg xmlns="x"><g/></svg>'
        self.assertEqual(self.n(s), s)

    def test_percent_size_not_viewbox(self):
        out = self.n('<svg width="100%" height="100%"><g/></svg>')
        self.assertNotIn("viewBox", out)
        self.assertNotIn("width=", out.split(">")[0])

    def test_skips_svg_in_comment(self):
        out = self.n('<!-- <svg width="1" height="1"> --><svg width="9" height="9" viewBox="0 0 9 9"><g/></svg>')
        self.assertIn('<svg width="1" height="1">', out)
        self.assertIn('<svg viewBox="0 0 9 9">', out)

    def test_multiline_tag(self):
        out = self.n('<svg\n  width="10"\n  height="10"\n  viewBox="0 0 10 10">\n<g/></svg>')
        self.assertNotIn("width=", out.split("<g")[0])
        self.assertIn('viewBox="0 0 10 10"', out)


class OverrideTests(unittest.TestCase):
    def test_names(self):
        es = [{"domain": "vercel.com", "name": "x"}, {"domain": "openai.com", "name": "y"}, {"domain": "a.com", "name": "A"}]
        build.apply_overrides(es)
        self.assertEqual([e["name"] for e in es], ["Vercel", "OpenAI", "A"])


class SimpleIconsTests(unittest.TestCase):
    SLUGS = {"Foo": ["foo"], "Bar": ["bar"], "Baz": ["baz"], "Dup": ["dup", "dup_two"], "Amb": ["a1", "a2"]}

    def item(self, title, source, hex="112233", **kw):
        d = {"title": title, "hex": hex, "source": source}
        d.update(kw)
        return d

    def run_si(self, items, blocked=None, taken=None):
        return build.build_si_entries(items, self.SLUGS, blocked or set(), taken or set())

    def test_code_and_wiki_hosts_dropped(self):
        hosts = ["github.com", "gitlab.com", "codeberg.org", "sourceforge.net", "bitbucket.org",
                 "commons.wikimedia.org", "en.wikipedia.org", "raw.githubusercontent.com",
                 "npmjs.com", "pypi.org", "foo.github.io"]
        for h in hosts:
            es, st = self.run_si([self.item("Foo", "https://%s/x/y.svg" % h)])
            self.assertEqual(es, [], h)
            self.assertEqual(st["code_host"], 1, h)

    def test_similar_name_not_dropped(self):
        es, _ = self.run_si([self.item("Foo", "https://notgithub.com/")])
        self.assertEqual([e["domain"] for e in es], ["notgithub.com"])

    def test_shared_host_dropped_for_all(self):
        items = [self.item("Foo", "https://www.acme.com/a"), self.item("Bar", "https://acme.com/b"),
                 self.item("Baz", "https://baz.com")]
        es, st = self.run_si(items)
        self.assertEqual([e["domain"] for e in es], ["baz.com"])
        self.assertEqual(st["ambiguous"], 2)

    def test_custom_license_skipped(self):
        es, st = self.run_si([self.item("Foo", "https://foo.com", license={"type": "custom", "url": "x"})])
        self.assertEqual(es, [])
        self.assertEqual(st["custom_license"], 1)

    def test_blocklist_applies(self):
        es, st = self.run_si([self.item("Foo", "https://foo.com")], blocked={"foo.com"})
        self.assertEqual(es, [])
        self.assertEqual(st["blocked"], 1)

    def test_gilbarbara_wins_conflict(self):
        es, st = self.run_si([self.item("Foo", "https://foo.com")], taken={"foo.com"})
        self.assertEqual(es, [])
        self.assertEqual(st["conflict"], 1)

    def test_slug_explicit_beats_table(self):
        es, _ = self.run_si([self.item("Foo", "https://foo.com", slug="custom-slug")])
        self.assertEqual(es[0]["slug"], "custom-slug")
        self.assertEqual(es[0]["files"], {"wordmark": "custom-slug.svg", "icon": "custom-slug.svg"})

    def test_slug_from_table_and_missing(self):
        es, st = self.run_si([self.item("Foo", "https://foo.com"), self.item("Nope", "https://nope.com")])
        self.assertEqual([e["slug"] for e in es], ["foo"])
        self.assertEqual(st["invalid"], 1)

    def test_parse_slugs(self):
        text = "| Brand name | Brand slug |\n| :--- | :--- |\n| `.NET` | `dotnet` |\n| `1&1` | `1and1` |\n"
        self.assertEqual(build.parse_slugs(text), {".NET": ["dotnet"], "1&1": ["1and1"]})

    def test_duplicate_title_resolved_by_explicit_slug(self):
        items = [self.item("Dup", "https://one.com", slug="dup_two"), self.item("Dup", "https://two.com")]
        es, st = self.run_si(items)
        self.assertEqual({e["domain"]: e["slug"] for e in es}, {"one.com": "dup_two", "two.com": "dup"})

    def test_duplicate_title_unresolved_is_invalid(self):
        es, st = self.run_si([self.item("Amb", "https://amb.com")])
        self.assertEqual(es, [])
        self.assertEqual(st["invalid"], 1)

    def test_index_fields(self):
        es, _ = self.run_si([self.item("Foo", "https://foo.com", hex="abcdef", license={"type": "MIT"}),
                             self.item("Bar", "https://bar.com")])
        by = {e["domain"]: e for e in es}
        self.assertEqual(by["foo.com"]["origin"], "simple-icons")
        self.assertEqual(by["foo.com"]["hex"], "ABCDEF")
        self.assertEqual(by["foo.com"]["license"], "MIT")
        self.assertEqual(by["foo.com"]["source"], "https://foo.com")
        self.assertNotIn("license", by["bar.com"])
        self.assertIn("hex", by["bar.com"])

    def test_gilbarbara_origin(self):
        es, _, _, _ = build.build_entries(
            [{"name": "A", "shortname": "a", "url": "https://a.com", "files": ["a.svg"]}], set())
        self.assertEqual(es[0]["origin"], "gilbarbara")
        self.assertNotIn("hex", es[0])

    def test_fill_injected_on_root(self):
        out = build.inject_fill(b'<svg role="img" viewBox="0 0 24 24"><path d="M0"/></svg>', "ff0000")
        self.assertEqual(out, b'<svg role="img" viewBox="0 0 24 24" fill="#FF0000"><path d="M0"/></svg>')

    def test_fill_replaces_existing_and_after_normalize(self):
        raw = b'<svg width="24" height="24" fill="none" xmlns="http://www.w3.org/2000/svg"><path fill="red" d="M0"/></svg>'
        out = build.inject_fill(build.normalize_svg(raw), "00AA00").decode()
        self.assertEqual(out.count('fill="#00AA00"'), 1)
        self.assertNotIn('fill="none"', out)
        self.assertIn('<path fill="red"', out)
        self.assertIn('viewBox="0 0 24 24"', out)

    def test_fill_skips_comment_and_bad_hex(self):
        out = build.inject_fill(b'<!-- <svg a="1"> --><svg b="2"/>', "010203").decode()
        self.assertIn('<svg b="2" fill="#010203"/>', out)
        self.assertEqual(build.inject_fill(b"<svg/>", "zz"), b"<svg/>")


class ExtrasTests(unittest.TestCase):
    def test_wordmark_and_icon(self):
        es, sk = build.build_extras_entries(["a.com.svg", "a.com-icon.svg"], set())
        self.assertEqual(es[0]["files"], {"wordmark": "a.com.svg", "icon": "a.com-icon.svg"})
        self.assertEqual(es[0]["origin"], "extras")
        self.assertEqual(sk, [])

    def test_icon_falls_back_to_wordmark(self):
        es, _ = build.build_extras_entries(["a.com.svg"], set())
        self.assertEqual(es[0]["files"], {"wordmark": "a.com.svg", "icon": "a.com.svg"})

    def test_wordmark_falls_back_to_icon(self):
        es, _ = build.build_extras_entries(["a.com-icon.svg"], set())
        self.assertEqual(es[0]["files"], {"wordmark": "a.com-icon.svg", "icon": "a.com-icon.svg"})

    def test_blocklist(self):
        es, sk = build.build_extras_entries(["a.com.svg", "b.com.svg"], {"a.com"})
        self.assertEqual([e["domain"] for e in es], ["b.com"])
        self.assertEqual(sk, ["a.com.svg"])

    def test_unsafe_names(self):
        bad = ["..svg", ".svg", "../x.com.svg", "A.com.svg", "a b.com.svg", "www.a.com.svg", "a..com.svg"]
        es, sk = build.build_extras_entries(bad, set())
        self.assertEqual(es, [])
        self.assertEqual(sorted(sk), sorted(bad))

    def test_name_from_sources(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("| Domain | Name | File |\n| --- | --- | --- |\n| elal.com | El Al | elal.com.svg |\n")
        try:
            names = build.load_extras_names(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(names, {"elal.com": "El Al"})
        es, _ = build.build_extras_entries(["elal.com.svg", "foo.com.svg"], set(), names)
        self.assertEqual([e["name"] for e in es], ["Foo", "El Al"][::-1] if False else ["El Al", "Foo"])

    def test_override_skips_extras(self):
        es = [{"domain": "vercel.com", "name": "X", "origin": "extras"},
              {"domain": "openai.com", "name": "Y", "origin": "gilbarbara"}]
        build.apply_overrides(es)
        self.assertEqual([e["name"] for e in es], ["X", "OpenAI"])

    def test_name_escaped_pipe(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("| a.com | A \\| B | a.com.svg | https://x | d | n |\n")
        try:
            self.assertEqual(build.load_extras_names(f.name), {"a.com": "A | B"})
        finally:
            os.unlink(f.name)

    def test_extra_overrides_simple_icons_only(self):
        import json, shutil
        tmp = tempfile.mkdtemp()
        old = (build.EXTRAS, build.DIST, build.DIST_TMP, build.fetch, build.cached, build.BLOCKLIST)
        try:
            ex = os.path.join(tmp, "extras")
            os.makedirs(ex)
            with open(os.path.join(ex, "b.com.svg"), "w") as f:
                f.write('<svg viewBox="0 0 1 1"><path d="M0 0"/></svg>')
            si = [{"title": "B", "slug": "b", "hex": "FF0000", "source": "https://b.com"}]
            build.EXTRAS, build.DIST = ex, os.path.join(tmp, "dist")
            build.DIST_TMP, build.BLOCKLIST = os.path.join(tmp, "dist.tmp"), os.path.join(tmp, "none")
            build.fetch = lambda url: (json.dumps(si).encode() if url == build.SI_JSON else
                                       b"[]" if url == build.LOGOS_JSON else b"")
            siy = os.path.join(tmp, "si.svg")
            with open(siy, "w") as f:
                f.write('<svg viewBox="0 0 1 1"><path d="M9 9"/></svg>')
            build.cached = lambda f, base=None, cache_dir=None: siy
            build.main()
            index = json.load(open(os.path.join(build.DIST, "index.json")))
            self.assertEqual([(e["domain"], e["origin"]) for e in index], [("b.com", "extras")])
            out = open(os.path.join(build.DIST, "b.com.svg")).read()
            self.assertIn("M0 0", out)
            self.assertNotIn("M9 9", out)
            self.assertNotIn("fill=", out)
        finally:
            (build.EXTRAS, build.DIST, build.DIST_TMP, build.fetch, build.cached, build.BLOCKLIST) = old
            shutil.rmtree(tmp, ignore_errors=True)

    def test_non_svg_ignored(self):
        es, sk = build.build_extras_entries(["SOURCES.md", "a.com.png"], set())
        self.assertEqual((es, sk), ([], []))

    def test_precedence_in_main(self):
        import json, shutil
        tmp = tempfile.mkdtemp()
        try:
            ex = os.path.join(tmp, "extras")
            os.makedirs(ex)
            with open(os.path.join(ex, "a.com.svg"), "w") as f:
                f.write('<svg width="1" height="1" viewBox="0 0 1 1"><path d="M0 0"/></svg>')
            gil = [{"name": "A", "shortname": "a", "url": "https://a.com", "files": ["a.svg"]}]
            si = [{"title": "A", "slug": "a", "hex": "000000", "source": "https://a.com"}]
            old = (build.EXTRAS, build.DIST, build.DIST_TMP, build.fetch, build.cached, build.BLOCKLIST)
            build.EXTRAS, build.DIST = ex, os.path.join(tmp, "dist")
            build.DIST_TMP, build.BLOCKLIST = os.path.join(tmp, "dist.tmp"), os.path.join(tmp, "none")

            def fake_fetch(url):
                if url == build.LOGOS_JSON:
                    return json.dumps(gil).encode()
                if url == build.SI_JSON:
                    return json.dumps(si).encode()
                return b""
            build.fetch = fake_fetch
            build.cached = lambda f, base=None, cache_dir=None: os.path.join(tmp, "up.svg")
            with open(os.path.join(tmp, "up.svg"), "w") as f:
                f.write("<svg viewBox='0 0 1 1'><path d='M9 9'/></svg>")
            build.main()
            index = json.load(open(os.path.join(build.DIST, "index.json")))
            self.assertEqual([(e["domain"], e["origin"]) for e in index], [("a.com", "extras")])
            self.assertIn("M0 0", open(os.path.join(build.DIST, "a.com.svg")).read())
            self.assertIn("M0 0", open(os.path.join(build.DIST, "icon", "a.com.svg")).read())
        finally:
            (build.EXTRAS, build.DIST, build.DIST_TMP, build.fetch, build.cached, build.BLOCKLIST) = old
            shutil.rmtree(tmp, ignore_errors=True)


class RootNameTests(unittest.TestCase):
    def _pick(self, dom, names):
        items = [{"name": n, "shortname": sn, "url": "https://" + dom, "files": [sn + ".svg"]} for n, sn in names]
        return build.build_entries(items, set())[0][0]["name"]

    def test_shortname_equals_label(self):
        self.assertEqual(self._pick("google.com", [("Chrome", "chrome"), ("Google", "google")]), "Google")

    def test_name_equals_label_slugified(self):
        self.assertEqual(self._pick("mastercard.com", [("Maestro", "maestro"), ("MasterCard", "x")]), "MasterCard")

    def test_name_contains_label_not_preferred(self):
        self.assertEqual(self._pick("elastic.co", [("Elasticsearch", "elasticsearch"), ("Elastic", "elastic-x")]), "Elastic")
        self.assertEqual(self._pick("elastic.co", [("Elasticsearch", "es"), ("Kibana", "kb")]), "Elasticsearch")

    def test_fallback_first(self):
        self.assertEqual(self._pick("x.com", [("One", "one"), ("Two", "two")]), "One")

    def test_microsoft(self):
        self.assertEqual(self._pick("microsoft.com", [("Azure", "azure"), ("Microsoft", "microsoft")]), "Microsoft")

    def test_dups_reported(self):
        items = [{"name": "Chrome", "shortname": "chrome", "url": "https://google.com", "files": ["a.svg"]},
                 {"name": "Google", "shortname": "google", "url": "https://google.com", "files": ["b.svg"]}]
        _, _, dups, _ = build.build_entries(items, set())
        self.assertEqual(dups, [("google.com", "Chrome")])


def _e(dom, name):
    return {"domain": dom, "name": name}


class CollapseTests(unittest.TestCase):
    def doms(self, entries):
        kept, dropped = build.collapse_entries(entries)
        return [e["domain"] for e in kept], dropped

    def test_same_name_subdomain_dropped(self):
        kept, dropped = self.doms([_e("contentful.com", "Contentful"), _e("press.contentful.com", "Contentful")])
        self.assertEqual(kept, ["contentful.com"])
        self.assertEqual(dropped, [("press.contentful.com", "contentful.com", "subdomain")])

    def test_suffix_name_dropped(self):
        kept, _ = self.doms([_e("x.com", "X"), _e("docs.x.com", "X Docs"), _e("blog.x.com", "X-Blog")])
        self.assertEqual(kept, ["x.com"])

    def test_extras_never_dropped(self):
        ex = dict(_e("docs.x.com", "X Docs"), origin="extras")
        ex2 = dict(_e("x.github.io", "X"), origin="extras")
        kept, dropped = self.doms([_e("x.com", "X"), ex, ex2])
        self.assertEqual(sorted(kept), ["docs.x.com", "x.com", "x.github.io"])
        self.assertEqual(dropped, [])

    def test_extras_can_drop_upstream(self):
        kept, dropped = self.doms([dict(_e("x.com", "X"), origin="extras"), _e("docs.x.com", "X")])
        self.assertEqual(kept, ["x.com"])

    def test_product_words_not_ignorable(self):
        kept, _ = self.doms([_e("google.com", "Google"), _e("developers.google.com", "Google Developers"),
                             _e("x.com", "X"), _e("developer.x.com", "X Developer")])
        self.assertEqual(len(kept), 4)

    def test_different_name_kept(self):
        kept, _ = self.doms([_e("google.com", "Google"), _e("home.google.com", "Google Home"),
                             _e("camel.apache.org", "Apache Camel"), _e("apache.org", "Apache")])
        self.assertEqual(sorted(kept), ["apache.org", "camel.apache.org", "google.com", "home.google.com"])

    def test_third_party_dropped_when_brand_domain_exists(self):
        kept, dropped = self.doms([_e("algolia.com", "Algolia"), _e("algolia.frontify.com", "Algolia"),
                                   _e("acme.github.io", "Acme"), _e("acme.org", "Acme")])
        self.assertEqual(sorted(kept), ["acme.org", "algolia.com"])
        self.assertEqual({d[2] for d in dropped}, {"third-party host"})

    def test_sole_third_party_kept(self):
        kept, _ = self.doms([_e("solo.github.io", "Solo"), _e("other.com", "Other")])
        self.assertEqual(sorted(kept), ["other.com", "solo.github.io"])

    def test_two_third_party_same_name_both_kept(self):
        kept, _ = self.doms([_e("a.github.io", "A"), _e("a.netlify.app", "A")])
        self.assertEqual(len(kept), 2)

    def test_alias_pair_kept(self):
        kept, _ = self.doms([_e("13tv.co.il", "13TV"), _e("reshet.tv", "13TV")])
        self.assertEqual(len(kept), 2)

    def test_deterministic(self):
        es = [_e("a.com", "A"), _e("x.a.com", "A"), _e("b.github.io", "B"), _e("b.com", "B")]
        self.assertEqual(build.collapse_entries(es), build.collapse_entries(list(reversed(es))))


if __name__ == "__main__":
    unittest.main()
