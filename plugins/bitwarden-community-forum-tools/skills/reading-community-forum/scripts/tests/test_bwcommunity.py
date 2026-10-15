"""Offline unit tests: no network. Run with `python3 -m unittest discover skills/reading-community-forum/scripts/tests`."""
import importlib.machinery
import importlib.util
import os
import unittest

_path = os.path.join(os.path.dirname(__file__), "..", "bwcommunity.py")
_loader = importlib.machinery.SourceFileLoader("bwcommunity", _path)
_spec = importlib.util.spec_from_loader("bwcommunity", _loader)
bw = importlib.util.module_from_spec(_spec)
_loader.exec_module(bw)

ROBOTS = """
User-agent: python-requests
Disallow: /

User-agent: *
Disallow: /search
Disallow: /tag/*/l
Disallow: /*?*api_key*
"""


class Robots(unittest.TestCase):
    def setUp(self):
        self.rules = bw.parse_robots(ROBOTS, "bwcommunity-cli")

    def test_search_blocked(self):
        self.assertEqual(bw.robots_disallowed(self.rules, "/search.json?q=x"), "/search")

    def test_wildcard(self):
        self.assertTrue(bw.robots_disallowed(self.rules, "/tag/foo/l/latest.json"))
        self.assertIsNone(bw.robots_disallowed(self.rules, "/tag/foo.json"))
        self.assertTrue(bw.robots_disallowed(self.rules, "/latest.json?a=1&api_key=z"))

    def test_allowed(self):
        for p in ("/t/123.json", "/latest.json", "/raw/1/2", "/categories.json"):
            self.assertIsNone(bw.robots_disallowed(self.rules, p), p)

    def test_specific_group_wins(self):
        rules = bw.parse_robots(ROBOTS, "python-requests/2.0")
        self.assertEqual(bw.robots_disallowed(rules, "/t/1.json"), "/")


class TopicRef(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(bw.parse_topic_ref("123"), (123, None))
        self.assertEqual(bw.parse_topic_ref("/t/slug/123"), (123, None))
        self.assertEqual(bw.parse_topic_ref("https://community.bitwarden.com/t/slug/123/7"), (123, 7))
        self.assertEqual(bw.parse_topic_ref("https://community.bitwarden.com/t/123"), (123, None))

    def test_bad(self):
        with self.assertRaises(bw.CLIError) as cm:
            bw.parse_topic_ref("nope")
        self.assertEqual(cm.exception.code, bw.EXIT_USAGE)


class HtmlToText(unittest.TestCase):
    def test_quote_and_formatting(self):
        cooked = ('<p>Hello,</p><aside class="quote no-group" data-username="alice" data-post="1" data-topic="9">'
                  '<div class="title"><div class="quote-controls"></div><img class="avatar" src="x"> alice:</div>'
                  '<blockquote><p>original text</p></blockquote></aside>'
                  '<p>Reply with <strong>bold</strong>, <s>old</s> and <a href="/t/x/1">a link</a>.</p>')
        out = bw.html_to_text(cooked, "https://f.example")
        self.assertIn("> **@alice** (#1) wrote:", out)
        self.assertIn("> original text", out)
        self.assertNotIn(">>", out)
        self.assertNotIn("image", out)
        self.assertIn("**bold**", out)
        self.assertIn("~~old~~", out)
        self.assertIn("[a link](https://f.example/t/x/1)", out)

    def test_same_thread_quote_collapses(self):
        cooked = ('<aside class="quote" data-username="bob" data-post="3" data-topic="9"><div class="title">bob:</div>'
                  '<blockquote><p>' + "long words " * 40 + '</p></blockquote></aside><p>my reply</p>')
        out = bw.html_to_text(cooked, topic_id=9)
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("> **@bob** (#3): long words"), first)
        self.assertTrue(first.endswith("…"))
        self.assertLess(len(first), bw.QUOTE_CHARS + 30)
        self.assertIn("my reply", out)
        other = bw.html_to_text(cooked, topic_id=10)  # quote from another topic stays in full
        self.assertIn("wrote:", other)

    def test_generic_image_alt(self):
        self.assertEqual(bw.html_to_text('<img src="a" alt="image">'), "[image]")
        self.assertEqual(bw.html_to_text('<img src="a" alt="Screenshot 2024-01-01.png">'), "[image]")
        self.assertEqual(bw.html_to_text('<img src="a" alt="vault settings">'), "[image: vault settings]")

    def test_heading_anchor_and_lists(self):
        out = bw.html_to_text('<h3><a class="anchor" href="#p-1"></a>Title</h3><ul><li>one</li><li>two</li></ul>'
                              '<pre><code>x = 1\n</code></pre>')
        self.assertIn("### Title", out)
        self.assertNotIn("[]", out)
        self.assertIn("- one\n- two", out)
        self.assertIn("```\nx = 1", out)

    def test_onebox(self):
        out = bw.html_to_text('<aside class="onebox" data-onebox-src="https://gh.example/pr/1"><div>big preview</div></aside><p>after</p>')
        self.assertIn("[link preview: https://gh.example/pr/1]", out)
        self.assertNotIn("big preview", out)
        self.assertIn("after", out)


class Misc(unittest.TestCase):
    def test_truncate(self):
        text, cut = bw.truncate("word " * 100, 50, "U")
        self.assertTrue(cut)
        self.assertIn("[truncated:", text)
        self.assertEqual(bw.truncate("short", 50, "U"), ("short", False))
        self.assertEqual(bw.truncate("x" * 99, 0, "U")[1], False)

    def test_num(self):
        self.assertEqual((bw.num(950), bw.num(9999), bw.num(12345), bw.num(216187), bw.num(None)), ("950", "9999", "12.3k", "216.2k", "?"))

    def test_prune(self):
        self.assertEqual(bw.prune({"a": None, "b": False, "c": [], "d": 0, "e": {"f": ""}, "g": [{"h": None, "i": 1}]}),
                         {"d": 0, "g": [{"i": 1}]})

    def test_raw_topic_split(self):
        raw = "alice | 2024-01-01 10:00:00 UTC | #1\n\nfirst\n\n-------------------------\n\nbob | 2024-01-02 10:00:00 UTC | #2\n\nsecond | with pipe\n"
        self.assertEqual(bw.parse_raw_topic(raw), {1: "first", 2: "second | with pipe"})

    def test_usage_exit_code(self):
        with self.assertRaises(SystemExit) as cm:
            bw.build_parser().parse_args(["thread"])
        self.assertEqual(cm.exception.code, bw.EXIT_USAGE)


if __name__ == "__main__":
    unittest.main()
