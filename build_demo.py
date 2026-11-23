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
        if ln.lstrip().startswith(">"):
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{inline(' '.join(quote))}</blockquote>")
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


def persona_parts(text):
    """Name, quote and body. The quote is either on the title line (Name: "...") or the first > line."""
    lines = text.strip().splitlines()
    first = lines[0].lstrip("# ").strip()
    body = lines[1:]
    m = re.match(r'(.+?)\s*[:–—-]\s*"(.+?)"\s*(.*)$', first)
    if m:
        tail = f"\n\n{m.group(3).strip()}" if m.group(3).strip() else ""
        return m.group(1), m.group(2), tail + "\n" + "\n".join(body)
    for k, ln in enumerate(body):
        if ln.strip().startswith(">"):
            quote = ln.strip()[1:].strip().strip('"').strip("“”")
            return first, quote, "\n".join(body[:k] + body[k + 1:])
        if ln.strip():
            break
    return first, "", "\n".join(body)


def table_rows(text, first_header):
    """Rows of the first Markdown table whose first header cell is first_header."""
    lines = text.splitlines()
    for k, ln in enumerate(lines):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if ln.lstrip().startswith("|") and cells[0] == first_header:
            rows = []
            for row in lines[k + 2:]:
                if not row.lstrip().startswith("|"):
                    break
                rows.append([c.strip() for c in row.strip().strip("|").split("|")])
            return rows
    return []


def sources():
    rows = table_rows((HERE / "research" / "field_notes.md").read_text(encoding="utf-8"), "#")
    def kind(s):
        s = s.lower()
        if "interview" in s:
            return "Recorded interview"
        if "review" in s:
            return "Google review"
        if "energias-renovables" in s:
            return "Magazine interview"
        return "Forum post"
    return "\n".join(f'<li><span class="src-type">{kind(s)}</span><span class="src-who">{inline(w)}</span>'
                     f'<span class="src-where">{html.escape(t)} &middot; {html.escape(d)}</span></li>' for _, w, t, s, d in rows), len(rows)


def pattern_cards():
    text = (HERE / "output" / "patterns.md").read_text(encoding="utf-8")
    rows = table_rows(text, "#")
    if not rows:  # the agent may also write one "## P1. Name" section per pattern, with bullet fields
        for m in re.finditer(r"^##\s*(P\d)[.:]?\s*(.+?)\n(.*?)(?=^##\s|\Z)", text, re.M | re.S):
            field = lambda k: (re.search(rf"\*\*{k}[^*]*:\*\*\s*(.+)", m.group(3)) or [None, ""])[1].strip()
            rows.append([m.group(1), m.group(2).strip(), field("Verbatim"), field("Job"), field("Insight")])
    cards = []
    for pid, name, verbatim, job, insight in rows:
        cards.append(f'''<li class="pcard"><span class="pid pc-id">{html.escape(pid)}</span>
  <div><h3>{html.escape(name)}</h3><p class="pcard-ins">{inline(insight)}</p></div>
  <div><p class="lab">Job to be done</p><p>{inline(job)}</p></div>
  <div><p class="lab">What people said</p><p class="verb">{inline(verbatim)}</p></div></li>''')
    return "\n".join(cards), len(rows)


def build():
    steps_html, steps = trace()
    run_dir = sorted((HERE / "runs").glob("*"))[-1].name if (HERE / "runs").exists() else ""
    run_date = datetime.datetime.strptime(run_dir, "%Y-%m-%d_%H%M").strftime("%d %b %Y, %H:%M") if run_dir else ""
    tabs, panels, verdicts = [], [], []
    for idx, (fname, pos, sub) in enumerate(PERSONAS):
        text = (HERE / "output" / fname).read_text(encoding="utf-8")
        v = checker(HERE / "output" / fname)
        verdicts.append(v["verdict"])
        name, quote, body = persona_parts(text)
        ok = v["verdict"] == "PASS"
        stamp = f'<span class="stamp {"pass" if ok else "fail"}">{icon("check-circle" if ok else "x-circle")}{v["verdict"]}</span>'
        tabs.append(f'<button class="tab" role="tab" id="t{idx}" aria-controls="p{idx}" aria-selected="{str(idx == 0).lower()}" '
                    f'tabindex="{0 if idx == 0 else -1}"><span class="pos">{pos}</span><span class="nm">{html.escape(name.replace("*", ""))}</span></button>')
        panels.append(f'''<article class="persona" role="tabpanel" id="p{idx}" aria-labelledby="t{idx}">
  <header class="ph">
    <p class="pos-l">{pos} &middot; {sub}</p>
    <h3>{html.escape(name.replace("*", ""))}</h3>
    {f"<blockquote>&ldquo;{inline(quote)}&rdquo;</blockquote>" if quote else ""}
    <p class="meta">{stamp}<span>{v["words"]} words</span><span>checked by <code>check_persona.py</code></span></p>
  </header>
  <div class="pbody">{md(body, shift=2)}</div>
</article>''')
    passed = sum(1 for v in verdicts if v == "PASS")
    report = (HERE / "output" / "report.md").read_text(encoding="utf-8").split("\n", 1)[1]
    report = re.sub(r"\s*\(`[^`]+\.md`\)", "", report)  # file names are noise for a reader
    src_html, n_src = sources()
    pat_html, n_pat = pattern_cards()
    css = (HERE / "assets" / "demo.css").read_text(encoding="utf-8")
    js = (HERE / "assets" / "demo.js").read_text(encoding="utf-8")
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JTBD Persona Agent</title>
<meta name="description" content="An agent that turns real user research into user personas, and checks its own work until it passes.">
<style>{css}</style>
</head>
<body>
<a class="skip" href="#run">Skip to the run</a>
<header class="top">
  <div class="wrap">
    <p class="kicker">Design thinking &middot; autonomous agent</p>
    <h1>JTBD Persona Agent</h1>
    <p class="lede">It reads real user research, writes user personas and checks each one with a script until it passes.</p>
    <p class="cta"><a class="btn" href="{REPO}">{icon("github-logo")}View the code</a><a class="btn ghost" href="#run">{icon("arrow-right")}See the last run</a></p>
    <dl class="stats">
      <div><dt>Research sources</dt><dd>{n_src}</dd></div>
      <div><dt>Patterns found</dt><dd>{n_pat}</dd></div>
      <div><dt>Personas passed</dt><dd>{passed}/{len(PERSONAS)}</dd></div>
      <div><dt>Last run</dt><dd class="sm">{run_date}</dd></div>
    </dl>
  </div>
