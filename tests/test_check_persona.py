"""Unit tests for the persona checker. Run: python -m unittest discover -s tests"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from check_persona import check  # noqa: E402

GOOD = """# Ana, the shop owner: "I just want to know where it is."

## Profile
- 44*, owns a bakery. Uses WhatsApp for everything.

## Background
Her file has been open for eight months (P1). The technician came twice for photos (P4).

## Goals
- Know who has the file now (P3).

## Pains and frustrations
- The status means nothing to her (P3).

## Jobs to be done
- Functional: know the next step (P3).
- Personal: feel someone is looking at it (P1).
- Social: give her staff a real date (P2).

## A day in her life during the wait
She calls the manager on Mondays (P2).

## How she looks for news today
- Phone calls to one person (P2).

## What makes her trust or doubt an installer
- Doubt: small signs of progress are missing (P5).

## Based on
- Profile: P1
- Goals: P3
- Pains: P3
- Jobs: P1, P2, P3
- Day: P2
- News: P2
- Trust: P5
"""


class CheckPersonaTest(unittest.TestCase):
    def test_good_persona_passes(self):
        res = check(GOOD)
        self.assertEqual(res["verdict"], "PASS", res["problems"])

    def test_missing_section_fails(self):
        res = check(GOOD.replace("## Goals", "## Aims"))
        self.assertIn("missing section: goals", res["problems"])

    def test_sections_out_of_order_fail(self):
        swapped = GOOD.replace("## Profile", "## TEMP").replace("## Background", "## Profile").replace("## TEMP", "## Background")
        self.assertIn("sections are out of order", check(swapped)["problems"])

    def test_unused_pattern_fails(self):
        res = check(GOOD.replace("P5", "P1"))
        self.assertIn("pattern P5 is never used", res["problems"])

    def test_solution_words_fail(self):
        res = check(GOOD.replace("Uses WhatsApp for everything.", "She needs an app to track it."))
        self.assertTrue(any(p.startswith("proposes solutions") for p in res["problems"]))

    def test_unmarked_invention_fails(self):
        res = check(GOOD.replace("44*", "44"))
        self.assertIn("no invented detail is marked with an asterisk", res["problems"])

    def test_too_long_fails(self):
        res = check(GOOD + ("word " * 700))
        self.assertTrue(any(p.startswith("too long") for p in res["problems"]))

    def test_shipped_personas_pass(self):
        for f in sorted((ROOT / "output").glob("persona-*.md")):
            with self.subTest(persona=f.name):
                self.assertEqual(check(f.read_text(encoding="utf-8"))["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
