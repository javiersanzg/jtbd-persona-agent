GOAL
Read our field research in the folder research/ and build the personas of our design challenge for Voltia, a small electrical installation company in Valencia. The challenge: clients with an Iberdrola file or an electrical certificate in progress do not know what is happening with it. Build three personas, one for each point of the line we researched: persona-1-hard-end.md (a client whose file is very slow or blocked), persona-2-easy-end.md (a user who follows many files with ease) and persona-3-regular.md (a client with a normal file). Then compare them in report.md. You are done when the three personas pass the checker and report.md exists.

TOOLS
- Read the files in research/. They are all the information you have: do not use the web and do not invent research.
- Write files only in output/ and memory/.
- Run the checker on each persona: python check_persona.py output/<file>.md. It returns PASS or FAIL with the problems it found.

EACH PERSONA
Act as a senior UX researcher who builds personas only from field research. First list the patterns you find in the research as P1 to P5 (verbatim, job to be done, insight) and save them in output/patterns.md, so every persona uses the same numbering. Each persona has these sections, in this order, as Markdown headings: the name and a one-line quote in the persona's own words; Profile; Background; Goals; Pains and frustrations; Jobs to be done (functional, personal, social); A day in their life during the wait; How they look for news today; What makes them trust or doubt an installer; Based on (a list that links each section to the patterns P1 to P5). Mark with an asterisk every detail that is not in the research. Each persona gets an invented first name that is not the name of anyone in the research. No solutions, apps or ideas: this is research, not ideation. About one page, at most 600 words, simple English.

LOOP (think, act, observe, reflect)
For each persona: think about which patterns define this point of the line, write the file, run the checker, read its verdict, and if it says FAIL fix exactly the problems it lists and run it again. Stop a persona after it passes, or after three failed fixes (then write in the report what is still failing). Use all five patterns across the three personas.

MEMORY
Keep a running log in memory/log.md: one line per step with the step number, what you did (THINK, ACT, OBSERVE or REFLECT) and the result, for example "4 | OBSERVE | checker on persona-1: FAIL, missing section Based on". Write the log as you go, not at the end.

REPORT
output/report.md: a table with the three personas and their checker verdicts and number of tries; what the three share (the common jobs to be done); what changes from one end of the line to the other; and which persona the team should design for first, with the reason, in three or four sentences. No solutions.