</header>

<main>
<section class="wrap" aria-labelledby="what-h">
  <h2 id="what-h">What this is</h2>
  <p class="intro">A <strong>persona</strong> is a fictional user built from real research. The challenge: clients of a small electrical installer in Valencia wait months for their electricity file and do not know what is happening. The agent writes three personas: the worst wait (<em>hard end</em>), the easiest (<em>easy end</em>) and a normal one (<em>regular</em>).</p>
  <ol class="flow" aria-label="How a run works">
    <li><span class="fn">1</span><h3>Research in</h3><p>{n_src} real sources. No web access.</p></li>
    <li><span class="fn">2</span><h3>Patterns</h3><p>{n_pat} patterns, <span class="pid">P1</span> to <span class="pid">P{n_pat}</span>.</p></li>
    <li><span class="fn">3</span><h3>Write and check</h3><p><code>check_persona.py</code> checks each persona. FAIL means fix and retry, up to 3 times.</p></li>
    <li><span class="fn">4</span><h3>Report out</h3><p>3 personas and a report.</p></li>
  </ol>
</section>

<section class="wrap" aria-labelledby="src-h">
  <h2 id="src-h">The research it read</h2>
  <p class="note">This is everything the agent reads, from <code>research/field_notes.md</code>: one recorded interview, four forum posts, one Google review and two magazine interviews with experts. Quotes are word for word. Company and staff names are changed.</p>
  <ul class="sources">
{src_html}
  </ul>
</section>

<section class="wrap" aria-labelledby="pat-h">
  <h2 id="pat-h">The patterns it found</h2>
  <p class="note">Written by the agent. In italics, the insight: why it happens.</p>
  <ol class="pcards">
{pat_html}
  </ol>
</section>

<section class="band" id="run" aria-labelledby="run-h">
  <div class="wrap">
    <h2 id="run-h">The run, step by step</h2>
    <p class="note">The agent's own log, <code>memory/log.md</code>. The runner checks every persona again at the end.</p>
    <ul class="legend" aria-label="Kinds of step">
      <li class="step think"><span class="kind">THINK</span> plans</li>
      <li class="step act"><span class="kind">ACT</span> writes</li>
      <li class="step observe"><span class="kind">OBSERVE</span> reads the check</li>
      <li class="step reflect"><span class="kind">REFLECT</span> decides what to fix</li>
    </ul>
    <ol class="trace">
{steps_html}
    </ol>
  </div>
</section>

<section class="wrap" aria-labelledby="per-h">
  <h2 id="per-h">The personas</h2>
  <p class="note"><span class="inv">*</span> not in the research. <span class="pid">P1</span> to <span class="pid">P{n_pat}</span>: the pattern each part comes from.</p>
  <div class="tabs" role="tablist" aria-label="Personas">{"".join(tabs)}</div>
  {"".join(panels)}
</section>

<section class="wrap" aria-labelledby="rep-h">
  <h2 id="rep-h">What the agent concluded</h2>
  <p class="note">The agent's report, unedited.</p>
  <div class="prose report">{md(report, shift=1)}</div>
</section>

<section class="wrap" aria-labelledby="try-h">
  <h2 id="try-h">Run it yourself</h2>
  <ol class="howto">
    <li>Install Python 3.10+ and <a href="https://code.claude.com">Claude Code</a>. Log in once with <code>claude</code>.</li>
    <li><code>git clone {REPO}.git</code></li>
    <li><code>python run_agent.py</code>. About 5 minutes. Ends with <code>RESULT: PASS</code> or <code>FAIL</code>.</li>
    <li>Results in <code>output/</code>, steps in <code>memory/log.md</code>. This page is rebuilt each run.</li>
  </ol>
  <p class="note">Another challenge: replace <code>research/field_notes.md</code> and the challenge in <code>AGENT.md</code>.</p>
</section>
</main>

<footer class="foot">
  <div class="wrap">
    <p>Team 3 &middot; Creativity and Innovation &middot; EDEM, Valencia</p>
    <p class="small">Icons: Phosphor (MIT)</p>
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
