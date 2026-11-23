import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build_demo  # noqa: E402


class DemoIsInEnglish(unittest.TestCase):
    def test_full_quote_is_translated(self):
        self.assertIn("cannot have electricity", build_demo.english(
            "Está todo perfectamente realizado y no puedo tener luz por este trámite"))

    def test_cut_quote_matches_its_source(self):
        self.assertIn("Great professionals", build_demo.english(
            "Grandes profesionales. [...] Consiguieron ejecutarlo con el tiempo y presupuesto pactado"))

    def test_inline_replaces_spanish(self):
        out = build_demo.inline("«Está todo perfectamente realizado y no puedo tener luz por este trámite» (P5)")
        self.assertNotIn("«", out)
        self.assertIn("cannot have electricity", out)

    def test_built_page_has_no_spanish_quote_marks(self):
        page = (build_demo.HERE / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("«", page)


if __name__ == "__main__":
    unittest.main()
