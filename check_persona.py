"""Persona checker: the agent's tool to know when a persona is good enough.

Usage:
    python check_persona.py output/persona-1.md

Prints a JSON verdict and exits 0 on PASS, 1 on FAIL. The rules are the team's quality bar for a
research persona (Assessment 2, Creativity and Innovation):

1. every required section is present, in order
2. each of the research patterns P1 to P5 is used at least once
3. a "Based on" list links the sections to patterns
4. no solutions: this is research, not ideation
5. invented details are marked with an asterisk
6. about one page (at most 600 words)
"""
import json
import re
import sys

SECTIONS = [
    "profile",
    "background",
    "goals",
    "pains and frustrations",
    "jobs to be done",
    "a day in",
    "how ",            # how he/she looks for news today
    "trust or doubt",
    "based on",
]
SOLUTION_WORDS = r"\b(app|apps|application|platform|dashboard|tracker|chatbot|solution|solutions|we should|should offer|could offer|we recommend|new feature|features)\b"
MAX_WORDS = 600


def headings(text):
    out = []
    for line in text.splitlines():
        s = line.strip().lstrip("#").strip().strip("*").strip().lower()
        if line.strip().startswith("#") or (line.strip().startswith("**") and line.strip().endswith("**")):
            out.append(s)
    return out


def check(text):
    problems = []
    heads = headings(text)
    pos = []
    for name in SECTIONS:
        idx = next((i for i, h in enumerate(heads) if h.startswith(name) or name in h), None)
        if idx is None:
            problems.append(f"missing section: {name.strip()}")
        else:
            pos.append(idx)
    if pos != sorted(pos):
        problems.append("sections are out of order")
    for p in ("P1", "P2", "P3", "P4", "P5"):
        if not re.search(rf"\b{p}\b", text):
            problems.append(f"pattern {p} is never used")
    based = text.lower().split("based on", 1)
    if len(based) < 2 or len(re.findall(r"\bp[1-5]\b", based[1])) < 5:
        problems.append("the Based on list does not link the sections to patterns")
    body = text.lower().split("based on", 1)[0]
    found = sorted(set(m.group(0) for m in re.finditer(SOLUTION_WORDS, body)))
    if found:
        problems.append(f"proposes solutions (words: {', '.join(found)})")
    if "*" not in text.replace("**", ""):
        problems.append("no invented detail is marked with an asterisk")
    words = len(re.findall(r"\w+", text))
    if words > MAX_WORDS:
        problems.append(f"too long: {words} words (max {MAX_WORDS})")
    return {"verdict": "PASS" if not problems else "FAIL", "words": words, "problems": problems}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python check_persona.py <persona.md>")
    with open(sys.argv[1], encoding="utf-8") as f:
        result = check(f.read())
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
