#
# test_examples.py
#
from importlib import import_module
import unittest


class TestExamples(unittest.TestCase):
    def _run(self, name):
        mod = import_module("examples." + name)
        getattr(mod, "main", lambda *args, **kwargs: None)()

    def test_numerics(self):
        self._run("numerics")

    def test_tap(self):
        self._run("TAP")

    def test_roman_numerals(self):
        self._run("romanNumerals")

    def test_sexp_parser(self):
        self._run("sexpParser")

    def test_oc(self):
        self._run("oc")

    def test_delta_time(self):
        self._run("delta_time")

    def test_eval_arith(self):
        self._run("eval_arith")

    def test_select_parser(self):
        self._run("select_parser")

    def test_booleansearchparser(self):
        self._run("booleansearchparser")

    def test_rosettacode(self):
        self._run("rosettacode")

    def test_excelExpr(self):
        self._run("excelExpr")

    def test_lucene_grammar(self):
        self._run("lucene_grammar")
