"""Build the demo page (docs/index.html) from the agent's last run.

    python build_demo.py

Reads output/ (patterns, personas, report) and memory/log.md, runs the checker on every persona,
and writes one self-contained HTML page: no network, no build step, system fonts and inline icons.
run_agent.py calls it at the end of every run, so the page always shows the latest run.
"""
import datetime
import html
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "docs" / "index.html"
PERSONAS = [
    ("persona-1-hard-end.md", "Hard end", "A file that is very slow or blocked"),
    ("persona-2-easy-end.md", "Easy end", "Follows many files with ease"),
    ("persona-3-regular.md", "Regular", "A normal file"),
]
REPO = "https://github.com/javiersanzg/jtbd-persona-agent"


def icon(name, label=None):
    svg = (HERE / "assets" / "icons" / f"{name}.svg").read_text(encoding="utf-8")
    attrs = 'class="ic" aria-hidden="true" focusable="false"' if not label else f'class="ic" role="img" aria-label="{label}"'
    return svg.replace("<svg ", f"<svg {attrs} ", 1)


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\b(P[1-5])\b", r'<span class="pid">\1</span>', t)
    t = re.sub(r"(?<=\w)\*", '<span class="inv" title="Not in the research">*</span>', t)
    return t


def md(text, shift=1):
    """A small Markdown renderer for what the agent writes: headings, lists, tables, paragraphs."""
    out, lines, i = [], text.strip().splitlines(), 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m:
            lvl = min(6, len(m.group(1)) + shift)
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if ln.lstrip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            head, body = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
            th = "".join(f"<th scope=\"col\">{inline(c)}</th>" for c in head)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|\s*[-*]\s|\s*\|)", lines[i]):
            para.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def checker(path):
    res = subprocess.run([sys.executable, str(HERE / "check_persona.py"), str(path)],
                         capture_output=True, text=True)
    return json.loads(res.stdout)


def trace():
    rows = []
    for ln in (HERE / "memory" / "log.md").read_text(encoding="utf-8").splitlines():
        parts = [p.strip() for p in ln.split("|", 2)]
        if len(parts) == 3 and parts[0].isdigit():
            rows.append(parts)
    items = []
    for n, kind, what in rows:
        k = kind.lower()
        verdict = ""
        if k == "observe":
            if "FAIL" in what:
                verdict = '<span class="stamp fail">FAIL</span>'
            elif "PASS" in what:
                verdict = '<span class="stamp pass">PASS</span>'
        items.append(f'<li class="step {k}"><span class="n">{n}</span><span class="kind">{kind}</span>'
                     f'<span class="what">{inline(what)}{verdict}</span></li>')
    return "\n".join(items), rows


def persona_title(text):
    first = text.strip().splitlines()[0].lstrip("# ").strip()
    m = re.match(r'(.+?):\s*"(.*)"\s*$', first)
    return (m.group(1), m.group(2)) if m else (first, "")


