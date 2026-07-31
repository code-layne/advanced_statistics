# Unit 1 — Open Items After the Five-Convention Retrofit

**Status: open.** Recorded 2026-07-31, at the close of the Unit 1 retrofit
(vocabpar → teacherprose → work rule → namestrip → boxguard).

The retrofit itself is done and verified: 0 compile failures, `make -C unit01 all`
exits 0, blank/key page parity is 50/50, and the one-page rule holds for all 40
warm-up and exit-ticket documents. The three items below were **deliberately left
unchanged** — none of them is a convention, so none was in scope — and all three
still need doing.

---

## 1. `movenotes.py` silently deletes student content — HARD BLOCKER

**Do not run the teacherprose retrofit on Unit 2 (or any other unit) until this is
fixed.** This is not a style issue; it destroys work.

`.claude/skills/lesson-planning/scripts/movenotes.py` anchors both delimiters of
its `NOTE_RE` at the start of a line:

```python
NOTE_RE = re.compile(
    r"\n*\\begin\{teachernote\}(?:\[[^\]]*\])?\s*\n(?P<body>.*?)\n\\end\{teachernote\}\n",
    re.S)
```

A note indented inside a box (`  \begin{teachernote}`) therefore never matches its
own `\end{teachernote}`. The non-greedy body runs on to a **later** note's
terminator, and every line in between is deleted. It also migrates only the first
note per file (`sub(..., count=1)`) and refuses to re-run once the plan carries its
marker, so the leftovers look like a no-op rather than a failure.

**Damage in Unit 1:** 6 of 50 key files lost real content — whole `\end{enumerate}`
blocks, `tcolorbox`es, and an entire AP-practice section. Recovered from git.
Some of the damaged files still compiled cleanly, so **a green build is not evidence
the migration was safe.**

### The fix

Tolerate indentation on both delimiters and drop the count limit:

```python
NOTE_RE = re.compile(
    r"\n*[ \t]*\\begin\{teachernote\}(?:\[[^\]]*\])?[ \t]*\n"
    r"(?P<body>.*?)\n[ \t]*\\end\{teachernote\}[ \t]*\n",
    re.S)
```

Then also handle what that exposes:

- **Read note text from `git show HEAD:<file>`, apply removal to the working copy.**
  This recovers originals even where a previous bad run already truncated a file.
- **Dedent lifted bodies** so they sit flush in the plan.
- **Wrap bodies containing bare `\item`** in an `itemize`, or the plan hits
  "Lonely \item".
- **The plan needs `\ans`.** Notes quote expected answers, and `\ans` lives in
  `apstats-key`, which a plan must not load (it would flip every `work` block
  visible). Add `\providecommand{\ans}[1]{\textcolor{keyred}{\textbf{#1}}}` to the
  plan instead.
- **The plan needs `apstats-boxes`** for `teachernote` itself — see item 4 below for
  why that was a separate prerequisite in Unit 1.

### Verification gate before trusting any future run

For every touched key, confirm the only delta against HEAD is complete teachernote
blocks:

```python
NOTE.sub("\n", git_show_head(path))  ==  path.read_text()   # modulo whitespace
```

and confirm the note count is conserved: notes removed from keys == notes added to
plans. In Unit 1 that was 73 in, 73 out, 50/50 keys byte-clean.

A corrected implementation was used for Unit 1; it lives only in the session
scratchpad, so **the script in `.claude/skills/` is still the buggy version.**

---

## 2. Lesson 1.4 violates the no-sketch rule in three places

The convention: never ask students to draw, sketch, or construct a graph freehand.
Replace with (a) a pre-drawn figure to read, (b) a table to fill in, or (c) a
computation.

Outstanding violations, all in Unit 1 Lesson 1.4:

| File | Line | Prompt |
| --- | --- | --- |
| `unit01/lesson04/notes/main.tex` | ~220 | "Sketch a relative frequency bar chart in the box below." |
| `unit01/lesson04/activity/main.tex` | ~55 | "Construct a relative frequency bar chart below." |
| `unit01/lesson04/homework/main.tex` | ~50 | "Construct a relative frequency bar chart in the space below." |

These were **preserved, not fixed**, during the retrofit: the parity work mirrored
the keys to the blanks, and rewriting the prompts is a content change with its own
pedagogical decision behind it.

Note that the retrofit did draw the expected chart into the key's reserved box for
the activity and homework, so those two now *answer* the question instead of
showing an empty rectangle. That makes the violation easier to fix, not harder —
the target figure already exists in the key and can be moved to the blank as a
read-and-interpret prompt.

**Model to follow:** Lessons 1.5 and 1.8 were authored around this rule. 1.5's
homework is interpret-a-dotplot / complete-a-stemplot / interpret-a-histogram;
1.8's is five-number-summary and read-a-boxplot. 1.4 is the unit's only outlier.

---

## 3. `sample_test/` and `sample_test_key/` are empty

`unit01/sample_test/` and `unit01/sample_test_key/` contain only `.gitkeep`.
Unit 1 has no unit assessment. Every other Unit 1 slot is populated — 10 lessons,
all seven components each, both keys, decks in both forms.

---

## Also worth knowing (done, but non-obvious)

**Seven of ten Unit 1 lesson plans used to bypass the shared style package.** Plans
1.4–1.10 re-declared `skillbox` and re-`\definecolor`'d the palette inline instead
of loading `apstats-boxes`. The local values were byte-identical to
`shared/apstats-colors.sty`, so the switch was a drop-in — but until it was made,
any palette change in `shared/` silently would not have reached most of the unit,
and `teachernote` (defined in `-boxes`) was unavailable to those plans. All ten now
load the shared package. **Check for this pattern in other units before retrofitting
them.**
