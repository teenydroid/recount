#!/usr/bin/env python3
"""Tests for recount.py: run with `python3 -m unittest`."""

import subprocess
import sys
import unittest

from recount import check_line

GOOD_SUM = "19 + 1 + 12 + 2 + 5 + 11 + 1 + 4 = 55"
BAD_SUM = "19 + 1 + 12 + 2 + 5 + 11 + 1 + 4 = 54"
GOOD_SHARE = "19 of 55 (34.5%)"
BAD_SHARE = "19 of 55 (36.0%)"
GOOD_MOVE = "1 in 38 (2.6%) to 2 in 55 (3.6%)"
BAD_MOVE = "1 in 38 (2.9%) to 2 in 55 (3.6%)"


class CheckLine(unittest.TestCase):
    def test_good_sum_passes(self):
        self.assertEqual(check_line(GOOD_SUM), [])

    def test_bad_sum_named(self):
        problems = check_line(BAD_SUM)
        self.assertEqual(len(problems), 1)
        self.assertIn("recomputes to 55", problems[0])

    def test_subtraction_sum(self):
        self.assertEqual(check_line("12 - 2 = 10"), [])
        self.assertNotEqual(check_line("12 - 2 = 11"), [])

    def test_decimal_sum(self):
        self.assertEqual(check_line("1.5 + 2.5 = 4"), [])
        self.assertNotEqual(check_line("1.5 + 2.5 = 5"), [])

    def test_good_share_passes(self):
        self.assertEqual(check_line(GOOD_SHARE), [])
        self.assertEqual(check_line("2 of 55 (3.6%)"), [])

    def test_bad_share_named(self):
        problems = check_line(BAD_SHARE)
        self.assertEqual(len(problems), 1)
        self.assertIn("34.545", problems[0])

    def test_share_of_zero_denominator_skipped(self):
        self.assertEqual(check_line("3 of 0 (0%)"), [])

    def test_good_move_passes(self):
        self.assertEqual(check_line(GOOD_MOVE), [])

    def test_bad_move_percent_named(self):
        problems = check_line(BAD_MOVE)
        self.assertEqual(len(problems), 1)
        self.assertIn("before", problems[0])
        self.assertIn("recomputes to 2.631", problems[0])

    def test_move_without_percents_passes(self):
        self.assertEqual(check_line("1 in 38 to 2 in 55"), [])

    def test_percent_word_form(self):
        self.assertEqual(check_line("5 of 100 (5 percent)"), [])
        self.assertNotEqual(check_line("5 of 100 (6 percent)"), [])

    def test_no_claims_is_clean(self):
        self.assertEqual(check_line("no numbers at all here"), [])
        self.assertEqual(check_line("a bare number like 42 makes no claim"), [])
        self.assertEqual(check_line(""), [])

    def test_mixed_line_reports_each_bad_claim(self):
        problems = check_line(BAD_SUM + " and " + BAD_SHARE)
        self.assertEqual(len(problems), 2)


def _run(args, stdin_text=None):
    return subprocess.run(
        [sys.executable, "recount.py"] + args,
        input=stdin_text,
        capture_output=True,
        text=True,
    )


class Cli(unittest.TestCase):
    def test_clean_file_exits_zero(self):
        text = "day 1: %s\n\nso %s, up from %s\n" % (GOOD_SUM, GOOD_SHARE, GOOD_MOVE)
        r = _run(["sample.txt"] if False else [], stdin_text=text)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("check out", r.stdout)

    def test_dirty_file_exits_one_and_names_lines(self):
        text = "ok line: %s\nbad line: %s\n" % (GOOD_SUM, BAD_SHARE)
        r = _run([], stdin_text=text)
        self.assertEqual(r.returncode, 1)
        self.assertIn("line 2:", r.stdout)
        self.assertNotIn("line 1:", r.stdout)

    def test_file_argument(self):
        with open("sample_ok.txt", "w") as f:
            f.write(GOOD_SUM + "\n" + GOOD_SHARE + "\n")
        r = _run(["sample_ok.txt"])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("check out", r.stdout)

    def test_empty_input_is_clean(self):
        r = _run([], stdin_text="")
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
