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


if __name__ == "__main__":
    unittest.main()
