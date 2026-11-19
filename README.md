# recount

Check the arithmetic a text states about itself.

`recount` reads a text file (or stdin), finds every arithmetic claim the text
makes, recomputes each one exactly, and **exits 1 naming the lines that do not
hold**. It is the hand recount pepperoperator does in the comments, done by a
machine: same work, no pencil.

## What it checks

**A sum with its parts**

```
19 + 1 + 12 + 2 + 5 + 11 + 1 + 4 = 55        # ok
19 + 1 + 12 + 2 + 5 + 11 + 1 + 4 = 54        # line 1: recomputes to 55
```

Signed parts work too: `12 - 2 = 10`.

**A share**

```
19 of 55 (34.5%)                             # ok
19 of 55 (36.0%)                             # line 1: recomputes to 34.545455%
```

`(34.5 percent)` is understood as well. Shares are compared with a tolerance of
half the last printed decimal place (0.05 percentage points), so a fairly
rounded percent never fails.

**A before-to-after move**

```
1 in 38 (2.6%) to 2 in 55 (3.6%)             # ok
1 in 38 (2.9%) to 2 in 55 (3.6%)             # before part: recomputes to 2.631579%
```

Each side's percent is checked against its own fraction. The percents are
optional: `1 in 38 to 2 in 55` passes as a move with nothing to contradict.

Everything else is left alone. A bare number (`42`), a date, or an isolated
`55` states no arithmetic, so `recount` stays silent about it. Claims whose
arithmetic cannot be resolved (like `3 of 0`) are skipped, not guessed.

## Run it

Python 3, standard library only, nothing to install.

```sh
python3 recount.py tally.txt        # prints problems, exits 1 if any
cat tally.txt | python3 recount.py  # same, from stdin
```

Output on a bad text:

```
line 1: sum '19 + 1 + 12 + 2 + 5 + 11 + 1 + 4 = 56' states 56, recomputes to 55
line 2: share '2 of 55 (4.6%)' states 4.6%, recomputes to 3.636364%
```

Exit code: `0` if every stated claim holds (or there are none), `1` if any
claim fails. Run it before you publish and after you are doubted.

## Tests

```sh
python3 -m unittest
```

17 tests: one per claim type, plus exit codes and line naming from the CLI.

## Limits

It checks what a text *states* about its own numbers; it cannot know whether a
correctly-added number was itself wrong upstream. Sums use `+` and `-` on plain
numbers; no `*`, `/`, parentheses, or named variables. Percent-word forms other
than `%`/`percent` are not matched.
