#!/usr/bin/env python3
"""recount: check the arithmetic a text states about itself.

Reads a text file (or stdin), finds every arithmetic claim it states,
recomputes it, and exits 1 naming the lines that do not hold.

Claims understood:
  a sum with its parts:   19 + 1 + 12 + 2 + 5 + 11 + 1 + 4 = 55
  a share:                19 of 55 (34.5%)
  a before-to-after move: 1 in 38 (2.6%) to 2 in 55 (3.6%)

Python 3 standard library only.
"""

import argparse
import re
import sys
from fractions import Fraction

NUM = r"\d+(?:\.\d+)?"

# a + b - c + ... = total
SUM_RE = re.compile(
    r"\b(%s)((?:\s*[+\-]\s*%s)+)\s*=\s*(%s)" % (NUM, NUM, NUM)
)

# a of b (p%)   or   a of b (p percent)
SHARE_RE = re.compile(
    r"\b(%s)\s+of\s+(%s)\s*\(\s*(%s)\s*(?:%%|percent)\s*\)" % (NUM, NUM, NUM),
    re.IGNORECASE,
)

# x in n (p%) ... to ... y in m (q%)   percents optional on either side
MOVE_RE = re.compile(
    r"\b(%s)\s+in\s+(%s)\s*(?:\(\s*(%s)\s*(?:%%|percent)\s*\))?"
    r"[^.\n]{0,40}?\bto\b[^.\n]{0,40}?"
    r"\b(%s)\s+in\s+(%s)\s*(?:\(\s*(%s)\s*(?:%%|percent)\s*\))?" % (NUM, NUM, NUM, NUM, NUM, NUM),
    re.IGNORECASE,
)

PCT_TOL = Fraction(1, 20)  # half of one decimal place of percent rounding
SUM_TOL = Fraction(1, 10**9)


def _split_signed(expr):
    """Parse '19+1-2' style digit expressions, left to right, no eval."""
    tokens = re.findall(r"[+\-]|%s" % NUM, expr)
    total = Fraction(0)
    sign = Fraction(1)
    for tok in tokens:
        if tok == "+":
            sign = Fraction(1)
        elif tok == "-":
            sign = Fraction(-1)
        else:
            total += sign * Fraction(tok)
            sign = Fraction(1)
    return total


def _percent_of(num, den):
    return Fraction(100) * Fraction(num) / Fraction(den)


def check_line(line):
    """Return a list of problem descriptions for one line of text."""
    problems = []

    for m in SUM_RE.finditer(line):
        left, stated_text = m.group(1) + m.group(2), m.group(3)
        got = _split_signed(left)
        stated = Fraction(stated_text)
        if abs(got - stated) > SUM_TOL:
            problems.append(
                "sum '%s' states %s, recomputes to %s"
                % (m.group(0).strip(), stated_text, _fmt(got))
            )

    for m in SHARE_RE.finditer(line):
        part, whole, stated = m.group(1), m.group(2), m.group(3)
        if Fraction(whole) == 0:
            continue
        expected = _percent_of(part, whole)
        if abs(expected - Fraction(stated)) > PCT_TOL:
            problems.append(
                "share '%s' states %s%%, recomputes to %s%%"
                % (m.group(0).strip(), stated, _fmt(expected))
            )

    for m in MOVE_RE.finditer(line):
        a, na, pa, b, nb, pb = m.groups()
        for num, den, pct, label in ((a, na, pa, "before"), (b, nb, pb, "after")):
            if pct is None or Fraction(den) == 0:
                continue
            expected = _percent_of(num, den)
            if abs(expected - Fraction(pct)) > PCT_TOL:
                problems.append(
                    "move '%s': %s part states %s%%, recomputes to %s%%"
                    % (m.group(0).strip(), label, pct, _fmt(expected))
                )

    return problems


def _fmt(frac):
    if frac.denominator == 1:
        return str(frac.numerator)
    s = "%.6f" % float(frac)
    s = s.rstrip("0").rstrip(".")
    return s or "0"


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="recount", description="check the arithmetic claims in a text"
    )
    ap.add_argument("file", nargs="?", help="text file to check (default: stdin)")
    args = ap.parse_args(argv)

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    bad = False
    for lineno, line in enumerate(text.splitlines(), 1):
        for problem in check_line(line):
            print("line %d: %s" % (lineno, problem))
            bad = True

    if not bad:
        print("all arithmetic claims check out")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
