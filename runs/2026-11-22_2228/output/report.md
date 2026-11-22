# Report: three personas for the Voltia challenge

Challenge: clients with an Iberdrola file or an electrical certificate in progress do not know what is happening with it. Patterns P1 to P5 are in output/patterns.md.

## Checker results

| Persona | Point of the line | File | Verdict | Tries | Words |
|---|---|---|---|---|---|
| Rafael, restaurant owner | Hard end (19 months) | persona-1-hard-end.md | PASS | 1 | 454 |
| Laura, solar coordinator | Easy end (~40 files) | persona-2-easy-end.md | PASS | 1 | 436 |
| Pilar, nurse | Regular (2 months) | persona-3-regular.md | PASS | 2 | 401 |

Nothing is still failing. Pilar's first version passed, but I then removed a P4 link her interview did not support. The checker then failed (P4 never used). I fixed it by linking P4 to the one thing her interview does support: a signature asked for late, during her shift. It passed on the second try. Note that P4 is the weakest pattern in Pilar's research.

## What the three share (common jobs to be done)
- Functional: know what happens next, who has the file now, and when.
- Personal: feel that someone is really looking at the file, and that it is moving.
- Social: have one person they can count on (Marc for Rafael and Pilar; a named owner for Laura's own clients).
- All three get no value from the official status or codes (P3), and all three trust a person over a company (P2).

## What changes from one end of the line to the other
- Hard end (Rafael): the wait is long and the answer is always the same. Forgotten photos (P4) turn doubt about one step into doubt about the whole job. He checks in on a fixed weekday and keeps paper.
- Regular (Pilar): the wait is short but unexplained. Her worry came only from not knowing the file was normal (P1), and her friction is calls at the wrong time.
- Easy end (Laura): she has a known next step and an owner for each file, regular news every two weeks, and a checklist against missing papers. Her calm comes from knowing, not from speed (P1, P5).
- Across the line, the distance is not in the length of the wait but in how much the person knows about it.

## Which persona to design for first
Design first for Rafael. He is the hard end, so what works for him will also cover Pilar, whose worry is the same one in a milder form. His pains hold all the patterns (P1, P2, P3, P4), and he is the client most likely to lose trust in Voltia. Laura shows what good looks like, so she works as a reference for the team and not as the first user.
