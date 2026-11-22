# JTBD Persona Agent - Team 3 (Voltia)

Level 3 of Assessment 2 (Creativity and Innovation, EDEM). Instead of chatting with an AI, we give an agent a goal and tools, and it works on its own until the goal is reached. We review the result.

## The goal

Read our field research and build the three personas of our challenge, one for each point of the line we researched (a client with a very slow file, a user who follows many files with ease, and a client with a normal file), check each one against our quality rules, fix it until it passes, and write a report that compares them.

Challenge: Voltia clients with an Iberdrola file or an electrical certificate in progress do not know what is happening with it.

## The four parts of the agent (slide 8)

| Part | In this agent |
|---|---|
| The Goal | `AGENT.md`: the brief, measurable, with constraints (only our research, no web, no solutions, max 600 words) and a clear end: three personas that pass the checker and a report |
| The Brain | Claude (Sonnet) running in Claude Code headless mode. It decides the next step by itself |
| The Tools | read files (`research/`), write files (`output/`, `memory/`), and run `check_persona.py`, our quality checker. No web access |
| The Memory | `memory/log.md`: the agent writes one line per step (THINK, ACT, OBSERVE, REFLECT) while it works. The runner also saves the full event stream in `runs/<time>/steps.jsonl` |

## The decision loop

THINK which patterns define this persona, ACT by writing it, OBSERVE the checker verdict, REFLECT and fix exactly the problems the checker lists. It stops a persona when it passes, or after three failed fixes.

`check_persona.py` is what makes the loop honest: the agent cannot decide by itself that a persona is good. It checks that all sections are there and in order, that the five patterns are used, that a "Based on" list links each section to a pattern, that there are no solutions (this is research, not ideation), that invented details carry an asterisk, and that the persona fits one page. At the end, `run_agent.py` runs the checker again on every file, so the final verdict does not depend on what the agent says about its own work.

## How to test it

1. Install Claude Code (https://code.claude.com) and log in once with `claude`.
2. In this folder, run: `python run_agent.py`
3. Wait a few minutes. The script prints the verdict of each persona and `RESULT: PASS` or `FAIL`.
4. Read the results in `output/` (patterns, three personas, report) and the step log in `memory/log.md`.

To test the checker alone: `python check_persona.py output/persona-1-hard-end.md`

## Files

| File | What it is |
|---|---|
| `AGENT.md` | the goal and rules given to the agent |
| `run_agent.py` | starts the agent, saves its steps and checks the results |
| `check_persona.py` | the quality checker the agent uses as a tool |
| `research/field_notes.md` | our field research: the only input |
| `output/` | what the agent produced in its last run |
| `memory/log.md` | the agent's own step log |
| `runs/` | the full record of each run |

## Risks we considered (slide 7)

- Cost runaway: the agent has a fixed goal and stops after three failed fixes per persona.
- Black box: every step is logged in `memory/log.md` and `runs/`.
- Accountability: the agent only drafts. The team reviews the personas before using them, and the checker is code we wrote and can read.

## About the data

The company name is changed to Voltia, a fictional name for a small electrical installation company in Valencia, and the names of its staff are changed too. The interviews in `research/` are simulated: they were built from real conversations with the company, for a university assignment. The raw event stream of each run (`runs/<time>/steps.jsonl`) is kept locally and not published.