def build():
    steps_html, steps = trace()
    run_dir = sorted((HERE / "runs").glob("*"))[-1].name if (HERE / "runs").exists() else ""
    run_date = datetime.datetime.strptime(run_dir, "%Y-%m-%d_%H%M").strftime("%d %b %Y, %H:%M") if run_dir else ""
    tabs, panels, verdicts = [], [], []
    for idx, (fname, pos, sub) in enumerate(PERSONAS):
        text = (HERE / "output" / fname).read_text(encoding="utf-8")
        v = checker(HERE / "output" / fname)
        verdicts.append(v["verdict"])
        name, quote = persona_title(text)
        body = text.strip().split("\n", 1)[1] if "\n" in text.strip() else ""
        ok = v["verdict"] == "PASS"
        stamp = f'<span class="stamp {"pass" if ok else "fail"}">{icon("check-circle" if ok else "x-circle")}{v["verdict"]}</span>'
        tabs.append(f'<button class="tab" role="tab" id="t{idx}" aria-controls="p{idx}" aria-selected="{str(idx == 0).lower()}" '
                    f'tabindex="{0 if idx == 0 else -1}"><span class="pos">{pos}</span><span class="nm">{html.escape(name)}</span></button>')
        panels.append(f'''<article class="persona" role="tabpanel" id="p{idx}" aria-labelledby="t{idx}">
  <header class="ph">
    <p class="pos-l">{pos} &middot; {sub}</p>
    <h3>{html.escape(name)}</h3>
    <blockquote>&ldquo;{inline(quote)}&rdquo;</blockquote>
    <p class="meta">{stamp}<span>{v["words"]} words</span><span>checked by <code>check_persona.py</code></span></p>
  </header>
  <div class="pbody">{md(body, shift=2)}</div>
</article>''')
    passed = sum(1 for v in verdicts if v == "PASS")
    report = (HERE / "output" / "report.md").read_text(encoding="utf-8").split("\n", 1)[1]
    patterns = (HERE / "output" / "patterns.md").read_text(encoding="utf-8").split("\n", 1)[1]
    css = (HERE / "assets" / "demo.css").read_text(encoding="utf-8")
    js = (HERE / "assets" / "demo.js").read_text(encoding="utf-8")
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JTBD Persona Agent</title>
<meta name="description" content="An autonomous agent that turns qualitative field research into checked user personas.">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#run">Skip to the run</a>
<header class="top">
  <div class="wrap">
    <p class="kicker">Design research &middot; autonomous agent</p>
    <h1>JTBD Persona Agent</h1>
    <p class="lede">Give it interview notes. It finds the patterns, writes the personas, checks each one against a quality bar it cannot argue with, and fixes them until they pass.</p>
    <p class="cta"><a class="btn" href="{REPO}">{icon("github-logo")}View the code</a><a class="btn ghost" href="#run">{icon("arrow-right")}See the last run</a></p>
    <dl class="stats">
      <div><dt>Personas</dt><dd>{passed}/{len(PERSONAS)} <span>pass</span></dd></div>
      <div><dt>Agent steps</dt><dd>{len(steps)}</dd></div>
      <div><dt>Patterns</dt><dd>5</dd></div>
      <div><dt>Last run</dt><dd class="sm">{run_date}</dd></div>
    </dl>
  </div>
</header>

<main>
<section class="wrap how" aria-labelledby="how-h">
  <h2 id="how-h">How it works</h2>
  <ol class="parts">
    <li>{icon("target")}<div><h3>Goal</h3><p>Three personas, one per point of the research line, each passing the checker, plus a report that compares them. Only the research as input: no web, no invented data, no solutions.</p></div></li>
    <li>{icon("brain")}<div><h3>Brain</h3><p>Claude, running headless in Claude Code. It chooses its next step on its own.</p></div></li>
    <li>{icon("wrench")}<div><h3>Tools</h3><p>Read the research, write files, and run <code>check_persona.py</code>: sections in order, all five patterns used, every section traced to a pattern, invented details flagged, no solutions, one page.</p></div></li>
    <li>{icon("notebook")}<div><h3>Memory</h3><p>A step log it writes as it works. Think, act, observe, reflect: every decision is on the record below.</p></div></li>
  </ol>
</section>

<section class="band" id="run" aria-labelledby="run-h">
  <div class="wrap">
    <h2 id="run-h">The run, step by step</h2>
    <p class="note">Written by the agent itself in <code>memory/log.md</code>. The verdicts are re-checked by the runner after the agent stops.</p>
    <ol class="trace">
{steps_html}
    </ol>
  </div>
</section>

<section class="wrap" aria-labelledby="per-h">
  <h2 id="per-h">The personas</h2>
  <p class="note">Details marked <span class="inv">*</span> are not in the research. <span class="pid">P1</span>&ndash;<span class="pid">P5</span> point to the patterns they come from.</p>
  <div class="tabs" role="tablist" aria-label="Personas">{"".join(tabs)}</div>
  {"".join(panels)}
</section>

<section class="wrap two" aria-labelledby="rep-h">
  <div>
    <h2 id="rep-h">What the agent concluded</h2>
    <div class="prose">{md(report, shift=1)}</div>
  </div>
  <details class="pat">
    <summary>The five patterns it worked from</summary>
    <div class="prose">{md(patterns, shift=2)}</div>
  </details>
</section>
</main>

<footer class="foot">
  <div class="wrap">
    <p>{icon("terminal-window")}Run it yourself: <code>python run_agent.py</code>. Needs Python 3.10+ and Claude Code. This page is rebuilt after every run.</p>
    <p class="small">Company and staff names in the research are changed. Icons: Phosphor (MIT).</p>
  </div>
</footer>
<script>{js}</script>
</body>
</html>
'''
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(OUT)


if __name__ == "__main__":
    build()
