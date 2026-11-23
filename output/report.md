# Report: three personas for the Voltia challenge

Challenge: clients with an Iberdrola (i-DE) file or an electrical certificate in progress do not know what is happening with it. Details marked with an asterisk (*) in the personas are not in the research. Patterns P1 to P5 are in `patterns.md`.

## Personas and checker verdicts

| Persona | Point of the line | Main patterns | Checker verdict | Tries |
|---|---|---|---|---|
| Rafael* (`persona-1-hard-end.md`) | Hard end: file very slow or blocked | P1, P2, P3, P4 | PASS (362 words) | 1 |
| Andres* (`persona-2-easy-end.md`) | Easy end: follows many files with ease | P5, P4, P3 | PASS (374 words) | 1 |
| Elena* (`persona-3-regular.md`) | Middle: a normal file | P1, P4, P3 | PASS (390 words) | 1 |

No fix was needed, so nothing is still failing.

## What the three share (common jobs to be done)
- **Know where the file is.** When the file is open, each one wants to know if it moves (P1).
- **Know how long it will take.** Nobody can say if it is two weeks or two years (P4).
- **Not be the cause of a stop.** A missed signature or a rejected paper stops the file, and all three depend on small papers (P3).
- **Trust a named person.** All three came by recommendation and judge Voltia by honesty and by keeping its word (P5).
- **Know whom to ask.** They do not know who does what between retailer, distributor and installer (P2).

## What changes from one end of the line to the other

| | Hard end (Rafael) | Regular (Elena) | Easy end (Andres) |
|---|---|---|---|
| Wait | Months, deadline passed | Normal, a few weeks* | Short for most files |
| Feeling | Desperate, helpless | Unsure, a little worried | In control |
| Calls | Every other day | Writes when a week passes* | Only when a file is quiet |
| Who he blames | Retailer and distributor | Nobody yet | Nobody |
| Knowledge of the process | Learns it by force | Knows nothing* | Knows it* |
| Main job | Find out who is stuck and why | Know if the file moves | Know which files need him |

The need is the same at all three points: news. What changes is how loud the need is. For Rafael it is a daily emergency, for Elena it is a quiet doubt, and for Andres it is a small gap he fills himself.

## Which persona to design for first
Design for Rafael first. He has the strongest and best-documented pain (P1, P2, P3, P4), and four independent sources describe it. If the team understands his case, it covers the doubts of Elena and Andres, which are the same needs with less force. The middle persona, Elena, has the weakest evidence: the research has no direct voice of a normal client, so she is built from the figures of i-DE and from Toni's account, and the team should test her with real clients next.
