"""Run the persona agent: Claude Code in headless mode, with the goal in AGENT.md.

    python run_agent.py

Needs Claude Code installed and logged in (`claude` on the PATH). The agent can only read files,
write files and run the checker; it cannot use the web. Every step it takes is saved to
runs/<time>/steps.jsonl (the raw event stream) and to memory/log.md (the agent's own log).
At the end this script re-runs the checker itself on every persona, so the result does not depend
on what the agent says about its own work.
"""
import datetime
import json
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
PERSONAS = ["persona-1-hard-end.md", "persona-2-easy-end.md", "persona-3-regular.md"]
MODEL = "sonnet"
ALLOWED = ["Read", "Write", "Edit", "Glob", "Bash(python check_persona.py:*)"]


def main():
    claude = shutil.which("claude")
    if not claude:
        sys.exit("Claude Code is not installed: https://code.claude.com")
    for d in ("output", "memory"):
        shutil.rmtree(HERE / d, ignore_errors=True)
        (HERE / d).mkdir()
    run_dir = HERE / "runs" / datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    run_dir.mkdir(parents=True, exist_ok=True)
    goal = (HERE / "AGENT.md").read_text(encoding="utf-8")
    cmd = [claude, "-p", "--model", MODEL, "--output-format", "stream-json", "--verbose",
           "--permission-mode", "acceptEdits", "--allowedTools", *ALLOWED]
    print(f"agent running ({MODEL}), log: {run_dir / 'steps.jsonl'}")
    with open(run_dir / "steps.jsonl", "w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, input=goal, text=True, encoding="utf-8", cwd=HERE,
                              stdout=log, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        sys.exit(f"agent failed: {proc.stderr[-2000:]}")

    tools = 0
    for line in (run_dir / "steps.jsonl").read_text(encoding="utf-8").splitlines():
        ev = json.loads(line)
        if ev.get("type") == "assistant":
            tools += sum(1 for b in ev["message"]["content"] if b.get("type") == "tool_use")
    print(f"agent finished after {tools} tool calls")

    ok = True
    for name in PERSONAS:
        path = HERE / "output" / name
        if not path.exists():
            print(f"MISSING {name}")
            ok = False
            continue
        res = subprocess.run([sys.executable, "check_persona.py", str(path)], cwd=HERE,
                             capture_output=True, text=True)
        verdict = json.loads(res.stdout)
        print(f"{verdict['verdict']:4} {name} ({verdict['words']} words) {verdict['problems']}")
        ok &= verdict["verdict"] == "PASS"
    ok &= (HERE / "output" / "report.md").exists()
    for d in ("output", "memory"):
        shutil.copytree(HERE / d, run_dir / d)
    print("RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
